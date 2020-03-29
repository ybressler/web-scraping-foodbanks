from urllib.parse import urlparse, urlunparse, quote


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
