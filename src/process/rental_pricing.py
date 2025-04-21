import pandas as pd
import json
import matplotlib.pyplot as plt

# Read in 2 files:
# SOURCE: https://www.realtor.com/research/data/
# 1. RDC Inventory Core Metrics Zip (current file)
# 2. RDC Inventory Core Metrics Zip History (historical)

historical_rent = pd.read_csv(
    "data/RDC_Inventory_Core_Metrics_Zip_History.csv")
current_rent = pd.read_csv("data/RDC_Inventory_Core_Metrics_Zip.csv")
rents = pd.concat([historical_rent, current_rent])

# Then we want to trim our dataset to retain only relevant NYC pricing
with open("data/ny_new_york_zip_codes_geo.min.json", "rb") as f:
    nyc_zips = json.load(f)

nyc_zip_codes = [int(k["properties"]["ZCTA5CE10"])
                 for k in nyc_zips['features']]

# Trim our dataset
nyc_rents = rents.loc[rents['postal_code'].isin(nyc_zip_codes)]

# Convert month_date_yyyymm to date-time
nyc_rents['month_date'] = pd.to_datetime(
    nyc_rents['month_date_yyyymm']
    .astype(str),
    format="%Y%m"
)

# Quickly visualize:
nyc_rents.to_parquet('data/nyc_rent_pricing.parquet.gzip', compression='gzip')

# Execute the following block to see the plot

# %#


def quick_scatter(plot_x, plot_y, color_var):
    plt.figure(figsize=(10, 6))
    plt.scatter(plot_x, plot_y, c=color_var, alpha=0.5, cmap='viridis')
    plt.title(f'Comparing {plot_y} vs {plot_x}')
    plt.grid(True)
    plt.show()
