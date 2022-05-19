import requests
from bs4 import BeautifulSoup
import json
import csv
import time

start_time = time.time()

url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
    'accept': '*/*'
}

def get_html(url):
    req = requests.get(url, headers=headers)
    return req.text

#Распарсиваю основную страницу. Получаю на выходе словарь с названиями категорий и ссылками
def get_page_href(html):
    soup = BeautifulSoup(html, 'lxml')
    all_products_hrefs = soup.find_all(class_='mzr-tc-group-item-href')[:1]
    all_href_categories_list = []
    all_categories_dict = {}
    for item in all_products_hrefs:
        item_text = item.text
        item_href = 'https://health-diet.ru' + item.get('href')
        all_href_categories_list.append(item_href)
        all_categories_dict[item_text] = item_href

    return all_categories_dict

# принимаю ссылки на категории, распарсиваю их. На выходе получаю словарь категорий + продукты-ссылки
def get_product_href(all_categories_dict):

    all_cat_and_href_products_dict = {}
    for cat_name, cat_href in all_categories_dict.items():
        rep = [",", " ", "-", "'"]
        for item in rep:
            if item in cat_name:
                cat_name = cat_name.replace(item, "_")

        soup = BeautifulSoup(get_html(cat_href), 'lxml')
        alert_block = soup.find(class_='uk-alert-danger')
        if alert_block is not None:
            continue
        product_dict = {}
        table_head = soup.find(class_='mzr-tc-group-table').find_all('tr')[1:]
        for item in table_head:
            table_i = item.find_all('td')
            product_name = table_i[0].text

            rep_1 = [",", " ", "-", "'", "/", "\n"]
            for i in rep_1:
                if i in product_name:
                    product_name = product_name.replace(i, "_").strip()
            product_href = 'https://health-diet.ru' + table_i[0].find('a').get('href')
            product_dict[product_name] = product_href
            # all_product_href_list.append(product_href)
        all_cat_and_href_products_dict[cat_name] = product_dict
    return all_cat_and_href_products_dict

#получаю список ссылок на продукты. На выходе данные по содержанию в каждом продукте(категории + продукты + содержание пит веществ)
def get_product_data(all_cat_and_href_products_dict):

    data_products_all = []
    count = 0
    # all_cat_and_href_products_dict = {'Баранина_и_дичь': {'Антилопа_': 'https://health-diet.ru/base_of_food/sostav/18812.php', 'Антилопа__запеченная': 'https://health-diet.ru/base_of_food/sostav/18813.php'}, 'Бобовые': {'LOMA_LINDA_Большие_сосиски__низкожирные__консервированные__неприготовленные': 'https://health-diet.ru/base_of_food/sostav/18605.php', 'MORI_NU__Тофу__мягкий__шелковый': 'https://health-diet.ru/base_of_food/sostav/18485.php'}}

    all_product_dict = {}
    for cat_name, href_dict in all_cat_and_href_products_dict.items():
        product_dict = {}
        for product, href in href_dict.items():
            soup = BeautifulSoup(get_html(href), 'lxml')
            data_head = soup.find('div', class_='mzr-block-content uk-margin-bottom')
            # name = data_head.find('h4').find('u').get_text()
            table = data_head.find('table', class_='mzr-table mzr-table-border mzr-tc-chemical-table').find_all('tr')[1:]
            product_info = {}
            for item_i in table:
                item = item_i.find_all('td')
                a = item[0].text
                b = item[1].text
                product_info[a] = b
            product_dict[product] = product_info
            count += 1
            print(f'Обработал продукт {count}')
            time.sleep(3)
        all_product_dict[cat_name] = product_dict
    return all_product_dict




def main():
    # all_dict = get_product_data(get_product_href(get_page_href(get_html(url))))
    # with open('data.json', 'w') as file:
    #     json.dump(all_dict, file, indent=4, ensure_ascii=False)
    print(get_product_data(get_product_href(get_page_href(get_html(url)))))
    finish_time = time.time() - start_time
    print(finish_time)


if __name__ == '__main__':
    main()