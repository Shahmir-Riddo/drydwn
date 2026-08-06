import json
import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Define custom Headers to mimic a real browser request
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_perfume(url):
    """Parses a single Fragrantica perfume detail URL and extracts key data fields."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(
                f"Failed to fetch {url} (Status Code: {response.status_code})"
            )
            return None

        soup = BeautifulSoup(response.content, "html.parser")

        # 1. Extract Name & Brand
        title_tag = soup.find("h1", {"itemprop": "name"})
        name = (
            title_tag.text.strip()
            if title_tag
            else soup.find("title").text.split(" - ")[0].strip()
        )

        brand_tag = soup.find("span", {"itemprop": "name"})
        brand = brand_tag.text.strip() if brand_tag else "Unknown"

        # 2. Extract Bottle Image URL
        img_tag = soup.find("img", {"itemprop": "image"})
        image_url = img_tag["src"] if img_tag and "src" in img_tag.attrs else ""

        # 3. Extract Main Accords
        accords = []
        accord_divs = soup.find_all("div", class_="accord-bar")
        for div in accord_divs:
            accords.append(div.text.strip())

        # 4. Extract Olfactory Pyramid (Top, Middle, Base Notes)
        top_notes, middle_notes, base_notes = [], [], []

        # Find pyramid container
        pyramid_div = soup.find("div", {"id": "pyramid"})
        if pyramid_div:
            # Extract notes by layer headings
            note_sections = pyramid_div.find_all("div")
            current_section = None

            for sec in note_sections:
                text = sec.text.lower()
                if "top notes" in text:
                    current_section = top_notes
                elif "middle notes" in text or "heart notes" in text:
                    current_section = middle_notes
                elif "base notes" in text:
                    current_section = base_notes
                elif current_section is not None:
                    # Collect note names inside spans/links
                    notes = [
                        a.text.strip()
                        for a in sec.find_all("a")
                        if a.text.strip()
                    ]
                    if notes:
                        current_section.extend(notes)

        # Remove duplicates while maintaining order
        top_notes = list(dict.fromkeys(top_notes))
        middle_notes = list(dict.fromkeys(middle_notes))
        base_notes = list(dict.fromkeys(base_notes))

        # Build clean data record
        perfume_data = {
            "name": name,
            "brand": brand,
            "url": url,
            "image_url": image_url,
            "main_accords": ", ".join(accords),
            "top_notes": ", ".join(top_notes),
            "middle_notes": ", ".join(middle_notes),
            "base_notes": ", ".join(base_notes),
        }

        return perfume_data

    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return None


def run_scraper(urls_file="urls.txt", output_csv="scraped_perfumes.csv"):
    """Reads URLs from a text file, scrapes each page, and exports to CSV."""
    # Example input URLs (Replace with your list of Fragrantica URLs)
    urls = [
        "https://www.fragrantica.com/perfume/Chanel/Bleu-de-Chanel-9099.html",
        "https://www.fragrantica.com/perfume/Dior/Sauvage-31861.html",
        "https://www.fragrantica.com/perfume/Creed/Aventus-9828.html",
    ]

    scraped_data = []

    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] Scraping: {url}")
        data = scrape_perfume(url)
        if data:
            scraped_data.append(data)

        # Politeness delay to avoid IP blocks
        time.sleep(2)

    # Export to pandas DataFrame & CSV
    df = pd.DataFrame(scraped_data)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"\nScraping complete! Saved {len(df)} records to '{output_csv}'.")


if __name__ == "__main__":
    run_scraper()