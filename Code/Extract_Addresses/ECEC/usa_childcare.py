import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED

df = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\childcare\USA\Child_Care_Centers.csv')

columns_to_keep = ['ID', 'NAME', 'LATITUDE', 'LONGITUDE', 'POPULATION', 'ST_SUBTYPE', 'TYPE']

df = df[columns_to_keep]

df.rename(columns={
    'ID': 'id', 
    'NAME': 'name',
    'ST_SUBTYPE': 'level_or', # Check with delegate to see if we're able to determine isced codes based on this variable
    'TYPE': 'sector', 
    'LATITUDE': 'lat',
    'LONGITUDE': 'lon',
    'POPULATION': 'students'
}, inplace=True)

df.loc[(df['sector'] == 'CENTER BASED')|(df['sector'] == 'SCHOOL BASED')|(df['sector'] == 'HEAD START'), 'sector'] = 'public'  # HEAD START is publicly funded, check with delegate about SCHOOL BASED
df.loc[(df['sector'] == 'RELIGIOUS FACILITY'), 'sector'] = 'private'
df.loc[df['students'] == -999, 'students'] = '-'

"""
# Specifying isced 01 facilities
df.loc[(df['level_or']=='CHILD CARE CENTER')|(df['level_or']=='DCC')|(df['level_or']=='CHILD CARE FACILITY')|(df['level_or']=='LICENSED CENTER - CHILD CARE PROGRAM')|
       (df['level_or']=='CHILD CARE PUBLIC SCHOOL')|(df['level_or']=='LICENSED CHILD CARE CENTER')|(df['level_or']=='INFANT CENTER')|(df['level_or']=='SCHOOL-AGE DAY CARE CENTER')|
       (df['level_or']=='DAY CARE CENTER (MIDLY ILL)')|(df['level_or']=='DAY CARE CENTER')|(df['level_or']=='CHILD CARE-NURSERY SCHOOL')|(df['level_or']=='CERTIFIED CHILD CARE CENTER')|
       (df['level_or']=='CENTER BASED CHILD CARE FACILITY')|(df['level_or']=='CHILD CARE - INFANTS/TODDLERS')|(df['level_or']=='LICENSED DAY CARE CENTER (CAPACITY 21 OR MORE'), 'isced'] = 'ISCED11_01'

# Specifying isced 02 facilities
df.loc[(df['level_or']=='PRESCHOOL PROGRAM')|df['level_or']=='HEAD START PROGRAM')|df['level_or']=='GA HEAD START')|df['level_or']=='GA EARLY HEAD START')|
       df['level_or']=='PRESCHOOL')|df['level_or']=='EARLY HEAD START/HEAD START')|df['level_or']=='OHIO DEPARTMENT OF EDUCATION LICENSED PRESCHOOL')|df['level_or']=='COMMERCIAL PRESCHOOL')|
       df['level_or']=='CERTIFIED PRE-SCHOOL'), 'isced'] = 'ISCED11_02'
"""

df['ref_date'] = '2023'
df['latest'] = True
df['isced'] = 'ISCED11_0' # Change this once we get a response for the 'ST_SUBTYPE' variable 
df['isced_detailed'] = df['isced']
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-')  


gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='childcare',
                    iso3='USA')

    