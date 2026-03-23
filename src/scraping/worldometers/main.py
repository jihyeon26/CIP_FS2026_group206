import os
from scraper import scrape_worldometers
from config import OUTPUT_PATH


def main():
    df = scrape_worldometers()

    na_count = df["population"].isna().sum()
    print(f"Total rows scraped: {len(df)}")
    print(f"Missing population values: {na_count}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()