import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def process_arrests(file_loc: str, output_loc: str, source: str=['url', 'api']):
    """
    If downloaded - all columns are in all CAPS
    If from API source - all columns are in lower case

    Location:
        data/processed/arrests_outside_buffer.csv
    """

    arrests = pd.read_csv(file_loc)
    zips = gpd.read_file("data/raw/ny_new_york_zip_codes_geo.min.json")

    if source == 'url':
        arrests.columns = [h.lower() for h in arrests.columns]

    # Convert some columns
    arrests['arrest_date'] = pd.to_datetime(arrests['arrest_date'])
    arrests['arrest_month'] = arrests['arrest_date'].dt.to_period('M') # Period for grouping
    arrests['arrest_year'] = arrests['arrest_date'].dt.to_period('Y')

    # Shapely information is lost from ipynb to csv
    # Restore information and store 'geometry' point value 
    arrests['geometry'] = arrests.apply(
        lambda x: Point(
            x['longitude'],
            x['latitude']
        ), axis=1
    )

    # Join our data via the geometry in zips
    arrests_gdf = gpd.GeoDataFrame(arrests, geometry='geometry')
    arrests_in_zips = gpd.sjoin(arrests_gdf, zips, how='inner')

    # Group our data by 
    arrests_by_zip = (arrests_in_zips
                    .groupby(['arrest_year', 'ZCTA5CE10', 'law_cat_cd'])
                    .size()
                    .reset_index(name='count')
                    )

    arrests_by_zip = arrests_by_zip.rename(columns={'ZCTA5CE10': 'zip'})

    arrests_by_zip.to_csv(output_loc, index=False)

    return arrests_by_zip

# TO RUN
process_arrests(
    "data/processed/arrests_outside_buffer_2016.csv",
    "data/processed/arrests_outside_buffer_by_zip_2016.csv",
    source="api"
)