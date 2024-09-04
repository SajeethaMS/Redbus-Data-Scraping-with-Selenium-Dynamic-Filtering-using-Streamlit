from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

#import streamlit as st

# Function to scrape bus routes and links for a given state
def scrape_bus_routes(state_url, state_name, max_pages, path):
    driver = webdriver.Chrome()
    driver.get(state_url)
    time.sleep(3)
    driver.maximize_window()
    
    wait = WebDriverWait(driver, 30)
    links = []
    routes = []

    for i in range(1, max_pages + 1):
        elements = driver.find_elements(By.XPATH, path)
        
        for element in elements:
            links.append(element.get_attribute("href"))
            routes.append(element.text)
        
        try:
            pagination = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="DC_117_paginationTable"]')))
            next_button = pagination.find_element(By.XPATH, f'//div[@class="DC_117_pageTabs " and text()={i+1}]')

            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            driver.execute_script("return document.readyState") == "complete"

            ActionChains(driver).move_to_element(next_button).click(next_button).perform()
            time.sleep(2)
        except TimeoutException:
            print(f"Pagination element not found within the specified time at page {i}.")
            break

        except NoSuchElementException:
            print(f"No more pages to paginate at step {i}")
            break
    
    driver.quit()
    
    driver = webdriver.Chrome()
    Bus_names = []
    Bus_types = []
    Start_Time = []
    End_Time = []
    Ratings = []
    Total_Duration = []
    Prices = []
    Seats_Available = []
    Route_names = []
    Route_links = []

    for link, route in zip(links, routes):
        driver.get(link)
        time.sleep(2)  

        # Click on elements to reveal bus details
        elements = driver.find_elements(By.XPATH, f"//a[contains(@href, '{link}')]")
        for element in elements:
            element.click()
            time.sleep(2)
        
        # Click elements to view buses
        try:
            clicks = driver.find_element(By.XPATH, "//div[@class='button']")
            clicks.click()
        except NoSuchElementException:
            continue  
        time.sleep(2)
        
        # Scroll through the page to load all bus details
        scrolling = True
        while scrolling:
            old_page_source = driver.page_source
            
            # Use ActionChains to perform a PAGE_DOWN
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            
            time.sleep(5)  
            
            new_page_source = driver.page_source
            
            if new_page_source == old_page_source:
                scrolling = False

        # Extract bus details
        bus_name = driver.find_elements(By.XPATH, "//div[@class='travels lh-24 f-bold d-color']")
        bus_type = driver.find_elements(By.XPATH, "//div[@class='bus-type f-12 m-top-16 l-color evBus']")
        start_time = driver.find_elements(By.XPATH, "//*[@class='dp-time f-19 d-color f-bold']")
        end_time = driver.find_elements(By.XPATH, "//*[@class='bp-time f-19 d-color disp-Inline']")
        total_duration = driver.find_elements(By.XPATH, "//*[@class='dur l-color lh-24']")
        rating = driver.find_elements(By.XPATH, "//div[@class='clearfix row-one']/div[@class='column-six p-right-10 w-10 fl']")
        price = driver.find_elements(By.XPATH, '//*[@class="fare d-block"]')
        seats = driver.find_elements(By.XPATH, "//div[contains(@class, 'seat-left')]")

        # Append data to respective lists
        for bus in bus_name:
            Bus_names.append(bus.text)
            Route_links.append(link)
            Route_names.append(route)
        for bus_type_elem in bus_type:
            Bus_types.append(bus_type_elem.text)
        for start_time_elem in start_time:
            Start_Time.append(start_time_elem.text)
        for end_time_elem in end_time:
            End_Time.append(end_time_elem.text)
        for total_duration_elem in total_duration:
            Total_Duration.append(total_duration_elem.text)
        for ratings in rating:
            Ratings.append(ratings.text)
        for price_elem in price:
            Prices.append(price_elem.text)
        for seats_elem in seats:
            Seats_Available.append(seats_elem.text)

    driver.quit()

    # Return the complete DataFrame
    return pd.DataFrame({
        "State": state_name,
        "Route_name": Route_names,
        "Route_link": Route_links,
        "Bus_name": Bus_names,
        "Bus_type": Bus_types,
        "Start_time": Start_Time,
        "End_time": End_Time,
        "Duration": Total_Duration,
        "Rating": Ratings,
        "Price": Prices,
        "Seats_available": Seats_Available
    })

# List of state URLs, names, and maximum pages to scrape
states = [
    {"url": "https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile", "name": "Kerala", "max_pages": 2},
    {"url": "https://www.redbus.in/online-booking/apsrtc/?utm_source=rtchometile", "name": "Andhra Pradesh", "max_pages": 4},
    {"url": "https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile", "name": "Telangana" , "max_pages":3},
    {"url": "https://www.redbus.in/online-booking/ktcl/?utm_source=rtchometile", "name": "Kadamba" , "max_pages":4},
    {"url": "https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile", "name": "Rajastan" , "max_pages":3},
    {"url": "https://www.redbus.in/online-booking/pepsu", "name": "Punjab" , "max_pages":3},
    {"url": "https://www.redbus.in/online-booking/south-bengal-state-transport-corporation-sbstc/?utm_source=rtchometile", "name": "South Bengal" , "max_pages":5},
    {"url": "https://www.redbus.in/online-booking/north-bengal-state-transport-corporation", "name": "North Bengal" , "max_pages":5},
    {"url": "https://www.redbus.in/online-booking/hrtc/?utm_source=rtchometile", "name": "Himachal" , "max_pages":5}
    {"url": "https://www.redbus.in/online-booking/uttar-pradesh-state-road-transport-corporation-upsrtc", "name": "Uttar Pradesh" , "max_pages":5}
    ]

# XPATH to find route links and names
route_xpath = "//a[@class='route']"

# DataFrame to store all the data
all_data = pd.DataFrame()

# Loop through each state and scrape the data
for state in states:
    df = scrape_bus_routes(state["url"], state["name"], state["max_pages"], route_xpath)
    all_data = pd.concat([all_data, df], ignore_index=True)

#changing the format for all required fields
all_data['Price'] = all_data['Price'].str.extract(r'(\d+)').astype(int)
all_data['Rating'] = pd.to_numeric(all_data['Rating'].str.split().str[0], errors='coerce')
all_data['Rating'] = all_data['Rating'].fillna(0.0)
all_data['Seats_available'] = all_data['Seats_available'].str.extract(r'(\d+)').astype(int)
all_data['Duration'] = all_data['Duration'].str.replace('h', ':').str.replace('m', ':00').str.replace(' ', '')
#create CSV file from dataframe all_data
all_data.to_csv('C:/Users/MDMS/Downloads/redbus_data_cleaned_2.csv', index=False)
