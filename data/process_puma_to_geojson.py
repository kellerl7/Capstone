# This file should only need to be used once
# Processes the PUMA csv data into geojson for plotly to read

import geopandas as gpd

gf = gpd.read_file('data/PUMA_nyc_2020.csv')
gdf = gpd.GeoDataFrame(
    gf,
    geometry=gpd.GeoSeries.from_wkt(
        gf['the_geom']
    )
)
gdf.to_file('data/PUMA_nyc_2020.geojson', driver='GeoJSON')
