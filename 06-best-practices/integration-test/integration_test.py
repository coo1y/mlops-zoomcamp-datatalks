import pandas as pd
from datetime import datetime

S3_ENDPOINT_URL = "http://localhost:4566"

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

data = [
    (None, None, dt(1, 1), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
]

columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
df = pd.DataFrame(data, columns=columns)

options = {
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT_URL
    }
}

# We will pretend that this is data for January 2023.
year = 2023
month = 1

df.to_parquet(
    f"s3://nyc-duration/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet",
    engine='pyarrow',
    compression=None,
    index=False,
    storage_options=options
)