import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from src.constants import RAND_STATE


def data_read(
        public_facilities: str = "data/raw/public_fac.csv",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_facilities = pd.read_csv(public_facilities)

    return df_facilities


def process_facility(
        df_facil: pd.DataFrame,
) -> pd.DataFrame:
    """
    This function takes in the initial read data
    and transforms it by performing a count
    per zipcode

    inputs:
      - df_facil: Dataframe that's the public facilities dataframe

    output:
      - Processed dataframe containing count per zipcode
      - This has one column per facility
    """

    df_facil['score'] = 1
    df_facil_pivot = df_facil.pivot_table(
        index='zipcode',
        columns='facgroup',
        aggfunc='sum',
        values='score'
    )
    df_facil_pivot = df_facil_pivot.fillna(0)
    df_facil_pivot['zip'] = df_facil_pivot.index
    df_facil_pivot['zip'] = df_facil_pivot['zip'].astype(int).astype(str)

    return df_facil_pivot


def process_scale_df(
        merged_df: pd.DataFrame,
        exclude_columns: list = []
) -> pd.DataFrame:
    """
    Take merged dataframe and output scale it using the standard scalar
    - If there are columns to be excluded from the scaling,
      provide the column names as a list
    """

    to_scale = merged_df.columns.to_list()  # all but the last (Itarget)

    if len(exclude_columns) > 0:
        to_scale = [col for col in to_scale if col not in exclude_columns]

    # Setup our scaler
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler
                             .fit_transform(
                                 merged_df[to_scale]),
                             columns=to_scale
                             )
    return df_scaled


def process_kmeans_scaled(
        processed_data: pd.DataFrame | np.ndarray,
        cols_to_cluster: list,
        clusters: int = 5
) -> pd.Series:
    """
    Scales the input dataframe (df), only based on the columns input
    uses the input number of clusters
    """

    # Test columns
    if isinstance(processed_data, np.ndarray):
        df = pd.DataFrame(processed_data)
    else:
        df = processed_data[cols_to_cluster]
        assert set(cols_to_cluster).issubset(df.columns), \
            f"Columns selected are not in dataframe.\
            Missing {set(cols_to_cluster) - set(df.columns)}"

    kmeans = KMeans(
        n_clusters=clusters,
        random_state=RAND_STATE,
        n_init=10)
    kmeans.fit(df)

    cluster = kmeans.fit_predict(df)

    return cluster


def process_pca_scaled(
        df: pd.DataFrame,
        cols_to_cluster: list = [],
        n_pca: int = 15
) -> np.ndarray:
    """
    Applies principal component analysis to help
    reduce dimensionality of our dataframe

    This takes in the dataframe df and applies PCA on the input number
    """

    pca = PCA(
        n_components=n_pca
    )
    processed_pca = pca.fit_transform(df[cols_to_cluster])
    pca_loadings = pca_explanation(pca, cols_to_cluster, n_pca)

    return processed_pca, pca_loadings


def pca_explanation(
        pca_: np.ndarray,
        feature_names: list,
        n_pca: int
) -> pd.DataFrame:
    """
    Helps explain the pca loadings by feature
    PCA objects give us an explanatory output worth noting:
        - pca.components_ - directions of maximum variance. Each component
          is a vector, where the row is the
          component and the column is the original
          feature.
            - SHAPE: (n_components, n_features)
            - USE: The weights/loadings of each original feature part of the PC
                Higher weights indicate a stronger influence on the PC
    """
    assert pca_.components_.shape[0] == n_pca, \
        "Number of principal components from PCA object \
        doesn't match input number of components (`n_pca`)."
    pca_loadings = pd.DataFrame(
        pca_.components_.T,
        index=feature_names,
        columns=[f'PC{i+1}' for i in range(n_pca)]
    )
    return pca_loadings


def main(
        facility_location: str,
        property_location: str,
        exclude_columns_to_scale: list = [],
        n_pca: int = 15,
        k_cluster: int = 5
):
    """
    Builds all the pieces together to return a cluster of columns based on
    PCA reduction

    The assumption is we will scale our dataframe based on all columns
    - This will be all facilities and the property values
    - If there are any columns to exclude, provide that as a list
    """
    df_facility = data_read(
        facility_location)
    df_facility = process_facility(df_facility)
    df_scaled = process_scale_df(
        df_facility, exclude_columns=exclude_columns_to_scale)

    scale_cols = df_facility.columns.to_list()
    # Apply PCA
    pca_composition, pca_loadings = process_pca_scaled(
        df_scaled,
        cols_to_cluster=scale_cols,
        n_pca=n_pca
    )

    # Apply KMeans clustering on pca data
    kmeans_cluster = process_kmeans_scaled(
        pca_composition,
        cols_to_cluster=scale_cols,
        clusters=k_cluster
    )
    print(f'Cluster shape: {kmeans_cluster.shape}')
    print(f'Scaled Dataframe shape: {df_scaled.shape}')
    print(f'PCA composition shape: {pca_composition.shape}')

    pca_composed_df = pd.DataFrame(pca_composition)
    pca_composed_df.columns = [f'PC{i+1}' for i in range(n_pca)]
    pca_composed_df['cluster'] = kmeans_cluster
    pca_composed_df['zip'] = df_facility['zip']

    # Merge PCA, clusters, and zip code as our training df
    # Output the PCA decomposition as
    return pca_composed_df, pca_loadings


if __name__ == "__main__":
    pca_composed_df, pca_loadings = main(
        facility_location="data/raw/public_fac.csv",
        n_pca=15,
        k_cluster=5
    )
