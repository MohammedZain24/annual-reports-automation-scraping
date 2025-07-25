import os
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

BASE_URL = "https://www.annualreports.com"

EXCHANGE_EXCEL_FILE = "exchange_list.xlsx"
INDUSTRY_EXCEL_FILE = "industry_list.xlsx"

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def extract_options(url: str, id_pattern: str, type_label: str):
    driver = create_driver()
    driver.get(url)
    time.sleep(2)

    result = []
    elements = driver.find_elements(By.CSS_SELECTOR, f"a[href*='{id_pattern}']")

    for el in elements:
        href = el.get_attribute("href")  # 🔗 الرابط الكامل
        match = re.search(f"{id_pattern}=([a-zA-Z0-9]+)", href)
        id_ = match.group(1) if match else None

        name = el.text.strip()

        # 🖼️ استخراج الصورة (إن وُجدت)
        img = ""
        img_elements = el.find_elements(By.TAG_NAME, "img")
        if img_elements:
            img_src = img_elements[0].get_attribute("src")
            img = img_src if img_src.startswith("http") else f"{BASE_URL}{img_src}"

        # ✅ إضافة كل المعلومات مع الرابط
        if id_ and name:
            result.append({
                "id": id_,
                "name": name,
                "image": img,
                "link": href  # 🔗 أضفنا الرابط هنا
            })

    driver.quit()

    filename = EXCHANGE_EXCEL_FILE if type_label == "exchange" else INDUSTRY_EXCEL_FILE
    df = pd.DataFrame(result)
    df.to_excel(filename, index=False)
    return result

def extract_exchange_options():
    return extract_options(f"{BASE_URL}/Browse/Exchange", "exch", "exchange")

def extract_industry_options():
    return extract_options(f"{BASE_URL}/Browse/Industry", "ind", "industry")
