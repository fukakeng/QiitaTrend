import json
import os
import traceback

import requests
from bs4 import BeautifulSoup

QIITA_URL = 'https://qiita.com/'


def scrape_trend():
    response = requests.get(QIITA_URL)
    bs = BeautifulSoup(response.text, 'html.parser')
    return bs.select('.tr-Item')


def post_trend_message(items):
    webhook_urls = [v for k, v in os.environ.items() if 'webhook_url' in k]
    attachments = [_create_attachment(item) for item in items[:5]]
    post_data = {
        'username': 'trend_notifier',
        'text': 'Qiitaのトレンド記事をおしらせします',
        'attachments': attachments
    }

    for webhook_url in webhook_urls:
        requests.post(webhook_url, json.dumps(post_data), headers={'Content-Type': 'application/json'})


def _create_attachment(tr_item):
    article_info_tag = tr_item.find('a', attrs={'class': 'tr-Item_title'})
    author_name = tr_item.find('a', attrs={'class': 'tr-Item_author'}).text

    attachment = {
        'author_name': author_name,
        'author_link': f'https://qiita.com/{author_name}',
        'author_icon': tr_item.find('img').get('src'),
        'title': article_info_tag.text,
        'title_link': article_info_tag.get('href'),
    }
    return attachment


def post_error_message(stack_trace):
    post_data = {
        'username': 'trend_notifier',
        'text': 'トレンド記事の取得に失敗しました',
        'attachments': [{'text': stack_trace, 'color': 'danger'}]
    }

    webhook_urls = [v for k, v in os.environ.items() if 'webhook_url' in k]
    for webhook_url in webhook_urls:
        requests.post(webhook_url, json.dumps(post_data), headers={'Content-Type': 'application/json'})


if __name__ == '__main__':
    try:
        trend_items = scrape_trend()
        post_trend_message(trend_items)
    except AttributeError:
        post_error_message(traceback.format_exc())
