#pip install --upgrade selenium

#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.common.exceptions import NoSuchElementException
import pandas as pd 
import os
import time
import geopandas as gpd
import pandas as pd
from utilities import gisdb_connection, finalise_and_upload, ISCED 

"""

# Webscraping code using the selenium package, this code breaks down a lot. therefore it's good to save often 
# then start from the place that the scrapper left off 

#################################### Webscraping code #####################################

driver = webdriver.Edge()

# wait 5 seconds for the elements to appear 
driver.implicitly_wait(30)

url = "https://siged.sep.gob.mx/tableros/mapas.html" 
driver.get(url)

# List to store links
regions = []
district = []
Identification = []
Grade= []
Sub_grade = []
Sector = []
Name = []
Lon = []
Lat = []
Students = []

# Now you can interact with the page, extract data, or perform any other actions using Selenium methods
elements = driver.find_elements(By.XPATH, "//section[@id='cuadros']/div/div/div")

# Iterate over each element found by the XPath expression
for element in elements:
    # Find all <a> elements within the current element
    links = element.find_elements(By.TAG_NAME, "a")
    # Iterate over each <a> element and extract its href attribute
    for link in links:
        href = link.get_attribute("href")
        # Append the href attribute to the list
        regions.append(href)

# Only add if starting to webscrape from a specific page/section       
#start_scraping = False
#counter = 0 # remove if starting from the beginning 

for href in regions:
    
    # Only needed if starting from a specific page, if not you could delete this portion between the comments
    #counter += 1
    #if counter < 34:
    #    continue
        
    driver.get(href)
    
    containers = driver.find_elements(By.XPATH, "//div[@class='i4ewOd-pbTTYe-haAclf']/div")

    # if webscraping from a specific container change the containter number here       v   and remove container/dropdown specification plus loop|
    #dropdown = driver.find_element(By.XPATH, "//div[@class='i4ewOd-pbTTYe-haAclf']/div[3]/div/div[3]/div[2]/div/div")                          
    #dropdown.click()
    
    for container in containers:    
            
        dropdown = container.find_element(By.XPATH, ".//div/div[3]/div[2]/div/div")
        dropdown.click()
        
        schools = dropdown.find_elements(By.XPATH, "//div[@class='HzV7m-pbTTYe-JNdkSc-PntVL']/div")
        
        for school in schools: 
            school.click()
            
            time.sleep(0.2)
        
#            school_id = driver.find_element(By.XPATH, "//div[@class='qqvbed-UmHwN']/div[1]/div[2]").text
                
#            if start_scraping:
        
            school_id = driver.find_element(By.XPATH, "//div[@class='qqvbed-UmHwN']/div[1]/div[2]").text
            print(school_id)
            grade = driver.find_element(By.XPATH, "//div[@class='qqvbed-UmHwN']/div[3]/div[2]").text
            print(grade)
            sub_grade = driver.find_element(By.XPATH, "//div[@class='qqvbed-UmHwN']/div[4]/div[2]").text
            print(sub_grade)
            sector = driver.find_element(By.XPATH, "//div[@class='qqvbed-UmHwN']/div[5]/div[2]").text
            print(sector)
            name = driver.find_element(By.XPATH, "//div[@class='qqvbed-UmHwN']/div[7]/div[2]").text
            print(name)
            lon = driver.find_element(By.XPATH, "//div[@class='qqvbed-UmHwN']/div[23]/div[2]").text
            print(lon)
            lat = driver.find_element(By.XPATH, "//div[@class='qqvbed-UmHwN']/div[24]/div[2]").text
            print(lat)
            students = driver.find_element(By.XPATH, "//div[@class='qqvbed-UmHwN']/div[25]/div[2]").text
            print(students)
            
            Identification.append(school_id)
            Grade.append(grade)
            Sub_grade.append(sub_grade)
            Sector.append(sector)
            Name.append(name)
            Lon.append(lon)
            Lat.append(lat)
            Students.append(students)
        
        # Specifying the exact school_id to start from (only add if starting to webscrape from a specific school/container)
#            if school_id == '15EPR4318V':
#                start_scraping = True
            
            button = driver.find_element(By.XPATH, "//div[@class='qqvbed-tJHJj']/div[1]/div")
            button.click()
        
        dropdown.click()
            
# After you're done, don't forget to close the web driver
driver.quit()
            
data = {
    'Identification': Identification,
    'Grade': Grade,
    'Sub_grade': Sub_grade,
    'Sector': Sector,
    'Name': Name,
    'Lon': Lon,
    'Lat': Lat,
    'Students': Students
}

# Convert the dictionary to a DataFrame
df = pd.DataFrame(data)

df.to_csv(r'V:\GIS_DATABASE\raw_data\education\schools\MEX\mex_webscrape.csv', index=False)
"""
#################################### Data cleaning and uploading to the education schema #####################################

df = pd.read_csv(r'V:\GIS_DATABASE\raw_data\education\schools\MEX\compiled_dataset.csv', encoding='latin1')

df.rename(columns={
    'Identification': 'id',
    'Grade': 'level_or', 
    'Sector': 'sector', 
    'Name': 'name', 
    'Lon': 'lat', # lon and lat coordinates are reversed 
    'Lat': 'lon', 
    'Students': 'students'
    }, inplace=True)

# Removing grade levels that aren't primary or secondary school 
df = df[df['level_or'] != 'LICENCIATURA Y POSGRADO']
df = df[df['level_or'] != 'INICIAL']
df = df[df['level_or'] != 'PREESCOLAR']

# Dropping CONAFE schools
df = df[~df['Sub_grade'].str.endswith('CONAFE')]

# Removing duplicates, most duplicates are due to the fact that schools provides a 
# morning and afternoon service and the cohort of students changes, but the schooling level 
# stays the same. This could be due to a lack of capacity at the schools. 
df = df.sort_values(by='students', ascending=False)
df = df.drop_duplicates(subset=['Sub_grade', 'id'], keep='first')

df['isced'] = '-'
df.loc[df['level_or'] == 'PRIMARIA', 'isced'] = 'ISCED11_1'
df.loc[df['level_or'] == 'SECUNDARIA', 'isced'] = 'ISCED11_2'
df.loc[df['level_or'] == 'MEDIA SUPERIOR', 'isced'] = 'ISCED11_3'


df['isced_detailed'] = df['isced']
df.loc[df['Sub_grade'] == 'BACHILLERATO GENERAL', 'isced_detailed'] = 'ISCED11_34' # Upper secondary general education
df.loc[df['Sub_grade'] == 'BACHILLERATO TECNOLÓGICO', 'isced_detailed'] = 'ISCED11_35'
df.loc[df['Sub_grade'] == 'PROFESIONAL TÉCNICO BACHILLER', 'isced_detailed'] = 'ISCED11_35'
df.loc[df['Sub_grade'] == 'PROFESIONAL TÉCNICO', 'isced_detailed'] = 'ISCED11_35'

df.loc[df['sector'] == 'PÚBLICO', 'sector'] = 'public'
df.loc[df['sector'] == 'PRIVADO', 'sector'] = 'private'

df.drop(columns=['Sub_grade'], inplace=True)
df['level_en'] = df['isced_detailed'].map(ISCED).fillna('-') 
df['ref_date'] = '2024'
df['latest'] = True

gdf = gpd.GeoDataFrame(df,
                       geometry=gpd.points_from_xy(df.lon, df.lat),
                       crs='EPSG:4326')
finalise_and_upload(gdf,
                    service='schools',
                    iso3='MEX')