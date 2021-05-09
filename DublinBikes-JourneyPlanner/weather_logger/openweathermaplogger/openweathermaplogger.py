"""
OpenWeatherMapLogger scrapes Current & Forecast data periodically
from OpenWeatherMap.org and commits data to a mySQL database

Add APIKEY & database credentials to credentials.py
"""

import datetime
import json
import logging
import threading as th
import time
import requests
from mysql.connector import connect
from openweathermaplogger.credentials import dbuser, dbpw, dbname, dbhost, APIKEY


log_level = logging.INFO
# log_level = logging.WARNING
logging.basicConfig(format='%(asctime)s %(funcName)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=log_level)

current_logger_freq = 10    # Number of minutes till re-scrape
forecast_logger_freq = 90

current_weather_uri = "http://api.openweathermap.org/data/2.5/weather?"
forecast_weather_uri = "http://api.openweathermap.org/data/2.5/forecast?"
city = 'Dublin,IE'

current_weather_query = "INSERT INTO weathercurrent values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

forecast_weather_query = """
    INSERT INTO weatherforecast values(%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE 
    temp = values(temp), 
    feelslike = values(feelslike),
    wind = values(wind),
    direction = values(direction),
    weather = values(weather),
    detail = values(detail),
    humidity = values(humidity)
    """


def connect_sql(user, pw, host, db):
    """ Setup connection to mySQL Database using mysql-connector

        Arguments are db credentials. Returns a mysql-connector connection.
    """
    return connect(user=user, password=pw, host=host, database=db)


def commit_to_db(data, query, conn):
    """ Takes prepared data points and inserts into or updates the db as appropriate

        list is a tuple or list of tuples of data points
        query is a prepared mySQL query
        conn is the connection to the db
    """
    try:
        cursor = conn.cursor()
        if type(data) is list and type(data[0]) is tuple:
            for row in data:
                cursor.execute(query, row)
        elif type(data) is tuple:
            cursor.execute(query, data)
        else:
            # todo: Do something in case where data passed to commit_to_db() is incompatible.
            pass
        conn.commit()
        cursor.close()
    except Exception as e:
        logging.warning("Error Committing Data to Database")
        print(e)


def trim_outdated_data(when, conn):
    """ Queries database and deletes row with timestamp older than given timestamp

        when is a UNIX timestamp
    """
    query = "DELETE FROM weatherforecast WHERE timestamp < " + str(when)
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
    except Exception as e:
        logging.warning("Error Trimming Outdated Data")
        print(e)


def create_table(mode, conn):
    """ Function to build table if not already existant
    """
    if mode == "forecast":
        table_query = """
                    CREATE TABLE IF NOT EXISTS weatherforecast (
                    timestamp INT PRIMARY KEY,
                    temp FLOAT, 
                    feelslike FLOAT,
                    wind FLOAT,
                    direction INT,
                    weather VARCHAR(256),
                    detail VARCHAR(256),
                    humidity INT,
                    icon VARCHAR(8)
                    )
                    """
    elif mode == "current":
        table_query = """
                    CREATE TABLE IF NOT EXISTS weathercurrent (
                    timestamp INT PRIMARY KEY,
                    temp FLOAT, 
                    feelslike FLOAT,
                    wind FLOAT,
                    direction INT,
                    weather VARCHAR(256),
                    detail VARCHAR(256),
                    humidity INT,
                    sunrise INT,
                    sunset INT,
                    icon VARCHAR(8)
                    )
                    """
    else:
        table_query = ""

    try:
        cursor = conn.cursor()
        cursor.execute(table_query)
        conn.commit()
        cursor.close()
    except Exception as e:
        logging.warning("Error Creating Table")
        print(e)


def get_last_timestamp(conn):
    """ Get the last timestamp in the current weather table
        Runs only once when Current Weather Logger begins.

        returns an integer (timestamp)
    """
    query = "SELECT timestamp FROM weathercurrent ORDER BY timestamp DESC LIMIT 1"
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        for (timestamp) in cursor:
            result = timestamp
        latest_timestamp = result[0]
        cursor.close()
    except Exception as e:
        print(e)
        latest_timestamp = 0
    return latest_timestamp


def get_owm_data(url):
    """ Get data from OpenWeatherMap API

        Returns a JSON
    """
    return requests.get(url, params={"appid": APIKEY, "q": city, "units": "metric"})


def parse_data_points(mode, text):
    """ Function to extract data from scraped OpenWeatherMap data dictionary

       mode is a string either 'current' or 'forecast'
       text is python dictionary of OpenWeatherMap API data.
       Returns a list of tuples containing data-points
    """
    if mode == "current":
        try:
            weather_data = text
            main_obj = weather_data["main"]
            wind = weather_data["wind"]
            descr = weather_data["weather"][0]
            system = weather_data["sys"]
            result = (int(weather_data["dt"]), float(main_obj["temp"]), float(main_obj["feels_like"]),
                      float(wind.get("speed")), int(wind["deg"]), (descr["main"]), (descr["description"]),
                      int(main_obj["humidity"]), int(system["sunrise"]), int(system["sunset"]), (descr["icon"])
                      )
        except Exception as e:
            logging.warning("Error in Parsing Data Points - mode:", mode)
            print(e)
            result = None
    elif mode == "forecast":
        try:
            forecast_data = text.get("list")
            forecasts = []
            for slot in forecast_data:
                main_obj = slot["main"]
                wind = slot["wind"]
                descr = slot["weather"][0]
                forecasts.append((int(slot["dt"]), float(main_obj["temp"]), float(main_obj["feels_like"]),
                                  float(wind.get("speed")), int(wind["deg"]), (descr["main"]), (descr["description"]),
                                  int(main_obj["humidity"]), (descr["icon"])
                                  ))
            result = forecasts
        except Exception as e:
            logging.warning("Error in Parsing Data Points for mode %s", mode)
            print(e)
            result = None
    else:
        logging.warning("Error Parsing Data Point - invalid mode passed")
        result = None

    return result


def current_weather_logger():
    """ Logs current weather data from OpenWeatherMap.org to database """
    mode = "current"
    retry = 30
    max_retries = 12

    conn = connect_sql(dbuser, dbpw, dbhost, dbname)
    last_timestamp = get_last_timestamp(conn)
    logging.info("Last Timestamp in Current Weather Database is %s", last_timestamp)
    conn.close()

    while True:
        try:
            logging.info("Starting Current Weather Logger")

            logging.info("Current Weather Logger Opening Connection to Database")
            conn = connect_sql(dbuser, dbpw, dbhost, dbname)

            r = get_owm_data(current_weather_uri)

            new_timestamp = json.loads(r.text).get("dt")
            retries = 1
            while new_timestamp <= last_timestamp and retries < max_retries:
                logging.info("Older Weather Data Found - sleep then retry number %s", retries)
                time.sleep(retry)
                r = get_owm_data(current_weather_uri)
                new_timestamp = json.loads(r.text).get("dt")
                if new_timestamp > last_timestamp:
                    logging.info("Newer Weather Data found after retry %s", retries)
                retries += 1
                if retries == max_retries:
                    logging.warning("Current Weather Logger max retries reached!")
            last_timestamp = new_timestamp

            # now = datetime.datetime.now()
            # write_to_file(mode, r.text, now)

            data = json.loads(r.text)
            datapoints = parse_data_points(mode, data)
            logging.info("Committing Current Weather Data to Database")
            commit_to_db(datapoints, current_weather_query, conn)
            logging.info("Current Weather Logger Closing Connection to Database")
            conn.close()
            time.sleep(60*current_logger_freq)
        except Exception as e:
            logging.warning("Error in current_weather_logger operation")
            print(e)
            time.sleep(60)


def forecast_weather_logger():
    """ Logs forecast weather data from OpenWeatherMap.org to database """
    mode = "forecast"
    while True:
        try:
            logging.info("Starting Forecast Weather Logger")
            r = get_owm_data(forecast_weather_uri)

            now = datetime.datetime.now()
            # write_to_file(mode, r.text, now)

            data = json.loads(r.text)
            datapoints = parse_data_points(mode, data)

            logging.info("Forecast Weather Logger Opening Connection to Database")
            conn = connect_sql(dbuser, dbpw, dbhost, dbname)
            logging.info("Committing Forecast Weather Data to Database")
            commit_to_db(datapoints, forecast_weather_query, conn)

            logging.info("Trimming old Forecast Weather Data from Database")
            now = int(now.timestamp())
            trim_outdated_data(now, conn)

            logging.info("Forecast Weather Logger Closing Connection to Database")
            conn.close()
            time.sleep(60*forecast_logger_freq)

        except Exception as e:
            logging.warning("Error in forecast_weather_logger operation")
            print(e)
            time.sleep(60)


def main():
    """ Make tables if needed then run loggers periodically """
    # First make tables in database if required
    try:
        logging.info("Making Tables in Database if not existent")
        conn = connect_sql(dbuser, dbpw, dbhost, dbname)
        create_table("current", conn)
        create_table("forecast", conn)
        conn.close()
    except Exception as e:
        logging.info("Error attempting to make tables in Database")
        print(e)

    # Now run Weather Loggers in threads
    log_current = th.Thread(target=current_weather_logger)      # First create the threads
    log_forecast = th.Thread(target=forecast_weather_logger)
    logging.info("Running Current Weather Logger Thread")
    log_current.start()                                         # Now start the threads
    logging.info("Running Forecast Weather Logger Thread")
    log_forecast.start()


if __name__ == '__main__':
    main()


# todo: email if error
# todo: check docStrings
# todo: check Exceptions

