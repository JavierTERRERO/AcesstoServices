# Original code ---------------------------------------------------------

import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED


df = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\childcare\FRA\fr-en-annuaire-education.xlsx')
df = df[df['Ecole_maternelle'] == 1]
columns_to_keep = ["Identifiant_de_l_etablissement", "Nom_etablissement", 
                   "Statut_public_prive", # "Adresse_1", "Code_postal", "Nom_commune", 
                   "Nombre_d_eleves", "latitude", "longitude",
                   "date_maj_ligne"]
df = df[columns_to_keep]
df.rename(columns={
    'Identifiant_de_l_etablissement': 'id', 
    'Nom_etablissement': 'name',
    'Statut_public_prive': 'sector',
    'Nombre_d_eleves': 'students',
    'longitude': 'lon', 
    'latitude': 'lat',
    'date_maj_ligne': 'ref_date'}, inplace=True)

df['level_or'] = 'Ecole Maternelle'
df['isced'] = 'ISCED11_0'
df['isced_detailed'] = 'ISCED11_02'
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')
df['latest'] = True

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')

finalise_and_upload(gdf,
                    service='childcare',
                    iso3='FRA')
