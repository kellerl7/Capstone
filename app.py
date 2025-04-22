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
	get_figure,
)
from utils import (
	get_model_input_df,
	get_pca_with_clusters,
	get_geo_json_zips,
	get_borough_zips,
	get_borough_geo_zips,
	get_arrests_outside_buffer,
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

    1. All data shown is for the year 2016 due to limitation of Market Value Data
    2. Arrest data is shown for area 1000' outside any facility noted as "public"
    3. Data is absolute and not normalized for population or any other metric
    4. Template and base design inspired by:
    [ivanlai - UK Housing prices](https://github.com/ivanlai/Plotly-App-UK-houseprices)
    
    **Other data sources:**
    - [OpenStreetMap](https://www.openstreetmap.org)
    - [NYC Zipcode data](https://github.com/OpenDataDE/State-zip-code-GeoJSON)
    - [NYC Zipcode and Borough data](https://www.nycbynatives.com/nyc_info/new_york_city_zip_codes.php)
    from NYC By Natives
    - [NYC Arrest data](https://data.cityofnewyork.us/Public-Safety/NYPD-Arrests-Data-Historic-/8h9b-rp9u/about_data)
    - [NYC Property Value data](https://data.cityofnewyork.us/City-Government/Revised-Notice-of-Property-Value-RNOPV-/8vgb-zm6e/about_data)
    - [NYC Facility Information](https://data.cityofnewyork.us/City-Government/Facilities-Database/ji82-xba5/about_data)

"""

t0 = time.time()

""" ----------------------------------------------------------------------------
Data Pre-processing
---------------------------------------------------------------------------- """
summary_market_value = get_model_input_df()
geo_zip_data = get_geo_json_zips()
geo_zip_key_data = get_borough_geo_zips(geo_zip_data)
zip_dict = get_borough_zips(geo_zip_key_data)
arrest_data = get_arrests_outside_buffer()

# ---------------------------------------------

# initial values:
initial_year = 2016
initial_borough = "NYC"

borough_filter = zip_dict[initial_borough]
initial_zip = random.choice(borough_filter)
#initial_geo_sector = [regional_geo_sector[initial_region][initial_sector]]

empty_series = pd.DataFrame(np.full(len(cfg["arrest_types"]), np.nan), index=list(cfg["arrest_types"].values()))
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
					"A property's market value as of 2016",  # noqa: E501
					href="https://data.cityofnewyork.us/City-Government/Revised-Notice-of-Property-Value-RNOPV-/8vgb-zm6e/about_data",  # noqa: E501
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
								for i in ["Market Value", "Arrests outside 1000'", "Neighborhood Cluster"]
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
						"width": "100%",
					},
					className="seven columns",
				),
				# Right Column ------------------------------------#
				# ***
				# Option to add in a graph column - not implemented
				# ***
				# html.Div(
				# 	id="graph-container",
				# 	children=[
				# 		html.Div(
				# 			[
				# 				dcc.Checklist(
				# 					id="arrest-type-checklist",
				# 					options=[
				# 						{"label": "F: Felony", "value": "F"},
				# 						{"label": "M: Misdemeanor", "value": "M"},
				# 						{"label": "V: Violation", "value": "V"},
				# 						{"label": "I: Other", "value": "I"},
				# 					],
				# 					value=["F", "M", "V", "I"],
				# 					labelStyle={"display": "inline-block"},
				# 					inputStyle={"margin-left": "10px"},
				# 				),
				# 			],
				# 			style={"textAlign": "right"},
				# 		),
				# 		html.Div([dcc.Graph(id="arrest-crime-count")]),
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
							"University of Michigan - Masters of Data Science Project |"
							+ " [Github link](https://github.com/kellerl7/Capstone) "
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
	elif gtype == "Arrests outside 1000'":
		return (
			f"Shows the average number of FELONY arrests when predicting the market value in {borough}, {initial_year}"
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
	# Graph options: "Market Value", "Arrests outside 1000'", "Neighborhood Cluster"
	if gtype in ["Market Value", "Neighborhood Cluster", "Arrests outside 1000'"]:
		df = summary_market_value.loc[
			(summary_market_value['year'] == initial_year) &
			(summary_market_value['borough'] == borough if borough != 'NYC' else True)
		]
	else:
		# Option to switch datasets if pick a different choice
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
# 	Output("arrest-crime-count", "figure"),
# 	[Input("postcode", "value"), Input("arrest-type-checklist", "value")],
# )
# @cache.memoize(timeout=cfg["timeout"])
# def update_arrest_count_graph(zips, arrest_types):
# 	if len(zips) == 0:
# 		return price_ts(empty_series, "Please select postcodes", colors)

# 	if len(arrest_types) == 0:
# 		return price_ts(
# 			empty_series, "Please select at least one property type", colors
# 		)

# 	# --------------------------------------------------#
# 	df = arrest_data.iloc[
# 		np.isin(arrest_data.index.get_level_values("zip"), zips),
# 		np.isin(arrest_data.columns, arrest_types),
# 	]
# 	df.reset_index(inplace=True)

#melted_df = filtered_df.reset_index().melt(id_vars='index', value_vars=arrest_checklist, 
#                                             var_name='Category', value_name='Value')
#
# 
#fig = px.bar(melted_df, x='Category', y='Value', color='index', 
#             title='Arrests by Zip Code and Category',
#             labels={'index': 'Zip Code', 'Category': 'Category', 'Value': 'Count'})
# 	if len(zips) == 1:
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

	# --------------------------------------------#
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
