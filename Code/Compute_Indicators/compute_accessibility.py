import pandas as pd
import os
import geopandas as gpd
import numpy as np
import oecdmaps
from oecdmaps import connect_gisdb
from rasterstats import gen_zonal_stats


POPULATION_GRID_PATH = r"\\gis.main.oecd.org\Data\GHSL\GHS_POP_R2023A\GHS_POP_E2020_GLOBE_R2023A_54009_1000_V1_0\GHS_POP_E2020_GLOBE_R2023A_54009_1000_V1_0.tif"

for service in ['pes', 'prim_edu', 'childcare', 'nurseries', 'kindergartens']:

    ISOCHRONES_FOLDER = os.path.join(r"\\main.oecd.org\em_sources\SPATIAL_INEQUALITIES\isochrones",
                                     f"{service}-isochrones")
    OUTPUT_FOLDER = os.path.join(r"\\main.oecd.org\ASgenELS\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\indicators",
                                 f"{service}-accessibility-indicators")
    

    for mode in ['driving', 'walking']:
        print(f"\nComputing indicators for {mode} times to {service}\n")
        df_final = pd.DataFrame()
        for file in os.listdir(ISOCHRONES_FOLDER):
            if file.endswith(f'{mode}.geojson')==True and file.startswith('ESP')==False and file.startswith('FRA')==False:
                iso = file[:3]
                if not os.path.exists(os.path.join(OUTPUT_FOLDER,
                                                   'by_country',
                                                   f'{iso}_tl3_{mode}.csv')):
                
                    print(f"Computing {iso}")
                    connection, _ = connect_gisdb()
                    tl3 = gpd.GeoDataFrame.from_postgis(f"SELECT tl3_id, geom, reg_name_publications AS reg_name FROM public.tl3 WHERE iso3='{iso}'",
                                                        connection,
                                                        geom_col='geom')
                    connection.close()
                    tl3 = tl3.to_crs('ESRI:54009')
                    tl3['tl3_pop']=pd.DataFrame(gen_zonal_stats(tl3, 
                                                                POPULATION_GRID_PATH, 
                                                                layer=0, 
                                                                band_num=1,
                                                                nodata=-200,
                                                                stats='sum', 
                                                                all_touched=False))['sum']
                    
                    isochrones_all = gpd.read_file(os.path.join(ISOCHRONES_FOLDER, f"{iso}_{mode}.geojson"))
                    isochrones_all = isochrones_all.dissolve(by='time').reset_index()[['time', 'geometry']]
                    df_iso = pd.DataFrame()
                    for time in isochrones_all.time.unique():
                        isochrones = isochrones_all[isochrones_all['time'] == time]
                        
                        isochrones = isochrones.to_crs('ESRI:54009')
            
                        within_isochrones = gpd.overlay(tl3, 
                                                        isochrones, 
                                                        how='intersection')
                        within_isochrones['iso_pop']=pd.DataFrame(gen_zonal_stats(within_isochrones, 
                                                                                  POPULATION_GRID_PATH, 
                                                                                  layer=0, 
                                                                                  band_num=1,
                                                                                  nodata=-200,
                                                                                  stats='sum', 
                                                                                  all_touched=False))['sum']
                        df = within_isochrones.drop(columns=['geometry', 'time', 'reg_name']) # drop tl3_pop here too
                        df = df.merge(tl3[['tl3_id', 'reg_name']],  # keep tl3_pop from the tl3 df
                                      on='tl3_id', 
                                      how='right')
                        df['time'] = time
                        df['sh_pop'] = df['iso_pop'] / df['tl3_pop']
                        df.fillna(0, inplace=True)
                        df['iso3'] = iso
                        df['year'] = 2020
                        df_iso = pd.concat([df_iso, df])
                        df_iso.to_csv(os.path.join(OUTPUT_FOLDER,
                                                   r'by_country',
                                                   f'{iso}_tl3_{mode}.csv'),
                                      encoding='utf-8',
                                      index=False)
                else:
                    print(f"{iso} already computed")
                    df_iso = pd.read_csv(os.path.join(OUTPUT_FOLDER,
                                                      'by_country',
                                                      f'{iso}_tl3_{mode}.csv'))
                df_final = pd.concat([df_final, df_iso])
            
        if not df_final.empty:
            if service == 'prim_edu':
                df_final.loc[df_final['tl3_id'].isin(['PT200', 'PT300']), 'sh_pop'] = np.nan # No data for Portuguese archipelagos Azores and Madeira
                df_final.loc[df_final['tl3_id']=='BE336', 'sh_pop'] = np.nan
            if service == 'pes':
                df_final.loc[df_final['tl3_id'].isin(['FI200', 'SE214', 'ES531', 'FRY50']), 'sh_pop'] = np.nan # Dropping islands regions with 0 values for now (because we are not sure they are covered by the location data)
            if service == 'childcare':
                df_final = df_final[df_final['iso3']!='CZE'] # Dropping CZE for now because the data is based on Apify and we’re not super confident about the data quality anymore
                df_final.loc[df_final['tl3_id']=='BE336', 'sh_pop'] = np.nan
            if service == 'kindergartens' or service == 'nurseries':
                df_final.loc[df_final['tl3_id']=='BE336', 'sh_pop'] = np.nan
                
            connection, _ = connect_gisdb() 
            typo_metro = pd.read_sql_query(f"SELECT reg_id AS tl3_id, typology_id, typology FROM public.typo_metro", 
                                           connection)
            connection.close()
                
            df_final = df_final.merge(typo_metro,
                                      on='tl3_id',
                                      how='left')
            df_final = df_final.round({'tl3_pop': 0,
                                       'iso_pop': 0,
                                       'sh_pop': 3})
            df_final.to_csv(os.path.join(OUTPUT_FOLDER,
                                       f'share_of_population_tl3_{mode}.csv'),
                            encoding='utf-8',
                            index=False)
            
            
            terr_grid = pd.read_excel(r"\\main.oecd.org\ASgenELS\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\indicators\regional-statistics\OECD Territorial grid and Regional typologies - March 2023.xlsx",
                                      sheet_name='List of regions - 2023',
                                      skiprows=2)[['REG_ID', 'Metropolitan region code', 'Metropolitan region name']]
            terr_grid.rename(columns={'REG_ID': 'tl3_id',
                                      'Metropolitan region code': 'tl3_id_agg',
                                      'Metropolitan region name': 'reg_name_agg'},
                             inplace=True)
    
            df_final = df_final.merge(terr_grid,
                                      on='tl3_id',
                                      how='left')
            df_final.loc[df_final['tl3_id_agg']!='..', 'tl3_id'] = df_final['tl3_id_agg']
            df_final.loc[df_final['tl3_id_agg']!='..', 'reg_name'] = df_final['reg_name_agg']
            df_final = df_final.groupby(['tl3_id', 'reg_name', 'time', 'iso3', 'year', 'typology_id', 'typology']).sum(min_count=1).reset_index()
            df_final['sh_pop'] = df_final['iso_pop'] / df_final['tl3_pop']
            if service == 'prim_edu':
                df_final.loc[df_final['tl3_id'].isin(['PT200', 'PT300']), 'sh_pop'] = np.nan # No data for Portuguese archipelagos Azores and Madeira
                df_final.loc[df_final['tl3_id']=='BE336', 'sh_pop'] = np.nan
            if service == 'pes':
                df_final.loc[df_final['tl3_id'].isin(['FI200', 'SE214', 'ES531', 'FRY50']), 'sh_pop'] = np.nan # Dropping islands regions with 0 values for now (because we are not sure they are covered by the location data)
            if service == 'childcare':
                df_final.loc[df_final['tl3_id']=='BE336', 'sh_pop'] = np.nan
            if service == 'kindergartens' or service == 'nurseries':
                df_final.loc[df_final['tl3_id']=='BE336', 'sh_pop'] = np.nan
                
            df_final = df_final.round({'tl3_pop': 0,
                                       'iso_pop': 0,
                                       'sh_pop': 3})
            df_final.to_csv(os.path.join(OUTPUT_FOLDER,
                                         f'share_of_population_tl3_{mode}_metro-aggregated.csv'),
                            encoding='utf-8',
                            index=False)



            # Median, top 20%, bottom 20% travel times

            quantiles = {0.5: 'median',
                         0.8: 'bottom 20%',
                         0.2: 'top 20%'}            

            dataset = pd.DataFrame()
            
            
            for agg_type in ['', '_metro-aggregated']:
                
                for mode in ['walking', 'driving']:
                    
                    if os.path.exists(os.path.join(OUTPUT_FOLDER,
                                                    f"share_of_population_tl3_{mode}{agg_type}.csv")):
                    
                        dataset = pd.DataFrame()
                        
                        for quantile, quantile_label in quantiles.items():
                            
    
                            data = pd.read_csv(os.path.join(OUTPUT_FOLDER,
                                                            f"share_of_population_tl3_{mode}{agg_type}.csv"))
                            data = data[~data['sh_pop'].isnull()]
                            data = data.sort_values(by=['tl3_id', 'time'],
                                                    ascending=True)
                            data_no_access = data[(data['sh_pop']<quantile)&(data['time']==60)] # regions for which less than half of the population can access the service no matter the time threshold
                            data = data[data['sh_pop']>=quantile]
                            data = data.drop_duplicates(subset=['tl3_id'],
                                                        keep='first')
                            data.rename(columns={'time': 'travel_time'},
                                        inplace=True)
                            data = data[[ 'iso3', 'tl3_id', 'reg_name', 'travel_time', 'typology_id', 'typology']]
                            data['travel_time'] = data['travel_time'].map({time: f'{str(time-5).zfill(2)}-{str(time).zfill(2)}' for time in range(5, 65, 5)})
                            data_no_access = data_no_access[['tl3_id', 'reg_name', 'iso3', 'typology_id', 'typology']]
                            data_no_access['travel_time'] = '>60'
                            data = pd.concat([data, data_no_access])
                            data['mode'] = mode
                            data['service'] = service
                            data['quantile'] = quantile_label
                            dataset = pd.concat([dataset, data])
                            
                        dataset.to_csv(os.path.join(OUTPUT_FOLDER,
                                                    f"travel_time_tl3_{mode}{agg_type}.csv"),
                                       index=False)