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

# import custom stuff
from fun.web_scraping.navigate import slow_scroll
from fun.web_scraping.soup import get_soup, get_address


# import data tools
import pandas as pd


# Get the largest file
curr_file = Path("Data/testing/scraped/first.csv")

# Create your df
df = pd.read_csv(curr_file)

# How many organizations have websites?
n_websites = sum(df["org_url"].notna())

# How many organizations overall?
n_overall = len(df)

# Pct of orgs with websites
print(n_websites/n_overall)

# lets go through the first website
for url in df["org_url"].dropna():
    print(f"scraping: {url}")
    soup = get_soup(url)
    print(soup)
    break
