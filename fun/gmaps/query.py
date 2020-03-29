import json
import os
from pathlib import Path
import requests

with open(Path("secret/gmaps_api.json"),"r") as f:
    GMAPS_API_KEY = json.load(f)["GMAPS_API_KEY"]


def query_gmaps(place, place_id=None, state="Texas", q_type="textsearch", verbose=True):
    """
    input a place (loose string) and a state (exact string) to return a json response
    query is validated for previous api call – no duplicate api calls are made
    –> reads locally if already queries

    input params:
        – place: a string
        – place_id: gid for the place (used in details query type)
        – state: string of the state
        – q_type: query type. Either "textsearch" or "details"
    """

    if q_type == "details":
        print("code not set up to handle detail queries yet...")
        return {}


    # make the dir off the bat
    save_path = Path(f"Data/gmaps_api/{state}/{q_type}")
    os.makedirs(save_path, exist_ok=True)

    # paths to be used
    address = f"{place}, {state}"
    file_name = os.path.join(save_path, f"{place}.json")

    # check if the file already exists
    if os.path.isfile(file_name):
        if verbose == True:
            print(f"loading locally for {address}")
        # load the data
        with open(Path(file_name), "r") as f:
            data = json.load(f)

    # make the query
    else:
        if verbose == True:
            print(f"querying gmaps api for {address}")

        query = f"https://maps.googleapis.com/maps/api/place/{q_type}/json?query={address}&key={GMAPS_API_KEY}"

        # load the response
        r = requests.get(query)
        data = r.json()

        # save
        with open(Path(file_name), "w") as f:
            json.dump(data, f)

    return data
