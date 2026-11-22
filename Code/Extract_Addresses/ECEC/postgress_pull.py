import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED, download_from_db

# BEL, ITA, LTU aren't found in the PostgreSQL database
countries = ['CZE', 'ESP', 'EST', 'FIN', 'FRA',
             'GRC', 'IRL', 'NLD', 'NOR', 'USA']
for country in countries:
    data = download_from_db(service='childcare', iso3=country)
    if country == 'USA':
        data.to_csv(f"Addresses/ECEC/{country.lower()}_childcare.csv", index=False)
    else: 
        data.to_csv(f"Addresses/ECEC/old/{country.lower()}_childcare.csv", index=False)