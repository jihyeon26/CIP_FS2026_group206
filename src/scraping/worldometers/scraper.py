import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import URL


def scrape_worldometers():
    response = requests.get(URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    table = soup.find("table")

    rows = []

    for tr in table.find("tbody").find_all("tr"):
        cols = tr.find_all("td")

        if len(cols) < 3:
            continue

        country = cols[1].text.strip()
        population = cols[2].text.strip().replace(",", "")

        try:
            population = int(population)
        except:
            population = None

        rows.append({
            "country": country,
            "population": population
        })

    df = pd.DataFrame(rows)
    return df