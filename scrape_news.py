import datetime
import pytz

import utils


proj_dir = '/Users/Chen/project/sentiment_analysis/'
today = datetime.datetime.now(pytz.timezone('Asia/Hong_Kong')).date()
news_outlets = (('SCMP', 'https://www.scmp.com/topics/hong-kong-stock-exchange'),
                ('TheStandard', 'https://www.thestandard.com.hk/section-news-list/section/finance/'),
                ('RTHK', 'https://news.rthk.hk/rthk/en/latest-news/finance.htm'),
                )

print('******************************')
print('Log for', today)
print('******************************')

for outlet_name, outlet_url in news_outlets:
    print('Start for ', outlet_name, '.', sep='')

    try:
        scrape = getattr(utils, 'scrape_' + outlet_name)
        titles = scrape(outlet_url)
    except Exception as err:
        print('Error occurred when scraping from ', outlet_name, '!', sep='')
        print(err)
        continue

    try:
        utils.store_for_single_outlet(outlet_name, titles, today, proj_dir)
    except Exception as err:
        print('Error occurred when storing for ', outlet_name, '!', sep='')
        print(err)
        continue

    print('End scraping and storing for ', outlet_name, '. Titles stored were:', sep='')
    print(*titles, sep='\n', end='\n\n')
