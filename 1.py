from requests import Session
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import time


start_time = time.time()

url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
    'accept': '*/*'
}

async def get_page(session, url):
    async with session.get(url) as r:
        return await r.text()

async def get_all(session, url, cat=None):
    dict_res = {}
    tasks = []

    task = asyncio.create_task(get_page(session, url))
    tasks.append(task)
    result = await asyncio.gather(*tasks)
    if cat:
        dict_res[cat] = result
        return dict_res
    return result

def parse_1(result):
    for html in result:
        soup = BeautifulSoup(html, 'lxml')
        all_products_hrefs = soup.find_all(class_='mzr-tc-group-item-href') #[:1]
        all_href_categories_list = []
        all_categories_dict = {}
        for item in all_products_hrefs:
            item_text = item.text
            item_href = 'https://health-diet.ru' + item.get('href')
            all_href_categories_list.append(item_href)
            all_categories_dict[item_text] = item_href

        return all_categories_dict

def parse_2(dict_res):
    all_cat_and_href_products_dict = {}
    for cat, html in dict_res.items():
        soup = BeautifulSoup(str(html), 'lxml')
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
                    product_name_1 = product_name.replace(i, "_").strip()
            a = '\\n'
            product_name = product_name_1[:a]
            product_name = product_name.rstrip()

            product_href = 'https://health-diet.ru' + table_i[0].find('a').get('href')
            product_dict[product_name] = product_href
            # all_product_href_list.append(product_href)
        all_cat_and_href_products_dict[cat] = product_dict
    return all_cat_and_href_products_dict


async def main(url, cat=None):
    async with aiohttp.ClientSession() as session:
        data = await get_all(session, url, cat)
        return data

if __name__ == '__main__':
    result = asyncio.run(main(url))

    all_category = parse_1(result)
    print(all_category)
    for cat, url in all_category.items():
        result_1 = asyncio.run(main(url, cat))
        print(parse_2(result_1))
