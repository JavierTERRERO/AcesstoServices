import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED

df = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\schools\NZL\directory.csv', header=15)

df = df.iloc[1:]
columns_to_keep = ['School Number', 'School Name', 'Authority', 'School Type', 
                   'Latitude', 'Longitude', 'Total School Roll']

df = df[columns_to_keep]

df.rename(columns={
    'Total School Roll': 'students', 
    'School Number': 'id', 
    'School Name': 'name',
    'School Type': 'level_or', 
    'Authority': 'sector', 
    'Latitude': 'lat',
    'Longitude': 'lon'
}, inplace=True)

df['sector'] = df['sector'].str.replace('.*State.*', 'public', regex=True)
df['sector'] = df['sector'].str.replace('.*Private.*', 'private', regex=True)
df['id'] = df['id'].astype(int).astype(str) 

df['isced'] = '-'
df.loc[df['level_or'] == 'Full Primary', 'isced'] = 'ISCED11_1'
df.loc[df['level_or'] == 'Contributing', 'isced'] = 'ISCED11_1'
df.loc[df['level_or'] == 'Composite (Year 1-10)', 'isced'] = 'ISCED11_1_2'
df.loc[df['level_or'] == 'Secondary (Year 7-10)', 'isced'] = 'ISCED11_2'
df.loc[df['level_or'] == 'Restricted Composite (Year 7-10)', 'isced'] = 'ISCED11_2'
df.loc[df['level_or'] == 'Intermediate', 'isced'] = 'ISCED11_2'
df.loc[df['level_or']== 'Correspondence School', 'isced'] = 'ISCED11_1_2_3' 
df.loc[df['level_or']== 'Special School', 'isced'] = 'ISCED11_1_2_3' 
df.loc[df['level_or']== 'Composite', 'isced'] = 'ISCED11_1_2_3' 
df.loc[df['level_or'] == 'Secondary (Year 7-15)', 'isced'] = 'ISCED11_2_3'
df.loc[df['level_or'] == 'Teen Parent Unit', 'isced'] = 'ISCED11_3'
df.loc[df['level_or'] == 'Activity Centre', 'isced'] = 'ISCED11_3'
df.loc[df['level_or'] == 'Secondary (Year 9-15)', 'isced'] = 'ISCED11_3' 
df.loc[df['level_or'] == 'Secondary (Year 11-15)', 'isced'] = 'ISCED11_3'

df['isced_detailed'] = df['isced']  # ask delegate about vocational training 
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')
df['ref_date'] = '2024'
df['latest'] = True

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')

finalise_and_upload(gdf,
                    service='schools',
                    iso3='NZL')
