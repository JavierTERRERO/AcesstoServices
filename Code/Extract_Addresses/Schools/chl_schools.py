import os
import geopandas as gpd
import pandas as pd
import numpy as np
from utilities import gisdb_connection, finalise_and_upload, ISCED


df = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\schools\CHL\20230912_Directorio_Oficial_EE_2023_20230430_WEB.csv', delimiter=';')

columns_to_keep = ['AGNO', 'NOM_RBD', 'RBD', 'LATITUD', 'LONGITUD', 'MAT_TOTAL', 'COD_DEPE', 
                   'ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08',
                   'ENS_09', 'ENS_10', 'ENS_11']

df = df[columns_to_keep]

df.rename(columns={
    'AGNO': 'ref_date',
    'NOM_RBD': 'name', 
    'RBD': 'id', 
    'LATITUD': 'lat', 
    'LONGITUD': 'lon', 
    'COD_DEPE': 'sector', 
    'MAT_TOTAL': 'students'}, inplace=True)

# removing schools that are closed 

# keeping only regular schools
values_to_keep = ['110', '310', '410', '510', '610', '710', '810', '910']
mask = df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 
           'ENS_09', 'ENS_10', 'ENS_11']].apply(lambda x: x.astype(str).isin(values_to_keep)).any(axis=1)
df = df[mask]

df['isced'] = '-'
condition = df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str).isin(['110']).any(axis=1)
df['isced'] = np.where(condition, 'ISCED11_1_2', df['isced'])
condition = ((df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '310').any(axis=1) | 
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '410').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '510').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '610').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '710').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '810').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '910').any(axis=1))
df['isced'] = np.where(condition, 'ISCED11_3', df['isced'])
condition = ((df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '110').any(axis=1) & 
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '310').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '110').any(axis=1) & 
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '410').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '110').any(axis=1) & 
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '510').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '110').any(axis=1) & 
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '610').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '110').any(axis=1) & 
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '710').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '110').any(axis=1) & 
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '810').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '110').any(axis=1) & 
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '910').any(axis=1))
df.loc[condition, 'isced'] = 'ISCED11_1_2_3'

df['isced_detailed'] = df['isced']
# specifying upper secondary schools with vocational training 
condition =  ((df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '410').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '510').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '610').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '710').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '810').any(axis=1) |
             (df[['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']].astype(str) == '910').any(axis=1))
df['isced_detailed'] = np.where(condition, 'ISCED11_35', df['isced_detailed']) 

# Assigning public and private values to the 'sector' column
df.loc[df['sector'].isin([1, 2, 3, 6]), 'sector'] = 'public'
df.loc[df['sector'].isin([4, 5]), 'sector'] = 'private'

# Final cleaning 
df['level_or'] = '-'
df['latest'] = True
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')
df.drop(columns=['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11'], inplace=True)
df['lon'] = df['lon'].str.replace(',', '.')
df['lat'] = df['lat'].str.replace(',', '.')
df = df.dropna(subset=['lat'])
df = df[df['lat'] != ' ']

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='schools',
                    iso3='CHL')