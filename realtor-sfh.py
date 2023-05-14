import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import logging
import house_to_yard as hy

logging.basicConfig(level=logging.INFO)


LOCATION = input("Location (e.g. Miami_FL, 90210): ").replace(" ", "")
BASE_URL = "https://www.realtor.com/realestateandhomes-search/"
STUB = (
    f"{LOCATION}/beds-1/baths-1/type-single-family-home/price-100000-na/age-3+/sby-6/"
)
URL = BASE_URL + STUB
PAGES = 5
AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0"


def getSoup(URL):
    headers = {"user-agent": AGENT}
    try:
        page = requests.get(URL, headers=headers)
        if page.status_code != 200:
            logging.error(f"Request returned status code {page.status_code}")
            raise requests.exceptions.HTTPError(
                f"HTTPError: Received status code {page.status_code}"
            )
        soup = BeautifulSoup(page.content, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
        return None


def extract_text(data, attr, default="-"):
    element = data.find("li", attrs={"data-label": attr})
    return element.span.text if element else default


def getHomeData(house):
    data = house.find("div", class_="property-wrap")
    price = data.span.text.replace("$", "")
    beds = extract_text(data, "pc-meta-beds")
    baths = extract_text(data, "pc-meta-baths")
    sqft = extract_text(data, "pc-meta-sqft").replace(",", "")
    lotsize = data.find("li", attrs={"data-label": "pc-meta-sqftlot"}).text

    size = hy.parse_lot_size(lotsize) if lotsize != "-" else "-"
    address = data.find("div", attrs={"data-label": "pc-address"}).text
    link = house.find("div", class_="photo-wrap").a["href"]

    hty_ratio = "-"
    house_ratio = "-"

    if size != "-" and sqft != "-" and size != 0:
        hty_ratio = round(int(size) / int(sqft), 2)
        house_ratio = round(int(sqft) / int(size), 2)

    return {
        "PRICE $": price,
        "BEDS": beds,
        "BATHS": baths.replace("+", ""),
        "SQFT": int(sqft.replace(",", "")),
        "LOTSIZE": hy.split_lot_size(lotsize)[0],
        "LOTUNIT": hy.split_lot_size(lotsize)[1],
        "SIZE": size,
        "HtY": hty_ratio or "-",
        "HtY %": house_ratio or "-",
        "ADDRESS": address,
        "LINK": f"https://www.realtor.com{link}",
    }


def parseSoup(URL):
    try:
        soup = getSoup(URL)
        if soup is None:  # If there was an error getting the page
            return None
        homes = []
        house_elements = soup.find_all("li", attrs={"data-testid": "result-card"})
        if not house_elements:  # If there are no house elements, stop scraping
            logging.warning(f"No house elements found at URL: {URL}")
            return None
        for house in house_elements:
            home_data = getHomeData(house)
            if home_data is not None:
                homes.append(home_data)
            else:
                logging.error(f"Error when parsing house data at URL: {URL}")
        return homes
    except requests.exceptions.HTTPError:
        logging.error("Stopping scraping due to 404 error")
        return None


def scrapeIt():
    all_homes = []
    for i in range(1, PAGES + 1):
        URL = BASE_URL + STUB + f"pg-{i}"
        new_homes = parseSoup(URL)
        if new_homes is None:
            logging.error("Stopping due to non 200 response")
            return None
        all_homes += new_homes
        logging.info(f"Scraped: {URL}")
        time.sleep(3)
    return all_homes


def sendIt():
    homes = scrapeIt()
    if not homes:
        logging.error("No home data scraped.")
        return
    df = pd.DataFrame(homes)
    df.to_csv(f"scans/{LOCATION}.csv", index=False)
    logging.info(df)


if __name__ == "__main__":
    sendIt()
