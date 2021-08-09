import csv
import json
import requests
import bs4
import time
import re
import os
from multiprocessing import Pool

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                  '91.0.4472.77 Safari/537.36'
}

url = 'https://green3.ru'
kresla = 'https://green3.ru/catalog/kreslo/?PAGEN_1=1'   # 1-9
kresla_kachalki = 'https://green3.ru/catalog/kresla_kachalki/?PAGEN_1={}'  # 1-7
divany = 'https://green3.ru/catalog/divany/?PAGEN_1={}'   # 1-2
interernye_kresla = 'https://green3.ru/catalog/interernye_kresla/?PAGEN_1={}'   # 1
tables = 'https://green3.ru/catalog/tables/?PAGEN_1={}'   # 1-4
chairs = 'https://green3.ru/catalog/chairs/?PAGEN_1={}'   # 1-2
pufy = 'https://green3.ru/catalog/pufy/?PAGEN_1={}'   # 1-4
detskie_kresla = 'https://green3.ru/catalog/detskie_kresla/?PAGEN_1={}'   # 1
dict_parsing = {kresla: 9,
                kresla_kachalki: 7,
                divany: 2,
                interernye_kresla: 1,
                tables: 4,
                chairs: 2,
                pufy: 4,
                detskie_kresla: 1}


def get_text(link):
    response = requests.get(link, headers=headers)
    if response.status_code != 200:
        print('не получилось подключиться!')
    else:
        return response.text


def find_links(text, filename):
    data = []
    soup = bs4.BeautifulSoup(text, 'lxml')
    items = soup.find_all('div', 'img-item')
    for item in items:
        link = item.find('a').get('href')
        data = parsing(link, data, filename)
        time.sleep(3)


def get_filename(link):
    if 'kreslo' in link:
        return 'kresla'
    elif 'kresla_kachalki' in link:
        return 'kresla_kachalki'
    elif 'divany' in link:
        return 'divany'
    elif 'interernye_kresla' in link:
        return 'interernye_kresla'
    elif 'tables' in link:
        return 'tables'
    elif 'chairs' in link:
        return 'chairs'
    elif 'pufy' in link:
        return 'pufy'
    elif 'detskie_kresla' in link:
        return 'detskie_kresla'


def parsing(link, data, filename):
    link = url + link
    html = get_text(link)
    if not os.path.exists('data'):
        os.mkdir('data')
    with open('data/page_1.html', 'w', encoding='utf-8') as file:
        file.write(html)
    soup = bs4.BeautifulSoup(html, 'lxml')
    name = soup.find('h1', 'title-card').text
    bio = soup.find('div', 'option-card-item').text
    price = soup.find('div', 'price').text
    price = re.sub(r'\D', '', price)
    about = soup.find('div', 'text-accordeon collapse').find('p').text
    colors_list = []
    colors = soup.find('div', 'list-color-frame')
    try:
        dop_colors = colors.find_all('a')
        for dop_color in dop_colors:
            colors_list.append(dop_color.find('span').text)
    except Exception as err:
        print(err)
    try:
        colors = soup.find('div', 'list-color-frame').find_all('div', 'not_awalible_link')
        for color in colors:
            colors_list.append(color.find('span').text)
    except Exception as err:
        print(err)
    upholsterys_list = []
    try:
        upholsterys = soup.find('div', 'upholstery-options')
        try:
            dop_upholsterys = upholsterys.find_all('a')
            for dop_upholstery in dop_upholsterys:
                upholsterys_list.append(dop_upholstery.find('span').text)
        except Exception as err:
            print(err)
        upholsterys = soup.find('div', 'upholstery-options').find_all('div', 'not_awalible_link')
        for upholstery in upholsterys:
            upholsterys_list.append(upholstery.find('span').text)
    except Exception as exc:
        print(exc)
    item_tabs = soup.find_all('div', 'item-characteristic-tabs')
    characteristic = ''
    for item_tab in item_tabs:
        name_characteristics = item_tab.find('div', 'name-characteristic').text
        value_characteristic = item_tab.find('div', 'value-characteristic').text
        if name_characteristics not in characteristic:
            characteristic = characteristic + name_characteristics + '\n' + value_characteristic + '\n'
    data_dict = {
            'name': name,
            'bio': bio,
            'price': price.strip(),
            'about': about,
            'characteristic': characteristic,
            'colors': colors_list,
            'upholsterys_list': upholsterys_list
        }
    write_csv(data_dict, filename)
    write_json(data_dict, filename)
    data.append(data_dict)
    return data


def write_json(data, filename):
    if not os.path.exists('json'):
        os.mkdir('json')
    with open(f'json\{filename}.json', 'a', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def write_csv(data, filename):
    if not os.path.exists('csv'):
        os.mkdir('csv')
    try:
        with open(f'csv\{filename}.csv', 'a', encoding='cp1251') as file:
            order = ['name', 'bio', 'price', 'about', 'characteristic', 'colors', 'upholsterys_list']
            writer = csv.DictWriter(file, fieldnames=order, delimiter=";", lineterminator="\n")
            writer.writerow(data)
    except Exception as err:
        print(err)


def make_all(link):
    text = get_text(link)
    find_links(text, get_filename(link))


if __name__ == '__main__':
    links_list = []
    for k, v in dict_parsing.items():
        for i in range(1, v+1):
            # find_links(get_text(k.format(i)))
            links_list.append(k.format(i))
            # time.sleep(3)
    print(len(links_list))
    with Pool(30) as p:
        p.map(make_all, links_list)
