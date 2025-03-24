import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

from plotly.subplots import make_subplots
from config import config as cfg


def get_scattergeo(df):
    fig = go.Figure()
    fig.add_trace(
        px.scatter_mapbox(
            df,
            lat="Latitude", lon="Longitude",
            color="Best Rank",
            size=np.ones(len(df)),
            size_max=8,
            opacity=1
        ).data[0]
    )
    fig.update_traces(hovertemplate=df['Info'])

    return fig


def get_Choropleth(
    df,
    geo_data,
    arg,
    marker_opacity,
    marker_line_width,
    marker_line_color,
    fig=None
):
    if fig is None:
        fig = go.Figure()

    fig.add_trace(
        go.Choroplethmapbox(
            geojson=geo_data,
            locations=df['zipcode'],
            featureidkey='properties.PUMA'
        )
    )


)
