import pandas as pd
import numpy as np
import json

def get_train_df() -> pd.DataFrame:
    """
    Returns a dataframe that is based on the input dataframe to our model

    Expected location:
    -- data/model_inputs/model_input_output.csv

    Returns:
    -- Dataframe with our target, predicted target, and inputs
    """

    df = pd.read_csv('data/model_inputs/model_input.csv')

    return df

def return_market_value():
    df = get_train_df()
    df_market_value = (
        df
        .groupby(
            ['year', 'zip', 'borough']
            )['revised_market_value']
        .mean()
        .reset_index()
    )

    return df_market_value

def get_pca_with_clusters() -> pd.DataFrame:
    """
    Returns a dataframe containing the information from using PCA on the clustering
    """
    return pd.read_csv('data/processed/pca_with_clusters.csv')

def get_geo_json_zips():
    """
    Returns the json data associated with the zipcodes of New York City
    """
    with ("data/raw/ny_new_york_zip_codes_geo.min.json", "rb") as file:
        return json.load(file)