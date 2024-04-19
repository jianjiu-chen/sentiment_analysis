from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import sqlite3


def scrape_SCMP(outlet_url, news_title_h_level='h2',
                max_scroll_n=10, max_n_of_title_to_scrape=30, scroll_y=2000,
                sleep_time=5):
    """
    :param outlet_url: pass a str when using this function
    :param news_title_h_level: default to 'h2'
    :param max_scroll_n: you can scroll down indefinitely for SCMP, need a limit; default to 10
    :param max_n_of_title_to_scrape:
    :param scroll_y: default to 2000; otherwise, too small a movement at a time
    :param sleep_time: default to 5; allow some time for the scroll action to happen
    :return: a list of strings, each being a news title
    """

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
        h_s = BeautifulSoup(driver.page_source, 'html.parser').find_all(news_title_h_level)
        titles = []
        for i, h_i in enumerate(h_s):
            try:
                titles.append(h_i.text)
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
    titles = [i.replace('\n', '').strip() for i in titles]
    titles = [i for i in titles if 'Opinion |' not in i and 'Editorial | ' not in i]  # opinion, etc, not useful

    return titles[0:max_n_of_title_to_scrape]


def scrape_TheStandard(outlet_url, news_title_h_level='h1',
                       sleep_time=10):
    """
    :param outlet_url: pass a str when using this function
    :param news_title_h_level: default to 'h1'
    :param sleep_time: default to 10; allow some time for this to work
    :return: a list of strings, each being a news title
    """

    driver = webdriver.Chrome()
    driver.get(outlet_url)
    time.sleep(sleep_time)

    # grab titles
    h_s = BeautifulSoup(driver.page_source, 'html.parser').find_all(news_title_h_level)
    driver.quit()
    titles = []
    for i, h_i in enumerate(h_s):
        try:
            titles.append(h_i.text)
        except AttributeError as err:
            print(err)

    titles = [i for i in titles if i != 'The Standard']
    # in hmtl file, the newspaper name (The Standard) is on the same level of heading with other news titles
    # delete 'The Standard' as it's non-informative

    return titles


def scrape_RTHK(outlet_url, news_title_h_level='h4',
                max_n_of_title_to_scrape=30,
                sleep_time=10):
    """
    :param outlet_url: pass a str when using this function
    :param news_title_h_level: default to 'h4'
    :param max_n_of_title_to_scrape: RTHK contains too many titles on one page, set a limit; default to 30
    :param sleep_time: default to 10; allow some time for this to work
    :return: a list of strings, each being a news title
    """

    driver = webdriver.Chrome()
    driver.get(outlet_url)
    time.sleep(sleep_time)

    # grab titles
    h_s = BeautifulSoup(driver.page_source, 'html.parser').find_all(news_title_h_level)
    driver.quit()
    titles = []
    for i, h_i in enumerate(h_s):
        try:
            titles.append(h_i.text)
        except AttributeError as err:
            print(err)

    return titles


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
