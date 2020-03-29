import re


def parse_organization(data):
    """
    returns structured data from input
    """

    rec = {
        "type": data.get("@type"),
        "name": data.get("name"),
        "url" : data.get("url")
    }
    social_media = data.get("sameAs",[])

    social_pattern = re.compile("(facebook|linkedin|youtube|instagram)")
    for x in social_media:
        match = re.search(social_pattern, x)
        if not match:
            continue
        # otherwise
        match = match.group()
        rec[match] = x

    return rec
