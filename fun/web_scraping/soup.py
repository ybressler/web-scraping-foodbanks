import re
import requests
from bs4 import BeautifulSoup


def get_soup(url):
    """returns a bs4 object from the urls html text"""
    r = requests.get(url)
    soup = BeautifulSoup(r.text,  'html.parser')
    return soup
