from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import sqlite3


def scrape_from_single_outlet(outlet_name, outlet_url):
    """
    :param outlet_name: str, could be 'SCMP', etc
    :param outlet_url:
    :return: a list of str, each element being a title
    """
    max_scroll_n = 10
    max_n_of_title_to_scrape = 50
    max_n_of_title_to_store = 30  # these 2 should differ b/c some titles are useless
    scroll_y = 2000  # otherwise, too small
    sleep_time = 5

    driver = webdriver.Chrome()
    driver.get(outlet_url)

    # scrape
    scroll_n = 0
    n_of_title_previous_iteration = 0
    while True:
        scroll_n += 1
        ActionChains(driver).scroll_by_amount(delta_x=0, delta_y=scroll_y).perform()
        time.sleep(sleep_time)
        print('Scrolled', scroll_n, 'time(s).')

        # grab titles
        h2s = BeautifulSoup(driver.page_source, 'html.parser').find_all('h2')
        titles = []
        for i, h2_i in enumerate(h2s):
            try:
                titles.append(h2_i.text)
            except AttributeError as err:
                print(err)

        # check whether to continue
        if ((scroll_n > max_scroll_n and (len(titles) - n_of_title_previous_iteration) == 0) or
                # If scroll too many times, yet don't get additional titles, it means I got to the bottom.
                len(titles) >= max_n_of_title_to_scrape):
            driver.quit()
            break
        else:
            n_of_title_previous_iteration = len(titles)

    # somehow clean title
    if outlet_name == 'SCMP':
        titles = [i.replace('\n', '').strip() for i in titles]
        titles = [i for i in titles if 'Opinion |' not in i and 'Editorial | ' not in i]  # opinion, etc, not useful

    return titles[0:max_n_of_title_to_store]


def store_for_single_outlet(outlet_name, titles, today, db_dir):
    """
    :param outlet_name: str, could be 'SCMP', etc
    :param titles: a list of str, each element being a title
    :param today: type of datetime.date
    :param db_dir: directory, where the database locates
    :return:
    """
    data_to_insert = [(str(today), i) for i in titles]
    with sqlite3.connect(db_dir + "news.db") as con:
        cur = con.cursor()
        # Need to create a new table on the first day
        existing_outlets = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        existing_outlets = [i[0] for i in existing_outlets]
        if outlet_name not in existing_outlets:
            cur.execute("CREATE TABLE {}(date, headline)".format(outlet_name))

        # Insert values
        cur.executemany("INSERT INTO {} VALUES(?, ?)".format(outlet_name), data_to_insert)
