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
    
    
  def wait_for_overlay_to_disappear(self):
    #WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "blockUI blockOverlay")))
    time.sleep(7)


  
    

#   def get_all_blocks(self, driver):
#     dist_block={}
#     for dist in self.districts:
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, dist))).click()
#         self.wait_for_overlay_to_disappear()
#         time.sleep(7)
#         tbody_elements = driver.find_elements(By.XPATH, "/html[1]/body[1]/div[1]/form[1]/span[1]/div[1]/table[1]/tbody[1]/tr[5]/td[3]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/table[1]/tbody[1]/tr[2]/td[1]/table[1]/tbody[1]/tr[1]/td[1]/table[1]/tbody[1]/tr[6]")
#         print(tbody_elements)
#         # self.wait_for_overlay_to_disappear()
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnViewRoadWiseProgressWork"))).click()
#         time.sleep(5)

#     return
    
    
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

    time.sleep(7)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html[1]/body[1]/div[2]/div[1]/form[1]/table[1]/tbody[1]/tr[1]/td[3]/select[1]/option[3]'))).click()

    time.sleep(7)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "DistrictList_RoadWiseProgressDetails")))

    # Extract options from the second dropdown
    second_dropdown = Select(driver.find_element(By.ID, "DistrictList_RoadWiseProgressDetails"))
    second_dropdown_options = [option.text for option in second_dropdown.options]

    del second_dropdown_options[:1]
    print(second_dropdown_options)
    self.districts = second_dropdown_options
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

    
    headers = ["District", "Block Name", "Total No of Works", "Road Length", "Sanction Cost", "Maintainance Cost"]

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
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnViewRoadWiseProgressWork"))).click()
            time.sleep(7)

            driver.switch_to.frame(0)
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
                        df.to_csv('scraped_data.csv', mode='a', header=False, index=False)
                    else:
                        df.to_csv('scraped_data.csv', index=False)
                else:
                    print("No rows found in the tbody.")
            else:
                print("Tbody not found.")

            driver.switch_to.default_content()
            time.sleep(5)

            
    time.sleep(7)
    driver.quit()
    print(self.state)

  
    

p1 = RoadProgress("Andhra Pradesh")
p1.main()