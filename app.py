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
        id="graph"
    ),
])

@app.callback(
    Output("graph", "figure"),
    Input("biteyear", "value")
)
def merge_geo_df(bite_year):
    for feature in geojson_data['features']:
        boro_name = feature['properties']['BoroName']
        dog_bite_count = (
            df_dog_summary[(
                df_dog_summary['borough'] == boro_name
        ) & (df_dog_summary['bite_year'] == bite_year)]['count']
            .values
        )
        feature['properties']['BiteCount'] = dog_bite_count[0] if dog_bite_count else 0

    fig = px.choropleth(
        df_dog_summary[df_dog_summary==bite_year],
        geojson=geojson_data,
        color="count",
        locations="borough",
        featureidkey="properties.BoroName",
        projection="mercator",
        range_color=[0, 6500]
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    return fig


app.run_server(debug=True)
