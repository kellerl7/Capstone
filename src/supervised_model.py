#%%
# DATA LOAD AND PREP
import pandas as pd

'''# -----------------------------
Define our input variables
----------------------------------'''
#%%
# Structure:
# year, zip, dog_bite_count
# median_days_on_market, active_listing_count
# median_listing_price, median_listing_price_per_square_foot
df_processed = pd.read_csv('data/processed/features_by_year.csv')

# Add in facility information
df_facility = pd.read_csv('data/processed/facility_clustered.csv')
# redundant column [zipcode:float, zip:str]
df_facility = df_facility.drop(['zipcode'])

# Add in boroughs tied to borough
df_zips = pd.read_csv('data/raw/zip_borough.csv')
df_arrests = pd.read_csv('data/processed/arrests_outside_buffer_by_zip_2016.csv')
# Market value as a target variable
df_market_value = pd.read_csv('data/raw/prop_values.csv')

df_ = pd.merge(df_processed, df_facility, how='left', left_on='zip', right_on='zip')
# Bring in arrests outside of buffer
df_ = pd.merge(df_, df_arrests, how='left', left_on=['zip', 'year'], right_on=['zip', 'arrest_year'])

# Convert zip from float to int
# Drop NAs
df_market_value = df_market_value.dropna(subset=['zip'])
df_market_value['zip'] = df_market_value['zip'].astype(int)
df_ = pd.merge(df_, df_market_value[['zip', 'revised_market_value']], how='left', on='zip')

# Add in borough information
df_zips['zip'] = df_zips['zip'].astype(int)
df = pd.merge(df_, df_zips, how='left', on='zip')
# Save intermediate dataframe as model_input
def save_dataframe(df: pd.DataFrame) -> None:
    df.to_csv('data/model_inputs/model_input.csv', index=False)

# Merge our data into one dataframe
#%%
save_dataframe(df)
# %%
