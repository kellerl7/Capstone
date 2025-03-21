import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import json
import pandas as pd

import data.data_endpoints as nyc_data
from query.api_socrata import nyc_api_read

with open('data/nyc_boroughs.json', 'rb') as f:
    json_borough = json.load(f)

with open('data/ny_new_york_zip_codes_geo.min.json', 'rb') as f:
    json_zipcode = json.load(f)

with open('data/PUMA_nyc_2020.geojson', 'rb') as f:
    json_puma = json.load(f)

# Load our crime data
df_arrests = nyc_api_read(nyc_data.nyc_ARREST, limit=2700000)
df_dog = nyc_api_read(nyc_data.nyc_DOG, limit=30000)  # interested - borough
df_target = nyc_api_read(nyc_data.nyc_NFHDM, limit=5000)

""" ---------------------------------------------------------------
DATA PREPROCESS
-------------------------------------------------------------------"""

# Dog bite
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
df_dog_summary = df_dog_summary.rename(columns={'species': 'count'})
years = df_dog_summary['bite_year'].unique().tolist()

# ------------
# Arrests
# Key to map "arrest_boro"
boro_key = pd.DataFrame(
    {"boro_code": ["B", "S", "K", "M", "Q"],
     "borough": ["Bronx", "Staten Island", "Brooklyn", "Manhattan", "Queens"]
     }
)

df_arrests = pd.merge(
    df_arrests,
    boro_key,
    how="left",
    left_on="arrest_boro",
    right_on="boro_code",
    copy=False
)

# Key to map "law_cat_cd"
law_code_key = pd.DataFrame({
    "law_cat_cd": ["F", "M", "V"],
    "law_cat_idx": [3, 2, 1]
}
)

df_arrests = pd.merge(
    df_arrests,
    law_code_key,
    on="law_cat_cd",
    how="left",
    copy=False
)

arrest_codes = (df_arrests
                .loc[:, ['law_cat_idx', 'ky_cd', 'ofns_desc']]
                .drop_duplicates().dropna()
                )

arrest_codes = arrest_codes.sort_values(
    ['law_cat_idx', 'ky_cd'], ascending=False)
arrest_codes['violation_ky_cd'] = arrest_codes['law_cat_idx'].astype(
    str) + '_' + arrest_codes['ky_cd'].astype(str)
arrest_codes['violation_idx'] = pd.factorize(
    arrest_codes['violation_ky_cd'])[0] + 1

df_arrests = pd.merge(
    df_arrests,
    arrest_codes[['ky_cd', 'violation_idx']],
    on='ky_cd',
    how='left'
)

# ---------------------------
# Target - Neighborhood Financial Helath Digital Mapping
df_nfhdm_summary = (df_target
                    .groupby('borough')['indexscore']
                    .mean()
                    .reset_index()
                    )

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
    dcc.RadioItems(
        id='dataset',
        options=['dog bites', 'arrests', 'health index'],
        value='arrests'
    ),
    dcc.Graph(
        figure={},
        id='final-map-chart',
        style={'height': '80vh', 'width': '100%'}
    ),
])


@callback(
    Output(component_id='final-map-chart', component_property='figure'),
    Input(component_id='dataset', component_property='value')
)
def update_graph(dataset_chosen):
    if dataset_chosen == "arrests":
        fig = px.scatter_map(
            df_arrests,
            lat='latitude',
            lon='longitude',
            color='violation_idx',
            map_style='carto-darkmatter'
        )
    else:
        if dataset_chosen == "dog bites":
            df_plot = df_dog_summary
            color_scale = "count"
            json_id = 'properties.BoroName'
        elif dataset_chosen == "health index":
            df_plot = df_nfhdm_summary
            color_scale = "indexscore"
            json_id = 'properties.BoroName'

        fig = px.choropleth_map(
            df_plot,
            geojson=json_borough,
            locations="borough",
            featureidkey=json_id,
            center={'lat': 40.71, "lon": -74.01},
            zoom=7,
            color=color_scale,
        )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
