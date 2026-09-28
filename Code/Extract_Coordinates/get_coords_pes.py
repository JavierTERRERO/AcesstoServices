import pandas as pd
import os
import geopandas as gpd
import geocoder
from sqlalchemy import create_engine


ROOT_FOLDER = r"\\main.oecd.org\ASgenELS\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\indicators"
# Clean coordinates data files ------------------------------------------------
RAW_DATA_FOLDER = os.path.join(ROOT_FOLDER,
                               r"pes-location-raw")
COORDS_FOLDER = os.path.join(ROOT_FOLDER,
                             r"pes-coordinates")
SHP_FOLDER = os.path.join(ROOT_FOLDER,
                          r"pes-shapefiles")


def export_csv_and_shp(data:pd.DataFrame, iso:str):
    data['iso3'] = iso
    if 'address' in data.columns:
        data = data[['iso3', 'address', 'lon', 'lat']]
    else:
        data = data[['iso3', 'lon', 'lat']]
    data.to_csv(os.path.join(COORDS_FOLDER,
                             f'{iso}.csv'),
                index=False)
    gdf = gpd.GeoDataFrame(data, 
                           geometry=gpd.points_from_xy(data.lon, data.lat))
    gdf = gdf.set_crs('EPSG:4326')
    gdf.to_file(os.path.join(SHP_FOLDER,
                             f'{iso}.shp'),
                index=False)


def addresses_to_coords(data:pd.DataFrame, column:str):
    df_coords = pd.DataFrame()
    for address in data[column].unique():
        print(address)
        g = geocoder.arcgis(address)
        df_coords = pd.concat([df_coords, pd.DataFrame({'address': [address], 'lon':[g.lng], 'lat':[g.lat]})])
    return df_coords



# AUT
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'AUT/aut_pes.xlsx'))
data.rename(columns={'address': 'street'},
            inplace=True)
data['address'] = data['street'] + ', ' + data['zip'].astype(str) + ' ' + data['city']
data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='AUT')


# CZE
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'CZE/List of personal agencies in CZ - address and only valid permit.xlsx'))
data = data[data['Application status']=='Platné povolení'] # keep only PES with valid permit
data.rename(columns={'Address': 'address'},
            inplace=True)
data = data[data['address'].notnull()]
data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='CZE')


# DNK
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'DNK/dnk_pes.xlsx'))
data.rename(columns={'dawa_xcoord_wgs84_longitude': 'lon',
                     'dawa_ycoord_wgs84_latitude': 'lat'},
            inplace=True)
data['address'] = data['StreetName'] + ' ' + data['StreetBuilding'].astype(str) + ', ' + data['PostCode'].astype(str) + ' ' + data['DistrictName']
export_csv_and_shp(data=data,
                   iso='DNK')


# ESP
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'ESP/spain-pes.csv'),
                   encoding='latin-1')
data.rename(columns={'original_address-code-txt': 'address'},
            inplace=True)
export_csv_and_shp(data=data,
                   iso='ESP')


# EST
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'EST/est_pes.xlsx'))
export_csv_and_shp(data=data,
                   iso='EST')


# FIN
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'FIN/finland_pes_geolocations.csv'),
                   encoding='latin-1')
export_csv_and_shp(data=data,
                   iso='FIN')


# FRA
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'FRA/france-pes.csv'))
data.rename(columns={'DCIRIS': 'address'},
            inplace=True)
data = data[data['LAMBERT_X'].notnull()]
gdf = gpd.GeoDataFrame(data, 
                       geometry=gpd.points_from_xy(data.LAMBERT_X, data.LAMBERT_Y))

gdf_metro = gdf[~gdf['DEP'].isin(['971', '972', '973', '974', '976'])]
gdf_973 = gdf[gdf['DEP']=='973'] # 973 Guyane
gdf_974 = gdf[gdf['DEP']=='974'] # 974 La Réunion
gdf_976 = gdf[gdf['DEP']=='976'] # 976 Mayotte
gdf_971_972 = gdf[gdf['DEP'].isin(['971', '972'])] # 971 Guadeloupe 972 Martinique

gdf_metro = gdf_metro.set_crs('EPSG:2154') # LAT and LON in Lambert 93 for France metropolitaine
gdf_973 = gdf_973.set_crs('EPSG:32622') # UTM22N
gdf_974 = gdf_974.set_crs('EPSG:32740') # UTM40S
gdf_976 = gdf_976.set_crs('EPSG:32738') # UTM38S (I supposed, based on this https://geodesie.ign.fr/contenu/fichiers/documentation/SRCfrance.pdf, the projection for Mayotte is not specified like for the rest in the metadata document)
gdf_971_972 = gdf_971_972.set_crs('EPSG:5490') # UTM20N

gdf_metro = gdf_metro.to_crs('EPSG:4326')
gdf_973 = gdf_973.to_crs('EPSG:4326')
gdf_974 = gdf_974.to_crs('EPSG:4326')
gdf_976 = gdf_976.to_crs('EPSG:4326')
gdf_971_972 = gdf_971_972.to_crs('EPSG:4326')

gdf = pd.concat([gdf_metro, gdf_973, gdf_974, gdf_976, gdf_971_972])
gdf['lon'] = gdf.geometry.x
gdf['lat'] = gdf.geometry.y
data = gdf.drop(columns=['geometry'])
export_csv_and_shp(data=data,
                   iso='FRA')



# GRC
coords_df = pd.DataFrame()
with open (os.path.join(RAW_DATA_FOLDER,
                        r'GRC/DYPA offices.txt'), 'rt', encoding='latin-1') as raw_file:  # Open lorem.txt for reading
    for line in raw_file:
        line = line.strip()
        if 'data-lat' in line:
            x = line.split()
            row = pd.DataFrame({'lon': [x[3][11:-1]], 'lat': [x[4][10:-2]]})
            coords_df = pd.concat([coords_df, row])
export_csv_and_shp(data=coords_df,
                   iso='GRC')



# IRL
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'IRL/ireland-pes.csv'))
data.rename(columns={'lng': 'lon',
                     'address-txt': 'address'},
                inplace=True)
export_csv_and_shp(data=data,
                   iso='IRL')


# ISL
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'ISL/isl_pes.xlsx'))
data['address'] = data['street address'] + ', ' +  data['city']
export_csv_and_shp(data=data,
                   iso='ISL')


# ITA 
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'ITA/italy_pes.xlsx'))
data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='ITA')


# LTU
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'LTU/ltu_pes.xlsx'))
data['address'] = data['street address'] + ', ' +  data['city']
export_csv_and_shp(data=data,
                   iso='LTU')


# LUX
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'LUX/luxembourg_pes.xlsx'))
data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='LUX')


# LVA
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'LVA/LVA-PES-coords.xlsx'))
data.rename(columns={'long': 'lon'},
            inplace=True)
export_csv_and_shp(data=data,
                   iso='LVA')


# SVN
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'SVN/svn_pes.xlsx'))
data.rename(columns={'address': 'street'},
            inplace=True)
data['address'] = data['street'] + ', ' + data['postal code'].astype(str) + ' ' + data['city']
data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='SVN')


# SWE
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'SWE/SWE-PES-coords.xlsx'))
data.rename(columns={'long': 'lon'},
            inplace=True)
export_csv_and_shp(data=data,
                   iso='SWE')


# NLD
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'NLD/nld_raw_data.csv'))
data.rename(columns={'latitude': 'lat', 'longitude': 'lon'},
            inplace=True)
export_csv_and_shp(data=data,
                   iso='NLD')



# POL 
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'POL/pol_pes.xlsx'))
data['address'] = data['street'] + ' ' + data['number'].astype(str) + ', ' + data['town'].astype(str) + ', ' + data['region']
data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='POL')


# SVK
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'SVK/svk_pes.xlsx'))
data.rename(columns={'Address': 'address'},
            inplace=True)
data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='SVK')


# PRT
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'PRT/prt_pes.xlsx'))
data.drop(['lon', 'lat'], axis=1, inplace=True)
data['address'] = data['street'] + ', ' + data['postal code'].astype(str) + ' ' + data['city']
data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='PRT')


# MEX
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'MEX/mex_pes.xlsx'))

data['address'] = data['address'] +  ', ' + 'Mexico'

data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='MEX')


# CHL
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'CHL/chl_pes.xlsx'))

data['address'] = data['address'] +  ', ' + data['city'] + ', ' + data['state'] + ', ' + 'Chile'

data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='CHL')


# ISR

data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'ISR/isr_pes.xlsx'))

data['address'] = data['Address'] +  ', ' + data['Settlement'] + ', ' + 'Israel'

data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='ISR')

# CHE

data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'CHE/che_pes.csv'))

data['address'] = data['Adresse'].astype(str) +  ', ' + data['PLZ'].astype(str) + ', ' + data['Ort'].astype(str) + ', ' + 'Switzerland'

data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='CHE')


# COL
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'COL/col_pes.csv'))
data['address'] = data['Dirección'].astype(str) +  ', ' + data['Municipio'].astype(str) + ', ' + 'Colombia'
data = addresses_to_coords(data=data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='COL')


# BGR
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'BGR/bgr_pes.xlsx'))
data['address'] = data['address'].astype(str) +  ', ' + data['postal code'].astype(str) + ' ' + data['city'].astype(str) +  ', ' + 'Bulgaria'
data = addresses_to_coords(data=data,
                           column='address') 
export_csv_and_shp(data=data,
                   iso='BGR')


# ROU
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'ROU/rou_pes.csv'))
data = addresses_to_coords(data=data,
                           column='address') 
export_csv_and_shp(data=data,
                   iso='ROU')


# NZL 
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'NZL/nzl_pes.csv'))
data.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'},
            inplace=True)     
export_csv_and_shp(data=data,
                   iso='NZL')

# NOR
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'NOR/nor_pes.csv'))
data['address'] = data['Address'] +  ', ' + 'Norway'
data = addresses_to_coords(data=data,
                           column='address') 
export_csv_and_shp(data=data,
                   iso='NOR')

# CAN
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'CAN/can_pes.xlsx'))
data['address'] = data['address'] +  ', ' + 'Canada'
data = addresses_to_coords(data=data,
                           column='address') 
export_csv_and_shp(data=data,
                   iso='CAN')


# HUN
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'HUN/hun_pes.csv'), encoding='latin-1')
data['address'] = data['street'].astype(str) +  ', ' + data['postal_code'].astype(str) + ' ' + data['town'].astype(str) + ' ' + 'Hungary'
data = addresses_to_coords(data=data,
                           column='address') 
export_csv_and_shp(data=data,
                   iso='HUN')


# DEU 
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'DEU/deu_pes.csv'), encoding='latin-1')
data['address'] = data['street_address'].astype(str) +  ', ' + data['postal_code'].astype(str) + ' ' + data['town'].astype(str) + ', ' + 'Germany'
data = addresses_to_coords(data=data,
                           column='address') 
export_csv_and_shp(data=data,
                   iso='DEU')