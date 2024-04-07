from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

import time
from datetime import datetime
import pytz
import sqlite3

proj_dir = '/Users/Chen/project/sentiment_analysis/'
today = datetime.now(pytz.timezone('Asia/Hong_Kong')).date()

print('******************************')
print('Log for', today)
print('******************************')

driver = webdriver.Chrome()

driver.get("https://www.scmp.com/news/hong-kong/hong-kong-economy")

# Scroll down to trigger the loading of additional content
# Adjust the number of scrolls and the sleep time as needed
for _ in range(10):
    ActionChains(driver).scroll_by_amount(delta_x=0,delta_y=2000).perform()
    time.sleep(5)

html_content = driver.page_source

driver.quit()

soup = BeautifulSoup(html_content, 'html.parser')

titles = []
h2s = soup.find_all('h2')
for i, h2_i in enumerate(h2s):
    try:
        titles.append(h2_i.text)
    except AttributeError as err:
        print(err)

headlines_today = [(str(today),i.replace('\n','').strip()) for i in titles]

con = sqlite3.connect(proj_dir + "news.db")
cur = con.cursor()

# need to create a new table on the first day
news_outlet_names = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
news_outlet_names = [i[0] for i in news_outlet_names]
if 'SCMP' not in news_outlet_names:
    cur.execute("CREATE TABLE SCMP(date, headline)")

cur.executemany("INSERT INTO SCMP VALUES(?, ?)", headlines_today)
con.commit()
con.close()

print('SCMP: ')
print(titles, end='\n\n')