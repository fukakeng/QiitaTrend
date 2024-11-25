import json
import os
import traceback

import feedparser
import requests

QIITA_URL = 'https://qiita.com'


def main():
    try:
        # trend_items = scrape_trend()
        trend_items = fetch_trend()
        post_trend_message(trend_items)
    except Exception:
        post_error_message(traceback.format_exc())


def fetch_trend():
    feed = feedparser.parse(f'{QIITA_URL}/popular-items/feed')
    return feed.entries


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
    response = requests.get(f'{QIITA_URL}/api/v2/users/{tr_item["author"]}')
    user_info = response.json()

    attachment = {
        'author_name': tr_item['author'],
        'author_link': f'{QIITA_URL}/{tr_item["author"]}',
        'author_icon': user_info['profile_image_url'],
        'title': tr_item['title'],
        'title_link': tr_item['link'],
    }
    return attachment


def post_error_message(stack_trace):
    post_data = {
        'username': 'trend_notifier',
        'text': 'トレンド記事の取得に失敗しました',
        'attachments': [{'text': stack_trace, 'color': 'danger'}]
    }
    _post_message(post_data)


def _post_message(post_data):
    webhook_urls = [v for k, v in os.environ.items() if 'webhook_url' in k]

    for webhook_url in webhook_urls:
        requests.post(webhook_url, json.dumps(post_data), headers={'Content-Type': 'application/json'})


if __name__ == '__main__':
    main()
