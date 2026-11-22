import pandas as pd 
import numpy as np
import geopandas as gpd
import pyproj
from utilities import gisdb_connection, finalise_and_upload, ISCED

df = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\childcare\NLD\Childcare-daycare_2022.xlsx')

columns_to_keep = ['lrk_id', 'actuele_naam_oko', 'XCoord', 'YCoord', 'aantal_kindplaatsen', 'type_oko']
df = df[columns_to_keep]

df['isced'] = 'ISCED11_0'
df['isced_detailed'] = 'ISCED11_0'
df['ref_date'] = '2022'
df['sector'] = 'public'

df.rename(columns={'lrk_id': 'id',
                     'actuele_naam_oko': 'name',
                     'XCoord': 'lon',
                     'YCoord': 'lat',
                     'aantal_kindplaatsen': 'students', 
                     'type_oko': 'level_or'
                     },
            inplace=True)


# Define the projection transformers
transformer = pyproj.Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)

# Function to transform coordinates
def transform_coordinates(x, y):
    lon, lat = transformer.transform(x, y)
    return lon, lat

# Apply the transformation to each row
df['lon'], df['lat'] = zip(*df.apply(lambda row: transform_coordinates(row['lon'], row['lat']), axis=1))

df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')
df['latest'] = True

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')

finalise_and_upload(gdf,
                    service='childcare',
                    iso3='NLD')
