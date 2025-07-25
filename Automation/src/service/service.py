#src/service/service.py
import os
import time
import re
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


EXCEL_FILE = "company_info.xlsx"

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def save_to_excel(data):
    df = pd.DataFrame([data])
    if not os.path.exists(EXCEL_FILE):
        df.to_excel(EXCEL_FILE, index=False)
    else:
        with pd.ExcelWriter(EXCEL_FILE, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, startrow=pd.read_excel(EXCEL_FILE).shape[0]+1, index=False, header=False)

def download_pdf(url, folder):
    try:
        os.makedirs(folder, exist_ok=True)
        filename = url.split("/")[-1]
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):  
            response = requests.get(url)
            with open(filepath, "wb") as f:
                f.write(response.content)
    except Exception as e:
        print(f"Download failed {url}: {e}")

def get_text_by_class(driver, class_name):
    try:
        return driver.find_element(By.CLASS_NAME, class_name).text.strip()
    except:
        return ""

def get_text_after_label(driver, label):
    try:
        return driver.execute_script(f'''
            let el = [...document.querySelectorAll("span.blue_txt")]
                .find(e => e.textContent.trim() === "{label}");
            return el && el.nextSibling ? el.nextSibling.textContent.trim() : "";
        ''')
    except:
        return ""

def get_description(driver):
    try:
        return driver.execute_script('''
            let c = document.querySelector(".company_description");
            if (!c) return "";
            let text = Array.from(c.childNodes)
                .filter(n => n.nodeType === 3 && n.textContent.trim())
                .map(n => n.textContent.trim()).join(" ");
            let hidden = c.querySelector('span[style*="display:none"]');
            return text + (hidden ? " " + hidden.textContent.trim() : "");
        ''')
    except:
        return ""

def scrape_company_links(driver, base_url):
    company_links = []
    driver.get(base_url)
    time.sleep(3)

    while True:
        time.sleep(2)
        companies = driver.find_elements(By.CSS_SELECTOR, "a[href^='/Company/']")
        for c in companies:
            link = c.get_attribute("href")
            name = c.text.strip()
            if link and name:
                company_links.append((name, link))
        
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next")
            if "disabled" in next_button.get_attribute("class").lower():
                break
            next_button.click()
        except:
            break

    return list(dict.fromkeys(company_links))

def extract_exchange_codes():
    url = "https://www.annualreports.com/Browse/Exchange"
    driver = create_driver()
    driver.get(url)
    time.sleep(2)

    exchanges = {}
    boxes = driver.find_elements(By.CSS_SELECTOR, "a[href^='/Companies?exch=']")
    for box in boxes:
        name = box.text.strip().split("\n")[0]
        match = re.search(r"exch=(\d+)", box.get_attribute("href"))
        if match and name:
            exchanges[name.upper()] = match.group(1)

    driver.quit()
    return exchanges

def extract_industry_codes():
    url = "https://www.annualreports.com/Browse/Industry"
    driver = create_driver()
    driver.get(url)
    time.sleep(2)

    industries = {}
    items = driver.find_elements(By.CSS_SELECTOR, "a[href^='/Companies?ind=']")
    for item in items:
        name = item.text.strip()
        match = re.search(r"ind=(i\d+)", item.get_attribute("href"))
        if match and name:
            industries[name] = match.group(1)

    driver.quit()
    return industries

def download_company_data(driver, name, link, start_year):
    driver.get(link)
    time.sleep(2)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "company_description"))
    )
    info = {
        "Company Name": name,
        "Ticker": get_text_by_class(driver, "ticker_name"),
        "Exchange": get_text_after_label(driver, "Exchange"),
        "Industry": get_text_after_label(driver, "Industry"),
        "Sector": get_text_after_label(driver, "Sector"),
        "Employees": get_text_by_class(driver, "employees"),
        "Location": get_text_by_class(driver, "location"),
        "Description": get_description(driver)
    }
    save_to_excel(info)

    pdf_links = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
    pdf_set = set()
    pdf_year_links = []

    for pdf in pdf_links:
        href = pdf.get_attribute("href")
        if href and href not in pdf_set:
            match = re.search(r'_(\d{4})\.pdf$', href)
            if match:
                year = int(match.group(1))
                if year >= start_year:
                    pdf_set.add(href)
                    pdf_year_links.append((year, href))

    pdf_year_links.sort()
    for year, pdf_url in pdf_year_links:
        download_pdf(pdf_url, f"downloads/{name}")

def download_all_companies(start_year=2010):
    driver = create_driver()
    base_url = "https://www.annualreports.com/Companies?exch=9"  
    company_links = scrape_company_links(driver, base_url)
    for name, link in company_links:
        download_company_data(driver, name, link, start_year)
    driver.quit()
    return len(company_links)

def download_companies_by_filter(start_year=2010, exchange=None, industry=None):
    exchange_codes = extract_exchange_codes()
    industry_codes = extract_industry_codes()

    driver = create_driver()
    base_url = "https://www.annualreports.com/Companies"
    params = []

    if exchange:
        exch_id = exchange_codes.get(exchange.upper())
        if not exch_id:
            driver.quit()
            raise ValueError(f"Invalid exchange: {exchange}")
        params.append(f"exch={exch_id}")

    if industry:
        ind_id = industry_codes.get(industry)
        if not ind_id:
            driver.quit()
            raise ValueError(f"Invalid industry: {industry}")
        params.append(f"ind={ind_id}")

    if params:
        base_url += "?" + "&".join(params)

    company_links = scrape_company_links(driver, base_url)

    for name, link in company_links:
        download_company_data(driver, name, link, start_year)
    driver.quit()
    return len(company_links)

def download_company_info_excel():
    driver = create_driver()
    base_url = "https://www.annualreports.com/Companies?exch=9"
    company_links = scrape_company_links(driver, base_url)

    if os.path.exists(EXCEL_FILE):
        os.remove(EXCEL_FILE)

    for name, link in company_links:
        driver.get(link)
        time.sleep(2)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "company_description"))
        )
        info = {
            "Company Name": name,
            "Ticker": get_text_by_class(driver, "ticker_name"),
            "Exchange": get_text_after_label(driver, "Exchange"),
            "Industry": get_text_after_label(driver, "Industry"),
            "Sector": get_text_after_label(driver, "Sector"),
            "Employees": get_text_by_class(driver, "employees"),
            "Location": get_text_by_class(driver, "location"),
            "Description": get_description(driver)
        }
        save_to_excel(info)
    driver.quit()
    return os.path.abspath(EXCEL_FILE)

def download_company_by_name(company_name, start_year=2010):
    driver = create_driver()
    base_url = "https://www.annualreports.com/Companies?exch=9"
    company_links = scrape_company_links(driver, base_url)

    matched_company = None
    for name, link in company_links:
        if name.strip().lower() == company_name.strip().lower():
            matched_company = (name, link)
            break

    if not matched_company:
        driver.quit()
        return None

    name, link = matched_company
    download_company_data(driver, name, link, start_year)
    driver.quit()

    folder = f"downloads/{name}"
    if os.path.isdir(folder):
        pdf_files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
        if pdf_files:
            pdf_path = os.path.join(folder, pdf_files[0])
            return pdf_path

    return None