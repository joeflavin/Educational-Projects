"""
Functions associated with connecting to the database for the dublin bikes app
"""

import json
import pandas as pd
import threading
import time
import traceback
from sqlalchemy import create_engine
import dbinfo

data_update_frequency = 30
availability_stats_update_frequency = 60*60

data_source = {
    'stationdata':pd.DataFrame(),
    'hourly_availability_stats': {},
    'daily_availability_stats': {}
}


def make_engine():
    """Returns new SQLAlchemy Engine object associated with our database"""
    engine = create_engine("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(dbinfo.USER, dbinfo.PASSWORD, dbinfo.URI, dbinfo.PORT, dbinfo.DB), echo=True)
    return engine


def get_stations():
    """Retrieves live and static station information from db

    returns dataframe with station info
    """
    while True:
        try:
            engine = make_engine()
            query = ''' SELECT ss.number, ss.address, ss.banking, ss.latitude, ss.longitude, ls.bikestands, 
            ls.availablestands, ls.availablebikes FROM dublinbikes.stationstatic as ss, dublinbikes.livestationdata 
            as ls WHERE ss.number=ls.stationnumber AND ss.number!=507'''
            df = pd.read_sql(query, engine)
            return df

        except Exception:
            traceback.print_exc()
            time.sleep(5)


def get_availability_stats():
    """Gets bike availability stats from database

    returns dataframe with availability stats between 5am-11pm
    """
    while True:
        try:
            engine = make_engine()
            query = """SELECT stationnumber,status,bikestands,availablestands,
            availablebikes, updatetime FROM historicalstationdata"""
            df = pd.read_sql(query, engine)
            df['DayOfWeek'] = df['updatetime'].apply(lambda x: x.weekday())
            df['HourInDay'] = df['updatetime'].apply(lambda x: x.hour)
            df = df[(df['HourInDay']>=5) & (df['HourInDay']<=23)]

            return df

        except Exception:
            traceback.print_exc()
            time.sleep(10)


def start_updating_thread():
    """Creates and starts a timer object that will run the update_station_data() function

    The frequency with which timer is scheduled is controlled by the data_update_frequency variable
    """
    update_data_thread = threading.Timer(data_update_frequency, update_station_data)
    update_data_thread.daemon = True
    update_data_thread.start()


def start_updating_availability_thread():
    """Creates a timer object that will run the update_availability_statistics() function

    The frequency with which the timer is scheduled is controlled by the availability_stats_update_frequency variable
    """
    update_availability_thread = threading.Timer(availability_stats_update_frequency, update_availability_statistics)
    update_availability_thread.daemon = True
    update_availability_thread.start()


def update_station_data():
    """Updates data_source['stationdata'] object with most recent data from db"""
    station_df = get_stations()
    data_source['stationdata'] = station_df
    start_updating_thread()


def get_availability_by_hour_by_station(availability_df):
    """Uses the raw data of historical bike availability to calculate average availability by hour for each station

        Creates or updates the data_source['hourly_availability_stats'] object with an entry for each station."""

    availability_by_hour_by_station = availability_df[['stationnumber', 'HourInDay', 'availablebikes']].groupby(
        by=['stationnumber', 'HourInDay']).mean()

    availability_by_hour_by_station = availability_by_hour_by_station.reset_index()

    availability_by_hour_by_station = availability_by_hour_by_station.pivot(index="HourInDay", columns="stationnumber",
                                                                            values="availablebikes")


    hours_in_day = list(availability_by_hour_by_station.index)
    station_numbers = list(availability_by_hour_by_station.columns)

    for station_number in station_numbers:
       # this is a format which the charts.js tool will take for a bar chart
       hourly_data = {'labels': [], 'data': []}
       #for every hour in the day get the availablity for this station number at that hour
       for hour in hours_in_day:
            hourly_data['labels'].append(hour)
            hourly_data['data'].append(round(availability_by_hour_by_station.loc[hour, station_number],1))

       # update the data source with the average hourly availability data
       data_source['hourly_availability_stats'][station_number] = hourly_data


def get_availability_by_day_by_station(availability_df):
    """Uses the raw data of historical bike availability to calculate average availability by day for each station

    Creates or updates the data_source['daily_availability_stats'] object with an entry for each station."""

    weekday_mappings = {
        0: 'Sun',
        1: 'Mon',
        2: 'Tue',
        3: 'Wed',
        4: 'Thur',
        5: 'Fri',
        6: 'Sat'
    }

    availability_by_day_by_station = availability_df[['stationnumber', 'DayOfWeek', 'availablebikes']].groupby(
        by=['stationnumber', 'DayOfWeek']).mean()

    availability_by_day_by_station = availability_by_day_by_station.reset_index()

    availability_by_day_by_station = availability_by_day_by_station.pivot(index="DayOfWeek", columns="stationnumber",
                                                                          values="availablebikes")

    days_of_week = list(availability_by_day_by_station.index)
    station_numbers = list(availability_by_day_by_station.columns)

    for station_number in station_numbers:
       # this is a format which the charts.js tool will take for a bar chart
       daily_data = {'labels': [], 'data': []}
       # for every day in the week get the average availability for this station that hour
       for day in days_of_week:
            daily_data['labels'].append(weekday_mappings[day])
            daily_data['data'].append(round(availability_by_day_by_station.loc[day, station_number],1))

       # update the data source with the average daily availability data for the station
       data_source['daily_availability_stats'][station_number] = daily_data


def update_availability_statistics():
    """Update the average hourly and daily bike availabilities for each station.

    The frequency with which the data is updated is controlled by the
    availability_stats_update_frequency variable."""

    # get the historical availability
    availability_df = get_availability_stats()

    # update the data source with hourly stats for each station
    get_availability_by_hour_by_station(availability_df)

    # update the data source with daily stats for each station
    get_availability_by_day_by_station(availability_df)

    # set the timer to run again in 1 hour
    start_updating_availability_thread()


def get_station_number_data(stationnumber):
    """ Gets Data for particular station identified by number

        Called in app.py by route /station/<int:stationnumber>
        stationnumber is an integer identifying a particular station
        returns a json of current station data
    """

    all_stations = data_source['stationdata']

    # set the keys of the dictionary to be the station number
    # with each value of that dict being the details dictionary for that stations
    station_data = all_stations.set_index('number').T.to_dict()

    # get the station data for the station number requested
    this_station_data = station_data.get(stationnumber, {})

    # add in the hourly statistics to the object
    this_station_data['hourly_availability'] = data_source['hourly_availability_stats'].get(stationnumber, {'labels':[],'data':[]})

    # add in the daily statistics to the object
    this_station_data['daily_availability'] = data_source['daily_availability_stats'].get(stationnumber,
                                                                                            {'labels': [], 'data': []})

    return json.dumps(this_station_data)
