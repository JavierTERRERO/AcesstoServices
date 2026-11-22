import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED

location = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\schools\AUS\school-location-2023504230404c94637ead88ff00003e0139.xlsx', sheet_name='SchoolLocations 2023')
student = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\schools\AUS\school-profile-2023.xlsx', sheet_name='SchoolProfile 2023')

columns_to_keep_location = ['ACARA SML ID', 'School Name', 'School Sector', 'School Type', 
                           'Latitude', 'Longitude', 'Calendar Year']
columns_to_keep_student = ['ACARA SML ID', 'School Name', 'Total Enrolments', 'Year Range']

location = location[columns_to_keep_location]
student = student[columns_to_keep_student]

data = pd.merge(location, student, how='outer')


data.rename(columns={'ACARA SML ID': 'id', 
                     'School Name': 'name', 
                     'School Sector': 'sector', 
                     'School Type': 'level_or', 
                     'Total Enrolments': 'students', 
                     'Calendar Year': 'ref_date', 
                     'Latitude': 'lat', 
                     'Longitude': 'lon'}, 
            inplace=True)

data.dropna(subset=['lon', 'lat'],
            inplace=True)

data['sector'] = data['sector'].map(
    {'Government': 'public',
     'Independent': 'private', 
     'Catholic': 'private'}
    )

data = data[~data.isin(['PP', 'K']).any(axis=1)] # Dropping schools dedicated solely to kindergarten or preschools grades

data['isced'] = '-'
data.loc[(data['level_or'] == 'Primary')|(data['Year Range']=='1-5')|(data['Year Range']=='1-3')|(data['Year Range']=='T-6')|(data['Year Range']=='U, R-6'), 'isced']= 'ISCED11_1'
data.loc[(data['Year Range'] == '5-9')|(data['Year Range'] =='7-8')|(data['Year Range'] =='7-9')|(data['Year Range'] =='5-7'), 'isced'] = 'ISCED11_2'
data.loc[data['level_or']=='Secondary', 'isced'] = 'ISCED11_3'
data.loc[(data['Year Range']=='Prep-7')|(data['Year Range']== 'K-8')|(data['Year Range']== 'R-7')|(data['Year Range']== 'R-9')|     # primary and lower secondary
         (data['Year Range']== 'K-7')|(data['Year Range']== 'K-9')|(data['Year Range']== 'Prep-9')|(data['Year Range']== '3-9')|
         (data['Year Range']== 'Prep-8')|(data['Year Range']== '1-9')|(data['Year Range']== 'PP-9')|(data['Year Range']== 'PP-8')|
         (data['Year Range']== 'PP-7')|(data['Year Range']== '3-7')|(data['Year Range']== 'T-7')|(data['Year Range']== '1-8')|
         (data['Year Range']== 'T-8')|(data['Year Range']== 'Prep-9')|(data['Year Range']== 'R-8')|(data['Year Range']== '2-7')|
         (data['Year Range']== '2-7')|(data['Year Range']== '1-7')|(data['Year Range']== '3-8')|(data['Year Range']== 'T-9')|
         (data['Year Range']== 'U, 3-7')|(data['Year Range']== 'U, Prep-9'), 'isced'] = 'ISCED11_1_2' 
data.loc[(data['Year Range']=='Prep-12')|(data['Year Range']=='Prep-10')|(data['Year Range']=='K-10')|(data['Year Range']=='K-12')| # For primary and secondary
         (data['Year Range']=='K-11')|(data['Year Range']=='Prep-11')|(data['Year Range']=='PP-12')|(data['Year Range']=='T-12')|
         (data['Year Range']=='3-12')|(data['Year Range']=='4-12')|(data['Year Range']=='5-12')|(data['Year Range']=='P-12')|
         (data['Year Range']=='2-12')|(data['Year Range']=='1-12')|(data['Year Range']=='PP-10')|(data['Year Range']=='PP-11')|
         (data['Year Range']=='R-12')|(data['Year Range']=='1-11')|(data['Year Range']=='2-10')|(data['Year Range']=='3-10')| 
         (data['Year Range']=='T-11')|(data['Year Range']=='T-10')|(data['Year Range']=='U, Prep-12')|(data['Year Range']=='R-10')|
         (data['Year Range']=='1-10')|(data['Year Range']=='4-10')|(data['Year Range']=='U, R-12')|(data['Year Range']=='R-11'),
         'isced'] = 'ISCED11_1_2_3' 
data.loc[(data['Year Range']=='7-11')|(data['Year Range']=='7-12')|(data['Year Range']=='8-12')|(data['Year Range']=='6-12')|       # For lower and upper secondary
         (data['Year Range']=='7-10')|(data['Year Range']=='U, 7-12')|(data['Year Range']=='6-10')|(data['Year Range']=='8-11'), 
         'isced'] = 'ISCED11_2_3'

data['isced_detailed'] = data['isced'] # No data on vocational secondary education
data['level_en'] = data['isced_detailed'].map(ISCED).fillna('-')
data['latest'] = True
data = data.drop(columns=['Year Range'])
data['ref_date'] = data['ref_date'].astype(int).astype(str)

gdf = gpd.GeoDataFrame(data,
                       geometry=gpd.points_from_xy(data.lon, data.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='schools',
                    iso3='AUS')