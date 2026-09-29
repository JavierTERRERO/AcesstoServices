import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED
import fiona

gdb_file = r"V:\GIS_DATABASE\raw_data\education\schools\COL\ColegiosColombia.gdb\ColegiosColombia.gdb"


layers = fiona.listlayers(gdb_file)

gdf = gpd.read_file(gdb_file,
                    layer='Colegios')
gdf.rename(columns={
    'Nombre': 'name', 
    'Descripción': 'level_or', 
    'X': 'lon',
    'Y': 'lat'},
    inplace=True)

gdf['id'] = gdf.index + 1

# Mapping from EDU GPS:
# https://gpseducation.oecd.org/Content/MapOfEducationSystem/COL/COL_2011_LL.pdf

level_or_to_isced = {
    'Básica Primaria': 'ISCED11_1', 
    'Básica Secundaria,Básica Primaria': 'ISCED11_1_2', 
    'Básica Secundaria,Media': 'ISCED11_2_3', 
    'Básica Secundaria,Media,Básica Primaria': 'ISCED11_1_2_3',  
    'Media': 'ISCED11_3', 
    'Media,Básica Secundaria': 'ISCED11_2_3',
    'Media,Básica Secundaria,Básica Primaria': 'ISCED11_1_2_3', 
    'Media,Básica Secundaria,Básica Primaria,Primera Infancia': 'ISCED11_1_2_3',
    'Media,Básica Secundaria,Primera Infancia': 'ISCED11_2_3',
    'Preescolar': 'ISCED11_0',
    'Preescolar,Básica Primaria': 'ISCED11_1',
    'Preescolar,Básica Primaria,Primera Infancia': 'ISCED11_1',
    'Preescolar,Básica Secundaria': 'ISCED11_2',
    'Preescolar,Básica Secundaria,Básica Primaria': 'ISCED11_1_2',
    'Preescolar,Básica Secundaria,Básica Primaria,Primera Infancia': 'ISCED11_1_2',
    'Preescolar,Básica Secundaria,Media': 'ISCED11_2_3',
    'Preescolar,Básica Secundaria,Media,Básica Primaria': 'ISCED11_1_2_3',
    'Preescolar,Básica Secundaria,Media,Básica Primaria,Primera Infancia': 'ISCED11_1_2_3',
    'Preescolar,Media': 'ISCED11_3', 
    'Preescolar,Media,Básica Primaria': 'ISCED11_1', # only primary based on google searches
    'Preescolar,Media,Básica Secundaria': 'ISCED11_2_3',
    'Preescolar,Media,Básica Secundaria,Básica Primaria': 'ISCED11_1_2_3',
    'Preescolar,Media,Básica Secundaria,Básica Primaria,Primera Infancia': 'ISCED11_1_2_3',
    'Preescolar,Primera Infancia': 'ISCED11_0'
    }

gdf['isced'] = gdf['level_or'].map(level_or_to_isced).fillna('-')
gdf['isced_detailed'] = gdf['level_or'].map(level_or_to_isced).fillna('-')

gdf['sector'] = '-'

gdf['level_en'] = gdf['isced_detailed'].map(ISCED).fillna('-')


gdf['students'] = '-'
# https://esri-colombia.maps.arcgis.com/home/item.html?id=52fcb282d5114d0fba4f5481ece134b9&view=list&sortOrder=desc&sortField=defaultFSOrder#overview
gdf['ref_date'] = 2023
gdf['latest'] = True


gdf = gpd.GeoDataFrame(gdf,
                       geometry=gpd.points_from_xy(gdf.lon, gdf.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='schools',
                    iso3='COL')
