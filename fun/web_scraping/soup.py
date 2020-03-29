import re
import requests
from bs4 import BeautifulSoup


def get_soup(url):
    """returns a bs4 object from the urls html text"""
    r = requests.get(url)
    soup = BeautifulSoup(r.text,  'html.parser')
    return soup


def get_address(string, look_for = ["city","state","zip"]):
    """
    input a string
    look for whichever params in `look_for`

    reuturns a dict with values
    """

    lookup_dict = dict(
        zip = re.compile("[0-9]+"),
        city = re.compile("([A-z]+),"),
        state = re.compile("[A-Z]{2}")
    )

    return_dict = {}

    for x in look_for:
        x_lookup = lookup_dict[x]
        x_result = x_lookup.findall(string)
        # save
        if len(x_result)==1:
            return_dict[x] = x_result[0]

    return return_dict
