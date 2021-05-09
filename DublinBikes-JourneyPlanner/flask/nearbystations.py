import math
import pandas as pd
import googlemaps
from flask import jsonify


API_KEY = ''

def distance_between_points(lat1, long1, lat2, long2):
#def top_n_closest_stations(latitude, longitude, n):

    """Finds the distance between two pairs of latitude/longitude points"""

    earth_radius = 6373.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    long1 = math.radians(long1)
    long2 = math.radians(long2)

    long_diff = long2-long1
    lat_diff = lat2 - lat1

    #USING THE HAVERSINE FORMULA
    term1 = math.sin(lat_diff / 2)**2
    term2 = math.cos(lat1) * math.cos(lat2) * math.sin(long_diff / 2)**2

    a = term1 + term2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = earth_radius * c

    return round(distance, 2)

def top_n_closest_stations(latitude, longitude, n, stationdata):

    """Takes a latitude and longitude coordinate and returns
    the top n closest stations sorted by increasing distance"""

    stationdata['distance_from_point_km'] = stationdata[['latitude','longitude']].apply(lambda x:
                                                        distance_between_points(x[0],x[1], latitude, longitude), axis=1)

    stationdata = stationdata.sort_values(by='distance_from_point_km', ascending=True)

    stationdata = stationdata.head(n)

    temp = stationdata.to_dict(orient="records")
    return stationdata


def get_distance_matrix(lat_lng, data):
    """calculates walking distance between latlng location and 25 nearest stations by walking distance

     returns sorted list of objects with station name, number, road distance, and availabililty"""

    data['lat_lngs'] = data.apply(lambda row: {'lat': row.latitude, 'lng': row.longitude}, axis=1)
    temp = data.to_dict(orient="records")
    client = googlemaps.Client(key=API_KEY)
    i=0

    #call API and save results
    for location in temp:
        matrix = client.distance_matrix(origins=lat_lng, destinations=location, mode="walking")
        temp[i]['distance'] = matrix['rows'][0]['elements'][0]['distance']['text']
        temp[i]['value'] = matrix['rows'][0]['elements'][0]['distance']['value']
        #temp[i]['duration'] = matrix['rows'][0]['elements'][0]['duration']['text']
        i += 1

    #order station data by nearest to start and return five nearest to frontend
    sorted_temp = sorted(temp, key=lambda x: x['value'])
    sorted_temp = sorted_temp[0:5]
    keys_to_keep = ['address', 'number', 'distance', 'availablebikes', 'availablestands']
    sorted_temp = [{k: v for k, v in d.items() if k in keys_to_keep} for d in sorted_temp]

    return sorted_temp