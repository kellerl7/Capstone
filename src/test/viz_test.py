import random
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
)

boroughs = [
	"Bronx",
	"Staten Island",
	"Brooklyn",
	"Manhattan",
	"Queens",
	"NYC"
]
train_df = get_train_df()
summary_market_value = return_market_value()
geo_zip_data = get_geo_json_zips()
# ---------------------------------------------

# initial values:
initial_year = 2016
initial_borough = "NYC"

borough_filter = summary_market_value.loc[
	(summary_market_value['year'] == initial_year
		) & (
			summary_market_value['borough'] == initial_borough if initial_borough != 'NYC' else True
			)]['zip']
initial_zip = random.choice(borough_filter)

'''#---------------------------------------------------
Callback Functions in app.py
-------------------------------------------------------
'''
def update_map_title(borough, year, gtype):
	if gtype == "Market Value":
		return f"Avg market value for properties in a given borough {borough}, {year}"
	elif gtype == "Model Error":
		return (
			f"Shows the average model error when predicting the market value in {borough}, {year}"
		)
	else:
		return f"The given cluster breakdown for the different zipcodes in the borough {borough}, {year}"
	

def update_region_postcode(borough, year):
	zipcode_list = [
		{"label": s, "value": s} for s in summary_market_value.loc[
			(summary_market_value['year'] == year) & 
			(summary_market_value['borough'] == borough if borough != 'NYC' else True)
			]['zip'].values]
	return zipcode_list


def update_Choropleth(year, borough, gtype, zips):
    # Graph type selection------------------------------#
	# Graph options: "Market Value", "Model Error", "Neighborhood Cluster"
	if gtype in ["Market Value", "Neighborhood Cluster"]:
		df = summary_market_value.loc[
			(summary_market_value['year'] == year) &
			(summary_market_value['borough'] == borough if borough != 'NYC' else True)
		]
	else:
		#TODO: Switch dataset to model output to graph error
		#df = regional_percentage_delta_data[year][region]
		pass

	# For high-lighting mechanism ----------------------#
	geo_sectors = dict()

	# if "borough" not in changed_id:
	# 	for k in regional_geo_data[region].keys():
	# 		if k != "features":
	# 			geo_sectors[k] = regional_geo_data[region][k]
	# 		else:
	# 			geo_sectors[k] = [
	# 				regional_geo_sector[region][sector]
	# 				for sector in sectors
	# 				if sector in regional_geo_sector[region]
	# 			]

	# Updating figure ----------------------------------#
	fig = get_figure(
		df,
		geo_zip_data,
		borough,
		gtype,
		year,
		geo_sectors
	)

	return fig

def update_postcode_dropdown(
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

	if "borough" in changed_id:
		zipcodes = []
	elif "selectedData" in changed_id:
		zipcodes = [D["location"] for D in selectedData["points"][: cfg["topN"]]]
	elif clickData is not None and "location" in clickData["points"][0]:
		zip = clickData["points"][0]["location"]
		if sector in postcodes:
			postcodes.remove(sector)
		elif len(postcodes) < cfg["topN"]:
			postcodes.append(sector)
	return postcodes

test_fig = update_Choropleth(initial_year, initial_borough, "Market Value", initial_zip)
test_fig.show()