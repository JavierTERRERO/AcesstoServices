# Original code ---------------------------------------------------------

import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED
import geocoder
import re
import numpy as np

kg_1 = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\childcare\EST\Estonia 2022-23.xlsx', sheet_name='kindergartens')
kg_2 = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\childcare\EST\Estonia 2022-23.xlsx', sheet_name='general ed. schools')
dc = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\childcare\EST\taotluse_tulemus.csv', delimiter=';', encoding='latin1')

###############################################################################
# Cleaning individual datasets 

### kg_1 ###

kg_1.rename(columns={'Name of kindergarten': 'name', 'Ownership': 'sector',
                     'Number of children 2022/23 acadmic year': 'students'}, inplace=True)
kg_1[['lon', 'lat']] = kg_1['coordinates'].apply(lambda x: pd.Series(x.split(', ', 1)))
columns_to_keep = ['name', 'sector', 'lon', 'lat', 'students']
kg_1 = kg_1[columns_to_keep]

### kg_2 ###

kg_2 = kg_2.dropna(subset=['Number of children in preprimary']) # dropping schools with no kindergarten students
kg_2.rename(columns={'Name of general education school': 'name', 'Ownership': 'sector', 
                     'Number of children in preprimary': 'students', 'N (dms)': 'lon', 'E (dms)': 'lat'}, inplace=True)
columns_to_keep = ['name', 'sector', 'students', 'lon', 'lat']
kg_2 = kg_2[columns_to_keep]

# Changing coordinates to decimal form
def dms_to_dd(dms):
    if isinstance(dms, str):
        parts = re.split('[°\'"]+', dms)
        degrees = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        return degrees + (minutes / 60) + (seconds / 3600)
    return np.nan

kg_2['lat'] = kg_2['lat'].apply(dms_to_dd)
kg_2['lon'] = kg_2['lon'].apply(dms_to_dd)

# checking how many students are excluded due to no coordinates 
no_coords = kg_2[pd.isna(kg_2['lat'])]

total_students = kg_2['students'].sum()
no_coords_students = no_coords['students'].sum()
share_no_coords = no_coords_students/total_students
print('Share of kindergarten students left out of analysis :', share_no_coords)
# the share equals close to 4% when accounting for only students getting  
# pre-primary education in general education schools (i.e. does not account for
# students who are getting pre-primary education at facilities specifically
# for pre-primary education)
kg_2 = kg_2.dropna(subset=['lat'])

### dc ###

# What we are doing here is keeping the observations where 'Ametlik aadress' (represents commerical address)
# is the same as 'Tegevuskoha aadress' (represents where the activity takes place) and dropping the other 
# observations. 
dc['Ametlik_prefix'] = dc['Ametlik aadress'].str.split(',').str[0]
dc['Tegevuskoha_prefix'] = dc['Tegevuskoha aadress'].str.split(',').str[0]

"""
# Share of children in daycare being left out of the analysis is 66.32%, this is also not taking into account
# the children for observations where there is an NaN for the number of students. 
dc_minder = dc[dc['Ametlik_prefix'] != dc['Tegevuskoha_prefix']]
minders_dropped = dc_minder['Kohtade arvud'].sum()
dc_total = dc['Kohtade arvud'].sum()
share_dropped = minders_dropped/dc_total
print('Share of daycare children left out of analysis :', share_dropped)
"""

dc = dc[dc['Ametlik_prefix'] == dc['Tegevuskoha_prefix']]
dc = dc.drop(columns=['Ametlik_prefix', 'Tegevuskoha_prefix'])

dc.rename(columns={'Number': 'id', 'Ettevõtja nimi': 'name', 'Tegevuskoha aadress': 'address',
                   'Kohtade arvud': 'students', 'Tegevusala': 'level_or'}, inplace=True) 

# This removes all observations that receive their licensing from the Social Insurance Board.               # ASK VANDA TO CONFIRM THIS WITH HER CONTACT 
# Some sources insinuate that those that receive licensing from this agency are childminders 
# while facilities would receive licensing from the municipality. 
#dc = dc[dc['Tegevusloa väljaandja'] != 'Sotsiaalkindlustusamet'] 
#dc = dc.dropna(subset=['Tegevusloa väljaandja'])

columns_to_keep = ['id', 'name', 'address', 'students', 'level_or'] 
dc = dc[columns_to_keep]
dc = dc.dropna(subset=['address']) # dropping observations where childcare is conducted at the childs residence
dc = dc.fillna('-')


def addresses_to_coords(data: pd.DataFrame, column: str):
    df_coords = pd.DataFrame()
    for idx, address in data[column].items():
        print(address)
        g = geocoder.arcgis(address)
        df_coords = pd.concat([df_coords, pd.DataFrame({
            'id': [data.loc[idx, 'id']],  # Include the 'id' column from the original dataframe
            'address': [address], 
            'lon': [g.lng], 
            'lat': [g.lat]
        })])
    return df_coords

df_coords = addresses_to_coords(dc, column='address')
dc = pd.merge(dc, df_coords, on=['id', 'address'], how='left')
dc = dc.drop(columns=['address'])
dc['sector'] = '-'
dc['isced'] = 'ISCED11_0'
dc['isced_detailed'] = 'ISCED11_01'
dc['ref_date'] = '2024-08-23'


###############################################################################
# Concat kg_1, kg_2 and dc dataframes

df = pd.concat([kg_1, kg_2])
df.loc[((df['sector']=='municipality') | (df['sector']=='municipality school')), 'sector'] = 'public' 
df.loc[df['sector']=='private school', 'sector'] = 'private'
df['isced'] = 'ISCED11_0'
df['isced_detailed'] = df['isced']
df['ref_date'] = '2023-02-28'
df['id'] = 'FIN' + (df.index + 1).astype(str) # creating an id column
df['level_or'] = '-'

df = pd.concat([df, dc])

df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')
df['latest'] = True

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')

finalise_and_upload(gdf,
                    service='childcare',
                    iso3='EST')
