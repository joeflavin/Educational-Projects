"""
Functions associated with getting weather data for bikes app
"""

import pandas as pd
from database import make_engine


def get_current_weather():
    """ Get's latest row of current weather table

        returns a dictionary of weather data
    """
    try:
        engine = make_engine()
        query = "SELECT * FROM weathercurrent ORDER BY timestamp DESC LIMIT 1"
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(e)
        data = [[0, 0, 0, 0, 'db-error', 'db-error', '01d']]
        df = pd.DataFrame(data, columns=['temp', 'feelslike', 'wind', 'direction', 'weather', 'detail', 'icon'])
        print("Database Query Failed: Using fallback dataframe")
    df["direction"] = convert_to_direction(df["direction"])
    return df.to_dict()


def convert_to_direction(degrees):
    """ Converts a direction given in degrees to compass direction in words

        degrees is an integer between 0 and 359
        returns a string
    """
    directions = ["n", "nne", "ne", "ene", "e", "ese", "se", "sse", "s", "ssw", "sw", "wsw", "w", "wnw", "nw", "nnw"]
    direction = int((degrees / 22.5) + 0.5)
    return directions[direction % 16]