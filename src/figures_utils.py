import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

from plotly.subplots import make_subplots
from config import config as cfg



def get_scattergeo(df):
    fig = go.Figure()
    fig.add_trace(
        px.scatter_map(
            df,
            lat="Latitude",
            lon="Longitude",
            color="Best Rank",
            size=np.ones(len(df)),
            size_max=8,
            opacity=1
        ).data[0]
    )
    fig.update_traces(hovertemplate=df['Cluster'])

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
        go.Choroplethmap(
            geojson=geo_data,
            locations=df['zip'],
            featureidkey='properties.ZCTA5CE10',
            colorscale=arg['colorscale'],
            z=arg['z_vec'],
            zmin=arg['min_value'],
            zmax=arg['max_value'],
            text=arg['text_vec'],
            hoverinfo="text",
            marker_opacity=marker_opacity,
            marker_line_width=marker_line_width,
            marker_line_color=marker_line_color,
            colorbar_title=arg["title"],
        )
    )

    return fig


def get_figure(
        df,
        geo_data,
        borough,
        gtype,
        year,
        geo_sectors
):
    """ref: https://plotly.com/python/builtin-colorscales/"""
    config = {"doubleClickDelay": 1000}  # set a high delay to make this easier

    _cfg = cfg["plotly_config"][borough]

    arg = dict()
    if gtype == "Market Value":
        arg["min_value"] = np.percentile(np.array(df.revised_market_value), 5)
        arg["max_value"] = np.percentile(np.array(df.revised_market_value), _cfg["maxp"])
        arg["z_vec"] = df["revised_market_value"]
        arg["text_vec"] = df["revised_market_value"] #TODO: Revise
        arg["colorscale"] = "YlOrRd"
        arg['viz_type'] = 'continuous'
        arg["title"] = "Revised Market Value ($)"

    elif gtype == "Neighborhood Cluster":
        print(df["cluster_name"].head())
        # Create our colorscale - Colors defined up to 10 clusters
        max_clusters = df["Cluster"].max()+1
        _colors = dict(list(cfg['cluster_colors'].items())[:max_clusters])

        # Visualize
        arg["min_value"] = np.percentile(np.array(df.Cluster), 5)
        arg["max_value"] = np.percentile(np.array(df.Cluster), 95)
        arg["z_vec"] = df["Cluster"]
        arg["text_vec"] = df["cluster_name"] #TODO: Revise
        arg["colorscale"] = 'Plasma'
        arg['viz_type'] = 'categorical'
        arg["title"] = "Public Facility Grouping"

    else:
        arg["min_value"] = np.percentile(np.array(df["felony_arrest_count"]), 10)
        arg["max_value"] = np.percentile(np.array(df["felony_arrest_count"]), 90)
        arg["z_vec"] = df["felony_arrest_count"]
        arg["text_vec"] = df['felony_arrest_count']
        arg["colorscale"] = "Picnic"
        arg['viz_type'] = 'continuous'
        arg["title"] = "Count of Arrests 1000' Away from Public Facility"

    # ----------------------------------------- #
    # Main Choropleth:
    fig = get_Choropleth(
        df,
        geo_data,
        arg,
        marker_opacity=0.4,
        marker_line_width=1,
        marker_line_color="#6666cc",
    )

    # -------------------------------------------- #
    """
    mapbox options:
     - 'basic'
     - 'carto-darkmatter'
     - 'carto-darkmatter-nolabels'
     - 'carto-positron'
     - 'carto-positron-nolabels'
     - 'carto-voyager'
     - 'carto-voyager-nolabels'
    """

    fig.update_layout(
        map_style='light',
        map_zoom=_cfg["zoom"],
        autosize=True,
        font=dict(color="#7FDBFF"),
        paper_bgcolor="#1f2630",
        map_center={"lat": _cfg["center"][0],
                       "lon": _cfg["center"][1]},
        #uirevision=borough,
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
    )

    # ------------------------------------------ #
    # Highlight selections:
    if geo_sectors is not None:
        fig = get_Choropleth(
            df,
            geo_sectors,
            arg,
            marker_opacity=1.0,
            marker_line_width=3,
            marker_line_color="aqua",
            fig=fig,
        )

    return fig


def price_volume_ts(price, volume, sector, colors):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # - Volume bar graph ------------------------ #
    colorsDict = {"D": "#957DAD", "S": "#AAC5E2",
                  "T": "#FDFD95", "F": "#F4ADC6"}

    for ptype in ["D", "S", "T", "F"]:
        fig.add_trace(
            go.Bar(
                x=cfg["Years"],
                y=volume.loc[volume["Property Type"] == ptype, "Count"],
                marker_color=colorsDict[ptype],
                name=ptype,
            ),
            secondary_y=False,
        )

    # - Price time series ------------------------ #
    fig.add_trace(
        go.Scatter(
            x=price.index,
            y=[p[0] for p in price[sector].values],
            marker_color="cyan",
            mode="lines+markers",
            name="Avg.Price",
        ),
        secondary_y=True,
    )

    # - Set Axes ---------------------------------- #
    fig.update_yaxes(showgrid=False)
    fig.update_yaxes(
        title_text="Sales Volume (Bar Chart)",
        secondary_y=False,
        showgrid=False
    )
    fig.update_yaxes(
        title_text="Avg. Revised Market Value ($)", secondary_y=True)

    # - Layout ------------------------------------- #
    fig.update_layout(
        title=f"{sector[0]}",
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        autosize=True,
        barmode="stack",
        margin={"l": 20, "b": 30, "r": 10, "t": 40},
        legend=dict(orientation="h", yanchor="bottom",
                    y=1, xanchor="right", x=1),
        font_color=colors["text"],
    )
    return fig


def price_ts(df, title, colors):
    fig = px.scatter(
        df,
        labels=dict(value="Average Market Value ($)",
                    variable="zip"),
        title=title
    )
    fig.update_traces(mode="lines+markers")
    fig.update_xaxes(showgrid=False)
    fig.update_layout(
        margin={"l": 20, "b": 30, "r": 10, "t": 60},
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        autosize=True,
        font_color=colors["text"],
    )
    return fig