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

    all_p = item.find_all("p")
    for p in all_p:
        p_class = p.get("class",[None])[0]

        if p_class == "name":
            org_name = p.text if p else None
        elif p_class == "url":
            org_url = p.find("a").get("href")
        else:
            # Not the neatest way to do it, but somple enough
            p = str(p).replace("<p>","").replace("</p>","").split("<br/>")

            # contains a po box
            if len(p)>3:
                po_box = p.pop(1)
            else:
                po_box = None
            # else, continue
            address_street = p[0]
            address_city = p[1]
            phone_number = p[2].replace(".","-")

            address_city_breakdown = get_address(address_city, look_for = ["city","state","zip"])

    rec = {
        "org_id" : org_id,
        "org_link" : org_link,
        "org_name" : org_name,
        "org_url" : org_url,
        "address_street":address_street,
        "phone_number":phone_number,
        "po_box":po_box,
        **address_city_breakdown # adds all values
    }
    records.append(rec)

    # Multiple locations (if)
    all_li = item.find_all("li")
    for x in all_li:

        # Not all of them have websites
        org_url = x.find("a")
        org_url = org_url.get("href") if org_url else None

        # parse through text
        text = str(x).replace("<li>","").replace("</li>","").split("<br/>")
        org_name = text[0]
        address_street = text[1]
        address_city = text[2]
        phone_number = text[3].replace(".","-")

        address_city_breakdown = get_address(address_city, look_for = ["city","state","zip"])

        rec = {
            "org_id" : org_id, # use parent org id
            "org_link" : org_link, # use parent org link
            "org_name" : org_name,
            "org_url" : org_url,
            "address_street":address_street,
            "phone_number":phone_number,
            "po_box":po_box,
            **address_city_breakdown # adds all values
        }
        records.append(rec)


# When all that is done, load to a df
df = pd.DataFrame.from_records(records)

# save to a csv
df.to_csv(Path("Data/testing/scraped/first.csv"), index=False)

print("complete!")
