import os

appDataPath = "/Users/mas/Projects/nyc_capstone/appData"
assetsPath = "/Users/mas/Projects/nyc_capstone/assets"

if os.path.isdir(appDataPath):
    app_data_dir = appDataPath
    assets_dir = assetsPath
    cache_dir = "cache"
else:
    app_data_dir = "appData"
    assets_dir = "assets"
    cache_dir = "/tmp/cache"

config = {
    "start_year": 2017,
    "end_year": 2023,
    "latest date": '31 December 2023',

    "app_data_dir": app_data_dir,
    "assets dir": assets_dir,
    "cache dir": cache_dir,

    "topN": 50,

    "timeout": 5 * 60,  # used as part of flask_caching
    "cache threshold": 10_000,  # Corresponds to ~350 MB max

    "boroughs_lookup": {
        'Staten Island': 'Staten Island',
        'Bronx': 'Bronx',
        'Queens': 'Queens',
        'Manhattan': 'Manhattan',
        'Brooklyn': 'Brooklyn'
    },

    "plotly_config": {
        "Staten Island": {
            "center": [40.579, -74.151],
            "maxp": 99,
            "zoom": 10
        },
        "Bronx": {
            "center": [40.837, -73.865],
            "maxp": 99,
            "zoom": 10
        },
        "Queens": {
            "center": [40.742, -73.769],
            "maxp": 99,
            "zoom": 10
        },
        "Manhattan": {
            "center": [40.777, -73.971],
            "maxp": 99,
            "zoom": 10
        },
        "Brooklyn": {
            "center": [40.650, -73.950],
            "maxp": 99,
            "zoom": 10
        },
        "NYC": {
            "center": [40.705, -74.0105],
            "maxp": 99,
            "zoom": 9
        }
    }, 
        
    "logging format": """
    pid %(process)5s [%(asctime)s] %(levelname)8s: %(message)s
    """

}

config['Years'] = list(range(config['start_year'], config['end_year']+1))
