from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
# from undetected_chromedriver import Chrome, ChromeOptions
import chromedriver_autoinstaller
import time
import os
import PyPDF2
from tqdm import tqdm

DOWNLOAD_DIR = r"C:\Users\suyog\Desktop\monsoon_24\capstone-legal-docs-analysis\Docs\food-safety-new-24022025" # change to your download directory
NUM_PAGES = 40

dates = {
    "01-01": "07-01", "08-01": "14-01", "15-01": "21-01", "22-01": "28-01",
    "29-01": "04-02", "05-02": "11-02", "12-02": "18-02", "19-02": "25-02",
    "26-02": "04-03", "05-03": "11-03", "12-03": "18-03", "19-03": "25-03",
    "26-03": "01-04", "02-04": "08-04", "09-04": "15-04", "16-04": "22-04",
    "23-04": "29-04", "30-04": "06-05", "07-05": "13-05", "14-05": "20-05",
    "21-05": "27-05", "28-05": "03-06", "04-06": "10-06", "11-06": "17-06",
    "18-06": "24-06", "25-06": "01-07", "02-07": "08-07", "09-07": "15-07",
    "16-07": "22-07", "23-07": "29-07", "30-07": "05-08", "06-08": "12-08",
    "13-08": "19-08", "20-08": "26-08", "27-08": "02-09", "03-09": "09-09",
    "10-09": "16-09", "17-09": "23-09", "24-09": "30-09", "01-10": "07-10",
    "08-10": "14-10", "15-10": "21-10", "22-10": "28-10", "29-10": "04-11",
    "05-11": "11-11", "12-11": "18-11", "19-11": "25-11", "26-11": "02-12",
    "03-12": "09-12", "10-12": "16-12", "17-12": "23-12", "24-12": "30-12",
    "31-12": "31-12"
}

years = ["2024"] # change years according to your requirement
batches_completed = []

chrome_driver = r"C:\Users\suyog\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe" # install chromedriver and replace the path here.
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
        driver.get(f"https://indiankanoon.org/search/?formInput=food%20safety%20%20%20%20doctypes%3A%20judgments%20fromdate%3A%20{from_date}-{year}%20todate%3A%20{to_date}-{year}&pagenum={page_num}")
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
        time.sleep(2)
        driver.get(f"https://indiankanoon.org{link}")
        
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
            batches_completed.append((from_date, to_date))
            #save batches completed
            with open("batches_completed.txt", "w") as f:
                for batch in batches_completed:
                    f.write(f"{batch[0]}-{year} {batch[1]}-{year}\n")
            yearly_count += count
            total_count += count
        yearly_dict[year] = yearly_count
        
    print(f"Downloaded {total_count} PDFs in total.")
    print(yearly_dict)
    print(batches_completed)
    
