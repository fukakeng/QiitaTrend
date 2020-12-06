import json
import os
import traceback

import requests
from bs4 import BeautifulSoup

QIITA_URL = 'https://qiita.com/'
AUTHOR_NAME_INDEX = -1


def scrape_trend():
    response = requests.get(QIITA_URL)
    bs = BeautifulSoup(response.text, 'html.parser')
    return bs.find_all('article')


def post_trend_message(items):
    if not items:
        raise ValueError('Item list is empty.')

    attachments = [_create_attachment(item) for item in items[:5]]
    post_data = {
        'username': 'trend_notifier',
        'text': 'Qiitaのトレンド記事をおしらせします',
        'attachments': attachments
    }
    _post_message(post_data)


def _create_attachment(tr_item):
    title_info_tag = tr_item.find('h2')
    author_name = tr_item.select('a:nth-of-type(2)')[0].contents[AUTHOR_NAME_INDEX]

    attachment = {
        'author_name': author_name,
        'author_link': f'https://qiita.com/{author_name}',
        'author_icon': tr_item.find('img').get('src'),
        'title': title_info_tag.text,
        'title_link': title_info_tag.find('a').get('href'),
    }
    return attachment


def post_error_message(stack_trace):
    post_data = {
        'username': 'trend_notifier',
        'text': 'トレンド記事の取得に失敗しました',
        'attachments': [{'text': stack_trace, 'color': 'danger'}]
    }
    print(post_data)
    _post_message(post_data)


def _post_message(post_data):
    webhook_urls = [v for k, v in os.environ.items() if 'webhook_url' in k]
    for webhook_url in webhook_urls:
        requests.post(webhook_url, json.dumps(post_data), headers={'Content-Type': 'application/json'})


if __name__ == '__main__':
    try:
        trend_items = scrape_trend()
        post_trend_message(trend_items)
    except Exception:
        post_error_message(traceback.format_exc())
