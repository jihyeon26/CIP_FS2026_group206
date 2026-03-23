import os
from scraper import scrape_temperature
from config import OUTPUT_PATH


def main():
    df = scrape_temperature()

    # N/A report
    na_count = df["temperature"].isna().sum()
    print(f"Total rows scraped: {len(df)}")
    print(f"Missing temperature values: {na_count}")

    if na_count > 0:
        print(df[df["temperature"].isna()][["country"]].to_string())

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()