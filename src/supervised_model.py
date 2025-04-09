# DATA LOAD AND PREP
import pandas as pd
import numpy as np
import sklearn
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import matplotlib.pyplot as plt
import seaborn as sns

'''# -----------------------------
Define our input variables
----------------------------------'''
df_processed = pd.read_csv('data/processed/features_by_year.csv')
df_facility = pd.read_csv('data/processed/facility_clustered.csv')
# Bring in arrests outside of buffer

'''#---------------------------------
Basic Model
--------------------------------------'''
