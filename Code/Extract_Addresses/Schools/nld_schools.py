import os
import geopandas as gpd
import pandas as pd
import pyproj
import openpyxl
import geoalchemy2
from utilities import gisdb_connection, finalise_and_upload, ISCED

primary = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\schools\NLD\Primary-Schools_2022.xlsx')
secondary = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\schools\NLD\Secondary-Schools_2022.xlsx')

columns_to_keep = ['Brin', 'BrinVest', 'naam_volle', 'XCoord', 'YCoord']

primary = primary[columns_to_keep]
secondary = secondary[columns_to_keep]

primary['isced'] = 'ISCED11_1' # need variable to identify correct isced code
secondary['isced'] = 'ISCED11_2_3' # need variable to identify correct isced code

primary['level_or'] = 'Primary'
secondary['level_or'] = 'Secondary'

df = pd.concat([primary, secondary], axis=0)

df['id'] = df['Brin'] + df['BrinVest'].astype(str).str.zfill(2)
df.drop(columns=['Brin', 'BrinVest'],
        inplace=True)
df.rename(columns={
    'naam_volle': 'name',
    'XCoord': 'lon',
    'YCoord': 'lat'
                     },
            inplace=True)

df['ref_date'] = '2022'
df['isced_detailed'] = df['isced'] # change once more information is received 
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-') 
df['latest'] = True
df['students'] = '-' # Need this information from deleagte 
df['sector'] = '-' # Need this information from delegate

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:28992')
gdf = gdf.to_crs('EPSG:4326')
gdf['lon'] = gdf.geometry.x
gdf['lat'] = gdf.geometry.y
gdf.rename(columns={'geometry': 'geom'},
           inplace=True)


finalise_and_upload(gdf,
                    service='schools',
                    iso3='NLD')