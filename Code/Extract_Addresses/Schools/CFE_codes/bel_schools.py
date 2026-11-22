import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED


gdf = gpd.read_file(r"V:\GIS_DATABASE\raw_data\education\schools\BEL\signaletique-fase.geojson")
gdf = gdf.set_crs("EPSG:4326")
gdf = gdf.loc[gdf['type_d_enseignement'].str.contains('|'.join(['Primaire ordinaire','Secondaire ordinaire','Secondaire CEFA']))]
gdf = gdf[gdf['adresse_de_l_etablissement'] == gdf['adresse_de_l_implantation']] # explanation in the merge request

gdf.rename(columns = {
    'numero_bce_de_l_etablissement': 'id',
    'nom_de_l_etablissement': 'name',
    'type_d_enseignement': 'level_or',
    'reseau': 'sector'},
    inplace=True)

# gdf_geom = gpd.GeoDataFrame(gdf[['name','id','adresse_de_l_implantation','geom']].groupby(['name','adresse_de_l_implantation','id'], as_index = False).first(), geometry='geom').set_crs('EPSG:4326')
# approach is to keep all écoles ordinaires for primary, secondarya and kindergarten.
# Keep also CEFA schools (schools for vocational secondary education), get rid of 
# specialised education, adult schooling, tertiary education

gdf = gdf.drop(columns = 
                   ['ndeg_fase_de_l_etablissement', 'adresse_de_l_etablissement',
                          'code_postal_de_l_etablissement', 'localite_de_l_etablissement',
                          'commune_de_l_etablissement', 'bassin', 'arrondissement_administratif',
                          'ndegfase_de_l_implantation', 'adresse_de_l_implantation',
                          'code_postal_de_l_implantation', 'localite_de_l_implantation',
                          'commune_de_l_implantation',
                          'ndeg_fase_du_p_o', 'nom_de_p_o', 'ndeg_bce_du_p_o', 'adresse_du_p_o',
                          'code_postal_du_p_o', 'localite_du_p_o', 'commune_du_p_o', 'niveau', 'genre'])
gdf['ref_date'] = '2023-11-13' # in yyyy-mm-dd
gdf['lon'] = gdf.geometry.x
gdf['lat'] = gdf.geometry.y

# gdf_data = gdf.groupby(['name', 'id', 'niveau', 'genre', 'sector'], as_index = False).agg({'level_or': ' '.join}).reset_index()
# gdf_wall = pd.merge(left= gdf_geom, right=gdf_data)

gdf_wall = gdf
gdf_wall['isced'] = '-'
gdf_wall.loc[gdf_wall['level_or'].str.contains('Primaire'), 'isced'] = "ISCED11_1"
gdf_wall.loc[gdf_wall['level_or'].str.contains('Secondaire'), 'isced'] = "ISCED11_2_3"
gdf_wall.loc[(gdf_wall['level_or'].str.contains('Primaire'))&(gdf_wall['level_or'].str.contains('Secondaire')), 'isced'] = "ISCED11_1_2_3"


gdf_wall['isced_detailed'] = '-'
gdf_wall.loc[gdf_wall['level_or'] == 'Primaire ordinaire', 'isced_detailed'] = "ISCED11_1"
gdf_wall.loc[(gdf_wall['level_or'].str.contains('Secondaire ordinaire')), 'isced_detailed'] = "ISCED11_2_34"
gdf_wall.loc[(gdf_wall['level_or'].str.contains('Secondaire CEFA')), 'isced_detailed'] = "ISCED11_2_35"

gdf_wall['level_en'] = gdf_wall['isced_detailed'].map(ISCED).fillna('-')






df_p = pd.read_csv(r"V:\GIS_DATABASE\raw_data\education\schools\BEL\Vestigingsplaatsen-van-scholen-gewoon-basisonderwijs.csv", delimiter = ';')
df_s = pd.read_csv(r"V:\GIS_DATABASE\raw_data\education\schools\BEL\Vestigingsplaatsen-van-scholen.csv", delimiter = ';')


gdf_p = gpd.GeoDataFrame(df_p, geometry=gpd.points_from_xy(df_p.lx, df_p.ly), crs="EPSG:31370").to_crs('EPSG:4326').drop(columns = 'aanmelden')
gdf_s = gpd.GeoDataFrame(df_s, geometry=gpd.points_from_xy(df_s.lx, df_s.ly), crs="EPSG:31370").to_crs('EPSG:4326')
gdf_flem = pd.concat([gdf_p,gdf_s])
gdf_flem = gdf_flem[gdf_flem['hoofdzetel'] != False] # Explanation in merge request
gdf_flem = gdf_flem.drop_duplicates(subset=['naam', 'adres', 'instellingstype']) # Explanation in merge request
gdf_flem.rename(columns = {
    'schoolnummer': 'id',
    'naam': 'name',
    'instellingstype': 'level_or',
    'net': 'sector'},
    inplace=True)

gdf_flem = gdf_flem.drop(columns = 
                   ['intern_vplnummer', 'hoofdzetel', 'adres',
                          'straat', 'huisnummer', 'busnummer', 'postcode', 'gemeente', 'niscode',
                          'provinciecode', 'provincie', 'VWO-vestigingsplaatscode', 'crab-code',
                          'crab-huisnr', 'lx', 'ly', 'kbo-nummer', 'telefoon', 'fax', 'e-mail',
                          'website', 'beheerder(s)', 'soort instelling', 'onderwijsniveau',
                          'begindatum', 'einddatum', 'status erkenning', 'clb',
                          'bestuur', 'scholengemeenschap', 'leersteuncentrum', 'taalstelsel',
                          'ingerichte hoofdstructuren'])
gdf_flem['ref_date'] = '2023-07-01' # in yyyy-mm-dd, data is for school year 2023-2024
gdf_flem['lon'] = gdf_flem.geometry.x
gdf_flem['lat'] = gdf_flem.geometry.y

gdf_flem['isced'] = '-'
gdf_flem.loc[gdf_flem['level_or'].str.contains('|'.join(['Basisschool', 'Autonome lagere school', 'Autonome kleuterschool'])), 'isced'] = "ISCED11_1"
gdf_flem.loc[gdf_flem['level_or'].str.contains('|'.join(['School voor voltijds gewoon secundair onderwijs',
                                                         'School voor voltijds gewoon secundair onderwijs en deeltijds beroepsonderwijs',
                                                         'Centrum voor deeltijds onderwijs'])), 'isced'] = "ISCED11_2_3"

gdf_flem['isced_detailed'] = '-'
gdf_flem.loc[gdf_flem['level_or'].str.contains('|'.join(['Basisschool', 
                                                         'Autonome lagere school', 
                                                         'Autonome kleuterschool'])), 'isced_detailed'] = "ISCED11_1"
gdf_flem.loc[gdf_flem['level_or'] == 'School voor voltijds gewoon secundair onderwijs', 'isced_detailed'] = "ISCED11_2_34"
gdf_flem.loc[gdf_flem['level_or'] == 'Centrum voor deeltijds onderwijs', 'isced_detailed'] = "ISCED11_35"
gdf_flem.loc[gdf_flem['level_or'] == 'School voor voltijds gewoon secundair onderwijs en deeltijds beroepsonderwijs', 'isced_detailed'] = "ISCED11_2_34_35"

gdf_flem['level_en'] = gdf_flem['isced_detailed'].map(ISCED).fillna('-')

gdf = pd.concat([gdf_wall, gdf_flem])

gdf['students'] = '-'
gdf['latest'] = True

finalise_and_upload(gdf,
                    service='schools',
                    iso3='BEL')
