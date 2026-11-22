import geopandas as gpd
import pandas as pd
import psycopg2
import geoalchemy2
from utilities import gisdb_connection, finalise_and_upload, ISCED 

public = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\schools\USA\Public_School_Characteristics_-_Current.csv')
private = pd.read_sas(r'V:\GIS_DATABASE\raw_data\education\schools\USA\pss2122_pu.sas7bdat')

"""
The public dataset provides a lot of specifications including whether the school is a charter or magnet school (good to use when studying low income areas), 
how many students qualify for the free lunch and reduced lunch program (good determinant of income level since its based on tax information), number of 
students in each grade, amount of teachers, student/teacher ratio, number of students by race and more. 
The private dataset provides demographic specifications, how many students are enrolled in each grade, the affiliation of the school (religious) etc. one 
thing that differs in the private school system is a clear distinction between childcare, pre-primary, primary, lower secondary and upper secondary schools. 
Therefore, I use the LOGR2022 and HIGR2022 variables to define ISCED codes. 
"""

public = public[~public['GSHI'].isin(['KG', 'PK'])] # Removing kindergarten and prekindergarten
private = private[private['HIGR2022'] > 4] # Removing anything before primary school 

public_columns_to_keep = ['NCESSCH', 'SCH_NAME', 'SCHOOL_LEVEL', 'SCHOOL_TYPE_TEXT', 'TOTAL', 'LATCOD', 'LONCOD']
public = public[public_columns_to_keep]
private_columns_to_keep = ['P305', 'PPIN', 'PINST', 'LOGR2022', 'HIGR2022', 'LATITUDE22', 'LONGITUDE22', 'LEVEL2', 'P415']
private = private[private_columns_to_keep]

public['sector'] = 'public'
public['ref_date'] = '2023'
private['sector'] = 'private'
private['ref_date'] = '2023'

private['PINST'] = private['PINST'].apply(lambda x: str(x)[2:-1])
private['PPIN'] = private['PPIN'].apply(lambda x: str(x)[2:-1]) # ID is usually 8 digits, with leading zero's 

public.rename(columns={
    'NCESSCH': 'id', 
    'SCH_NAME': 'name',
    'TOTAL': 'students',
    'SCHOOL_LEVEL': 'level_or',
    'LATCOD': 'lat',
    'LONCOD': 'lon'
}, inplace=True)

private.rename(columns={
    'PPIN': 'id', 
    'PINST': 'name',
    'LEVEL2': 'level_or',
    'P305': 'students',
    'LATITUDE22': 'lat', 
    'LONGITUDE22': 'lon'
}, inplace=True)


private.loc[private['level_or']==1, 'level_or']='Elementary_Middle'
private.loc[private['level_or']==2, 'level_or']='Secondary_High'
private.loc[private['level_or']==3, 'level_or']='Combination_Other'

public['isced'] = '-'
public.loc[public['level_or'].str.contains('High|Secondary', case=False), 'isced'] = 'ISCED11_3'
public.loc[public['level_or'].str.contains('Middle', case=False), 'isced'] = 'ISCED11_2'
public.loc[public['level_or'].str.contains('Elementary', case=False), 'isced'] = 'ISCED11_1'

public['isced_detailed'] = '-'
public.loc[public['isced'] == 'ISCED11_1', 'isced_detailed'] = "ISCED11_1"
public.loc[public['isced'] == 'ISCED11_2', 'isced_detailed'] = "ISCED11_2"
public.loc[public['isced'] == 'ISCED11_3', 'isced_detailed'] = "ISCED11_3"
public.loc[(public['isced'] == 'ISCED11_3')&(public['SCHOOL_TYPE_TEXT'] == 'Regular school'), 'isced_detailed'] = "ISCED11_34"
public.loc[(public['isced'] == 'ISCED11_3')&(public['SCHOOL_TYPE_TEXT'] == 'Career and Technical School'), 'isced_detailed'] = "ISCED11_35"


# level_or column provides the specification Elementary/Middle for schools that are just 
# primary schools, that's the reason for extra specficiations
private['isced'] = '-'
private.loc[private['level_or'].str.contains("Elementary_Middle", case=False), 'isced'] = "ISCED11_1_2"
private.loc[(private['LOGR2022'] >= 5)&(private['HIGR2022']==14) | (private['LOGR2022'] >= 5)&(private['HIGR2022'] == 13) | (private['LOGR2022'] >= 5)&(private['HIGR2022'] == 12), 'isced'] = "ISCED11_1_2"
private.loc[(private['LOGR2022'] >= 5)&(private['HIGR2022']<=11), 'isced'] = "ISCED11_1"
private.loc[(private['LOGR2022'] >= 12)&(private['HIGR2022']<=14), 'isced'] = "ISCED11_2"
private.loc[(private['LOGR2022'] >= 15)&(private['HIGR2022']<=17), 'isced'] = "ISCED11_3"
private.loc[private['level_or'] == 'Secondary_High', 'isced'] = "ISCED11_3"
private.loc[(private['LOGR2022'] >= 12)&(private['HIGR2022']<=17), 'isced'] = "ISCED11_2_3"


private['isced_detailed'] = '-'
private.loc[(private['isced'] == 'ISCED11_1_2'), 'isced_detailed'] = "ISCED11_1_2"
private.loc[(private['isced'] == 'ISCED11_1'), 'isced_detailed'] = "ISCED11_1"
private.loc[(private['isced'] == 'ISCED11_2'), 'isced_detailed'] = "ISCED11_2"
private.loc[(private['isced'] == 'ISCED11_3'), 'isced_detailed'] = "ISCED11_3"
private.loc[(private['isced'] == 'ISCED11_3')&(private['P415']==1), 'isced_detailed'] ='ISCED11_34'
private.loc[(private['isced'] == 'ISCED11_3')&(private['P415']==5), 'isced_detailed'] ='ISCED11_35'
private.loc[(private['isced'] == 'ISCED11_2_3'), 'isced_detailed'] = "ISCED11_2_3"
private.loc[(private['isced'] == 'ISCED11_2_3')&(private['P415']==1), 'isced_detailed'] = "ISCED11_2_34"
private.loc[(private['isced'] == 'ISCED11_2_3')&(private['P415']==5), 'isced_detailed'] = "ISCED11_2_35"

public['level_en'] = public['isced_detailed'].map(ISCED).fillna('-')
private['level_en'] = private['isced_detailed'].map(ISCED).fillna('-')

public.drop(columns=['SCHOOL_TYPE_TEXT'],inplace=True)
private.drop(columns=['LOGR2022', 'HIGR2022', 'P415'],inplace=True)

data = pd.concat([public, private], axis=0)

data['latest'] = True


gdf = gpd.GeoDataFrame(data,
                       geometry=gpd.points_from_xy(data.lon, data.lat),
                       crs='EPSG:4326')

finalise_and_upload(gdf,
                    service='schools',
                    iso3='USA')
