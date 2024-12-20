from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import time
import os
import PyPDF2
from tqdm import tqdm

DOWNLOAD_DIR = r"C:\Users\suyog\Desktop\monsoon_24\capstone-legal-docs-analysis\Docs\food-safety-new"
NUM_PAGES = 40

dates = {"01-01": "28-02", "01-03": "30-04", "01-05": "30-06", "01-07": "31-08", "01-09": "31-10", "01-11": "31-12"}
years = ["2023", "2022", "2021"]


chrome_driver = r"C:\Users\suyog\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"  # Update path to ChromeDriver
chromedriver_autoinstaller.install()
preferences = {"download.default_directory": DOWNLOAD_DIR,
                "download.prompt_for_download": False,
                "directory_upgrade": True,
                "safebrowsing.enabled": True
                }
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option("prefs", preferences)
driver = webdriver.Chrome(options=chromeOptions)

def get_all_links(from_date, to_date, year):
    all_links = []
    print("Getting all links...")
    for i in tqdm(range(NUM_PAGES)):
        page_num=i  
        driver.get(f"https://indiankanoon.org/search/?formInput=%22food%20safety%20and%20standards%20act%22%20%20%20doctypes%3A%20sc%2Chighcourts%20fromdate%3A%20{from_date}-{year}%20todate%3A%20{to_date}-{year}%20sortby%3A%20leastrecent&pagenum={page_num}")
        time.sleep(1)  # Wait for page to load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        if "No matching results" in soup.text:
            print("got all links, stopping")
            break
        links = [a['href'] for a in soup.select('a[class="cite_tag"]') if a['href'].startswith('/doc/')]
        all_links.extend(links)
    print(f"Found {len(all_links)} links.")
    return all_links

def download_pdfs(all_links):
    print("Downloading PDFs...")
    num = 0
    for link in tqdm(all_links):
        driver.get(f"https://indiankanoon.org{link}")
        time.sleep(1)
        try:
            download_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(),'Get this document in PDF')]"))
                    )
            download_button.click()
        except Exception as e:
            print(e)
            pass
        num += 1
        # print(f"Completed {num}/{len(all_links)} downloads.")
    print(f"Downloaded {num} PDFs.")
    return num

if __name__ == '__main__':
    total_count = 0
    yearly_dict = {}

    for year in years:
        yearly_count = 0
        for from_date, to_date in dates.items():
            all_links = get_all_links(from_date, to_date, year)
            count = download_pdfs(all_links)
            yearly_count += count
            total_count += count
        yearly_dict[year] = yearly_count
        
    print(f"Downloaded {total_count} PDFs in total.")
    print(yearly_dict)
