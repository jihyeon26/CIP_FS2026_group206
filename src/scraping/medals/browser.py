from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import URL, WAIT_TIME


def start_browser():
    driver = webdriver.Chrome()
    driver.get(URL)
    driver.maximize_window()

    wait = WebDriverWait(driver, WAIT_TIME)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="row"]')))
    return driver


def close_browser(driver):
    driver.quit()