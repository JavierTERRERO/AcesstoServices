import os
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED

data_path = r"V:\GIS_DATABASE\raw_data\education\schools\DNK\DNK_adhoc_survey_on_primary_schools.xlsx"

data = pd.read_excel(data_path,
                     sheet_name='Data',
                     skiprows=3)


# Missing coords for 4 schools. Coordinates from Google Maps
address2coords = {
    'Lindorffs Alle 5, 2900, Gentofte, Denmark': '55.73903811129983, 12.56704724197929',
    'Universitetsvej 9, 4000, Roskilde, Denmark': '55.652498096526685, 12.135564251886365',
    'Holmehøjvej 3, 5750, Faaborg-Midtfyn, Denmark': '55.24056973596896, 10.469149188573239',
    'Bomhusvej 4, 6300, Sønderborg, Denmark': '54.90590978442588, 9.578162589922472'
    }

data['Geographical location (as latitude and longitude)'] = data['Address'].map(address2coords).fillna(data['Geographical location (as latitude and longitude)'])

data[['lat', 'lon']] = data['Geographical location (as latitude and longitude)'].str.split(', ',
                                                                                           expand=True)




print(f"Reference year: {data['Reference date (dd/mm/yyyy)'].unique()}")

data.rename(columns={'Unique school ID': 'id',
                     'Statut_public_prive': 'sector',
                     'ISCED level(s) provided': 'isced',
                     },
            inplace=True)

data.drop(columns=['Unnamed: 0', 'Country', 'Address',
                   'Reference date (dd/mm/yyyy)',
                   'Geographical location (as latitude and longitude)',
                   'TL3 region \n(if geographical location not available)',
                   'TL2 region\n (if TL3 region not available)'],
          inplace=True)


isced_dnk = {
    'ISCED 1+24': 'ISCED11_1_2',
    'ISCED 1': 'ISCED11_1'
    }
data['isced'] = data['isced'].map(isced_dnk).fillna('-') 



data['isced_detailed'] = data['isced']


data['level_en'] = data['isced_detailed'].map(ISCED).fillna('-')
data['level_or'] = '-'

data['sector'] = '-'
data['students'] = '-'
data['name'] = '-'

data['ref_date'] = 2021
data['latest'] = True

gdf = gpd.GeoDataFrame(data,
                       geometry=gpd.points_from_xy(data.lon, data.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='schools',
                    iso3='DNK')

