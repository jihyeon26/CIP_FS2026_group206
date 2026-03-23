import time
import pandas as pd
from selenium.webdriver.common.by import By
from browser import get_driver
from config import URL


def scrape_temperature():
    driver = get_driver()
    driver.get(URL)

    # wait for JS to load
    time.sleep(5)

    rows = []

    table_rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    for row in table_rows:
        cols = row.find_elements(By.TAG_NAME, "td")

        if len(cols) < 2:
            continue

        country = cols[0].text.split("(")[0].strip()

        temps = [c.text for c in cols[1:]]

        years = list(range(1990, 1990 + len(temps)))

        for year, val in zip(years, temps):
            try:
                val = float(val)
            except:
                val = None

            rows.append({
                "country": country,
                "year": year,
                "temperature": val
            })

    driver.quit()

    df = pd.DataFrame(rows)
    return df