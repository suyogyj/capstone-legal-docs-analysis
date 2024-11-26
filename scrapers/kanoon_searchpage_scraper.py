from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import time
import os

DOWNLOAD_DIR = r"C:\Users\suyog\Desktop\monsoon_24\capstone-legal-docs-analysis\Docs\food-safety"
NUM_PAGES = 20

# Set up Chrome options and driver path
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

def get_all_links():
    all_links = []
    print("Getting all links...")
    for i in range(NUM_PAGES):
        page_num=i  
        driver.get(f"https://indiankanoon.org/search/?formInput=food%20safety%20and%20standards%20act%20%20%20%20%20%20%20%20doctypes%3A%20judgments%20fromdate%3A%201-1-2022%20todate%3A%2031-12-2023%20sortby%3A%20leastrecent&pagenum={page_num}")
        time.sleep(1)  # Wait for page to load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = [a['href'] for a in soup.select('a[class="cite_tag"]') if a['href'].startswith('/doc/')]
        all_links.extend(links)
    print(f"Found {len(all_links)} links.")
    return all_links

def download_pdfs(all_links):
    print("Downloading PDFs...")
    num = 0
    for link in all_links:
        print(f"Downloading {link}")
        driver.get(f"https://indiankanoon.org{link}")
        time.sleep(2)
        try:
            download_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(),'Get this document in PDF')]"))
                    )
            download_button.click()
        except Exception as e:
            print(e)
            pass
        num += 1
    print(f"Downloaded {num} PDFs.")

if __name__ == '__main__':
    all_links = get_all_links()
    download_pdfs(all_links)
        
driver.quit()
