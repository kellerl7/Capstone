import pandas as pd
import numpy as np
import json
import csv
from collections import defaultdict

from config import config as cfg

def get_model_input_df(
        file_loc: str='data/model_inputs/model_input.csv'
        ) -> pd.DataFrame:
    """
    Returns a dataframe that is based on the input dataframe to our model

    Expected location:
    -- data/model_inputs/model_input.csv

    Returns:
    -- Dataframe with our target, predicted target, and inputs
    """

    df = pd.read_csv(file_loc)
    df['zip'] = df['zip'].astype(int).astype(str)
    df['cluster_name'] = df['Cluster'].apply(lambda x: 'Cluster ' + str(x+1))

    return df

def get_pca_with_clusters() -> pd.DataFrame:
    """
    Returns a dataframe containing the information from using PCA on the clustering
    """
    return pd.read_csv('data/processed/pca_with_clusters.csv')

def get_geo_json_zips():
    """
    Returns the json data associated with the zipcodes of New York City
    """
    with open("data/raw/ny_new_york_zip_codes_geo.min.json", "rb") as file:
        geo_zips = json.load(file)

    return geo_zips
    
    

def get_borough_geo_zips(geo_json_zips):
    '''
    Expected output:
        - dict{
            zipcode: {
                'type': 'Feature',
                'properties': [properties]
                'geometry': [
                    lat/lon
                ]
            }
        }
    '''
    borough_geo_zips = dict()

    for geo_features in geo_json_zips['features']:
        for k, v in geo_features.items():
            if k == 'type':
                zip_type = v
            elif k == 'properties':
                zip_value = v['ZCTA5CE10']
                zip_property = v
            else:
                zip_geo = v
                
        borough_geo_zips[zip_value] = {
            'type': zip_type,
            'properties': zip_property,
            'geometry': zip_geo
            }
    return borough_geo_zips


def get_borough_zips(
        nyc_zips_geojson: dict,
        file_loc: str='data/raw/zip_borough.csv') -> dict:
    """
    Returns a dictionary of all zips with a geojson reference:
      key: borough (NYC will be the "borough" for all zips)
      value: [list of all zipcodes]
    """


    # Initialize a defaultdict to hold boroughs and their associated zipcodes
    borough_zipcodes = defaultdict(list)
    nyc_zips_with_geojson = list(nyc_zips_geojson.keys())

    # Read the CSV file
    with open(file_loc, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            borough = row['borough']
            zip = row['zip']
            if zip not in nyc_zips_with_geojson:
               continue
            else:
                borough_zipcodes[borough].append(zip)
                borough_zipcodes['NYC'].append(zip)

    # Convert defaultdict to regular dict if needed
    borough_zipcodes = dict(borough_zipcodes)
    return borough_zipcodes

def get_arrests_outside_buffer(
        file_loc: str='data/processed/arrests_outside_buffer_by_zip_2016.csv'
        ) -> pd.DataFrame:
        """
        Returns a dataframe with the summarized arrests outside buffer
        """

        df = pd.read_csv(file_loc)
        df = df.set_index(df['zip'].astype(str)).drop(columns = ['arrest_year'])
        return df