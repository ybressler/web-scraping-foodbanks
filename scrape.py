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

# find all items on the page
all_items = soup.find_all("div",{"class":"results-box"})
for item in all_items:
    print(item)


# # Structured data
# all_items = soup.find_all("script",type="application/ld+json")
# for item in all_items:
#     print(item)
#
#
# # Get all links
# all_items = soup.find_all("a")
