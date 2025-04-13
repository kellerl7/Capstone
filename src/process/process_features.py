import pandas as pd

from process.api_socrata import nyc_api_read
import data_endpoints as nyc_data

"""------------------------------------------------------------
DATA READ
---------------------------------------------------------------"""
df_dog = nyc_api_read(nyc_data.nyc_DOG, limit=30000)
df_pricing = pd.read_parquet(
    'data/raw/nyc_rent_pricing.parquet.gzip',
    engine='pyarrow'
)
df_financial_health = nyc_api_read(nyc_data.nyc_NFHDM, limit=5000)

""" ---------------------------------------------------------------
DATA PREPROCESS
-------------------------------------------------------------------"""


def process_property_value(
        prop_loc: str
) -> pd.DataFrame:
    """
    Takes in the location for the property values
    to ingest and process
    how we need

    inputs:
      - prop_loc: Location of the poperty value dataframe

    outputs:
      - Processes the property value dataframe by aggregating by zipcode
        and averaging the market value
    """
    df_prop = pd.read_csv(prop_loc)
    df_property_value = (df_prop[['zip', 'revised_market_value']]
                         .groupby(by='zip')
                         .mean())

    return df_property_value


def process_dog_bite(
        df_dog_bite: pd.DataFrame
) -> pd.DataFrame:
    df_dog_bite['bite_date'] = pd.to_datetime(df_dog_bite['dateofbite'])
    df_dog_bite['bite_year'] = df_dog_bite['bite_date'].dt.year
    df_dog_bite['bite_myear'] = df_dog_bite['bite_date'].dt.to_period('M')

    df_bite_summary = (
        df_dog_bite
        .groupby([
            'bite_year',
            'zipcode'
        ])
        .size()
        .reset_index(name='count')
        .rename(columns={'count': 'dog_bite_count',
                         'zipcode': 'zip',
                         'bite_year': 'year'})
    )

    return df_bite_summary


def process_pricing_data(
        df_pricing: pd.DataFrame
) -> pd.DataFrame:
    '''
    This data is from realtor.com
    It contains rental pricing information
    Relevant fields we'll keep:
    - median_days_on_market
    - active_listing_count
    - median_listing_price
    - median_listing_price_per_square_foot
    '''

    df_pricing['year'] = df_pricing['month_date'].dt.year
    df_year_summary = (
        df_pricing
        .groupby([
            'year',
            'postal_code'
        ])
        .agg({
            'median_days_on_market': 'median',
            'active_listing_count': 'median',
            'median_listing_price': 'median',
            'median_listing_price_per_square_foot': 'median'
        })
        .reset_index()
        .rename(columns={'postal_code': 'zip'})
    )

    # Convert zip to string
    df_year_summary['zip'] = df_year_summary['zip'].astype(str)

    return df_year_summary


def main():
    """
    Pulls together our different functions and groups
    on index to return a dataframe to add to our model
    """

    df_dog_bite = process_dog_bite(df_dog)
    df_price = process_pricing_data(df_pricing)

    df_features = pd.merge(
        df_dog_bite,
        df_price,
        on=['zip', 'year'],
        how='inner'
    )

    return df_features


if __name__ == "__main__":
    df_yearly_features = main()
    df_yearly_features.to_csv('data/processed/features_by_year.csv', index=False)
