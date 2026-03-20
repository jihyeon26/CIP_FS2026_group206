import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_olympic_medals():
    url = "https://www.olympics.com/en/milano-cortina-2026/medals"

    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)

    all_data = []
    seen_countries = set()
    
    try:
        # Wait for the table to actually load (Initial wait)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="row"]')))
        
        last_height = 0
        while True:
            # 1. Grab all currently visible rows. 
            # Note: We use a loop and scrolling because the website only rendering rows that are visible in the viewport. 
            # Scrolling ensures all rows are eventually injected into the DOM.
            current_rows = driver.find_elements(By.XPATH, '//div[@role="row"]')
            
            for row in current_rows:
                cells = row.find_elements(By.XPATH, './/div[@role="cell"]')
                values = [cell.text.strip() for cell in cells if cell.text.strip()]
                
                # Check if we have valid data and haven't seen this country yet
                if len(values) >= 2:
                    country_name = values[1] 
                    if country_name not in seen_countries:
                        all_data.append(values)
                        seen_countries.add(country_name)

            # 2. Scroll down incrementally
            driver.execute_script("window.scrollBy(0, 700);")
            time.sleep(1.5) 
            
            # 3. Check for the end of the page
            new_height = driver.execute_script("return window.pageYOffset;")
            if new_height == last_height:
                break 
            last_height = new_height

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()

    # 4. Process and Save Data
    if all_data:
        cols = ["Rank", "Country", "Gold", "Silver", "Bronze", "Total"]        
        df = pd.DataFrame(all_data, columns=cols)        
        df.to_csv("../../data/raw/olympics_medals.csv", index=False)
    else:
        print("No data was found.")

if __name__ == "__main__":
    scrape_olympic_medals()