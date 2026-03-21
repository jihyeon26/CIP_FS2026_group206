import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
)

from helpers import get_all_rows, scroll_down, scroll_to_top, parse_main_country_row
from config import SCROLL_PAUSE, SCROLL_PIXELS_MAIN, SCROLL_PIXELS_FIND


def collect_country_table(driver):
    country_data = []
    seen_countries = set()
    last_scroll = -1

    while True:
        rows = get_all_rows(driver)

        for row in rows:
            parsed = parse_main_country_row(row)
            if parsed is None:
                continue

            country = parsed["Country"]
            if country not in seen_countries:
                country_data.append({
                    "Rank": parsed["Rank"],
                    "Country": parsed["Country"],
                    "Gold": parsed["Gold"],
                    "Silver": parsed["Silver"],
                    "Bronze": parsed["Bronze"],
                    "Total": parsed["Total"],
                })
                seen_countries.add(country)

        new_scroll = scroll_down(driver, pixels=SCROLL_PIXELS_MAIN, pause=SCROLL_PAUSE)
        if new_scroll == last_scroll:
            break
        last_scroll = new_scroll

    country_df = pd.DataFrame(country_data)

    if not country_df.empty:
        country_df["Rank_num"] = pd.to_numeric(country_df["Rank"], errors="coerce")
        country_df = (
            country_df.sort_values(["Rank_num", "Country"])
            .drop(columns=["Rank_num"])
            .reset_index(drop=True)
        )

    return country_df


def find_country_row(driver, country_name, max_scrolls=20):
    last_scroll = -1

    for _ in range(max_scrolls):
        rows = get_all_rows(driver)

        for row in rows:
            parsed = parse_main_country_row(row)
            if parsed is None:
                continue

            if parsed["Country"] == country_name:
                return parsed

        new_scroll = scroll_down(driver, pixels=SCROLL_PIXELS_FIND, pause=SCROLL_PAUSE)
        if new_scroll == last_scroll:
            break
        last_scroll = new_scroll

    return None


def expand_country_row(driver, row):
    try:
        expand_btn = row.find_element(By.XPATH, './/button[@type="button"]')
    except NoSuchElementException:
        raise Exception("Expand button not found for this row.")

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", expand_btn)
    time.sleep(0.2)

    details_id = expand_btn.get_attribute("aria-controls")
    expanded = expand_btn.get_attribute("aria-expanded")

    if expanded == "false":
        driver.execute_script("arguments[0].click();", expand_btn)
        
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, details_id))
    )

    # wait until text is non-empty
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, details_id).text.strip() != ""
    )

    # small extra pause for dynamic content
    time.sleep(0.5)

    details_row = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, details_id))
    )

    return details_row, expand_btn


def collapse_country_row(driver, expand_btn):
    try:
        expanded = expand_btn.get_attribute("aria-expanded")
        if expanded == "true":
            driver.execute_script("arguments[0].click();", expand_btn)
            time.sleep(0.1)
    except Exception:
        pass


def parse_details_text(details_text):
    lines = [line.strip() for line in details_text.splitlines() if line.strip()]

    sports = []
    i = 0

    while i + 4 < len(lines):
        sport = lines[i]
        gold = lines[i + 1]
        silver = lines[i + 2]
        bronze = lines[i + 3]
        total = lines[i + 4]

        if gold.isdigit() and silver.isdigit() and bronze.isdigit() and total.isdigit():
            sports.append({
                "Sport": sport,
                "Sport_Gold": int(gold),
                "Sport_Silver": int(silver),
                "Sport_Bronze": int(bronze),
                "Sport_Total": int(total),
            })
            i += 5
        else:
            i += 1

    return sports


def collect_sport_table(driver, country_df):
    all_sports = []
    scroll_to_top(driver, pause=0.5)

    for _, crow in country_df.iterrows():
        country_name = crow["Country"]
        print(f"Processing details for: {country_name}")

        country_info = find_country_row(driver, country_name)

        if country_info is None:
            print(f"Could not find row for {country_name}")
            continue

        try:
            details_row, expand_btn = expand_country_row(driver, country_info["row"])
            parsed_sports = parse_details_text(details_row.text)

            for item in parsed_sports:
                all_sports.append({
                    "Rank": crow["Rank"],
                    "Country": country_name,
                    **item,
                })

            collapse_country_row(driver, expand_btn)

        except TimeoutException:
            print(f"Timeout while extracting {country_name}")
        except Exception as e:
            print(f"Expand/read failed for {country_name}: {e}")

    sport_df = pd.DataFrame(all_sports)
    return sport_df


def build_grouped_sport_summary(sport_df, country_df):
    if sport_df.empty:
        return pd.DataFrame()

    df = sport_df.merge(country_df[["Country", "Rank"]], on="Country", how="left")
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")

    summary_df = (
        df.groupby(["Country", "Sport", "Rank"])[
            ["Sport_Gold", "Sport_Silver", "Sport_Bronze", "Sport_Total"]
        ]
        .sum()
        .reset_index()
        .sort_values(["Rank", "Country", "Sport"])
        .set_index(["Country", "Sport"])
        .drop(columns=["Rank"])
    )

    return summary_df