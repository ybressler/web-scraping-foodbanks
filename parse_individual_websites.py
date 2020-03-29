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


save_dir = Path("Data/scraped/individual")
curr_files = [os.path.join(save_dir, x) for x in os.listdir(save_dir) if x.endswith("html")]


for file in curr_files:
    print(f"parsing {file}")
    with open(file,"r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Get the title
    title = soup.head.find("meta", {"property":"og:title"})
    title = title["content"] if title else None
    if not title:
        title = soup.title
        title = title.text if title else None


    description = soup.head.find("meta", {"property":"og:description"})
    description =  description["content"] if description else None
    h1s = [x.text for x in soup.find_all("h1")]

    # test if it's a foodbank
    if description:
        z = foodbank_type(description)
        break
    # print(title, description, h1s)

    # Get the description

    # is this a foodbank or a distrubution center?
    # code here


    # these sites have wonky data
    # if file in [
    #     "Data/scraped/individual/www.food-finders.org.html",
    #     "Data/scraped/individual/www.firstfoodbank.org.html",
    #     "Data/scraped/individual/www.trcac.org.html"
    #     ]:
    #     continue
    #
    # # get structured data
    # all_items = soup.find_all("script",type="application/ld+json")
    #
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


print(all_items_by_type)
sys.exit()
# ======================================================



print("complete")
