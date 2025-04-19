import logging
import random
import sys
import time
import warnings

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State
from flask_caching import Cache

from config import config as cfg
from figures_utils import (
	get_average_price_by_year,
	get_figure,
	price_ts,
	price_volume_ts,
)
from utils import (
	get_train_df,
	return_market_value,
	get_pca_with_clusters,
	get_geo_json_zips,
	get_borough_zips,
	get_borough_geo_zips,
)

warnings.filterwarnings("ignore")


logging.basicConfig(format=cfg["logging format"], level=logging.INFO)
logging.info(f"System: {sys.version}")


""" ----------------------------------------------------------------------------
 App Settings
---------------------------------------------------------------------------- """
boroughs = [
	"Bronx",
	"Staten Island",
	"Brooklyn",
	"Manhattan",
	"Queens",
	"NYC"
]

colors = {"background": "#1F2630", "text": "#7FDBFF"}

NOTES = """
    **Notes:**
    1. Property type "Other" is filtered from the house price data.
    2. School ranking (2018-2019) is the best of GCSE and A-Level rankings.
    3. GCSE ranking can be misleading - subjects like
    Classics and Latin are excluded from scoring,
    unfairly penalising some schools.

    **Other data sources:**
    - [OpenStreetMap](https://www.openstreetmap.org)
    - [Postcode regions mapping](https://www.whichlist2.com/knowledgebase/uk-postcode-map/)
    - [Postcode boundary data](https://www.opendoorlogistics.com/data/)
    from [www.opendoorlogistics.com](https://www.opendoorlogistics.com)
    - Contains Royal Mail data © Royal Mail copyright and database right 2015
    - Contains National Statistics data © Crown copyright and database right 2015
    - [School 2019 performance data](https://www.gov.uk/school-performance-tables)
    (Ranking scores: [Attainment 8 Score](https://www.locrating.com/Blog/attainment-8-and-progress-8-explained.aspx)
    for GCSE and
    [Average Point Score](https://dera.ioe.ac.uk/26476/3/16_to_18_calculating_the_average_point_scores_2015.pdf)
    for A-Level)
"""

t0 = time.time()

""" ----------------------------------------------------------------------------
Data Pre-processing
---------------------------------------------------------------------------- """
train_df = get_train_df()
summary_market_value = return_market_value()
geo_zip_data = get_geo_json_zips()
zip_dict = get_borough_zips()
geo_zip_key_data = get_borough_geo_zips(geo_zip_data)
# ---------------------------------------------

# initial values:
initial_year = 2016
initial_borough = "NYC"

borough_filter = zip_dict[initial_borough]
initial_zip = random.choice(borough_filter)
#initial_geo_sector = [regional_geo_sector[initial_region][initial_sector]]

empty_series = pd.DataFrame(np.full(len(cfg["Years"]), np.nan), index=cfg["Years"])
empty_series.rename(columns={0: ""}, inplace=True)


""" ----------------------------------------------------------------------------
 Dash App
---------------------------------------------------------------------------- """
# stylesheet with the .dbc class to style  dcc, DataTable and AG Grid components with a Bootstrap theme
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
# if using the vizro theme
vizro_bootstrap = "https://cdn.jsdelivr.net/gh/mckinsey/vizro@main/vizro-core/src/vizro/static/css/vizro-bootstrap.min.css?v=2"

app = dash.Dash(__name__, 
				meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
				],
				external_stylesheets=[vizro_bootstrap])


server = app.server  # Needed for gunicorn
cache = Cache(
	server,
	config={
		"CACHE_TYPE": "filesystem",
		"CACHE_DIR": cfg["cache dir"],
		"CACHE_THRESHOLD": cfg["cache threshold"],
	},
)
app.config.suppress_callback_exceptions = True

# --------------------------------------------------------#

app.layout = html.Div(
	id="root",
	children=[
		# Header -------------------------------------------------#
		html.Div(
			id="header",
			children=[
				html.Div(
					[
						html.Div(
							[html.H1(children="Pricing Value of NYC - Understood through Public Facilities")],
							style={
								"display": "inline-block",
								"width": "74%",
								"padding": "10px 0px 0px 20px",  # top, right, bottom, left
							},
						),
						html.Div(
							[html.H6(children="Created with")],
							style={
								"display": "inline-block",
								"width": "10%",
								"textAlign": "right",
								"padding": "0px 20px 0px 0px",  # top, right, bottom, left
							},
						),
						html.Div(
							[
								html.A(
									[
										html.Img(
											src=app.get_asset_url("dash-logo.png"),
											style={"height": "100%", "width": "100%"},
										)
									],
									href="https://plotly.com/",
									target="_blank",
								)
							],
							style={
								"display": "inline-block",
								"width": "14%",
								"textAlign": "right",
								"padding": "0px 10px 0px 0px",
							},
						),
					]
				),
			],
		),
		html.Div(
			[
				dcc.Link(
					f"HM Land Registry Price Paid Data from 01 Jan 1995 to {cfg['latest date']}",  # noqa: E501
					href="https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads",  # noqa: E501
					target="_blank",
					# style={'color': colors['text']}
				)
			],
			style={"padding": "5px 0px 5px 20px"},
		),
		# Selection control -------------------------------------#
		html.Div(
			[
				html.Div(
					[
						dcc.Dropdown(
							id="borough",
							options=[{"label": r, "value": r} for r in boroughs],
							value=initial_borough,
							clearable=False,
							style={"color": "black"},
						)
					],
					style={
						"display": "inline-block",
						"padding": "0px 5px 10px 15px",
						"width": "15%",
					},
					className="one columns",
				),
				html.Div(
					[
						dcc.Dropdown(
							id='zipcode',
							options=[
								{"label": s, "value": s}
								for s in zip_dict[initial_borough]
							],
							value=[initial_zip],
							clearable=True,
							multi=True,
							style={"color": "black"},
						),
					],
					style={
						"display": "inline-block",
						"padding": "0px 5px 10px 0px",
						"width": "40%",
					},
					className="seven columns",
				),
				html.Div(
					[
						dbc.RadioItems(
							id="graph-type",
							options=[
								{"label": i, "value": i}
								for i in ["Market Value", "Model Error", "Neighborhood Cluster"]
							],
							value="Market Value",
							inline=True,
						)
					],
					style={
						"display": "inline-block",
						"textAlign": "center",
						"padding": "5px 0px 10px 10px",
						"width": "33%",
					},
					className="two columns",
				),
			],
			style={"padding": "5px 0px 10px 20px"},
			className="row",
		),
		# App Container ------------------------------------------#
		html.Div(
			id="app-container",
			children=[
				# Left Column ------------------------------------#
				html.Div(
					id="left-column",
					children=[
						html.Div(
							id="choropleth-container",
							children=[
								html.Div(
									[
										html.Div(
											[
												html.H5(id="choropleth-title"),
											],
											style={
												"display": "inline-block",
												"width": "64%",
											},
											className="eight columns",
										),
									]
								),
								dcc.Graph(id="choropleth"),
							],
						),
					],
					style={
						"display": "inline-block",
						"padding": "20px 10px 10px 40px",
						"width": "59%",
					},
					className="seven columns",
				),
				# Right Column ------------------------------------#
				# html.Div(
				# 	id="graph-container",
				# 	children=[
				# 		html.Div(
				# 			[
				# 				dcc.Checklist(
				# 					id="property-type-checklist",
				# 					options=[
				# 						{"label": "F: Flats/Maisonettes", "value": "F"},
				# 						{"label": "T: Terraced", "value": "T"},
				# 						{"label": "S: Semi-Detached", "value": "S"},
				# 						{"label": "D: Detached", "value": "D"},
				# 					],
				# 					value=["F", "T", "S", "D"],
				# 					labelStyle={"display": "inline-block"},
				# 					inputStyle={"margin-left": "10px"},
				# 				),
				# 			],
				# 			style={"textAlign": "right"},
				# 		),
				# 		html.Div([dcc.Graph(id="price-time-series")]),
				# 	],
				# 	style={
				# 		"display": "inline-block",
				# 		"padding": "20px 20px 10px 10px",
				# 		"width": "39%",
				# 	},
				# 	className="five columns",
				# ),
			],
			className="row",
		),
		# Notes and credits --------------------------#
		html.Div(
			[
				html.Div(
					[dcc.Markdown(NOTES)],
					style={
						"textAlign": "left",
						"padding": "0px 0px 5px 40px",
						"width": "69%",
					},
					className="nine columns",
				),
				html.Div(
					[
						dcc.Markdown(
							"© 2020 Ivan Lai "
							+ "[[Blog]](https://www.ivanlai.project-ds.net/) "
							+ "[[Email]](mailto:ivanlai.uk.2020@gmail.com)"
						)
					],
					style={
						"textAlign": "right",
						"padding": "10px 20px 0px 0px",
						"width": "29%",
					},
					className="three columns",
				),
			],
			className="row",
		),
	],
)

""" ----------------------------------------------------------------------------
 Callback functions:
 Overview:
 region, year, graph-type, school -> choropleth-title
 region, year -> postcode options
 region, year, graph-type, postcode-value, school -> choropleth
 postcode-value, property-type-checklist -> price-time-series
 choropleth-clickData, choropleth-selectedData, region, postcode-State -> postcode-value
---------------------------------------------------------------------------- """


# Update choropleth-title with year and graph-type update
@app.callback(
	Output("choropleth-title", "children"),
	[
		Input("borough", "value"),
		Input("graph-type", "value"),
	],
)
def update_map_title(borough, gtype):
	if gtype == "Market Value":
		return f"Avg market value for properties in a given borough {borough}, {initial_year}"
	elif gtype == "Model Error":
		return (
			f"Shows the average model error when predicting the market value in {borough}, {initial_year}"
		)
	else:
		return f"The given cluster breakdown for the different zipcodes in the borough {borough}, {initial_year}"


# Update zipcode dropdown options with region selection
@app.callback(
	Output("zipcode", "options"),
	[
		Input("borough", "value"),
	]
)
def update_region_postcode(borough):
	return [
		{"label": s, "value": s}
		for s in zip_dict[borough]
	]


# Update choropleth-graph with year, region, graph-type update & sectors
@app.callback(
	Output("choropleth", "figure"),
	[
		Input("borough", "value"),
		Input("graph-type", "value"),
		Input("zipcode", "value"),
	],
)  # @cache.memoize(timeout=cfg['timeout'])
def update_Choropleth(borough, gtype, zips):
	# Graph type selection------------------------------#
	# Graph options: "Market Value", "Model Error", "Neighborhood Cluster"
	if gtype in ["Market Value", "Neighborhood Cluster"]:
		df = summary_market_value.loc[
			(summary_market_value['year'] == initial_year) &
			(summary_market_value['borough'] == borough if borough != 'NYC' else True)
		]
	else:
		#TODO: Switch dataset to model output to graph error
		#df = regional_percentage_delta_data[year][region]
		pass

	# For high-lighting mechanism ----------------------#
	changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
	geo_sectors = dict()

	# If we are still looking at the same borough,
	# Update our list and zipcodes to highlight
	# Use our geojson by zip to get a filtered list ready by our filter
	if "borough" not in changed_id:
		for k in geo_zip_data.keys():
			if k != "features":
				geo_sectors[k] = geo_zip_data[k]
			else:
				geo_sectors[k] = [
					geo_zip_key_data[z]
					for z in zips
				]

	# Updating figure ----------------------------------#
	fig = get_figure(
		df,
		geo_zip_data,
		borough,
		gtype,
		initial_year, # placeholder if we want to change years later
		geo_sectors
	)

	return fig


# # Update price-time-series with postcode updates and graph-type
# @app.callback(
# 	Output("price-time-series", "figure"),
# 	[Input("postcode", "value"), Input("property-type-checklist", "value")],
# )
# @cache.memoize(timeout=cfg["timeout"])
# def update_price_timeseries(sectors, ptypes):
# 	if len(sectors) == 0:
# 		return price_ts(empty_series, "Please select postcodes", colors)

# 	if len(ptypes) == 0:
# 		return price_ts(
# 			empty_series, "Please select at least one property type", colors
# 		)

# 	# --------------------------------------------------#
# 	df = price_volume_df.iloc[
# 		np.isin(price_volume_df.index.get_level_values("Property Type"), ptypes),
# 		np.isin(price_volume_df.columns.get_level_values("Sector"), sectors),
# 	]
# 	df.reset_index(inplace=True)
# 	avg_price_df = get_average_price_by_year(df, sectors)

# 	if len(sectors) == 1:
# 		index = [(a, b) for (a, b) in df.columns if a != "Average Price"]
# 		volume_df = df[index]
# 		volume_df.columns = volume_df.columns.get_level_values(0)
# 		return price_volume_ts(avg_price_df, volume_df, sectors, colors)
# 	else:
# 		title = f"Average prices for {len(sectors)} sectors"
# 		return price_ts(avg_price_df, title, colors)


# ----------------------------------------------------#


# Update postcode dropdown values with clickData, selectedData and region
@app.callback(
	Output("zipcode", "value"),
	[
		Input("choropleth", "clickData"),
		Input("choropleth", "selectedData"),
		Input("borough", "value"),
		State("zipcode", "value"),
		State("choropleth", "clickData"),
	],
)
def update_zipcode_dropdown(
	clickData, selectedData, borough, zipcodes, clickData_state
):
	# Logic for initialisation or when Schoold sre selected
	if dash.callback_context.triggered[0]["value"] is None:
		return zipcodes

	changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]

	if len(zipcodes) > 0 or "zipcode" in changed_id:
		clickData_state = None
		return []

	# --------------------------------------------#
	print(f"clickData: {clickData['points']}")
	if "borough" in changed_id:
		zipcodes = []
	elif "selectedData" in changed_id:
		zipcodes = [D["location"] for D in selectedData["points"][: cfg["topN"]]]
	elif clickData is not None and "location" in clickData["points"][0]:
		z = clickData["points"][0]["location"]
		if z in zipcodes:
			zipcodes.remove(z)
		elif len(zipcodes) < cfg["topN"]:
			zipcodes.append(z)
	print(f"EOF zipcode list: {zipcodes}")
	return zipcodes


# ----------------------------------------------------#

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

logging.info(f"Data Preparation completed in {time.time() - t0:.1f} seconds")

# ------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------#

if __name__ == "__main__":
	logging.info(sys.version)

	# If running locally in Anaconda env:app
	if "conda-forge" in sys.version:
		app.run_server(debug=True)

	# If running on AWS/Pythonanywhere production
	else:
		app.run_server(port=8050, host="0.0.0.0", debug=True)

""" ----------------------------------------------------------------------------
Terminal cmd to run:
gunicorn app:server -b 0.0.0.0:8050
or
python app.py
---------------------------------------------------------------------------- """
