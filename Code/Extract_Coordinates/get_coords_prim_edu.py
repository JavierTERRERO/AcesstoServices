import pandas as pd
import os
import geopandas as gpd
import geocoder


ROOT_FOLDER = r"\\main.oecd.org\ASgenELS\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\indicators"
# Clean coordinates data files ------------------------------------------------
RAW_DATA_FOLDER = os.path.join(ROOT_FOLDER,
                               r"prim_edu-location-raw")
COORDS_FOLDER = os.path.join(ROOT_FOLDER,
                             r"prim_edu-coordinates")
SHP_FOLDER = os.path.join(ROOT_FOLDER,
                          r"prim_edu-shapefiles")


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




# BEL
# F
dataF = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'BEL/Vestigingsplaatsen-van-scholen-lager-onderwijs.csv'),
                   delimiter=';')
dataF.rename(columns={'lx': 'lon',
                     'ly': 'lat'},
            inplace=True)
gdfF = gpd.GeoDataFrame(dataF, 
                       geometry=gpd.points_from_xy(dataF.lon, dataF.lat))
gdfF = gdfF.set_crs('EPSG:31370') # The projection of the Belgian (Flemish) data is EPSG:31370
gdfF = gdfF.to_crs('EPSG:4326')
gdfF['lon'] = gdfF.geometry.x
gdfF['lat'] = gdfF.geometry.y


# W
dataW = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                     r'BEL/Ecoles_primaires_Wallonie et Bruxelles.xlsx'),
                           skiprows=1)
dataW['address'] = dataW['Rue et numéro'] + ', ' + dataW['CP'].astype(str) + ' ' + dataW['Localité'] + ', Belgium' 
dataW = addresses_to_coords(dataW,
                                column='address')
gdfW = gpd.GeoDataFrame(dataW, 
                            geometry=gpd.points_from_xy(dataW.lon, dataW.lat))
gdfW = gdfW.set_crs('EPSG:4326')


gdf = pd.concat([gdfF, gdfW])
data = gdf.drop(columns=['geometry'])
export_csv_and_shp(data=data,
                   iso='BEL')



# ESP
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                   r"ESP/Listado.xls"))
data = data[~data['Denominación genérica'].astype(str).str.contains("Adult")]
data['address'] = data['Domicilio'].str.strip() + ', ' + data['C. Postal'].astype(str) + ' ' + data['Localidad'] + ', Spain'
data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='ESP')


# FRA
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'FRA\fr-en-annuaire-education.csv'),
                   delimiter=';')
data = data[data['Ecole_elementaire']==1]
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
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'GRC\sxoleia.csv'))
data.rename(columns={'long': 'lon'},
            inplace=True)
data = data[data['onoma'].str.contains("ΔΗΜΟΤΙΚΟ")] 
data = data[data['lon'].notnull()] 
export_csv_and_shp(data=data,
                   iso='GRC')


# IRL
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'IRL\irl_prim_edu.xlsx'))
data = data.iloc[:, [1,2]]
export_csv_and_shp(data=data,
                   iso='IRL')


# LTU
data = gpd.read_file(os.path.join(RAW_DATA_FOLDER,
                                  r'LTU\SMIR_istaigos.shp'))
#data = data[data['Tipas']=='Pagrindinė mokykla']
data.loc[data['Tipas'].isnull(), 'Tipas'] = 'not defined'
data1 = data[data['Tipas'].str.contains('Pagrindinė mokykla')]
data2 = data[data['Tipas'].str.contains('Pradinė mokykla')]
data3 = data[data['Tipas'].str.contains('progimnazija')]
data4 = data[data['Tipas'].str.contains('daugiafunkcis centras')]
data = pd.concat([data1, data2, data3, data4])
data = data.to_crs('EPSG:4326')
data['lon'] = data.geometry.x
data['lat'] = data.geometry.y
data = data.drop(columns=['geometry'])
export_csv_and_shp(data=data,
                    iso='LTU')


# PRT
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                r'PRT\OECD_schools_20230324.csv'),
                   delimiter=';')
data = data[data['ISCED1']=='YES'] # Keep only primary schools
data.rename(columns={'Y_WGS84': 'lat',
                     'X_WGS84': 'lon',
                     'NAME': 'address'},
            inplace=True)
export_csv_and_shp(data=data,
                    iso='PRT')


# SWE
# We don't use this data because there are no detailed addresses only communes
#data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
#                                r'SWE\basic_data.csv'),
#                   encoding='latin-1')


# FIN
gdf = gpd.read_file(os.path.join(RAW_DATA_FOLDER,
                                r'FIN\oppilaitokset\oppilaitokset.shp'))
# Primary schools are: Peruskoulut (id 11), Peruskouluasteen erityiskoulut (id 12), Perus- ja lukioasteen koulut (id 19)
gdf = gdf[gdf['oltyp'].isin(['11', '12', '19'])]
gdf = gdf.to_crs('EPSG:4326')
gdf['lon'] = gdf.geometry.x
gdf['lat'] = gdf.geometry.y
data = gdf.drop(columns=['geometry'])
export_csv_and_shp(data=data,
                    iso='FIN')


# CZE
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r'CZE\cze_schools.xlsx'),
                     skiprows=1)
data1 = data[data["SkolaPlnyNazev"].str.contains('Základní škola')]
data2 = data[data["SkolaPlnyNazev"].str.contains('Přípravný stupeň základní školy speciální')]
data3 = data[data["SkolaPlnyNazev"].str.contains('Základní umělecká škola')]
data = pd.concat([data1, data2, data3])
data.loc[data['RedAdresa3'].notnull(), 'address'] = data['RedAdresa1'] + ', ' + data['RedAdresa2'] + ', ' + data['RedAdresa3'] + ', Czech Republic'
data.loc[data['RedAdresa3'].isnull(), 'address'] = data['RedAdresa1'] + ', ' + data['RedAdresa2'] + ', Czech Republic'
data.drop_duplicates(subset=['address'],
                     inplace=True)
data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='CZE')


# EST
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                r'EST\Estonia 2022-23.xlsx'),
                   sheet_name='general ed. schools')
data['Northing'] = data['N (dms)'].str.replace('°', ';').str[:-1]
data['Northing'] = data['Northing'].str.replace("'", ';')
data['Easting'] = data['E (dms)'].str.replace('°', ';').str[:-1]
data['Easting'] = data['Easting'].str.replace("'", ';')
data[['d', 'm', 's']] = data.Northing.str.split(';', expand=True)
data['lat'] = data['d'].astype(float) + data['m'].astype(float)/60 + data['s'].astype(float)/3600
data[['d', 'm', 's']] = data.Easting.str.split(';', expand=True)
data['lon'] = data['d'].astype(float) + data['m'].astype(float)/60 + data['s'].astype(float)/3600

# primary education schools in Estonia are schools that offer ISCED1 and ISCED2 levels (they do not have the concept of “primary” schools offering only ISCED1).
data = data[data['ISCED'].isin(['ISCED 1-3', 'ISCED 1-2', 'ISCED 0-2', 'ISCED 0-1', 'ISCED 0-3'])]

data.rename(columns={'Name of general education school': 'address'},
            inplace=True)
export_csv_and_shp(data=data,
                    iso='EST')


# NOR 
data = pd.read_excel(os.path.join(RAW_DATA_FOLDER,
                                  r"NOR\nor_raw_data.xlsx"))
# renaming columns 
data.rename(columns={data.columns[5]: 'country'}, inplace=True)
data.rename(columns={data.columns[4]: 'city'}, inplace=True)
data.rename(columns={data.columns[3]: 'postal code'}, inplace=True)
data.rename(columns={data.columns[2]: 'street address'}, inplace=True)
data.rename(columns={data.columns[1]: 'name'}, inplace=True)
data.rename(columns={data.columns[0]: 'id'}, inplace=True)
data = data.loc[data['country'] == 'Norge'] # removing schools in other countries (11 observations)
data.drop_duplicates(subset=['id', 'street address', 'postal code'], inplace=True) # Removing duplicates (4 observations)
data = data.dropna() # dropping NA's (15 observation)
data['address'] = data['street address'].str.strip() + ', ' + data['postal code'].astype(str) + ' ' + data['city'] + ', ' + data['country']
data = data[data['address'] != 'Vei 102 3, 9170 LONGYEARBYEN, Norge'] # dropping value not in Norway mainland

data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='NOR')


# ITA
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                   r"ITA/ita_prim_edu.csv"))
data['address'] = data['street_address'].astype(str) + ', ' + data['postal_code'].astype(str) + ' ' + data['province'].astype(str) + ', Italy'
data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='ITA')


# NLD
data = pd.read_csv(os.path.join(RAW_DATA_FOLDER,
                                   r"NLD/nld_prim_edu.csv"))
data['address'] = data['street'].astype(str) + ' ' + data['number'].astype(str) + ', ' + data['post_code'].astype(str) + ' ' + data['municipality'].astype(str) + ', Netherlands'
data = addresses_to_coords(data,
                           column='address')
export_csv_and_shp(data=data,
                    iso='NLD')