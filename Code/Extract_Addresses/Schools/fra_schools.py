import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED

data_path = r"V:\GIS_DATABASE\raw_data\education\schools\FRA\fr-en-annuaire-education.csv"

data = pd.read_csv(data_path,
                   delimiter=';')

data.rename(columns={'Identifiant_de_l_etablissement': 'id',
                     'Nom_etablissement': 'name',
                     'Type_etablissement': 'level_or',
                     'Statut_public_prive': 'sector',
                     'Nombre_d_eleves': 'students',
                     'date_maj_ligne': 'ref_date',
                     'latitude': 'lat', 
                     'longitude': 'lon'
                     },
            inplace=True)

data.drop(columns=['Adresse_1', 'Adresse_2',
       'Adresse_3', 'Code postal', 'Code_commune', 'Nom_commune',
       'Code_departement', 'Code_academie', 'Code_region',
       'Telephone', 'Fax', 'Web', 'Mail',
       'coordonnee_X', 'coordonnee_Y', 'epsg', 'nom_circonscription',
       'etat', 'ministere_tutelle', 'precision_localisation',
       'etablissement_multi_lignes', 'rpi_concentre', 'rpi_disperse',
       'code_nature', 'libelle_nature', 'Code_type_contrat_prive', 'PIAL',
       'etablissement_mere', 'type_rattachement_etablissement_mere',
       'code_bassin_formation', 'libelle_bassin_formation',
       'Libelle_departement', 'Libelle_academie', 'SIREN_SIRET',
       'Fiche_onisep', 'position', 'Type_contrat_prive', 'Libelle_region',
       'Section_arts', 'Section_cinema', 'Section_theatre', 'Section_sport',
       'Section_internationale', 'Section_europeenne',
       'Appartenance_Education_Prioritaire', 'GRETA', 'ULIS',
       'Restauration', 'Hebergement',
       'Post_BAC', 'Segpa',
       'date_ouverture',
       'Apprentissage', 'Lycee_Agricole', 'Lycee_militaire',
       'Lycee_des_metiers'],
          inplace=True)


data = data[data['level_or'].isin(['Collège', 'Lycée', 'Ecole'])]
data = data[(data['level_or']!='Ecole')|data['Ecole_elementaire']==1] # Drop écoles maternelles


data['isced'] = '-'
data.loc[data['level_or'] == 'Ecole', 'isced'] = "ISCED11_1"
data.loc[data['level_or'] == 'Collège', 'isced'] = "ISCED11_2"
data.loc[data['level_or'] == 'Lycée', 'isced'] = "ISCED11_3"

data['isced_detailed'] = '-'
data.loc[data['level_or'] == 'Ecole', 'isced_detailed'] = "ISCED11_1"
data.loc[data['level_or'] == 'Collège', 'isced_detailed'] = "ISCED11_2"
data.loc[(data['level_or'] == 'Lycée')&((data['Voie_technologique'] == 1)|(data['Voie_generale'] == 1))&(data['Voie_professionnelle'] != 1), 'isced_detailed'] = "ISCED11_34"
data.loc[(data['level_or'] == 'Lycée')&(data['Voie_professionnelle'] == 1)&((data['Voie_technologique'] != 1)&(data['Voie_generale'] != 1)), 'isced_detailed'] = "ISCED11_35"
data.loc[(data['level_or'] == 'Lycée')&(data['Voie_professionnelle'] == 1)&((data['Voie_technologique'] == 1)&(data['Voie_generale'] == 1)), 'isced_detailed'] = "ISCED11_34_35"


data['level_en'] = data['isced_detailed'].map(ISCED).fillna('-')


data['sector'] = data['sector'].map(
    {'Public': 'public',
     'Privé': 'private'}
    )

data.drop(columns=['Ecole_maternelle', 'Ecole_elementaire', 
                   'Voie_generale', 'Voie_technologique',
                   'Voie_professionnelle'],
          inplace=True)


gdf = gpd.GeoDataFrame(data,
                       geometry=gpd.points_from_xy(data.lon, data.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='schools',
                    iso3='FRA')

