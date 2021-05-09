import requests
import datetime
import time
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
import os
import traceback
from mysql.connector import MySQLConnection, Error, connect 

dbuser = ""
dbpw = ""
dbname=""
dbhost = ""

apikey = ""
api_url="https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey="+apikey  

def connect_sql(user, pw, host, db):  

    """Establishes connection with database using credentials"""

    connection = connect(user=user, password=pw, 
    host=host, database=db)  
    return connection  

def delete_static_data_point(connection, stationname): 
    
    """Deletes a row from static station for a specific station name. Used in the bulk upload 
    if we needed to refresh details in this table (change in number/address etc)"""

    qry_str = "DELETE FROM stationstatic where name={0}".format('"' + stationname + '"')
    try:
        cursor = connection.cursor()
        cursor.execute(qry_str) 
        connection.commit()
        cursor.close() 
    except Exception as e:
        print(e)

def upload_static_data_point(connection, datapoint):   
    """Uploads row corresponding to a station with details for static table in database"""

    delete_static_data_point(connection, datapoint['name']) 

    qry_str = "INSERT INTO stationstatic (name, address, latitude, longitude, number,banking,bonus) \
        VALUES ({0}, {1}, {2}, {3}, {4}, {5},{6})".format('"'+datapoint['name']+'"', '"'+datapoint['address']+'"',datapoint['position']['lat'], datapoint['position']['lng'],
    datapoint['number'],datapoint['banking'],datapoint['bonus'])  
    try:
        cursor = connection.cursor()
        cursor.execute(qry_str) 
        connection.commit()
        cursor.close() 
    except Exception as e:
        print(e)


def bulk_upload_static_data(connection): 
    
    """Function to bulk upload all stations and static data to our static table in the db"""

    static_data = requests.get(api_url)
    
    data = static_data.json()    
    
    for i in range(len(data)): 
        
        datapoint = data[i]  

        upload_static_data_point(connection, datapoint) 


def get_static_station_numbers(connection): 

    """Retrieves the stations currently present in the static table"""

    slct_static_qry="SELECT number from stationstatic" 
    cursor = connection.cursor()
    cursor.execute(slct_static_qry) 
    numbers = []
    for number in cursor:
        numbers.append(number[0])
    cursor.close()
    return numbers

def get_live_station_numbers(connection): 

    """Retrieves the station numbers currently in the live table - used to check 
    existence of station number to decide whether insert/update statement is needed."""

    current_live_qry = "SELECT stationnumber from livestationdata"
    cursor = connection.cursor()
    cursor.execute(current_live_qry) 
    numbers = []
    for number in cursor:
        numbers.append(number[0])
    cursor.close() 
    return numbers

def update_row_live_table(connection, datapoint): 

    """Updates row in the live table with the current availability"""

    try:
        updatetime = datetime.datetime.strftime(datetime.datetime.fromtimestamp(datapoint['last_update']/1000),"%Y-%m-%d %H:%M:%S")
    except:
        updatetime = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
    update_qry = "UPDATE livestationdata SET status={0}, bikestands={1}, availablestands={2}, availablebikes={3}, \
        updatetime={4} WHERE stationnumber={5}".format('"'+datapoint["status"] + '"', datapoint["bike_stands"], datapoint["available_bike_stands"],
        datapoint["available_bikes"], '"'+updatetime+'"', datapoint["number"]) 

    try:
        cursor = connection.cursor()
        cursor.execute(update_qry) 
        connection.commit()
        cursor.close() 
    except Exception as e:
        print(e)
    

def insert_row_live_table(connection, datapoint): 

    """Inserts a row in the live table with the current availability"""

    try:
        updatetime = datetime.datetime.strftime(datetime.datetime.fromtimestamp(datapoint['last_update']/1000),"%Y-%m-%d %H:%M:%S")
    except:
        updatetime = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
    insert_qry = "INSERT INTO livestationdata (stationnumber, status, bikestands, availablestands, availablebikes,updatetime) \
    VALUES ({0}, {1}, {2}, {3}, {4}, {5})".format(datapoint["number"], '"' + datapoint["status"] + '"', datapoint["bike_stands"],datapoint["available_bike_stands"],
    datapoint["available_bikes"], '"' + updatetime + '"')
    
    try:
        cursor = connection.cursor()
        cursor.execute(insert_qry) 
        connection.commit()
        cursor.close() 
    except Exception as e:
        print(e)
   
def insert_row_historical_table(connection, datapoint):
    """Inserts row in the historical table with the latest availability"""
    
    try:
        updatetime = datetime.datetime.strftime(datetime.datetime.fromtimestamp(datapoint['last_update']/1000),"%Y-%m-%d %H:%M:%S")
    except Exception as e:
        updatetime = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d %H:%M:%S")
        print(e)
    
    
    insert_qry = "INSERT INTO historicalstationdata (stationnumber, status, bikestands, availablestands, availablebikes,updatetime) \
    VALUES ({0}, {1}, {2}, {3}, {4}, {5})".format(datapoint["number"], '"' + datapoint["status"] + '"', datapoint["bike_stands"],datapoint["available_bike_stands"],
    datapoint["available_bikes"], '"' + updatetime + '"')

    try:
        cursor = connection.cursor()
        cursor.execute(insert_qry) 
        connection.commit()
        cursor.close() 
    except Exception as e:
        print(e)


def log_dynamic_data(connection):  

    """Function run every 3 minutes to retrieve station data from api, 
    update or insert for each station into the live availability table, 
    and insert data into the historical table"""

    #get the live station data from jcdeaux
    station_data = requests.get(api_url).json()  
    
    #get the station numbers we have in our static table
    current_station_numbers = get_static_station_numbers(connection)

    #get the station numbers we have in our live table
    live_station_numbers = get_live_station_numbers(connection)
    
   
    
    for datapoint in station_data:

        number = datapoint['number']  
        
        #for every station in the live data, first check if it is in our static table
        #if it is not, then add it to the static table
        if number not in current_station_numbers: 
            print("New station found.")
            upload_static_data_point(connection, datapoint)  
            print("New station uploaded.")
         
        #insert the station data into the historical table
        insert_row_historical_table(connection, datapoint) 

        #if this station exists in our live table then update that row
        #if it does not then insert a new row with it's details.
        if number in live_station_numbers: 
            update_row_live_table(connection, datapoint)
        else:
            insert_row_live_table(connection, datapoint)

def send_notification_email(err): 
    server = smtplib.SMTP('smtp.gmail.com',587) 
    server.ehlo()
    server.starttls() 
    server.login("offthechaindublin@gmail.com","overviewderbytrailsideglarepromenadegraves")
    sent_from = 'offthechaindublin@gmail.com'
    to = ['offthechaindublin@gmail.com'] 
    subject = "Logger down!"
    body="Message from the logger: I think I'm broken. Error message: {0}".format(err) 
    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)  

    server.sendmail(sent_from, to, email_text) 
    server.close()
    

def initialise_logging(connection):

    error_count = 0

    while True: 
        
        try:
            log_dynamic_data(connection)
            
        except Exception as e:

            traceback.print_exc()
            error_count+=1
            errormessage = str(e)
        
        if error_count%3==0 and error_count>0:
            send_notification_email(e)
        time.sleep(300)

        
def main():
    connection = connect_sql(dbuser, dbpw, dbhost, dbname)
    #only need to run the bulk_upload_static_data on the first go
    #bulk_upload_static_data(conn)

    error_count = 0

    while True: 
        
        #every 3 minutes try to log availability
        try:
            log_dynamic_data(connection)
            
        except Exception as e:
            #increment error count by 1
            traceback.print_exc()
            error_count+=1
            errormessage = str(e)
        
        #send email if logging process fails 3 times
        if error_count%3==0 and error_count>0:
            send_notification_email(e)
        
        time.sleep(300)
        
main()
