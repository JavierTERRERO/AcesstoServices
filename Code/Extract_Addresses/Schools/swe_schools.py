import geopandas as gpd
import pandas as pd
import requests
import json
from utilities import gisdb_connection, finalise_and_upload, ISCED 
"""
################################### Fetching data from API ############################################
response_API = requests.get('https://api.skolverket.se/skolenhetsregistret/v1/skolenhet') 
print(response_API.status_code)

data = response_API.text
parse_json = json.loads(data)

lists = parse_json['Skolenheter']
school_id = pd.DataFrame(lists)

# Dropping non-active and planned facilities 
school_id = school_id[school_id['Status'] != 'Planerad']
school_id = school_id[school_id['Status'] != 'Vilande']

columns_to_keep = ['Skolenhetskod', 'Skolenhetsnamn', 'PeOrgNr']
school_id = school_id[columns_to_keep]

school_id = school_id.rename(columns={'Skolenhetskod': 'id', 'Skolenhetsnamn': 'name'})

# Run when needing to collect the following data 
school_type = []
identification = []
name = []
status = []
school_isced = []
latitude = []
longitude = []

for id in school_id['id']:
    # Construct the API request URL with the value of 'Skolenhetskod' in the URL
    api_url = f'https://api.skolverket.se/skolenhetsregistret/v1/skolenhet/{id}/20240408'
    
    # Make the API request
    response_API = requests.get(api_url)
    
    data = response_API.text
    parse_json = json.loads(data)

    SkolenhetInfo = parse_json['SkolenhetInfo']

    # Extracting the school_type value 
    school_type1 = SkolenhetInfo['Inriktningstyp']
    
    # Extracting id 
    id1 = SkolenhetInfo['Skolenhetskod']

    # Extracting name 
    Name = SkolenhetInfo['Namn']

    # Extracting status 
    Status = SkolenhetInfo['Status']

    # Extracting longitude and latitude values 
    besoksadress = SkolenhetInfo['Besoksadress']
    geo_data = besoksadress['GeoData']
    lat = geo_data['Koordinat_WGS84_Lat']
    lng = geo_data['Koordinat_WGS84_Lng']

    # Extracting school_isced level 
    skolformer = SkolenhetInfo['Skolformer']
    isced = skolformer[0].get('type', '')

    # Append latitude and longitude values to their respective lists
    school_type.append(school_type1)
    identification.append(id1)
    name.append(Name)
    status.append(Status)
    latitude.append(lat)
    longitude.append(lng)
    school_isced.append(isced)
    
data = {
    'school_type': school_type,
    'id': identification, 
    'name': name,
    'status': status,
    'latitude': latitude,
    'longitude': longitude,
    'school_isced': school_isced
}

coordinates = pd.DataFrame(data)

df = pd.merge(coordinates, school_id, how='outer', on=['name', 'id'])
df.to_csv(r'V:\GIS_DATABASE\raw_data\education\schools\SWE\swe_schools.csv', index=False)
"""
################################### Cleaning data and uploading to education schema ############################################
df = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\schools\SWE\swe_schools.csv')

df = df.drop(columns=['status', 'PeOrgNr'])

df.rename(columns={
    'school_type': 'sector',
    'school_isced': 'level_or', 
    'Authority': 'sector', 
    'latitude': 'lat',
    'longitude': 'lon'
}, inplace=True)

df = df[df['level_or'] != 'Sfi']
df = df[df['level_or'] != 'Komvux']
df = df[df['level_or'] != 'Fritidshem']
df = df[df['level_or'] != 'Central']
df = df[df['level_or'] != 'Grundsarskola'] # Grundsarskola represents primary schools for children with disabilities 
df = df[df['level_or'] != 'Gymnasiesarskola'] # Gymnasiesarskola reprsents secondary schools for pupils with disabilities
df = df[df['level_or'] != 'Sarvux'] # Sarvux is in reference to special schools for adults with disabilities

df.loc[df['sector']=='Ej relevant', 'sector']= 'public'
df.loc[df['sector']=='Allmän', 'sector']= 'private'
df.loc[df['sector']=='Konfessionell', 'sector']= 'private'
df.loc[df['sector']=='Internationell', 'sector']= 'private'
df.loc[df['sector']=='Waldorf', 'sector']= 'private'

df['isced'] = '-'
df.loc[df['level_or']=='Grundskola', 'isced']= 'ISCED11_1' 
df.loc[df['level_or']=='Gymnasieskola', 'isced']= 'ISCED11_3' 

df = df.dropna(subset=['lon', 'lat'])
df['isced_detailed'] = df['isced']
df['latest'] = True 
df['ref_date'] = '2022'
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')

prim_students = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\schools\SWE\Grundskola - Antal elever per årskurs 2023 Skolenhet.xlsx', header=5)
columns_to_keep = ['Skol-enhetskod', 'Elever, årskurs 1-9']
prim_students = prim_students[columns_to_keep]
prim_students.rename(columns={'Skol-enhetskod': 'id', 'Elever, årskurs 1-9': 'students'}, inplace=True)

sec_students = pd.read_excel(r'V:\GIS_DATABASE\raw_data\education\schools\SWE\Gymnasieskola - Antal elever 2023 Skolenhet.xlsx', header=7)
columns_to_keep = ['Skol-enhetskod', 'Antal elever']
sec_students = sec_students[columns_to_keep]
sec_students.rename(columns={'Skol-enhetskod': 'id', 'Antal elever': 'students'}, inplace=True)
students = pd.concat([prim_students, sec_students])

df = pd.merge(df, students, how='left', on='id')

# 2.4% of schools are missing student data
#nan_ratio = df['students'].isna().sum() / len(df)
#print(nan_ratio)

df['students'] = df['students'].fillna('-')

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')

finalise_and_upload(gdf,
                    service='schools',
                    iso3='SWE')