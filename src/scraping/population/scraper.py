import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import URL


def scrape_population():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "wikitable"})

    if table is None:
        raise ValueError("Could not find population table on Wikipedia page.")

    rows = []
    for tr in table.find_all("tr")[1:]:  # skip header
        cols = tr.find_all(["td"])
        if len(cols) < 2:
            continue

        country = cols[0].get_text(strip=True)
        population_raw = cols[1].get_text(strip=True)

        # Remove commas and footnotes like [1]
        population_clean = population_raw.replace(",", "").split("[")[0].strip()

        try:
            population = int(population_clean)
        except ValueError:
            population = None  # N/A — handled in main

        rows.append({
            "country": country,
            "population": population
        })

    df = pd.DataFrame(rows)
    df = df[df["country"] != "World"]
    return df
