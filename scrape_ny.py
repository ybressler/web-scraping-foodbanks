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
from fun.web_scraping.validate import validate_url, url_to_file_name

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



with open(Path("Data/foodbank_indexes.json"),"r") as f:
    url_dict = json.load(f)

# begin with just one url

os.makedirs(Path("Data/scraped/indexes"), exist_ok=True)
url = url_dict["New York City"]
soup_path = Path(f"Data/scraped/indexes/{url_to_file_name(url)}.html")


# don't make too many requests...
if not os.path.isfile(soup_path):

    # download with selenium
    print(f"downloading {url} with selenium")

    # active the driver
    driver = webdriver.Chrome(chromedriver)
    driver.get(url);

    # Scroll to the bottom of the page (like a human!)
    slow_scroll(driver, px=30, max_timeout=20)

    # save
    with open(soup_path,"w") as f:
        f.write(driver.page_source)

    # close the driver
    driver.quit()

else:
    print(f"already downloaded {url}...")

with open(soup_path,"r") as f:
    soup = BeautifulSoup(f.read(), "html.parser")



# ==============================================================================
# Begin parsing

records = []

# get index
my_index = {}
all_items = soup.find_all("div",{"index":True, "subindex":False})
for x in all_items:
    n = x.get("index")
    my_index[n] = x.text

all_items = soup.find_all("div",{"index":True, "subindex":True})
for x in all_items:
    n = x.get("index")
    category = my_index[n]

    rec = {"org_type":category, "org_name":x.text}
    records.append(rec)


# When all that is done, load to a df
df = pd.DataFrame.from_records(records)

# save to a csv
df.to_csv(Path(f"Data/scraped/indexes/{url_to_file_name(url)}.csv"), index=False)

print("complete!")
