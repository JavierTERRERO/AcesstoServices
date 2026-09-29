import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED



gdf = gpd.read_file(r"V:\GIS_DATABASE\raw_data\education\schools\LTU\LT_svietimo_istaigos\SMIR_istaigos.shp")
gdf = gdf.to_crs("EPSG:4326")
gdf = gdf.loc[~gdf['Grupe'].isnull()]
gdf = gdf.loc[gdf['Grupe'].str.contains('|'.join(['Bendrojo ugdymo mokykla','Profesinio mokymo įstaiga']))]
gdf.rename(columns = {
    'Inst_kodas': 'id',
    'Tipas': 'level_or',
    'Pav_LT': 'name'},
    inplace=True)
gdf = gdf.loc[~gdf['level_or'].isnull()]


gdf.drop(columns = ['Grupe', 'Pagr_paskr', 'Paskirtis', 'PagrTipas',
       'Pav_EN', 'Pav_trump', 'Priklausom', 'Finansavim', 'Akr_VUP',
       'Akr_NVSP', 'Akr_DR', 'Adresas', 'ButoNr', 'NamoNr', 'Gatves_kod',
       'Gyv_kodas', 'Pasto_ind', 'Sav_kodas', 'Sen_kodas', 'Tel_nr', 'Faksas',
       'El_pastas', 'URL', 'JAR_kod_1', 'JAR_kod_2', 'Kodas', 'Mokytojas',
       'Mot_inst_k', 'Mot_inst_J', 'Obj_tipas', 'Ireg_data', 'Isreg_data',
       'Red_data'], inplace=True)

gdf['ISCED_1'] = gdf.level_or.str.contains('|'.join(['Pradinė mokykla','Pagrindinė mokykla','Progimnazija']))
gdf['ISCED_2'] = gdf.level_or.str.contains('|'.join(['Pagrindinė mokykla','Progimnazija','Vidurinė mokykla']))
gdf['ISCED_3'] = gdf.level_or.str.contains('|'.join(['Gimnazija','Profesinio mokymo','Profesinės mokyklos']))
gdf['ISCED_34'] = gdf.level_or.str.contains('Gimnazija')
gdf['ISCED_35'] = gdf.level_or.str.contains('|'.join(['Profesinio mokymo','Profesinės mokyklos']))

gdf['isced'] = ''
gdf.loc[gdf['ISCED_3'], 'isced'] = "ISCED11_3"
gdf.loc[gdf['ISCED_2'], 'isced'] = "ISCED11_2"
gdf.loc[gdf['ISCED_1'], 'isced'] = "ISCED11_1"
gdf.loc[gdf['ISCED_3'] & gdf['ISCED_2'], 'isced'] = "ISCED11_2_3"
gdf.loc[gdf['ISCED_1'] & gdf['ISCED_2'] & gdf['ISCED_3'], 'isced'] = "ISCED11_1_2_3"

gdf['isced_detailed'] = gdf['isced']
gdf.loc[(gdf['isced'] == 'ISCED11_3') & gdf['ISCED_35'] & ~gdf['ISCED_34'], 'isced_detailed'] = "ISCED11_35"
gdf.loc[(gdf['isced'] == 'ISCED11_3') & gdf['ISCED_34'] & ~gdf['ISCED_35'], 'isced_detailed'] = "ISCED11_34"
gdf.loc[(gdf['isced'] == 'ISCED11_3') & gdf['ISCED_34'] & gdf['ISCED_35'], 'isced_detailed'] = "ISCED11_34_35"
gdf.loc[(gdf['isced'].str.contains('|'.join(['ISCED11_2_3','ISCED11_1_2_3']))) & gdf['ISCED_35'] & ~gdf['ISCED_34'], 'isced_detailed'] = "ISCED11_2_35"
gdf.loc[(gdf['isced'].str.contains('|'.join(['ISCED11_2_3','ISCED11_1_2_3']))) & gdf['ISCED_34'] & ~gdf['ISCED_35'], 'isced_detailed'] = "ISCED11_2_34"
gdf.loc[(gdf['isced'].str.contains('|'.join(['ISCED11_2_3','ISCED11_1_2_3']))) & gdf['ISCED_34'] & gdf['ISCED_35'], 'isced_detailed'] = "ISCED11_2_34_35"


gdf['level_en'] = gdf['isced_detailed'].map(ISCED).fillna('-')


gdf.drop(columns=['ISCED_1', 'ISCED_2', 'ISCED_34',
                  'ISCED_35', 'ISCED_3'],
                  inplace=True)


gdf['students'] = '-'
gdf['ref_date'] = '2022-08-30' # Last revision date
gdf['sector'] = '-'
gdf['lon'] = gdf.geometry.x
gdf['lat'] = gdf.geometry.y

finalise_and_upload(gdf,
                    service='schools',
                    iso3='LTU')







