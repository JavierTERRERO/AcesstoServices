import requests
import os
import pandas as pd
import geopandas as gpd
import logging 
from datetime import datetime
import time
from requests import JSONDecodeError

now = datetime.now()

logging.basicConfig(filename=f"isochrones_{now.year}-{str(now.month).zfill(2)}-{str(now.day).zfill(2)}_{str(now.hour).zfill(2)}-{str(now.minute).zfill(2)}.log", 
					format='%(asctime)s %(levelname)s %(message)s', 
					filemode='w') 

logger=logging.getLogger() 


logger.setLevel(logging.INFO) 



modes_by_service = {'pes': ['driving'],
                    'childcare': ['driving', 'walking'],
                    'prim_edu': ['driving', 'walking']}


# using a recursive function to download isochrones from mapbox
def fetch_from_mapbox(lon, lat, mode, params, logger):
    response = requests.get(f'https://api.mapbox.com/isochrone/v1/mapbox/{mode}/{lon},{lat}', params=params)
    try:
        gdf = gpd.GeoDataFrame.from_features(response.json())
    except IndexError:
        logger.warning(f'IndexError for coordinates ({lon}, {lat})')
        return gpd.GeoDataFrame()
    except JSONDecodeError:
        logger.warning(f'JSONDecodeError for coordinates ({lon}, {lat})')
        return gpd.GeoDataFrame()
    except:
        try:
            message = response.json()['message']
            if message == 'Too Many Requests':
                logger.info('Sleeping for 1 minute ...')
                time.sleep(60)
                return fetch_from_mapbox(lon, lat, mode, params, logger)
            else:
                logger.warning(response.json()['message'])
                return gpd.GeoDataFrame()
        except:
            logger.warning(response.json())
            return gpd.GeoDataFrame()                          
    else:
        return gdf
            


with open(r"utilities\api_key_mapbox.txt") as f:
    token = f.readlines()[0]


time_thresholds = {
    '5to20': '5,10,15,20',
    '25to40': '25,30,35,40',
    '45to60': '45,50,55,60'
    }

for service in ['pes', 'childcare', 'prim_edu']:
    

    COORDS_FOLDER = os.path.join(r"\\main.oecd.org\ASgenELS\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\indicators",
                                 f"{service}-coordinates")
    ISOCHRONES_FOLDER = os.path.join(r"\\main.oecd.org\em_sources\SPATIAL_INEQUALITIES\isochrones",
                                     f"{service}-isochrones")


    for mode in modes_by_service[service]:
        
        for time_range, contours in time_thresholds.items():
            
            params = (
                ('contours_minutes', contours),
                ('polygons', 'true'),
                ('access_token', token),
            )
        
            print(f"\nDownloading the {mode} isochrones for {service} and contours {contours} minutes\n")
            logger.info(f"\nDownloading the {mode} isochrones for {service} and contours {contours} minutes\n")
            for file in os.listdir(COORDS_FOLDER):
                if iso != 'ESP' and iso != 'FRA'
                iso = file[:-4]
                if not os.path.exists(os.path.join(ISOCHRONES_FOLDER,
                                                   'temp',
                                                   f"{iso}_{mode}_{time_range}.geojson")):
                    print(iso)
                    logger.info(iso)
                    coords_df = pd.read_csv(os.path.join(COORDS_FOLDER,
                                                         file))
                    coords_df.dropna(subset=['lon', 'lat'], inplace=True)
                    coords_df['id'] = coords_df.index
                    coords_df['coords'] = list(zip(coords_df.lon, coords_df.lat))
                    coords_dict = coords_df.set_index('id')['coords'].to_dict()
                    isochrones = gpd.GeoDataFrame()
                    for coords_id, coords in coords_dict.items():
                        lon = round(coords[0], 10)
                        lat = round(coords[1], 10)
                        gdf = fetch_from_mapbox(lon, lat, mode, params, logger)
                        if gdf.empty == False:
                            gdf.drop(columns=['fill', 'fillOpacity', 'fill-opacity', 'fillColor', 'color', 'opacity', 'metric'],
                                     inplace=True)
                            gdf.rename(columns={'contour': 'time'},
                                             inplace=True)
                            gdf['lon'] = lon
                            gdf['lat'] = lat
                            gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
                            gdf = gdf.set_crs("EPSG:4326")
                            isochrones = pd.concat([isochrones, gdf])
                        else: 
                            logger.warning('gdf is None')
                    isochrones = isochrones[~isochrones['geometry'].is_empty]
                    isochrones = isochrones[~isochrones.geometry.isnull()]
                    isochrones.to_file(os.path.join(ISOCHRONES_FOLDER,
                                                    r'temp',
                                                    f"{iso}_{mode}_{time_range}.geojson"),
                                       index=False,
                                       driver='GeoJSON')


logging.shutdown()





# Split the isochrones nurseries/kindergartens when possible
COORDS_FOLDER = os.path.join(r"\\main.oecd.org\ASgenELS\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\indicators",
                             "childcare-coordinates")

for iso in ['BEL']:
    for file in os.listdir(os.path.join(r"\\main.oecd.org\em_sources\SPATIAL_INEQUALITIES\isochrones",
                                        r"childcare-isochrones\temp")):
        if file.endswith('.geojson') and file.startswith(iso):
            gdf = gpd.read_file(os.path.join(r"\\main.oecd.org\em_sources\SPATIAL_INEQUALITIES\isochrones\childcare-isochrones\temp",
                                             file))
            type_data = pd.read_csv(os.path.join(COORDS_FOLDER,
                                                 f'{iso}.csv'))
            gdf = gdf.round({'lon': 10,
                             'lat': 10})
            type_data = type_data.round({'lon': 10,
                                         'lat': 10})
            print(len(gdf))
            gdf = gdf.merge(type_data,
                            on=['lon', 'lat'],
                            how='left')
            print(len(gdf))
            if 'type' in gdf.columns:
                print(file)
                gdf_nurseries = gdf[gdf['type']=='nursery']
                gdf_nurseries = gdf_nurseries.dissolve(by='time').reset_index()[['time', 'geometry']]
                gdf_nurseries.to_file(os.path.join(r"\\main.oecd.org\em_sources\SPATIAL_INEQUALITIES\isochrones\nurseries-isochrones\temp",
                                                   file),
                                      driver='GeoJSON')
                gdf_kindergartens = gdf[gdf['type']=='kindergarten']
                gdf_kindergartens = gdf_kindergartens.dissolve(by='time').reset_index()[['time', 'geometry']]
                gdf_kindergartens.to_file(os.path.join(r"\\main.oecd.org\em_sources\SPATIAL_INEQUALITIES\isochrones\kindergartens-isochrones\temp",
                                                       file),
                                          driver='GeoJSON')
                
                
                
# Assemble isochrone shapefiles (putting together all the time thresholds)
for service in ['pes', 'childcare', 'prim_edu', 'kindergartens', 'nurseries']:

    ISOCHRONES_FOLDER = os.path.join(r"\\main.oecd.org\em_sources\SPATIAL_INEQUALITIES\isochrones",
                                     f"{service}-isochrones" )

    for mode in ['driving', 'walking']:
        for file in os.listdir(os.path.join(ISOCHRONES_FOLDER,
                                            r'temp')):
            iso = file[:3]
            if not os.path.exists(os.path.join(ISOCHRONES_FOLDER,
                                         f"{iso}_{mode}.geojson")):
                print(f"Asssembling {service} {mode} isochrones for {iso}")
                gdf_iso = gpd.GeoDataFrame()
                for contours in time_thresholds.keys():
                    contours_shp = os.path.join(ISOCHRONES_FOLDER,
                                                'temp',
                                                f"{iso}_{mode}_{contours}.geojson")
                    contours_shp_dissolved = os.path.join(ISOCHRONES_FOLDER,
                                                          'temp',
                                                          f"{iso}_{mode}_{contours}_dissolved.geojson")
                    if os.path.exists(contours_shp)==True and os.path.exists(contours_shp_dissolved)==False:
                        print(f"Dissolving contours {contours}")
                        gdf = gpd.read_file(contours_shp)
                        gdf = gdf.dissolve(by='time').reset_index()[['time', 'geometry']]
                        gdf.to_file(contours_shp_dissolved,
                                    index=False,
                                    driver='GeoJSON')
                        gdf_iso = pd.concat([gdf_iso, gdf])
                    elif os.path.exists(contours_shp)==True and os.path.exists(contours_shp_dissolved)==True:
                        gdf = gpd.read_file(contours_shp_dissolved)
                        gdf_iso = pd.concat([gdf_iso, gdf])
                
                if gdf_iso.empty == False:
                    if gdf_iso.time.nunique() == 12:
                        gdf_iso.to_file(os.path.join(ISOCHRONES_FOLDER,
                                                     f"{iso}_{mode}.geojson"),
                                        index=False,
                                        driver='GeoJSON')
                    else:
                        print(f"Only {gdf_iso.time.unique()} contours available for {service} {mode} isochrones in {iso}")
                else:
                    print("No file available")