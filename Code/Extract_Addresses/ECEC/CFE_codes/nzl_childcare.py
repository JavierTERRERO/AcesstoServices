import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED 

df = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\childcare\NZL\directory.csv', header=15)

df = df.iloc[1:]
# There are different types of specifications such as demographic attributes, whether the centre provides a 20 hour free service and 
# the equity index of the school itself   
columns_to_keep = ['Service Number', 'Service Name', 'Service Type', 'Authority',
                   'Latitude', 'Longitude', 'Total']
df = df[columns_to_keep] 


df['Authority'] = df['Authority'].replace('Community based', 'public')
df['Authority'] = df['Authority'].replace('Privately owned', 'private')
df.rename(columns={
    'Total': 'students', 
    'Service Number': 'id', 
    'Service Name': 'name',
    'Service Type': 'level_or', 
    'Authority': 'sector', 
    'Latitude': 'lat',
    'Longitude': 'lon'
}, inplace=True)
df['id'] = df['id'].astype(int).astype(str) 

df['isced'] = 'ISCED11_0'
df['isced_detailed'] = df['isced']

df['ref_date'] = '2022'
df['latest'] = True
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')

finalise_and_upload(gdf,
                    service='childcare',
                    iso3='NZL')