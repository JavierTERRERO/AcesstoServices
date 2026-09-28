# You must pip install --upgrade selenium 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd 
import os
from lxml import html 
import time

# Path to Edge webdriver executable file on your system
edge_driver_path = 'C:/Users/Salazar-lozada_M/Downloads/edgedriver_win64 (1)/msedgedriver.exe'

# Create a new Edge browser instance
edge_options = webdriver.EdgeOptions()
driver = webdriver.Edge(executable_path=edge_driver_path, options=edge_options)

# wait 5 seconds for the elements to appear 
driver.implicitly_wait(30)

url = "https://barnehagefakta.no/sok" 
driver.get(url)

# create empty lists to store data 
School = []
Street_address = []
Zipcode = []
Region = []
Type_of_educational_institution = []
Number_of_pupils = []
Ages = []

# Scroll down to the bottom of the page
last_height = driver.execute_script("return document.body.scrollHeight")

try:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(5)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
    
###############################################################################################
# extracting the name of the educatinal institution 

# Find all the school names on the page 
schools = driver.find_elements(by='xpath', value='//div[@class="ng-scope"]/div/div/div/div/a/h3')

# Store the name of each institution element 
for school in schools: 
    text = school.text
    
    # Append the list of schools to the list already created 
    School.append(text)

###############################################################################################
# extracting the address of the educatinal institution 

# find all addresses on the webpage 
street_addresses = driver.find_elements(by='xpath', value='//div[@class="ng-scope"]/div/div/div/div/a/span[1]')

for street_address in street_addresses: 
    text = street_address.text
    
    # Append the list of addresses to the list already created 
    Street_address.append(text)
    
# find all addresses on the webpage 
zipcodes = driver.find_elements(by='xpath', value='//div[@class="ng-scope"]/div/div/div/div/a/span[2]')

for zipcode in zipcodes: 
    text = zipcode.text
    
    # Append the list of addresses to the list already created 
    Zipcode.append(text)
    
# find all addresses on the webpage 
regions = driver.find_elements(by='xpath', value='//div[@class="ng-scope"]/div/div/div/div/a/span[3]')

for region in regions: 
    text = region.text
#    if not text: 
#        text = region.fillna('-')
    
    # Append the list of addresses to the list already created 
    Region.append(text)

###############################################################################################
# extracting the type of the educatinal institution 

# find type of educational institution 
institutions = driver.find_elements(by='xpath', value='//div[@class="ng-scope"]/div/div/div/div[2]/ul/li[1]/span')

for institution in institutions: 
    text = institution.text 
    
    # Append the list of institutions to the list already created 
    Type_of_educational_institution.append(text)
    
###############################################################################################
# extracting the number of pupils of the educatinal institution 
    
# find the number of pupils in each school 
pupils = driver.find_elements(by='xpath', value='//div[@class="ng-scope"]/div/div/div/div[2]/ul/li[2]/span')

for pupil in pupils: 
    text = pupil.text 
    
    # Append the list of number of pupils to the list already created 
    Number_of_pupils.append(text)

###############################################################################################
# extracting the age range of pupils of the educatinal institution 
    
# find the age range of the pupils 
ages = driver.find_elements(by='xpath', value='//div[@class="ng-scope"]/div/div/div/div[2]/ul/li[3]/span')

for age in ages: 
    text = age.text
    
    # Append the list of ages to that already created 
    Ages.append(text)

###############################################################################################    

# creating a directory for the dataset 
data = {'school': School, 'street address': Street_address, 'zipcode': Zipcode, 'region': Region, 'type of educational institution': Type_of_educational_institution, 'number of pupils': Number_of_pupils, 'ages': Ages}

childcare_data = pd.DataFrame(data)


childcare_data.to_excel(r"\\portal.oecd.org@SSL\eshare\els\pc\Deliverables\Collaboration-with-CFE\GeographicInequalities\Data\childcare-location-raw\NOR\nor_childcare_data.xlsx", encoding='utf-8-sig', index=False)