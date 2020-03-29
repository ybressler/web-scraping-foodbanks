import re
import json
from pathlib import Path
import pandas as pd
import datetime

# algolia stuff
from algoliasearch.search_client import SearchClient

# expected format is below:
data_path = Path("Data/cleaned/texas-locations-multi.csv")
df = pd.read_csv(data_path)

# get algolia api key
with open(Path("secret/algolia_api.json"),"r") as f:
    data = json.load(f)
    ALGOLIA_API_KEY = data["ALGOLIA_API_KEY"]
    APP_ID = data["APP_ID"]
    del data

all_records = []

for idx, row in df.iterrows():

    # lets set the information here
    siteName = row["gmaps_name"]
    siteStatus = any(row[["breakfast","lunch","dinner"]].notnull())
    siteStatus = 'Open' if siteStatus else 'Closed'

    # this will require parsing
    siteAddress_pre = row["address"].split(',')
    if len(siteAddress_pre)==4:
        if len(siteAddress_pre[2].split())==2:
            siteAddress_json = {
                "streetAddress" : siteAddress_pre[0].strip(),
                "city" : siteAddress_pre[1].strip(),
                "state" : siteAddress_pre[2].strip().split()[0],
                "zip" : siteAddress_pre[2].strip().split()[1],
            }
        else:
            siteAddress_json = {
                "streetAddress" : siteAddress_pre[0].strip(),
                "city" : siteAddress_pre[1].strip(),
                "state" : siteAddress_pre[2].strip(),
                "zip" : None,
            }

    elif len(siteAddress_pre)==3:
        siteAddress_json = {
            "streetAddress" : siteAddress_pre[0].strip(),
            "city" : None,
            "state" : siteAddress_pre[1].strip(),
            "zip" : None,
        }
    streetAddress_str = row["address"]
    siteState = siteAddress_json["state"]
    siteZip = siteAddress_json["zip"]
    contactPhone = None # can get this using gmaps api again

    # not sure how to deliver this data...
    startDate = None # not sure how to deliver this data...
    endDate = None # not sure how to deliver this data...

    # again, not sure how to present this data..
    # will say it's all schooldays for now
    daysofOperation = ["M","T","W","Th", "F"]

    # get the start and end times
    start_time_1, end_time_1 = row[["start_time_1","end_time_1"]]
    start_time_2, end_time_2 = row[["start_time_2","end_time_2"]]
    start_time_3, end_time_3 = row[["start_time_3","end_time_3"]]

    breakfastTime = f"{start_time_1}–{end_time_1}" if type(start_time_1)==str else None
    lunchTime = f"{[start_time_2]}–{end_time_2}"  if type(start_time_2)==str else None
    snackTimeAM = None
    snackTimePM = None
    dinnerSupperTime = f"{start_time_3}–{end_time_3}" if type(start_time_3)==str else None
    openTimes = " ,".join([x for x in [breakfastTime, lunchTime, dinnerSupperTime] if x])

    # get locations
    _geoloc = {"lat": row["latitude"], "lng":row["longitude"]}
    _createdOn = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")


    # load them all up
    record = {
        "siteName":siteName,
        "siteStatus":siteStatus,
        "siteAddress":streetAddress_str,
        "siteAddress_json":siteAddress_json,
        "siteState":siteState,
        "siteZip":siteZip,
        "contactPhone":contactPhone,
        "startDate":startDate,
        "endDate":endDate,
        "daysofOperation":daysofOperation,
        "breakfastTime":breakfastTime,
        "lunchTime":lunchTime,
        "snackTimeAM":snackTimeAM,
        "snackTimePM":snackTimePM,
        "dinnerSupperTime":dinnerSupperTime,
        "openTimes":openTimes,
        "_geoloc":_geoloc,
        "_createdOn":_createdOn,
        "_updatedOn":None, # not sure what to put here
    }

    all_records.append(record)


# ========================================
# Now, need to commit the data!

# Upload this way
client = SearchClient.create(APP_ID, ALGOLIA_API_KEY)

# push to production
index = client.init_index('prod_schools')
index.save_objects(all_records, {'autoGenerateObjectIDIfNotExist': True})
