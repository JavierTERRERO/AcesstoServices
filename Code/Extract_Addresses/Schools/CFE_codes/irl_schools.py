import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED


df = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\schools\IRL\230608_SID_OECD.xlsx')

df['OpenClosedStatus'] = df['OpenClosedStatus'].str.strip()
df['EDUCATION_ORG_TYPE'] = df['EDUCATION_ORG_TYPE'].str.strip()

# Apply the filters
df = df[df['OpenClosedStatus'] == 'Open']
df = df[df['EDUCATION_ORG_TYPE'] == 'Primary']

df.rename(columns={'Roll_Number': 'id', 'School_Name': 'name', 'Total': 'students',
                   'EDUCATION_ORG_TYPE': 'level_or', 'Longitude': 'lon',
                   'Latitude': 'lat'}, inplace=True)
columns_to_keep = ['id', 'name', 'level_or', 'students', 'lon', 'lat']
df = df[columns_to_keep]
df['isced'] = 'ISCED11_1'
df['isced_detailed'] = df['isced']
df['sector'] = '-'
df['latest'] = True
df['ref_date'] = '2023-06-21'
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='schools',
                    iso3='IRL')
