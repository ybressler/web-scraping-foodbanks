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

# Web scraping
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.alert import Alert

# import custom stuff
from fun.web_scraping.navigate import slow_scroll
from fun.web_scraping.soup import get_soup

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

# save the soup (for testing)
os.makedirs(Path("Data/testing/scraped"), exist_ok=True)
soup_path = Path("Data/testing/scraped/first.html")

# Use selenium to get the content (since requests doesn't deliver it...)
url = url_dict["USA (all)"]

# don't make too many requests...
if not os.path.isfile(soup_path):

    # download with selenium
    print(f"downloading {url} with selenium")

    # active the driver
    driver = webdriver.Chrome(chromedriver)
    driver.get(url);

    # Scroll to the bottom of the page (like a human!)
    slow_scroll(driver, px=75)

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

# find all items on the page
all_items = soup.find_all("div",{"class":"results-box"})
for item in all_items:
    org_id = item.get("data-orgid")

    # extract through the link
    a = item.find("a",{"aria-label":True})
    if not a:
        continue
    org_link = a.get("href")

    name = item.find("p",{"class":"name"})
    org_name = name.text if name else name #weird but works!
    org_url = item.find("p",{"class":"url"}).find("a").get("href")

    # still need to get:
    # – address
    # – phone number
    # – multiple locations (if)

    rec = {
        "org_id" : org_id,
        "org_link" : org_link,
        "org_name" : org_name,
        "org_url" : org_url,
    }
    records.append(rec)

# When all that is done, load to a df
df = pd.DataFrame.from_records(records)

# save to a csv
df.to_csv(Path("Data/testing/scraped/first.csv"), index=False)

print("complete!")
