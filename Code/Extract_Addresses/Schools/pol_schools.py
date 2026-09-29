import pandas as pd 
import sqlalchemy
import os 
import geocoder
import geopandas as gpd
from utilities import gisdb_connection, finalise_and_upload, ISCED

# We're using the grade organization specified by the Eurydice report 
# "The System of Education in Poland" (page 9). In this report there are 
# three types of compulsory schooling: Szkoła podstawowa (primary school),
# Gimnazjum (lower secondary school) and Liceum ogólnokształcące (upper
# secondary school). The data only include Szkoła podstawowa (ISCED 1) and 
# Liceum ogólnokształcące (ISCED 3), therefore only those are specified, while
# also adding Technikum (technical schools).

# School counts closely resemble those reported by Statista, you can find 
# those numbers here: https://www.statista.com/statistics/1168742/poland-number-of-schools-by-type/

RAW_DATA = r'V:\GIS_DATABASE\raw_data\education\schools\POL\2025'

url = f"postgresql://{os.environ['USERNAME'].capitalize()}:@gis.main.oecd.org:5432/oecd_tl"
gisdb_connection = sqlalchemy.create_engine(url).connect()

pol_tl2 = pd.read_sql_query("SELECT name_en FROM public.tl2 WHERE iso3='POL'",
                        gisdb_connection)

pol_tl2 = pol_tl2[pol_tl2['name_en']!="Warsaw's capital city"]

regions = pol_tl2['name_en'].unique().tolist()

data = pd.DataFrame()

bad_lines_log = os.path.join(RAW_DATA, "logs.txt")                  # logging error in data 
with open(bad_lines_log, 'w') as log_file:
    log_file.write("Skipped Rows:\n")
def handle_bad_line(bad_line):
    with open(bad_lines_log, 'a') as log_file:
        log_file.write(";".join(bad_line) + "\n")
    return None

for region in regions: 
    
    df = pd.read_csv(os.path.join(RAW_DATA,
                                  f'rspo_2025_04_10_{region}.csv'), 
                     delimiter=';',
                     on_bad_lines=handle_bad_line,
                     engine='python'
                     )
    
    data = pd.concat([data, df])


data.rename(columns={
    'Numer RSPO': 'id',
    'Nazwa': 'name', 
    'Numer budynku': 'street_number', 
    'Ulica': 'street', 
    'Kod pocztowy': 'postal_code', 
    'Gmina': 'municipality', 
    'Województwo': 'province',
    'Publiczność status': 'sector', 
    'Typ': 'level_or',
    'Data założenia': 'date_established',           # extra data on school openings
    'Data likwidacji': 'date_closed',               # extra data on school consolidations 
    'Liczba uczniów': 'students'
    }, inplace=True)

data = data[['id', 'name', 'street_number', 'street', 'postal_code', 'municipality', 
             'province', 'sector', 'level_or', 'students']]

# Przedszkole = Kindergarten
# Szkoła podstawowa = Elementary school 
# Liceum ogólnokształcące = General secondary school 
# Technikum = Technical school 
data = data[(data['level_or']=='Szkoła podstawowa')|(data['level_or']=='Liceum ogólnokształcące')|
            (data['level_or']=='Technikum')]


count = data[data["level_or"] == "Szkoła podstawowa"].shape[0]
print("Number of primary schools in Poland: ", count)                       # Number of primary schools in Poland:  13415 

count = data[data["level_or"] == "Liceum ogólnokształcące"].shape[0]
print("Number of general secondary schools in Poland: ", count)             # Number of general secondary schools in Poland:  3761

count = data[data["level_or"] == "Technikum"].shape[0]
print("Number of technical schools in Poland: ", count)                     # Number of technical schools in Poland:  1864

data['isced'] = ''
data.loc[data['level_or']=='Szkoła podstawowa', 'isced']='ISCED11_1'
data.loc[data['level_or']=='Liceum ogólnokształcące', 'isced']='ISCED11_3'
data.loc[data['level_or']=='Technikum', 'isced']='ISCED11_3'

data['isced_detailed'] = ''
data.loc[data['level_or']=='Szkoła podstawowa', 'isced_detailed']='ISCED11_1'
data.loc[data['level_or']=='Liceum ogólnokształcące', 'isced_detailed']='ISCED11_34'
data.loc[data['level_or']=='Technikum', 'isced_detailed']='ISCED11_35'
data['level_en'] = data['isced_detailed'].map(ISCED).fillna('-')

data['street_number'] = data['street_number'].str.replace(r'[="]', '', regex=True)
data['postal_code'] = data['postal_code'].str.replace(r'[="]', '', regex=True)
data['ref_date'] = '2025-04-11'
data['latest'] = True

def addresses_to_coords(data:pd.DataFrame, column:str):
    def get_coords(address):
        print(address)
        g = geocoder.arcgis(address)
        return pd.Series({'lon': g.lng, 'lat': g.lat})
    coords = data['address'].apply(get_coords)
    df = pd.concat([data, coords], axis=1)
    return df

data = data.head(20) # provisional
data['address'] = data['street'] + ' ' + data['street_number'] + ', ' + data['postal_code'] + ' ' + data['municipality'] + ', ' + 'Poland'
data = addresses_to_coords(data, 'address')

gdf = gpd.GeoDataFrame(data,
                       geometry=gpd.points_from_xy(data.lon, data.lat),
                       crs='EPSG:4326')

finalise_and_upload(gdf,
                    service='schools',
                    iso3='POL')
