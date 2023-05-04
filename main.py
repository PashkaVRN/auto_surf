import logging
import time

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    encoding='utf-8-sig')

# настройки логгирования в терминале
logging.StreamHandler().setLevel(logging.INFO)
logging.StreamHandler().setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s'))
logging.getLogger('').addHandler(logging.StreamHandler())


def scrape_website(base_url):
    """Функция парсинга сайта и перехода по ссылкам"""

    # список уже посещенных URL
    visited_urls = []
    # создаем словарь для хранения статистики запросов
    requests_status = {}
    # получаем часть ссылки для проверки на внешние ссылки
    netloc_base_url = urlparse(base_url).netloc

    while True:
        # запрашиваем главную страницу сайта
        response = requests.get(base_url)
        logging.info(f'Статус код {response.status_code}')
        requests_status[response.status_code] = requests_status.get(
            response.status_code, 0) + 1
        soup = BeautifulSoup(response.content, 'html.parser')
        # находим все ссылки на этой странице
        for link in soup.find_all('a'):
            url = link.get('href')
            # проверяем, что мы не посещали еще этот URL
            if url and url not in visited_urls:
                # исключаем ссылки на почту и файлы
                if url.startswith('mailto:') or url.endswith(('.pdf', '.doc', '.docx')):
                    continue
                # если ссылка ведет на другой сайт, то переходим по ней
                if 'http' in url and urlparse(url).netloc != netloc_base_url:
                    visited_urls.append(url)
                    response = requests.get(url)
                    if response.status_code != 200:
                        logging.warning(f"По ссылке {url} получен статус код {response.status_code}")
                        continue
                    logging.info(f"Переход на страницу: {url}, статус страницы: {response.status_code}")
                    requests_status[response.status_code] = requests_status.get(response.status_code, 0) + 1
                    for status_code, count in requests_status.items():
                        logging.info(f"Статус код {status_code}: {count} запросов")
                    # ждем 5 секунд перед следующим запросом страницы
                    time.sleep(5)
                # если ссылка ведет на текущий сайт, то запрашиваем страницу
                elif base_url in url:
                    visited_urls.append(url)
                    response = requests.get(url)
                    if response.status_code != 200:
                        logging.warning(f"По ссылке {url} получен статус код {response.status_code}")
                        continue
                    logging.info(f"Посещена страница: {url}, статус страницы: {response.status_code}")
                    requests_status[response.status_code] = requests_status.get(response.status_code, 0) + 1
                    for status_code, count in requests_status.items():
                        logging.info(f"Статус код {status_code}: {count} запросов")
                    # ждем 5 секунд перед следующим запросом страницы
                    time.sleep(5)
        # ждем 10 минут перед повторным запросом главной страницы
        time.sleep(10 * 60)


if __name__ == '__main__':
    scrape_website('https://pythonist.ru/')
