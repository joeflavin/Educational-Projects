import pickle
from database import make_engine
import sklearn
import datetime
import pandas as pd
from weather import get_current_weather

months = ["Jan","Feb","Mar","Apr","May","June","July","Aug", "Sep","Oct","Nov","Dec"]

default_station_model = 31

#LOAD THE MODEL FEATURE NAMES
with open('model/list_features.pkl','rb') as f:
    feature_list = pickle.load(f)

#LOAD THE MODEL
with open('model/decision_tree_models.pkl','rb') as f:
    station_models = pickle.load(f)

def make_availability_forecasts(resp, dt, tm):

    #create a datetime object from the selected date and time strings
    date_time = construct_datetime(dt, tm)
    #get the weather forecast closest to this datetime
    weather_forecast = get_weather_forecast(date_time)

  
    if len(weather_forecast)>0:
        weather = {'weather':list(weather_forecast['weather'])[0], 'detail':list(weather_forecast['detail'])[0].title(), 'icon':list(weather_forecast['icon'])[0], 'temp':list(weather_forecast['temp'])[0]}
    else:
        weather = {}

    for i in range(len(resp)):

        #station object initially has live available bikes and available stands
        station_obj = resp[i]

        station_number = station_obj['number']

        #format the model input for this station to be correct for the model
        model_input = format_model_input(station_number, date_time, weather_forecast)

        station_model = station_models.get(station_number, station_models.get(default_station_model))

        #use the model to predict the forecast for % bikes available
        predicted_percentage_bike_availability = station_model.predict(model_input)[0]

        total_stands = station_obj['availablestands'] + station_obj['availablebikes']

        #use the predicted % and the total number of stands to get predicted bikes/stands available
        predicted_bikes_available = int(predicted_percentage_bike_availability*total_stands)

        predicted_stands_available = total_stands - predicted_bikes_available

        #update the station object availability with the forecasts
        station_obj['availablebikes'] = predicted_bikes_available

        station_obj['availablestands'] = predicted_stands_available

        resp[i] = station_obj

    return resp, weather

def encode_weather_details(df):
    df['light_rain'] = df['weather'].apply(lambda x: 1 if x in ['Drizzle', 'Fog', 'Mist'] else 0)
    df['rain'] = df['weather'].apply(lambda x: 1 if x in ['Rain', 'Snow'] else 0)
    df['clear'] = df['weather'].apply(lambda x: 1 if x in ['Clear', 'Clouds'] else 0)
    return df

def format_model_input(station_number, date_time, weather_forecast):

    """Formats an array using the correct model features in the correct order."""

    input_df = pd.DataFrame()

    input_df['stationnumber'] = [station_number]

    input_df['Hour'] = [str(date_time.hour)]

    input_df['Weekday'] = [str(date_time.weekday())]

    input_df = input_df.reset_index(drop=True)

    weather_forecast = weather_forecast.reset_index(drop=True)

    input_df = pd.concat([input_df, weather_forecast], axis=1)

    input_df = encode_weather_details(input_df)

    input_df = input_df[feature_list].values

    return input_df

def construct_datetime(dt, tm):
    year = datetime.datetime.now().year

    if dt=="Today":
        month = datetime.datetime.today().month
        day = datetime.datetime.today().day
    else:
        month = months.index(dt[dt.rfind(" ") + 1:]) + 1
        day = int(dt[dt.find(" ") + 1:dt.rfind(" ")])

    hour = datetime.datetime.strptime(tm, "%H:%M").hour
    minute = datetime.datetime.strptime(tm, "%H:%M").minute
    date_time = datetime.datetime(year, month, day, hour, minute)
    return date_time


def get_weather_forecast(dt):

    """Takes input dt (a datetime) and returns the weather forecast
    from our database for the time closest to this datetime."""

    engine = make_engine()

    query = """select * from weatherforecast"""

    df = pd.read_sql(query, engine)

    df['updatetime'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x))

    closest_time = min(list(df['updatetime']), key=lambda x: abs((x-dt).total_seconds()))

    weather = df[df['updatetime']==closest_time]

    return weather
