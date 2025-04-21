import plotly.express as px
import plotly.graph_objs as go
import json
import geopandas as gpd
import pandas as pd

try:
    import preprocess.data_preprocess as data_pre
except ModuleNotFoundError as e:
    print(e)

# Load in our zipcode data
with open('data/ny_new_york_zip_codes_geo.min.json', 'rb') as f:
    nyc_zips = json.load(f)

# Load in data we want to show
map_df, loadings = data_pre.main(
    'data/public_fac.csv',
    'data/prop_values.csv',
    n_pca=15,
    k_cluster=5)

# Define our mapping variables
map_json = nyc_zips
map_idkey = 'properties.ZCTA5CE10'

# Create our map
fig = px.choropleth_map(
    map_df,
    geojson=map_json,
    featureidkey=map_idkey,
    locations='zip',
    color='revised_market_value',
    map_style='outdoors'
)
fig.show()