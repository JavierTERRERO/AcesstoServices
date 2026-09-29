import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED


poi_path = r"V:\GIS_DATABASE\raw_data\education\schools\KOR"



codes_to_level_or = {
    '103001021300': 'Primary school',
    '103001021101': 'General high school',
    #'103001021102': 'Autonomous schools (not publicly founded)',
    #'103001021103': 'Special purpose school' 
    '103001021104': 'Vocational high school',
    '103001021201': 'General middle school',
    #'103001021202': 'International school',
    #'103001021203': 'Art school'
    #'103001021204': 'Physical exercise school'
    }

level_or_to_isced = {
    'Primary school': 'ISCED11_1',
    'General middle school': 'ISCED11_2',
    'General high school': 'ISCED11_3',
    'Vocational high school': 'ISCED11_3'
    }


level_or_to_isced_detailed = {
    'Primary school': 'ISCED11_1',
    'General middle school': 'ISCED11_2',
    'General high school': 'ISCED11_34',
    'Vocational high school': 'ISCED11_35'
    }

gdf = gpd.GeoDataFrame()

for folder in  os.listdir(poi_path):
    for file in os.listdir(os.path.join(poi_path,
                                        folder,
                                        r'TN_POI')):
        if file.endswith('.shp'):
            gdf_region = gpd.read_file(os.path.join(poi_path,
                                                    folder,
                                                    r'TN_POI',
                                                    file))
            gdf_region = gdf_region[gdf_region['POI_CL_DC'].isin(list(codes_to_level_or.keys()))]
            gdf = pd.concat([gdf, gdf_region])

gdf = gdf.to_crs("EPSG:4326")
gdf['ref_date'] = '2023'
gdf['latest'] = True
gdf['level_or'] = gdf['POI_CL_DC'].map(codes_to_level_or)
gdf['isced'] = gdf['level_or'].map(level_or_to_isced)
gdf['isced_detailed'] =  gdf['level_or'].map(level_or_to_isced_detailed)
gdf['level_en'] = gdf['isced'].map(ISCED)
gdf['lon'] = gdf['geometry'].x
gdf['lat'] = gdf['geometry'].y
gdf.rename(columns={'POI_NM': 'name',
                    'NF_ID': 'id'},
           inplace=True)
gdf['students'] = '-'
gdf['sector'] = '-'

finalise_and_upload(gdf,
                    service='schools',
                    iso3='KOR')