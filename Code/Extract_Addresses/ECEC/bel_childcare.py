# Original code ---------------------------------------------------------

from pyproj import Transformer
import geocoder
import pandas as pd 
import os
import geopandas as gpd
from utilities import gisdb_connection, finalise_and_upload, ISCED 

###############################################################################
#                                  Flanders                                   #
###############################################################################

# flanders_nurseries = pd.read_excel(r"V:\GIS_DATABASE\raw_data\education\childcare\BEL\flanders\Maurizio Salazar_Lozado OECD addresses childcare settings.xlsx")
flanders_kindergartens = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\childcare\BEL\flanders\vestigingsplaatsen-van-scholen-kleuteronderwijs (1).csv', delimiter=';')

# ### Flanders Nurseries ###

# flanders_nurseries.rename(columns={
#     'Dag': 'ref_date',
#     'Legal Form provider': 'sector',
#     'Naam locatie': 'name', 
#     'Straat - huisnummer - busnummer locatie': 'street_address',
#     'Postcode locatie': 'postal_code', 
#     'Gemeente locatie': 'region', 
#     '# of places': 'students'}, inplace=True)
# flanders_nurseries['address'] = (flanders_nurseries['street_address'].astype(str) + ', ' + flanders_nurseries['postal_code'].astype(str) + ' ' + flanders_nurseries['region'].astype(str))
# columns_to_keep = ['ref_date', 'sector', 'name', 'address', 'students']
# flanders_nurseries = flanders_nurseries[columns_to_keep]

# flanders_nurseries['isced'] = 'ISCED11_0'
# flanders_nurseries['isced_detailed'] = 'ISCED11_01'
# flanders_nurseries['level_or'] = 'kinderdagverblijven'

### Flanders Kindergartens ###

flanders_kindergartens.rename(columns={
    'schoolnummer': 'id',
    'naam': 'name',
    'adres': 'address'}, inplace=True)
columns_to_keep = ['id', 'name', 'address', 'lx', 'ly']
flanders_kindergartens = flanders_kindergartens[columns_to_keep]

# 'kleuterschool' stands for kindergarten, 'basisschool' stands for primary school. 
# Although it seems that the primary schools in this dataset also provide 
# kindergarten service. 

flanders_kindergartens['students'] = '-'
flanders_kindergartens['sector'] = '-'
flanders_kindergartens['ref_date'] = '2024-03-20'
flanders_kindergartens['level_or'] = 'kleuterschool'
flanders_kindergartens['isced'] = 'ISCED11_0'
flanders_kindergartens['isced_detailed'] = 'ISCED11_02'

flanders = pd.concat([flanders_kindergartens, flanders_nurseries])

def addresses_to_coords(data:pd.DataFrame, column:str):
    def get_coords(address):
        print(address)
        g = geocoder.arcgis(address)
        return pd.Series({'lon': g.lng, 'lat': g.lat})
    coords = flanders['address'].apply(get_coords)
    df = pd.concat([flanders, coords], axis=1)
    return df

flanders['address'] = flanders['address'] + ', Belgium'
flanders = addresses_to_coords(flanders, 'address')

"""
source_crs = "EPSG:31370"
target_crs = "EPSG:4326"

transformer = Transformer.from_crs(source_crs, target_crs)
flanders[['lx', 'ly']] = flanders.apply(lambda row: transformer.transform(row['lx'], row['ly']), axis=1, result_type='expand')
flanders['lon_diff'] = flanders['lon'] - flanders['ly']
flanders['lat_diff'] = flanders['lat'] - flanders['lx']

average_lon_diff = flanders['lon_diff'].mean(skipna=True)
print(average_lon_diff)
average_lat_diff = flanders['lat_diff'].mean(skipna=True)
print(average_lat_diff)

flanders.drop(columns={'lx', 'ly', 'lon_diff', 'lat_diff'}, inplace=True)

# the average difference in longitude between the coordinates given by the authorities 
# and the ones calculate is of -2.868752946276092e-08. For latitude it's 5.680702019757562e-06
"""

###############################################################################
#                                  Wallonia                                   #
###############################################################################


wallonia = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\childcare\BEL\wallonia\Ecoles_maternelles_Wallonie et Bruxelles.xlsx', header=1)
wallonia.rename(columns={
    'Etablissement': 'name', 
    'Rue et numéro': 'street_address', 
    'CP': 'postal_code', 
    'Localité': 'city'}, inplace=True),

def addresses_to_coords(data:pd.DataFrame, column:str):
    def get_coords(address):
        print(address)
        g = geocoder.arcgis(address)
        return pd.Series({'lon': g.lng, 'lat': g.lat})
    coords = wallonia['address'].apply(get_coords)
    df = pd.concat([wallonia, coords], axis=1)
    return df

wallonia['street_address'] = wallonia['street_address'].str.replace(', ', '', regex=False)
wallonia['address'] = wallonia['street_address'].astype(str) + ', ' + wallonia['postal_code'].astype(str) + ' ' + wallonia['city'].astype(str) + ', ' + 'Belgium' 
wallonia = addresses_to_coords(wallonia, 'address')

wallonia['isced'] = 'ISCED11_0'
wallonia['isced_detailed'] = 'ISCED11_02'
wallonia['students'] = '-'
wallonia[ 'sector'] = '-'
wallonia['ref_date'] = '2023-04-19'
wallonia['level_or'] = 'Ecoles Maternelles'
wallonia['id'] = '-'

columns = ['id', 'name', 'lon', 'lat', 'isced', 'isced_detailed', 'students', 'sector', 'ref_date', 'level_or']
wallonia = wallonia[columns]
flanders = flanders[columns]

df = pd.concat([flanders, wallonia])

df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')

