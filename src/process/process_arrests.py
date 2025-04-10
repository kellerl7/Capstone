import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

arrests = pd.read_csv("data/processed/arrests_outside_buffer.csv")
zips = gpd.read_file("data/raw/ny_new_york_zip_codes_geo.min.json")

# Convert some columns
arrests['ARREST_DATE'] = pd.to_datetime(arrests['ARREST_DATE'])
arrests['ARREST_MONTH'] = arrests['ARREST_DATE'].dt.to_period('M') # Period for grouping
arrests['ARREST_YEAR'] = arrests['ARREST_DATE'].dt.to_period('Y')

# Shapely information is lost from ipynb to csv
# Restore information and store 'geometry' point value 
arrests['geometry'] = arrests.apply(
    lambda x: Point(
        x['Longitude'],
        x['Latitude']
    ), axis=1
)

# Join our data via the geometry in zips
arrests_gdf = gpd.GeoDataFrame(arrests, geometry='geometry')
arrests_in_zips = gpd.sjoin(arrests_gdf, zips, how='inner')

# Group our data by 
arrests_by_zip = (arrests_in_zips
                  .groupby(['ARREST_YEAR', 'ZCTA5CE10', 'LAW_CAT_CD'])
                  .size()
                  .reset_index(name='count')
                  )

arrests_by_zip = arrests_by_zip.rename(columns={'ZCTA5CE10': 'zip'})

arrests_by_zip.to_csv('arrests_outside_buffer_by_zip.csv')