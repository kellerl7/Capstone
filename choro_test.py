import plotly.express as px
from urllib.request import urlopen
import plotly.graph_objs as go
import json
import geopandas as gpd
import pandas as pd

import data.data_endpoints as nyc_data
from query.api_socrata import nyc_api_read
from config import config as cfg

with open('data/nyc_boroughs.json', 'rb') as f:
    nyc_boro_json = json.load(f)

with open('data/ny_new_york_zip_codes_geo.min.json', 'rb') as f:
    nyc_zip = json.load(f)

with open('data/PUMA_nyc_2020.geojson', 'rb') as f:
    nyc_puma = json.load(f)
target = nyc_api_read(nyc_data.nyc_NFHDM, limit=5000)

df_dog = nyc_api_read(nyc_data.nyc_DOG, limit=30000)
df_dog['bite_date'] = pd.to_datetime(df_dog['dateofbite'])
df_dog['bite_year'] = df_dog['bite_date'].dt.year

# Group selection
grouping_variable = 'puma'

if grouping_variable == 'zipcode':
    map_json = nyc_zip
    map_idkey = 'properties.ZCTA5CE10'
elif grouping_variable == 'borough':
    map_json = nyc_boro_json
    map_idkey = 'properties.BoroName'
elif grouping_variable == 'puma':
    map_json = nyc_puma
    map_idkey = 'properties.'


# df_dog_summary = (df_dog
    # .groupby([
    # 'bite_year',
    # grouping_variable
    # ])['species']
    # .count()
    # .reset_index()
    # )
# df_dog_summary = df_dog_summary.rename(
    # columns={'species': 'count'}
# )

# fig = px.choropleth(
# df_dog_summary,
# geojson=map_json,
# locations=grouping_variable,
# animation_frame='bite_year',
# center=dict(lat=40.7128, lon=-74.0060),
# featureidkey=map_idkey,
# color='count',
# scope='usa',
# color_continuous_scale='Viridis',
# labels={'count': 'dog bite count'}

_cfg = cfg['plotly_config']['Bronx']
plot_df = target.loc[(target['year_published'] == 2020) & (target['goal'])
                     ]
fig = px.choropleth_map(
    plot_df,
    geojson=nyc_puma,
    featureidkey='properties.PUMA',
    locations='puma',
    color='indexscore',
    map_style='outdoors'
)
fig.show()
