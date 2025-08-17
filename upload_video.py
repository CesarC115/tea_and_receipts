import time, json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from pathlib import Path

def load_cookies(driver, file_path:str):
    for cookie in json.load(open(file_path)):
        driver.add_cookie(cookie)

def save_cookies(driver, file_path:str):
    with open(file_path, 'w') as f:
        json.dump(driver.get_cookies(), f)
        
def upload_video(video_path:Path, caption:str):
    driver = uc.Chrome()
    stealth(driver, platform='Win64', fix_hairline=True)
    
    driver.get("https://www.tiktok.com/@tea.and.receipts")
    load_cookies(driver, "cookies.json")
    driver.refresh()
    time.sleep(3)
    
    element = By()

    # REVIEW LINK
    # Simulate manual access to uploading video
    # driver.get("https://www.tiktok/com/upload")
    # time.sleep(5)
    # driver.find_element(...).send_keys(video_path)
    # time.sleep(3)
    # driver.find_element().send_keys(caption)
    # time.sleep(3)
    # driver.find_element().click()
    # time.sleep(10)
    # save_cookies(driver, "cookies.json")
    # driver.quit()