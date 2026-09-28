# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 16:50:43 2022

@author: Mavroeidi_E
"""

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
import csv

# set directory
dir_path = "V:\SPATIAL_INEQUALITIES\BACKUP\Access to services\spatial_inequalities_phaseII\PES"
os.chdir(dir_path)

PATH = "C:\Programs\chromedriver.exe"
driver = webdriver.Chrome(PATH)

## Finland
driver.get("https://toimistot.te-palvelut.fi/")

#implicit wait
driver.implicitly_wait(5)

templist = []

# loop through all areas:
area_dropdown = Select(driver.find_element_by_id("selectbox"))
area_list = [x.get_attribute('href') for x in driver.find_elements_by_xpath('//*[@id="toggle-27"]/li[*]/a')]

for i in range(1,15): 
    area_dropdown.select_by_index(i)
    # click to expand Contact
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT,'Yhteystiedot')).click() 
#    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(driver.find_element_by_link_text('Yhteystiedot'))).click()
    #    driver.find_element_by_link_text('Yhteystiedot').click()
    # click all sublinks - one link per agency
    agency_list = [x.get_attribute('href') for x in driver.find_elements_by_xpath('//*[@id="toggle-27"]/li[*]/a')]
    print(agency_list)
    for agency in agency_list:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(agency)).click()
#        driver.get(agency)
    # extract address and location
    name_txt = driver.find_element_by_xpath('//*[@id="portlet_com_liferay_journal_content_web_portlet_JournalContentPortlet_INSTANCE_tzXbElGvqk03"]/div/div[2]/div/div[2]/h1').text
    address_txt = driver.find_element_by_xpath('//*[@id="portlet_com_liferay_journal_content_web_portlet_JournalContentPortlet_INSTANCE_tzXbElGvqk03"]/div/div[2]/div/div[2]/p[1]').text
    Table_dict = {
        'name' : name_txt,
        'address' : address_txt
        }
    templist.append(Table_dict)
    df = pd.DataFrame(templist, index=[0])
#    df['address'] = df['address'].str.strip('Osoite: ')
            
# save the data frame to csv
df.to_csv('fin-pes.csv')

# close driver
driver.close()    
