import time

def slow_scroll(driver, px = 50, s = 0.05, max_timeout=15):

    """
    scroll slowly through a page

    :params:
        :driver: a selenium driver
        :px: number of pixels to scroll at an interval
        :s: the number of seconds between each interval

    """

    page_bottom = driver.execute_script(f"return window.document.body.scrollHeight")
    px_per_s = px/s

    print(f"Scrolling at {px_per_s}px/s")
    print(f"This will take {page_bottom /(px_per_s)} seconds")


    # Start off at device height
    y = 1000
    start_time = time.time()

    while True:
        driver.execute_script(f"window.scrollTo(0, {y})")
        y += px
        time.sleep(s)

        if y >= (page_bottom-px):
            break

        # if it takes more than max timeout
        time_since = time.time() - start_time
        if time_since>=max_timeout:
            break
