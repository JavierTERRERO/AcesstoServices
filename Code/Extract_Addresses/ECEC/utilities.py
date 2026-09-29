import os
import sqlalchemy
import geopandas as gpd

url = f"postgresql://{os.environ['USERNAME'].capitalize()}:@gis.main.oecd.org:5432/oecd_tl"
gisdb_connection = sqlalchemy.create_engine(url).connect()
def finalise_and_upload(gdf:gpd.GeoDataFrame,
                        service:str,
                        iso3:str):
    gdf.rename(columns={'geometry': 'geom'},
               inplace=True)
    gdf = gpd.GeoDataFrame(gdf,
                           geometry='geom')
    gdf = gdf[['id', 'name', 'level_en', 'level_or', 'isced', 'isced_detailed',
               'sector', 'students', 
               'lat', 'lon', 'ref_date', 'geom', 'latest']]
    gdf.to_postgis(name=f'{iso3.lower()}_{service}',
                   con=gisdb_connection,
                   schema='education', 
                   if_exists='replace')
    
    
ISCED = {
    'ISCED11_0': 'Early childhood education',
    'ISCED11_01': 'Early childhood educational development',
    'ISCED11_02': 'Pre-primary education',
    'ISCED11_1': 'Primary education',
    'ISCED11_1_2': 'Primary and lower secondary education',
    'ISCED11_2_3' : 'Secondary education',
    'ISCED11_1_2_3' : 'Primary and secondary education',
    'ISCED11_2': 'Lower secondary education',
    'ISCED11_3': 'Upper secondary education',
    'ISCED11_34' : 'Upper secondary general education',
    'ISCED11_35' : 'Upper secondary vocational education',
    'ISCED11_2_34' : 'Lower secondary and upper secondary general education',
    'ISCED11_2_35' : 'Lower secondary and upper secondary vocational education',
    'ISCED11_34_35': 'Upper secondary general and vocational education'
    }