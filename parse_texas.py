# Core python
import os
import json
import re
import datetime
import time
import sys
import random
import datetime

# Make paths compatible for both mac and PC
from pathlib import Path
from urllib.parse import quote


# Web scraping
import requests
from bs4 import BeautifulSoup

# Load from gmaps
from fun.gmaps.query import query_gmaps

# import data tools
import pandas as pd

# set view options (more relevant for notebooks)
pd.options.display.max_rows = 1000
pd.options.display.max_colwidth = 500
pd.options.display.max_seq_items = 500


# ===============================================================================

# 1. C R E A T E    F U N C T I O N S


def find_start_end_date(string):
    # seems redundent but is necessary
    if type(string)!=str:
        string = str(string)

    if  re.search("indefinite|states closed",string, re.I):

        # if no date is posted, say it closed 3/1/2020
        start_date = datetime.date(2020, 3, 1)

        # if no date is posted, say it will remain closed until 3/1/2021
        end_date = datetime.date(2021, 3, 1)

        return {"start_date":start_date, "end_date":end_date, "indefinitely":True}

    month_re = re.compile("march|april|may|june|july|august|september|october|november|december|january|february", re.I)
    month_dict = {"march":3, "april":4, "may":5,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12,"january":1,"febraury":2}
    months = month_re.findall(string)

    months = [month_dict[x.lower()] for x in months]
    days = [int(x) for x in re.findall("[0-9]+", string)]


    start_date = None
    end_date = None

    if len(months)==1 and len(days)==1 and re.search("only",string,re.I):
        start_date = datetime.date(2020, months[0], days[0])
        end_date = datetime.date(2020, months[0], days[0])

    elif len(months)==1 and len(days)==1:
        # if no date is posted, say it closed 3/1/2020
        start_date = datetime.date(2020, 3, 1)
        end_date = datetime.date(2020, months[0], days[0])

    elif len(months)==1 and len(days)==2:
        start_date = datetime.date(2020, months[0], days[0])
        end_date = datetime.date(2020, months[0], days[1])

    elif len(months)>=2 and len(days)>=2:
        start_date = datetime.date(2020, months[0], days[0])
        end_date = datetime.date(2020, months[-1], days[-1])

    return {"start_date":start_date, "end_date":end_date, "indefinitely":False}

# find_start_end_date("Through March 20")


def find_meals(string):
    # seems redundent but is necessary
    if type(string)!=str:
        string = str(string)

    meal_dict = {"breakfast":"breakfast", "lunch":"lunch", "dinner":"dinner|supper"}
    my_meal_dict = {}

    for key,value in meal_dict.items():
        # if there's a match
        my_meal_dict[key] = True if re.search(value, string, re.I) else False

    return my_meal_dict

# find_meals("Curbside Meal Pickup (Breakfast & Lunch)")


def meal_delivery(string):
    # seems redundent but is necessary
    if type(string)!=str:
        string = str(string)

    delivery_dict = {
        "curbside meal pickup" : re.compile("curbside|cubrside", re.I),
        "walk-in meal pickup" : re.compile("walk|grab|grav|pickup meal|food pickup|^meal", re.I),
        "pending or unspecified" : re.compile("pending|unspecified", re.I),
        "meal delivery" : re.compile("delivery", re.I),
    }
    my_delivery_dict = {}
    for key, value in delivery_dict.items():
        my_delivery_dict[key] = True if value.search(string) else False

    return my_delivery_dict


# meal_delivery("Meal Pickup (Lunch Only)")

def get_details(string):
    # seems redundent but is necessary
    if type(string)!=str:
        string = str(string)

    details_re = re.compile("Details:([A-z \.\-\–]+)")
    details = details_re.search(string)
    details = details.group().strip() if details else None
    return details


def get_meal_times(string):
    # seems redundent but is necessary
    if type(string)!=str:
        string = str(string)

    times_re = re.compile("([0-9]+:[0-9]{2})\s*(AM|PM)", re.I)
    times = times_re.findall(string)
    times = [" ".join(x) for x in times]

    if re.search("Noon\n", string):
        times.append("12:00 PM")

    if len(times)==1:
        return {"start_time_1":times[0], "end_time_1":None}

    # an even number of times
    times_dict = {}
    if len(times)>6:
        return {} # this is a delivery service and is cray

    if len(times)%2==0:
        for n, i in enumerate(range(0, len(times)-1, 2)):
            times_dict.update({
                f"start_time_{n+1}":times[i],
                f"end_time_{n+1}":times[i+1]
            })

    return times_dict

# for testing
# text = 'Start Date: 3/17\nWhen: Breakfast 7:00 AM – 9:00 AM ; 11:00 AM – 1:00 PM\nWhere: Martinez Elementary, Johnston Elementary, Bowie Elementary, Clark Middle School, Craig Middle School, Madison Middle School, Mann Middle School\nDetails: Only children who are in the vehicle at the time of pickup will be allowed to get a meal. All children in the vehicle – whether on free-and-reduced lunch or not – will be allowed to get a meal.\n'


def get_location(string):
    # seems redundent but is necessary
    if type(string)!=str:
        string = str(string)

    location_re = re.compile("Where:([A-z ,\.]+)")
    location = location_re.search(string)
    location = location.group().strip().replace("Where: ","") if location else None
    return location

#     if re.search("Noon\n", string):
#         times.append("12:00 PM")

# get_location(text)

# ===============================================================================

# 2.  L O A D     A N D   C L E A N   T H E   D A T A

texas_file = Path("Data/downloaded/texas.csv")
os.makedirs(Path("Data/cleaned"), exist_ok=True)
save_path = Path("Data/cleaned/texas.csv")

df = pd.read_csv(texas_file)

# rename the column websites if it's named websites
# the column names are going to be important....
df.rename(columns={"Unnamed: 4":"website"}, inplace=True)

# apply the functions
df_closed = df["Dates Closed"].apply(find_start_end_date).apply(pd.Series)
df_closed.columns = ["dates_closed – "+x for x in df_closed.columns]

df_meals = df["School Meal Alternative"].apply(find_meals).apply(pd.Series)
df_meals_pickup = df["School Meal Alternative"].apply(meal_delivery).apply(pd.Series)
df_meals_pickup.columns = ["meal_delivery – "+x for x in df_meals_pickup.columns]


df["details"] = df["When & Where Meals Are Available"].apply(get_details)

# all children allowed food?
f = lambda x: True if re.search("all children", str(x), re.I) else False
df["all_children"] = df["When & Where Meals Are Available"].apply(f)

df_start_end_times = df["When & Where Meals Are Available"].apply(get_meal_times).apply(pd.Series)
df["location"] = df["When & Where Meals Are Available"].apply(get_location)

# save the data!
df = pd.concat([df, df_closed, df_meals, df_meals_pickup, df_start_end_times], axis=1).drop(['Dates Closed','School Meal Alternative',"When & Where Meals Are Available"], axis=1)
df.to_csv(save_path, index=False)

print(f"Completed. Data has been saved to {save_path}")

# ===============================================================================
# 3.  L O A D    F R O M   G M A P S


all_gmaps_data = []

for idx, row in df.iterrows():
    place = row["District Name"].replace("/","")

    # query gmaps
    gmaps_data = query_gmaps(place, verbose=False).get("results")

    for item in gmaps_data:

        # get variables
        address = item["formatted_address"]

        # make flexible
        latitude = item["geometry"].get("location",{"lat":None})["lat"]
        longitude =  item["geometry"].get("location",{"lng":None})["lng"]

        gmaps_name = item["name"]
        gmaps_id = item["id"]

        rec = {
            "place":place,
            "address":address,
            "latitude":latitude,
            "longitude":longitude,
            "gmaps_name":gmaps_name,
            "gmaps_id":gmaps_id
        }

        all_gmaps_data.append(rec)

df_gmaps = pd.DataFrame.from_records(all_gmaps_data)

# there are quiet a few places with multiple locations...
df_gmaps.rename(columns = {"place":"District Name"},inplace=True)


# save multiple
df_loc_mult = df.merge(df_gmaps, how="right")
save_path = Path("Data/cleaned/texas-locations-multi.csv")
df_loc_mult.to_csv(save_path, index=False)


# save single
df_loc_single = df.merge(df_gmaps, how="left")
save_path = Path("Data/cleaned/texas-locations-single.csv")
df_loc_single.to_csv(save_path, index=False)
