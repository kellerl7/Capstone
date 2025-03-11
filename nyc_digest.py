import dash
from dash import dcc, html
import plotly.express as px
import json

import data.data_endpoints as nyc_data
from query.api_socrata import nyc_api_read

with open('data/nyc_boroughs.json', 'rb') as f:
    geojson_data = json.load(f)


# Load our crime data
nyc_arrest = nyc_data.nyc_ARREST 
#df_arrests = nyc_api_read(nyc_arrest, limit=2700000)
df_dog = nyc_api_read(nyc_data.nyc_DOG, limit = 30000)

# DASHBOARD

