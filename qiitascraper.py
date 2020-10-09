import json
import os
import traceback

import requests
from bs4 import BeautifulSoup

QIITA_URL = 'https://qiita.com/'


def scrape_trend():
    response = requests.get(QIITA_URL)
    bs = BeautifulSoup(response.text, 'html.parser')
    trend_text = bs.find('div', attrs={'data-hyperapp-app': 'Trend'}).get('data-hyperapp-props')
    return [item['node'] for item in json.loads(trend_text)['trend']['edges']]


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


def _create_attachment(item):
    attachment = {
        'author_name': item['author']['urlName'],
        'author_link': QIITA_URL + item['author']['urlName'],
        'author_icon': item['author']['profileImageUrl'],
        'title': item['title'],
        'title_link': QIITA_URL + item['author']['urlName'] + '/items/' + item['uuid'],
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
