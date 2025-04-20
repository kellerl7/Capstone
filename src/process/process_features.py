import pandas as pd

""" ---------------------------------------------------------------
DATA PREPROCESS
-------------------------------------------------------------------"""

def process_facility_clusters(
        file_loc: str
) -> pd.DataFrame:
    """
    Reads in the post-processed facility data

    inputs:
     - file_loc: Location of the file to read in

    outputs:
     - Clean up the facility database file
    
    Key: 'zip'
    Feature: 'column'
    """
    
    df_facility = pd.read_csv(file_loc)
    if 'zipcode' in df_facility.columns:
        assert 'zip' in df_facility.columns, "Missing key 'zip'"
        df_facility = df_facility.drop(['zipcode'], axis=1)
    df_facility['zip'] = df_facility['zip'].astype(int)

    return df_facility


def process_arrests_by_zip(
        file_loc: str
) -> pd.DataFrame:
    """
    Reads in the post-processed arrest data
    inputs:
     - file_loc: Location of the file to read in

    outputs:
     - Cleaned up arrest data
    
    Key: 'zip'
    Feature: '*_arrest_count' columns
    """

    df_arrests = pd.read_csv(file_loc)
    df_arrests = df_arrests.rename(columns={'F': 'felony_arrest_count',
                                        'I': 'other_arrest_count',
                                        'M': 'misdemeanor_arrest_count',
                                        'V': 'violation_arrest_count'}
                                        )
    
    return df_arrests


def read_zip_borough_key(
        zip_borough_loc: str
) -> dict:
    zip_df = pd.read_csv('data/raw/zip_borough.csv')
    zip_dict = zip_df.set_index('zip')['borough'].to_dict()

    return zip_dict


def main(
        facility_file = 'data/processed/zips_with_clusters.csv',
        arrest_file = 'data/processed/arrests_outside_buffer_by_zip_2016.csv'
):
    """
    Pulls together our different functions and groups
    on index to return a dataframe to add to our model
    """

    df_facility = process_facility_clusters(
        facility_file
    )

    df_arrests = process_arrests_by_zip(
        arrest_file
    )

    zip_borough_key = read_zip_borough_key(
        'data/raw/zip_borough.csv'
    )

    # MERGE
    df_ = pd.merge(df_facility, df_arrests,
                   how='left', left_on='zip',
                   right_on='zip')
    
    df_ = df_.rename(columns={'arrest_year': 'year'})
    
    df_['borough'] = df_['zip'].map(zip_borough_key)
    df_

    return df_


if __name__ == "__main__":
    df_model_features = main()
    df_model_features = df_model_features.drop(columns=['Unnamed: 0'])
    df_model_features.to_csv(
        'data/model_inputs/model_input.csv',
        index=False)
