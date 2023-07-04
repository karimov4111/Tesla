from typing import List, Dict

import os
import datetime
import csv
import json
import requests
import pandas as pd
import time
from random import randint
import sys

import chromedriver_binary
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
scrape_datetime = datetime.datetime.utcnow().isoformat()

options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu')
options.add_argument("--disable-dev-shm-usage")
proxy_address = os.environ.get("HTTP_PROXY")
if proxy_address:
    options.add_argument(f"--proxy-server={proxy_address}")
driver=webdriver.Chrome(options=options)

country_with_codes = {
    "de_de": {"country": "Germany", "currency": "€"},
    "en_GB": {"country": "United Kingdom", "currency": "£"},
    "fr_FR": {"country": "France", "currency": "€"},
    "it_IT": {"country": "Italy", "currency": "€"}
}

def clear_price_amount(price_str:str) -> int:
    price_int = ""
    for i in price_str:
        if i.isnumeric():
            price_int += i
    return int(price_int)

def get_tesla_data_by_model(driver, url, country, currency):
    data = []
    driver.get(url)
    time.sleep(4)
    button=driver.find_element(By.CSS_SELECTOR, '#tds-global-menu > dialog > div > button').click()
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    estimated_delivery_p = soup.find('p', attrs={"data-id": "estimated-delivery-date"})
    estimated_delivery = estimated_delivery_p.text.split(": ")[-1] if estimated_delivery_p else ""
    scraped_data = {
        "delivery": estimated_delivery
    }
    divs = soup.find_all("div", class_="trim-title-container")
    for div in divs:
        model_name_span = div.find('span', class_="tds-label-title tds-o-label-title")
        model_name = model_name_span.text.strip() if model_name_span else ""
        price_span = div.find('span', class_="tds-form-label-text tds-o-label-descriptor")
        price = clear_price_amount(price_span.text)
        full_obj = {
            "scrape_datetime": scrape_datetime,
            "country": country,
            "currency": currency,
            "model": model_name,
            "price": price,
        }
        full_obj.update(scraped_data)
        data.append(full_obj)
        print(full_obj)
    return data

def get_tesla_data(driver):
    driver = driver
    driver.maximize_window()
    driver.get("https://www.tesla.com/de_de/model3/design#overview")
    final_data = []
    for country_code, obj in country_with_codes.items():
        country = obj["country"]
        currency = obj["currency"]
        url_1 = f"https://www.tesla.com/{country_code}/modely/design#overview"
        url_2 = f"https://www.tesla.com/{country_code}/model3/design#overview"
        final_data.extend(get_tesla_data_by_model(driver, url_1, country, currency))
        final_data.extend(get_tesla_data_by_model(driver, url_2, country, currency))
        
        
    return final_data
all_data=get_tesla_data(driver)
df = pd.DataFrame(data=all_data)
df.to_csv(
    sys.argv[1], encoding="utf-8",
    line_terminator="\n",
    quotechar='"',
    quoting=csv.QUOTE_ALL,
    index=False)