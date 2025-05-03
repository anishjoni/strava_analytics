# Importing libraries
import requests
import pandas as pd
import polars as pl
from sqlalchemy import create_engine

# Request data from Strava API
url = 'https://www.strava.com/api/v3/athlete'
headers = {'Authorization':'Bearer 6e07251a4e5e8164e4ee6a656d372f1be12c6dfa'}

r = requests.get(url, headers=headers)

data =  r.json()
data = pd.DataFrame([data])
pl.DataFrame(data)


data = data[['id','username', 'firstname', 'lastname', 'city', 'sex', 'weight']]
(data)

