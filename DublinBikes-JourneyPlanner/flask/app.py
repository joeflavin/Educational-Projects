from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from weather import get_current_weather
from nearbystations import top_n_closest_stations, get_distance_matrix
from database import update_station_data, update_availability_statistics, data_source, get_station_number_data
from availability_model import make_availability_forecasts

app = Flask(__name__)

#start threads for updating station data and availability statistics
update_station_data()
update_availability_statistics()


@app.route("/")
def index():
    latest_weather_data = get_current_weather()
    return render_template("index.html", wdata=latest_weather_data)


@app.route("/stations")
def stations():
    stations_data = data_source['stationdata']
    return stations_data.to_json(orient="records")


@app.route("/station/<int:stationnumber>")
def station_data(stationnumber):
    return get_station_number_data(stationnumber)

@app.route("/closeststation/<lat>/<long>")
def closest_station(lat, long):
    """Returns the closest station to a latitude/longitude point. Used
    for displaying closest station to user's location"""

    stationdata = data_source['stationdata']
    closest = top_n_closest_stations(float(lat), float(long), 1, stationdata)
    return closest.to_json(orient='records')


@app.route("/API/<node>", methods=['POST'])
def api_test(node):
    """This function returns the top 5 closest stations to a latitude/longitude provided in the
    payload of the request. The incoming data should contain a latitude, longitude, date and time
    for which user is planning journey. Return array of closest stations with live or
    forecasted availability to browser"""

    req_params = request.get_json()
    #get the current live station data
    stationdata = data_source['stationdata']
    # find 25 nearest stations by distance
    df = top_n_closest_stations(req_params['lat'], req_params['lng'], 25, stationdata)
    # get 5 closest stations by walking distance
    resp = get_distance_matrix(req_params, df)
    #if the time is not Now then use the model to update availabilities to be forecast
    if req_params['tm']!='Now':
        #update the response with the model forecasts and return weather forecast for time chosen
        resp, weather = make_availability_forecasts(resp, req_params['dt'], req_params['tm'])
    else:
        #if the time is now then do not return a weather forecast
        weather = {}

    response = {'stations':resp, 'weather':weather}

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
