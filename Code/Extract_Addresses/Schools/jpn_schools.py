import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED

#https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P29-v2_0.html

gdf_2013 = gpd.read_file(r"V:\GIS_DATABASE\raw_data\education\schools\JPN\P29-13\P29-13\P29-13.shp")
gdf_2013 = gdf_2013.to_crs("EPSG:4326")
gdf_2013.rename(columns = {
    'P29_005': 'name',
    'P29_004': 'level_or',
    'P29_007': 'sector'},
    inplace = True)
gdf_2013 = gdf_2013.loc[gdf_2013['level_or'].str.contains('|'.join(['16001','16002','16003','16004']))].reset_index(drop = True)
gdf_2013['id'] = gdf_2013.index+1
gdf_2013['ref_date'] = '2013'
gdf_2013['latest'] = False

gdf_2021 = gpd.read_file(r"V:\GIS_DATABASE\raw_data\education\schools\JPN\P29-21_GML\P29-21.shp")
gdf_2021 = gdf_2021.to_crs("EPSG:4326")
gdf_2021.rename(columns = {
    'P29_004': 'name',
    'P29_003': 'level_or',
    'P29_006': 'sector',
    'P29_002': 'id'},
    inplace = True)
gdf_2021 = gdf_2021.loc[gdf_2021['level_or'].isin([16001, 16002, 16003, 16004])].reset_index(drop = True) # codelist https://nlftp.mlit.go.jp/ksj/gml/codelist/SchoolClassCd-v2_0.html
gdf_2021['ref_date'] = '2021'
gdf_2021['latest'] = True


gdf_school = pd.concat([gdf_2013, gdf_2021])


gdf_school['level_or'] = gdf_school['level_or'].astype(str).replace(to_replace = {
    '16001': 'primary school',
    '16002': 'junior high school',
    '16003': 'secondary school',
    '16004': 'high school'})
gdf_school['sector'] = gdf_school['sector'].replace(to_replace = {0: '-',
                                                                  1: 'public',
                                                                  2: 'public',
                                                                  3: 'public',
                                                                  4: 'private',})




gdf_school['isced'] = ''
gdf_school.loc[gdf_school['level_or'] == 'primary school', 'isced'] = "ISCED11_1"
gdf_school.loc[gdf_school['level_or'] == 'junior high school', 'isced'] = "ISCED11_2"
gdf_school.loc[gdf_school['level_or'] == 'high school', 'isced'] = "ISCED11_3"
gdf_school.loc[gdf_school['level_or'] == 'secondary school', 'isced'] = "ISCED11_2_3"

gdf_school['isced_detailed'] = gdf_school['isced']
gdf_school.loc[gdf_school['level_or'] == 'high school', 'isced_detailed'] = "ISCED11_34"
gdf_school.loc[gdf_school['level_or'] == 'secondary school', 'isced_detailed'] = "ISCED11_2_34"



gdf_school['level_en'] = gdf_school['isced_detailed'].map(ISCED).fillna('-')


gdf_school['students'] = '-'
gdf_school['lon'] = gdf_school.geometry.x
gdf_school['lat'] = gdf_school.geometry.y

finalise_and_upload(gdf_school,
                    service='schools',
                    iso3='JPN')

