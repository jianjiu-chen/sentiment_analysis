from datetime import datetime
import pytz

from utils import scrape_from_single_outlet, store_for_single_outlet


proj_dir = '/Users/Chen/project/sentiment_analysis/'
today = datetime.now(pytz.timezone('Asia/Hong_Kong')).date()
news_outlets = (('SCMP', 'https://www.scmp.com/topics/hong-kong-stock-exchange'),
                )

print('******************************')
print('Log for', today)
print('******************************')

for outlet_name, outlet_url in news_outlets:
    print('Start for ', outlet_name, '.', sep='')

    try:
        titles = scrape_from_single_outlet(outlet_name, outlet_url)
    except Exception as err:
        print('Error occurred when scraping from ', outlet_name, '!', sep='')
        print(err)
        continue

    try:
        store_for_single_outlet(outlet_name, titles, today, proj_dir)
    except Exception as err:
        print('Error occurred when storing for ', outlet_name, '!', sep='')
        print(err)
        continue

    print('End scraping and storing for ', outlet_name, '. Titles stored were:', sep='')
    print(titles, end='\n\n')
