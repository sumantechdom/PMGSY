from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import requests
import re
from selenium.webdriver.support.ui import Select
import pandas as pd
import os


class RoadProgress:
  def __init__(self, state):
    self.state = state
    self.url = 'https://omms.nic.in'
    self.districts = []
    self.blocks = []
    self.state_options = {"Andhra Pradesh": 3, 
                          "Bihar": 6, 
                          "Haryana": 14, 
                          "Maharashtra": 22, 
                          "Rajasthan": 31}
    
    
  def wait_for_overlay_to_disappear(self):
    #WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "blockUI blockOverlay")))
    time.sleep(7)

  def get_all_district_and_block(self, driver):

    #Get the option value of the state
    state_value = self.state_options.get(self.state)
    
    time.sleep(7)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, f'/html[1]/body[1]/div[2]/div[1]/form[1]/table[1]/tbody[1]/tr[1]/td[3]/select[1]/option[{state_value}]')
        )).click()

    # Extract options from the second dropdown
    second_dropdown = Select(driver.find_element(By.ID, "DistrictList_RoadWiseProgressDetails"))
    second_dropdown_options = [option.text for option in second_dropdown.options]

    del second_dropdown_options[:1]
    print(second_dropdown_options)
    self.districts = second_dropdown_options
    self.get_all_blocks(driver)

    return    

  def get_all_blocks(self,driver):
    dist_block = []

    for dist in self.districts:
        dropdown = Select(driver.find_element(By.ID,"DistrictList_RoadWiseProgressDetails"))

        # Replace 'Your Option Text' with the actual visible text of the option you want to select
        option_text_to_select = dist
        dropdown.select_by_visible_text(option_text_to_select)

        block_drop = Select(driver.find_element(By.ID, "BlockList_RoadWiseProgressDetails"))
        block_list = [opt.text for opt in block_drop.options ]
        # print(block_list)
        del block_list[:1]
        dist_block_map = {'district':dist, 'blocks':block_list}
        dist_block.append(dist_block_map)
        time.sleep(5)
    self.get_block_data_to_csv(driver,dist_block)

  def get_block_data_to_csv(self,driver,dist_block):

    headers = ["District", "Block Name", "Total No of Works", 
                    "Road Length", "Sanction Cost", "Maintainance Cost"]
    for bl in dist_block:
        print(bl)
        dropdown = Select(driver.find_element(By.ID,"DistrictList_RoadWiseProgressDetails"))
        option_text_to_select = bl['district']
        dropdown.select_by_visible_text(option_text_to_select)
        for bl_name in bl['blocks']:
            time.sleep(7)
            dropdown2 = Select(driver.find_element(By.ID,"BlockList_RoadWiseProgressDetails"))
            dropdown2.select_by_visible_text(bl_name)
            time.sleep(7)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnViewRoadWiseProgressWork")
                                    )).click()
            time.sleep(7)

            #driver.switch_to.frame(driver.find_element_by_tag_name(iframe_tag_name))
            driver.switch_to.frame(driver.find_element(By.TAG_NAME, 'iframe'))
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'html.parser')
                

            target_tbody = soup.select('body > div:nth-child(1) > form:nth-child(1) > span:nth-child(12) > div:nth-child(1) > table:nth-child(8) > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(6) > td:nth-child(3)')
            if target_tbody:
                    # Print the entire tbody content
                rows = target_tbody[0].find_all('tr')

                    # Check if there are any rows
                if rows:
                        # Extract details from the last tr (table row)
                    last_tr = rows[-1]  # Get the last tr element

                        # Print or extract information from the cells within the last tr
                    cell_data = [cell.get_text().strip() for cell in last_tr.find_all('td')]
                        # Create a DataFrame
                    df = pd.DataFrame([cell_data], columns=headers)
                    df['District'] = bl['district']
                    df['Block Name'] = bl_name
                    df['State'] = self.state
                    df = df.drop('Maintainance Cost', axis=1)
                    df = df.fillna(0)
                    print(df)

                    if os.path.isfile('scraped_data.csv'):
                        df.to_csv('scrapped_data.csv', mode='a', header=False, index=False)
                    else:
                        df.to_csv('scrapped_data.csv', index=False)
                else:
                    print("No rows found in the tbody.")
            else:
                print("Tbody not found.")

            driver.switch_to.default_content()
            time.sleep(5)
    return True
        
  def main(self):

    driver = webdriver.Firefox()
    driver.get(self.url)

    time.sleep(7)
    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "Progress Monitoring"))).click()

    time.sleep(7)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="divMenuBar"]/div/div/ul/li[4]/ul/div/li[1]/ul/li[7]'))).click()

    time.sleep(7)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="YearList_RoadWiseProgressDetails"]' ))).click()
        
    time.sleep(7)
    # Wait for the dropdown option to be clickable
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="YearList_RoadWiseProgressDetails"]/option[17]'))).click()
        
    time.sleep(7)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnViewRoadWiseProgressWork"))).click()


    self.get_all_district_and_block(driver)
    time.sleep(7)
    driver.quit()
    print(self.state)

  
    

p1 = RoadProgress("Rajasthan")
p1.main()