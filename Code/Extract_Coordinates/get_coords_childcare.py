import pandas as pd
import os
import geopandas as gpd
import geocoder

ROOT_FOLDER = r"\\main.oecd.org\ASgenELS\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\indicators"
# Clean coordinates data files ------------------------------------------------
RAW_DATA_FOLDER = os.path.join(ROOT_FOLDER,
                               r"childcare-location-raw")
COORDS_FOLDER = os.path.join(ROOT_FOLDER,
                             r"childcare-coordinates")
SHP_FOLDER = os.path.join(ROOT_FOLDER,
                          r"childcare-shapefiles")


def export_csv_and_shp(data:pd.DataFrame, iso:str):
    data['iso3'] = iso
    if 'address' in data.columns and 'type' in data.columns:
        data = data[['iso3', 'address', 'type', 'lon', 'lat']]
    elif 'address' in data.columns:
        data = data[['iso3', 'address', 'lon', 'lat']]
    elif 'type' in data.columns:
        data = data[['iso3', 'type', 'lon', 'lat']]
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




# BEL
# Flemish region - kindergartens
data_3to6F = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                     r'BEL/Vestigingsplaatsen-van-scholen-kleuteronderwijs.csv'),
                        delimiter=';')
data_3to6F.rename(columns={'lx': 'lon',
                          'ly': 'lat',
                          'adres': 'address'},
                 inplace=True)
data_3to6F_nocoords = data_3to6F[(data_3to6F['lon']==0)&(data_3to6F['lat']==0)]
data_3to6F = data_3to6F[(data_3to6F['lon']!=0)|(data_3to6F['lat']!=0)]

data_3to6F_nocoords['address'] = data_3to6F_nocoords['address'] + ', Belgium' 
data_3to6F_nocoords = addresses_to_coords(data_3to6F_nocoords,
                                          column='address')
data_3to6F_nocoords = gpd.GeoDataFrame(data_3to6F_nocoords, 
                                       geometry=gpd.points_from_xy(data_3to6F_nocoords.lon, data_3to6F_nocoords.lat))
data_3to6F_nocoords = data_3to6F_nocoords.set_crs('EPSG:4326')

gdf_3to6F = gpd.GeoDataFrame(data_3to6F, 
                            geometry=gpd.points_from_xy(data_3to6F.lon, data_3to6F.lat))
gdf_3to6F = gdf_3to6F.set_crs('EPSG:31370') # The projection of the Belgian (Flemish) data is EPSG:31370
gdf_3to6F = gdf_3to6F.to_crs('EPSG:4326')

gdf_3to6F = pd.concat([gdf_3to6F, data_3to6F_nocoords])
gdf_3to6F['type'] = 'kindergarten'


# Flemish region - nurseries
data_0to3F = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                        r'BEL/16012023_adresses_childcare_settings.xlsx'))
data_0to3F['address'] = data_0to3F['Straat - huisnummer - busnummer locatie'] + ', ' + data_0to3F['Postcode locatie'].astype(str) + ' ' + data_0to3F['Gemeente locatie'] + ', Belgium' 
data_0to3F = addresses_to_coords(data_0to3F,
                                 column='address')
gdf_0to3F = gpd.GeoDataFrame(data_0to3F, 
                             geometry=gpd.points_from_xy(data_0to3F.lon, data_0to3F.lat))
gdf_0to3F = gdf_0to3F.set_crs('EPSG:4326')
gdf_0to3F['type'] = 'nursery'


# Wallonia - nurseries
data_0to3W = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                        r'BEL/bru_wall_childcare.xlsx'))
data_0to3W['address'] = data_0to3W['number'].astype(str) + ' ' + data_0to3W['address'] + ', ' + data_0to3W['zipcode'].astype(str) + ' ' + data_0to3W['locatie'].str.title() + ', Belgium'
data_0to3W = addresses_to_coords(data_0to3W,
                                 column='address')
gdf_0to3W = gpd.GeoDataFrame(data_0to3W, 
                             geometry=gpd.points_from_xy(data_0to3W.lon, data_0to3W.lat))
gdf_0to3W = gdf_0to3W.set_crs('EPSG:4326')
gdf_0to3W['type'] = 'nursery'


# Wallonia - kindergartens
data_3to6W = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                     r'BEL/Ecoles_maternelles_Wallonie et Bruxelles.xlsx'),
                           skiprows=1)
data_3to6W['address'] = data_3to6W['Rue et numéro'] + ', ' + data_3to6W['CP'].astype(str) + ' ' + data_3to6W['Localité'] + ', Belgium' 
data_3to6W = addresses_to_coords(data_3to6W,
                                column='address')
gdf_3to6W = gpd.GeoDataFrame(data_3to6W, 
                            geometry=gpd.points_from_xy(data_3to6W.lon, data_3to6W.lat))
gdf_3to6W = gdf_3to6W.set_crs('EPSG:4326')
gdf_3to6W['type'] = 'kindergarten'


# Concat the 4 datasets
gdf = pd.concat([gdf_3to6F, gdf_0to3F, gdf_3to6W, gdf_0to3W])
gdf['lon'] = gdf.geometry.x
gdf['lat'] = gdf.geometry.y
data = gdf.drop(columns=['geometry'])
export_csv_and_shp(data=data,
                   iso='BEL')


# ESP
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r"ESP\Listado.xls"))
data['address'] = data['Domicilio'].str.strip() + ', ' + data['C. Postal'].astype(str) + ' ' + data['Localidad'] + ', Spain'
data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='ESP')


# FRA
data = pd.read_csv(os.path.join(ROOT_FOLDER,
                                r'prim_edu-location-raw',
                                r'FRA\fr-en-annuaire-education.csv'),
                   delimiter=';')
data = data[data['Ecole_maternelle']==1]
data.rename(columns={'coordonnee_X': 'lon',
                     'coordonnee_Y': 'lat'},
            inplace=True)
gdf = gpd.GeoDataFrame(data, 
                       geometry=gpd.points_from_xy(data.lon, data.lat))
gdf = gdf[gdf['epsg'].notnull()]
gdf_total = gpd.GeoDataFrame()
for epsg in gdf.epsg.unique(): # For each observation, the EPSG is specified
    gdf_epsg = gdf[gdf['epsg']==epsg] 
    gdf_epsg = gdf_epsg.set_crs(epsg) 
    gdf_epsg = gdf_epsg.to_crs('EPSG:4326')
    gdf_total = pd.concat([gdf_total, gdf_epsg])

gdf_total['lon'] = gdf_total.geometry.x
gdf_total['lat'] = gdf_total.geometry.y
data = gdf_total.drop(columns=['geometry'])
export_csv_and_shp(data=data,
                   iso='FRA')



# GRC
data = pd.read_csv(os.path.join(ROOT_FOLDER,
                                r'prim_edu-location-raw',
                                r'GRC\sxoleia.csv'))
data.rename(columns={'long': 'lon'},
            inplace=True)
data = data[(data['onoma'].str.contains("ΠΑΙΔΙΚΟΣ ΣΤΑΘΜΟΣ"))|(data['onoma'].str.contains("ΝΗΠΙΑΓΩΓΕΙΟ"))] 
data = data[data['lon'].notnull()] 
export_csv_and_shp(data=data,
                   iso='GRC')



# FIN
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                 r'FIN\fin_official_data.xlsx'))
data['address'] = data['Visiting address'] + ', ' + data['Postal code'].astype(str) + ' ' + data['Town or city'] + ', Finland' 
data = data[data['address'].notnull()] # one observation has no postal code and no city/town
data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                   iso='FIN')


# CZE
# We don't use this data because it was collected using Apify which is not trusted
"""
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'CZE\cze_childcare.csv'))
data.rename(columns={'location/lng': 'lon',
                     'location/lat': 'lat'},
            inplace=True)
data = data[['address', 'lon', 'lat']]
export_csv_and_shp(data=data,
                   iso='CZE')
"""


# EST
data = pd.read_excel(os.path.join(ROOT_FOLDER,
                                  r'prim_edu-location-raw',
                                  r'EST\Estonia 2022-23.xlsx'),
                     sheet_name='kindergartens')
data[['lat', 'lon']] = data['coordinates'].str.split(pat=', ',
                                                     expand=True)
data.rename(columns={'Name of kindergarten': 'address'},
            inplace=True)
data = data[['address', 'lon', 'lat']]
export_csv_and_shp(data=data,
                   iso='EST')


# NOR
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r"NOR\nor_childcare_data.xlsx"))
data = data.drop(['school', 'type of educational institution', 'number of pupils', 'ages'], axis=1)
data = data[~data['street address'].str.match(r'^\d{4}$')] # removing observations with no street address (38 observations)
data = data.dropna() # dropping rows with NA's (0 observations)
data['address'] = data['street address'].str.strip() + ' ' + data['zipcode'].astype(str) + ' ' + data['region'] + ' ' +'Norway'
data = data[data['street address'] != 'Vei 108 1, 9170 Longyearbyen, Norway'] # doesn't belong on Norway mainland 
data = data[data['street address'] != 'Vei 229 2, 9170 Longyearbyen, Norway'] # doesn't belong on Norway mainland
data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='NOR')



# IRL
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r"IRL\irl_childcare.xlsx"))
data.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'},
            inplace=True)
data = data[['lon', 'lat']]
export_csv_and_shp(data=data,
                   iso='IRL')


# ITA 
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                   r"ITA/ita_childcare.csv"))
data['address'] = data['street_address'].astype(str) + ', ' + data['postal_code'].astype(str) + ' ' + data['province'] + ', Italy'
data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='ITA')
                    

# NZL
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                  r"NZL\nzl_childcare.csv"))
data.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'},
            inplace=True)
data = data[data['Street'] != 'North Road'] # Coordinates are incorrect, mapped in the middle of the ocean
data = data[['lon', 'lat']]
export_csv_and_shp(data=data,
                   iso='NZL')


# NLD 
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                   r"NLD/nld_childcare.csv"))
data['address'] = data['street_address'].astype(str) + ', ' + data['postal_code'].astype(str) + ' ' + data['municipality'] + ', Netherlands'
data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='NLD')