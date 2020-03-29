from urllib.parse import urlparse, urlunparse, quote
import re

def validate_url(url):

    # only allow it for strings
    if type(url)!=str:
        return url
    o = urlparse(url)

    if not o.scheme:
        o = o._replace(scheme='http')
        url = urlunparse(o)

    return url


def url_to_file_name(url):

    # only allow it for strings
    if type(url)!=str:
        return url

    o = urlparse(url)

    return quote(o.netloc)


def foodbank_type(text):
    """
    will go through content and check if it's a foodbank or not

    valid types are:
        – food bank
        – food pantry
        – soup kitchen
        – wic site ?
        – food organization
    """
    pattern = re.compile("(food bank|foodbank)", re.IGNORECASE)

    z = pattern.findall(text)
    print(z)

    return "foodbank"
