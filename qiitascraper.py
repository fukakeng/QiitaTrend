import requests
import json
from bs4 import BeautifulSoup

QIITA_URL = 'https://qiita.com/'


def scrape_trend():
    response = requests.get(QIITA_URL)
    bs = BeautifulSoup(response.text, 'html.parser')
    trend_text = bs.find('div', attrs={'data-hyperapp-app': 'Trend'}).get('data-hyperapp-props')
    return [item['node'] for item in json.loads(trend_text)['trend']['edges']]


def post_slack_message(items):
    webhook_url = ''
    attachments = [_create_attachment(item) for item in items[:5]]
    post_data = {
        'username': 'trend_notifier',
        'text': 'Qiitaのトレンド記事をおしらせします',
        'attachments': attachments
    }

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


if __name__ == '__main__':
    trend_items = scrape_trend()
    post_slack_message(trend_items)
