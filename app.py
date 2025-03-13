import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import json
import pandas as pd

import data.data_endpoints as nyc_data
from query.api_socrata import nyc_api_read

with open('data/nyc_boroughs.json', 'rb') as f:
    geojson_data = json.load(f)


# Load our crime data
nyc_arrest = nyc_data.nyc_ARREST 
#df_arrests = nyc_api_read(nyc_arrest, limit=2700000)

# Add some features to test out mapping
df_dog = nyc_api_read(nyc_data.nyc_DOG, limit = 30000) # interested - borough
df_dog['bite_date'] = pd.to_datetime(df_dog['dateofbite'])
df_dog['bite_year'] = df_dog['bite_date'].dt.year

# Summarize our data
df_dog_summary = (df_dog
                  .groupby([
                    'bite_year',
                    'borough'
                  ])['species']
                  .count()
                  .reset_index()
                  )
df_dog_summary = df_dog_summary.rename(columns = {'species': 'count'})
years = df_dog_summary['bite_year'].unique().tolist() 
# Data table:
# bite_year | borough | count

# DASHBOARD
app = dash.Dash(__name__)

fig = px.choropleth_map(
    geojson = geojson_data,
    locations=[feature['properties']['BoroName'] for feature in geojson_data['features']],
    color=[1]*len(geojson_data['features']),
    zoom=10,
    center={"lat":40.7128, "lon": -74.0060},
    opacity=0.5,
    height=600,
)

app.layout = html.Div([
    html.H1("NYC Dog Bite by Borough"),
    html.P("Select a year:"),
    dcc.RadioItems(
        id='biteyear',
        options=years,
        value=2017,
        inline=True
    ),
    dcc.Graph(
        figure=fig
    ),
])

app.run_server(debug=True)
