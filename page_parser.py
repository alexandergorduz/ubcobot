import config
import requests
from bs4 import BeautifulSoup as BS

def parse_input(message):
        return message.split(' - ')

def get_html(url):
    r = requests.get(url, headers=config.HEADERS)
    return r

def get_page_content(html):
    soup = BS(html, 'html.parser')
    card_image = config.HOST + soup.find('img', id='cardimage').get('src').strip('/')
    card_name = soup.find('div', class_='cardparams').find('h1').get_text(strip=True)
    card_price = soup.find('p', class_='price4').get_text().replace('Цена ', '').replace(' грн', '')
    return {
        'card_image': card_image,
        'card_name': card_name,
        'card_price': card_price
    }