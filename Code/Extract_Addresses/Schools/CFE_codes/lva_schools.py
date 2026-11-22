import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED

df = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\schools\LVA\20230923_Data_Latvia.xlsx', sheet_name='2022_2023', header=1)

columns_to_keep = ['Reg.Nr.', 'School name in English', 'Type of school 1 in English, 2022/2023', 'ISCED level(s), 2022/2023', 'Ownership',
                   'Y (lat)', 'X (lon)', 'Nbr of students, 2022/2023']

df = df[columns_to_keep]

df.rename(columns={
    'Nbr of students, 2022/2023': 'students', 
    'Reg.Nr.': 'id', 
    'School name in English': 'name',
    'Type of school 1 in English, 2022/2023': 'level_or', 
    'Ownership': 'sector', 
    'Y (lat)': 'lon', # Lat and lon are reversed in the raw data
    'X (lon)': 'lat',
    'ISCED level(s), 2022/2023': 'isced'
}, inplace=True)

df.loc[df['isced'] == 'ISCED 1, 2 AND 3', 'isced'] = 'ISCED11_1_2_3'
df.loc[df['isced'] == 'ISCED 0 AND 1', 'isced'] = 'ISCED11_1'
df.loc[df['isced'] == 'ISCED 0, 1 AND 2', 'isced'] = 'ISCED11_1_2'
df.loc[df['isced'] == 'ISCED 0, 1, 2 AND 3', 'isced'] = 'ISCED11_1_2_3'
df.loc[df['isced'] == 'ISCED 1', 'isced'] = 'ISCED11_1'
df.loc[df['isced'] == 'ISCED 1 AND 2', 'isced'] = 'ISCED11_1_2'
df.loc[df['isced'] == 'ISCED 2 AND 3', 'isced'] = 'ISCED11_2_3'

df['isced_detailed'] = df['isced']

df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')
df['ref_date'] = '2023'
df['latest'] = True

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='schools',
                    iso3='LVA')
