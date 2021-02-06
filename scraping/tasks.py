import requests
from bs4 import BeautifulSoup
from datetime import datetime
from celery import shared_task

from .models import News


@shared_task
def hackernews_rss():
    article_list = []
    try:
        print('Starting the scraping tool')
        # execute my request, parse the data using XML
        # parser in BS4
        r = requests.get('https://news.ycombinator.com/rss')
        soup = BeautifulSoup(r.content, features="lxml-xml")
        # select only the "items" I want from the data
        articles = soup.findAll('item')
        # for each "item" I want, parse it into a list
        for a in articles:
            title = a.title.string
            link = a.link.string
            published_wrong = a.pubDate.string
            published = datetime.strptime(published_wrong, '%a, %d %b %Y %H:%M:%S %z')
            # print(published, published_wrong) # checking correct date format

            # create an "article" object with the data
            # from each "item"
            article = {
                'title': title,
                'link': link,
                'published': published,
                'source': 'HackerNews RSS'
            }
            # append my "article_list" with each "article" object
            article_list.append(article)
        return save_function(article_list)
    except Exception as e:
        print('The scraping job failed. see exception:')
        print(e)


@shared_task(serializer='json')
def save_function(article_list):
    print('starting')
    new_count = 0
    for article in article_list:
        try:
            News.objects.create(
                title=article['title'],
                link=article['link'],
                published=article['published'],
                source=article['source']
            )
            new_count += 1
        except Exception as e:
            print('failed at latest_article is none')
            print(e)
            break
    return print('finished')


# from celery import Celery
# import requests
# import json
# from bs4 import BeautifulSoup
# from datetime import datetime
# from celery.schedules import crontab # scheduler
#
# app = Celery('tasks')
#
# # schedule task execution
# app.conf.beat_schedule = {
#     # executes every 1 minute
#     'scraping-task-one-min': {
#         'task': 'tasks.hackernews_rss',
#         'schedule': crontab()
#     }
# }
#
# @shared_task
# def hackernews_rss():
#     article_list = []
#     try:
#         print('Starting the scraping tool')
#         # execute my request, parse the data using XML
#         # parser in BS4
#         r = requests.get('https://news.ycombinator.com/rss')
#         soup = BeautifulSoup(r.content, features="xml")
#         # select only the "items" I want from the data
#         articles = soup.findAll('item')
#         # for each "item" I want, parse it into a list
#         for a in articles:
#             title = a.title.string
#             link = a.link.string
#             published_wrong = a.pubDate.string
#             published = datetime.strptime(published_wrong, '%a, %d %b %Y %H:%M:%S %z')
#             # print(published, published_wrong) # checking correct date format
#
#             # create an "article" object with the data
#             # from each "item"
#             article = {
#                 'title': title,
#                 'link': link,
#                 'published': published,
#                 'created_at': str(datetime.now()),
#                 'source': 'HackerNews RSS'
#             }
#             # append my "article_list" with each "article" object
#             article_list.append(article)
#             print('Finished scraping the articles')
#         return save_function(article_list)
#     except Exception as e:
#         print('The scraping job failed. see exception:')
#         print(e)
#
#
# @shared_task(serializer='json')
# def save_function(article_list):
#     print('strting')
#     new_count = 0
#     for article in article_list:
#         try:
#             News.objects.create(
#                 title=article['title'],
#                 link=article['link'],
#                 published=article['published'],
#                 source=article['source']
#             )
#             new_count += 1
#         except Exception as e:
#             print('failed at latest_article is none')
#             print(e)
#             break
#     return print('finished')

print('Starting Scraping')
hackernews_rss()
print('Finished Scraping')