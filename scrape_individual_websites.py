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

save_dir = Path("Data/scraped")
curr_files = [os.path.join(save_dir, x) x for x in os.listdir(save_dir)]
curr_file = curr_files[0]

# save your files
save_path = Path("Data/scraped/individual")
os.makedirs(save_path, exist_ok=True)

# Create your df
df = pd.read_csv(curr_file)

# How many organizations have websites?
n_websites = sum(df["org_url"].notna())

# How many organizations overall?
n_overall = len(df)

# Pct of orgs with websites
print(n_websites/n_overall)


# ======================================================

# tip: download all the html upfront – since it will take a while
# (It operates slowly because we want to appear like a human)

# activate the driver
driver = webdriver.Chrome(chromedriver)

for url in enumerate(df["org_url"]):

    # file_name = quote(url)
    soup_path = os.path.join(save_path,f"{quote(url)}.html")

    # don't make too many requests...
    if not os.path.isfile(soup_path):

        # download with selenium
        print(f"downloading {url} with selenium")
        driver.get(url);

        # Scroll to the bottom of the page (like a human!)
        slow_scroll(driver, px=75)

        # save
        with open(soup_path,"w") as f:
            f.write(driver.page_source)

        # close the driver
        # driver.quit()

    else:
        print(f"already downloaded {url}...")

    with open(soup_path,"r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")


# deactivate the driver
driver.quit()

# ======================================================



# Now parse
