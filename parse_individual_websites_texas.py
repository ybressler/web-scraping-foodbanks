# Core python
import os
import json
import re
import datetime
import time
import sys
import random

# Make paths compatible for both mac and PC
from pathlib import Path
from urllib.parse import quote


# Web scraping
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.alert import Alert

# import custom stuff
from fun.web_scraping.navigate import slow_scroll
from fun.web_scraping.soup import get_soup, get_address
from fun.web_scraping.validate import validate_url, url_to_file_name, foodbank_type
from fun.web_scraping.parsing import parse_organization

# import data tools
import pandas as pd

# ======================================================


# Validate the chromedriver
def chromedriver_path():
    if ((len(sys.argv) > 1) and (len(sys.argv[1]) > 0)):
        return sys.argv[1]
    return str(Path('ChromeDriver/chromedriver'))

# Define the location
chromedriver = chromedriver_path()
os.environ["webdriver.chrome.driver"] = chromedriver


# ======================================================


texas_file = Path("Data/downloaded/texas-cleaned.csv")
save_path = Path("Data/scraped/individual")

df = pd.read_csv(texas_file)

all_records = []



# ============================================================
# This parses individual websites
# The code is not perfect though....

for i, url in enumerate(df["website"].dropna()[2:]):
    print(f"parsing {url}")
    # file_name = quote(url)
    soup_path = os.path.join(save_path,f"{url_to_file_name(url)}.html")

    # don't make too many requests...
    if not os.path.isfile(soup_path):

        # activate the driver
        driver = webdriver.Chrome(chromedriver)

        # download with selenium
        print(f"downloading {url} with selenium")
        driver.get(url);
        time.sleep(1)

        # Scroll to the bottom of the page (like a human!)
        slow_scroll(driver, px=50, max_timeout=0.5)

        # save
        with open(soup_path,"w") as f:
            f.write(driver.page_source)

        # close the driver
        driver.quit()

    else:
        print(f"already downloaded {url}...")

    with open(soup_path,"r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")


    soup = get_soup(url)
    if not soup:
        continue

    record = {"url":url}
    # get structured data
    all_items = soup.find_all("script",type="application/ld+json")
    # print(all_items)


    texas_address = re.compile("[0-9]+[A-z\s,\.\S]+TX\s*\S*[0-9]+")
    address = soup.find_all(text=texas_address)
    address = address[0] if len(address)>0 else None
    record['address'] = address

    phone_number = re.compile("[(]*[0-9]{3}[-\.) ]{1,2}[0-9]{3}[-\.]{1}[0-9]{4}")
    phone_number = soup.find_all(text=phone_number)
    phone_number = phone_number[-1] if len(phone_number)>0 else None

    record['phone'] = phone_number
    all_records.append(record)

    # # Now we parse this!
    #
    # all_items_by_type = []
    #
    # for item in all_items:
    #
    #     item = json.loads(item.text, strict=True)
    #
    #     if len(item)>100:
    #         continue
    #
    #     if type(item)==list:
    #         for x in item:
    #             all_items_by_type.append(x)
    #         continue
    #
    #
    #     # Otherwise
    #     # i_type = item.get("@type")
    #     #
    #     if item.get("@graph"):
    #         for x in item.get("@graph"):
    #             i_type = x.get("@type")
    #             all_items_by_type.append(x)
    #
    #     sys.exit()

    # Use this later...
    # if i_type == "organization":
    #     data = parse_organization(sub_item)


print(all_records)
# sys.exit()
# ======================================================



print("complete")
