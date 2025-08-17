# from upload_video import *
import time, json
# import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium_stealth import stealth
# from pathlib import Path


TEST_VIDEO_PATH:str


def test_selenium_webdriver():
    driver = webdriver.Chrome() # Instantiate driver and select link
    driver.get('https://selenium.dev/dumentation') # 
    
    # Making sure we link the driver to the web page
    assert 'Selenium' in driver.title
    
    # Select an element in current page
    elem = driver.find_element(By.ID, 'm-documentationwebdriver') # ID located in 
    elem.click()
    assert 'WebDriver' in driver.title
    
    # Close the browser and driver executable
    driver.quit()
    
# def test_upload_video():
    
    
#     upload_video()


if __name__ == '__main__':
    print("Starting Upload Video Tests...")
    test_selenium_webdriver()