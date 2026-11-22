# Original code ---------------------------------------------------------

import pandas as pd 
import os
import time
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED 

# Same data that was webscraped for mex_schools
df = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\schools\MEX\compiled_dataset.csv', encoding='latin1')

df.rename(columns={
    'Identification': 'id',
    'Grade': 'level_or', 
    'Sector': 'sector', 
    'Name': 'name', 
    'Lon': 'lat', # lon and lat coordinates are reversed 
    'Lat': 'lon', 
    'Students': 'students'
    }, inplace=True)

# Removing grade levels that aren't primary or secondary school 
df = df[df['level_or'] != 'LICENCIATURA Y POSGRADO']
df = df[df['level_or'] != 'MEDIA SUPERIOR']
df = df[df['level_or'] != 'SECUNDARIA']
df = df[df['level_or'] != 'PRIMARIA']

# Dropping CONAFE schools
df = df[~df['Sub_grade'].str.endswith('CONAFE')]

duplicated = df[df.duplicated(subset=['id', 'name'], keep=False)]

# There are 1203 PREESCOLAR CENDI and INICIAL GENERAL meaning they are 
# paired with each other. Preescolar CENDI are child development centers
# for infants and children in the maternal stage. Meanwhile Inicial General 
# can be between the ages of 0-6
# Keeping both as they are different services (ISCED11_01 and ISCED11_02)
df_counts = df['Sub_grade'].value_counts()
#print(df_counts)
duplicated_counts = duplicated['Sub_grade'].value_counts()
#print(duplicated_counts)


# Checking the the 142 duplicates and they're all attributed to PREESCOLAR GENERAL.
# (except for two that are INICIAL GENERAL and PREESCOLAR CENDI) When checking on 
# the website we see again that some are morning and the others are afternoon services 

#duplicated = df[df.duplicated(subset=['id', 'Sub_grade'], keep=False)]

# Summing values and dropping duplicated schools 
df = df.groupby(['id', 'Sub_grade']).agg({
    'students': 'sum',
    'level_or': 'first',
    'sector': 'first', 
    'name': 'first',
    'lat': 'first', 
    'lon': 'first',
    'students': 'first'
}).reset_index()


df['isced'] = '-'
df.loc[df['level_or'] == 'PREESCOLAR', 'isced'] = 'ISCED11_0'
df.loc[df['level_or'] == 'INICIAL', 'isced'] = 'ISCED11_0'


df['isced_detailed'] = df['isced']
df.loc[df['Sub_grade'] == 'PREESCOLAR CENDI', 'isced_detailed'] = 'ISCED11_01'
df.loc[df['Sub_grade'] == 'PREESCOLAR INDIGENA', 'isced_detailed'] = 'ISCED11_02'
df.loc[df['Sub_grade'] == 'PREESCOLAR GENERAL', 'isced_detailed'] = 'ISCED11_02'


df.loc[df['sector'] == 'PÚBLICO', 'sector'] = 'public'
df.loc[df['sector'] == 'PRIVADO', 'sector'] = 'private'

df.drop(columns=['Sub_grade'], inplace=True)
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-') 
df['ref_date'] = '2024'
df['latest'] = True


gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='childcare',
                    iso3='MEX')
