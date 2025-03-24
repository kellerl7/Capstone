import pandas as pd
import requests
from sodapy import Socrata

# Initialize our client

# The required arguments are:
#   domain: the domain you wish to access
#   app_token: your Socrata application token
# simple requests are possible without an app_token, though these
# requests will be rate-limited

def nyc_api_read(url: str, limit: int=5000):

    # Source the domain for the NYC Open Data
    socrata_domain = "data.cityofnewyork.us"

    client = Socrata(
        socrata_domain,
        app_token="XLvpOacSkjniOArUFmY0iq5kI",
        timeout=100
    )

    limit='$limit=' + str(limit)

    url_limit = url + '?' + limit
    df = pd.read_json(url_limit)

    return df

