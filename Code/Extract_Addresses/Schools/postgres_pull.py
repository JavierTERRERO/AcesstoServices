import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED, download_from_db


# All countries
countries = ["aus", "bel", "chl", "col", "cze", "dnk", "esp", "est", "fin",
                   "fra", "grc", "irl", "jpn", "kor", "ltu", "lva", "mex", "nld", "nor", "nzl",
                   "pol", "swe", "usa"]

# Data used in the initial publication
old = ["bel", "cze", "esp", "est", "fin", "fra", "grc", "irl", "ltu", "nld", "nor"]

for country in countries:
    data = download_from_db(service='schools', iso3=country)
    data = data[data["isced"].isin(["ISCED11_1", "ISCED11_1_2", "ISCED11_1_2_3"])]
    if country in old:
        data.to_csv(f"Addresses/Schools/old/{country}_schools.csv", index=False)
    else:
        data.to_csv(f"Addresses/Schools/{country}_schools.csv", index=False)