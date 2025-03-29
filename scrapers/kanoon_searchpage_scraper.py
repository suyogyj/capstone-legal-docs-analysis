from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import time
import os
import PyPDF2
from tqdm import tqdm
import random
import pickle
import sys
import json
import threading

DOWNLOAD_DIR = r"C:\Users\suyog\Desktop\monsoon_24\capstone-legal-docs-analysis\Docs\food-safety-new-24022025"
NUM_PAGES = 40
COOKIES_FILE = "kanoon_cookies.pkl"
PROGRESS_FILE = "scraping_progress.json"
CAPTCHA_WAIT_TIME = 5  # Seconds to wait for CAPTCHA solving

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
    "05-11": "11-11", "12-11": "18-11","19-11": "25-11", "26-11": "02-12",
    "03-12": "09-12", "10-12": "16-12", "17-12": "23-12", "24-12": "30-12",
    "31-12": "31-12"
}

years = ["2024"]
batches_completed = []

def setup_driver():
    """Setup and return a configured Chrome driver"""
    chromedriver_autoinstaller.install()
    preferences = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_experimental_option("prefs", preferences)
    
    # Add realistic user agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chromeOptions.add_argument(f'user-agent={user_agent}')
    
    # Additional options to make detection harder
    chromeOptions.add_argument("--disable-blink-features=AutomationControlled")
    chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
    chromeOptions.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chromeOptions)
    
    # Execute CDP commands to prevent detection
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Load cookies if they exist
    if os.path.exists(COOKIES_FILE):
        try:
            driver.get("https://indiankanoon.org")
            cookies = pickle.load(open(COOKIES_FILE, "rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)
            print("Loaded cookies from previous session")
        except Exception as e:
            print(f"Error loading cookies: {e}")
    
    return driver

def random_delay(min_seconds=1, max_seconds=3):
    """Add a random delay to mimic human behavior"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay/1.7)

def is_captcha_present(driver):
    """Check if a CAPTCHA or verification screen is present"""
    captcha_indicators = [
        "captcha", 
        "verification", 
        "verify you're a human",
        "security check",
        "prove you're not a robot",
        "human?"
    ]
    
    page_source = driver.page_source.lower()
    return any(indicator in page_source for indicator in captcha_indicators)

def handle_captcha(driver):
    """Handle CAPTCHA when detected with automatic continuation after timeout"""
    if is_captcha_present(driver):
        print(f"\nCAPTCHA detected! You have {CAPTCHA_WAIT_TIME} seconds to solve it manually.")
        print("The browser window is waiting for you to solve the CAPTCHA.")
        print("Press 'c' to continue immediately after solving, or 'q' to quit.")
        
        # Setup a timer to continue automatically
        continue_flag = {"should_continue": False, "should_quit": False}
        
        def wait_for_input():
            user_input = input()
            if user_input.lower() == 'c':
                continue_flag["should_continue"] = True
            elif user_input.lower() == 'q':
                continue_flag["should_quit"] = True
        
        # Start input thread
        input_thread = threading.Thread(target=wait_for_input)
        input_thread.daemon = True
        input_thread.start()
        
        # Wait for either timeout or user input
        start_time = time.time()
        while time.time() - start_time < CAPTCHA_WAIT_TIME:
            if continue_flag["should_continue"]:
                print("Continuing as requested...")
                break
            if continue_flag["should_quit"]:
                save_cookies(driver)
                sys.exit("Exiting as requested by user")
            time.sleep(0.1)
        
        # Save cookies after CAPTCHA handling
        save_cookies(driver)
        return True
    return False

def save_cookies(driver):
    """Save browser cookies to file"""
    try:
        pickle.dump(driver.get_cookies(), open(COOKIES_FILE, "wb"))
        print("Cookies saved")
    except Exception as e:
        print(f"Error saving cookies: {e}")

def load_progress():
    """Load progress information from file"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
                
                # Convert list of lists back to list of tuples for batches_completed
                if 'batches_completed' in progress:
                    batches_completed = [tuple(batch) for batch in progress['batches_completed']]
                else:
                    batches_completed = []
                    
                return {
                    'batches_completed': batches_completed,
                    'current_year': progress.get('current_year', None),
                    'current_batch': tuple(progress['current_batch']) if 'current_batch' in progress else None,
                    'current_page': progress.get('current_page', 0),
                    'processed_links': set(progress.get('processed_links', []))
                }
        except Exception as e:
            print(f"Error loading progress: {e}")
    
    return {
        'batches_completed': [],
        'current_year': None,
        'current_batch': None,
        'current_page': 0,
        'processed_links': set()
    }

def save_progress(progress_data):
    """Save progress information to file"""
    try:
        # Convert sets to lists and tuples to lists for JSON serialization
        json_compatible = {
            'batches_completed': [list(batch) for batch in progress_data['batches_completed']],
            'current_year': progress_data['current_year'],
            'current_batch': list(progress_data['current_batch']) if progress_data['current_batch'] else None,
            'current_page': progress_data['current_page'],
            'processed_links': list(progress_data['processed_links'])
        }
        
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(json_compatible, f)
        print("Progress saved")
    except Exception as e:
        print(f"Error saving progress: {e}")

def get_all_links(from_date, to_date, year, start_page=0):
    all_links = []
    print(f"Getting links starting from page {start_page}...")
    
    for i in tqdm(range(start_page, NUM_PAGES)):
        page_num = i
        url = f"https://indiankanoon.org/search/?formInput=food%20safety%20%20%20%20doctypes%3A%20judgments%20fromdate%3A%20{from_date}-{year}%20todate%3A%20{to_date}-{year}&pagenum={page_num}"
        driver.get(url)
        
        # Update progress information
        progress['current_page'] = page_num
        save_progress(progress)
        
        # Add random delay to mimic human behavior
        random_delay(1, 2)
        
        # Check for CAPTCHA and handle it if present
        if handle_captcha(driver):
            # Reload the page after solving CAPTCHA
            driver.get(url)
            random_delay(1, 2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        if "No matching results" in soup.text:
            print("Got all links, stopping")
            break
            
        links = [a['href'] for a in soup.select('a[class="cite_tag"]') if a['href'].startswith('/doc/')]
        all_links.extend(links)
        
        # Random delay between pages to avoid detection
        random_delay(1, 3)
        
    print(f"Found {len(all_links)} links.")
    return all_links

def download_pdfs(all_links, processed_links=None):
    if processed_links is None:
        processed_links = set()
        
    print("Downloading PDFs...")
    num = 0
    
    # Filter out already processed links
    links_to_process = [link for link in all_links if link not in processed_links]
    print(f"Processing {len(links_to_process)} new links (skipping {len(all_links) - len(links_to_process)} already processed)")
    
    for link in tqdm(links_to_process):
        # Add randomized delay between downloads
        random_delay(1, 2)
        
        driver.get(f"https://indiankanoon.org{link}")
        
        # Check for CAPTCHA and handle it if present
        if handle_captcha(driver):
            # Reload the page after solving CAPTCHA
            driver.get(f"https://indiankanoon.org{link}")
            random_delay(1, 2)
        
        try:
            download_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(),'Get this document in PDF')]"))
            )
            download_button.click()
            
            # Wait a bit longer after clicking download
            random_delay(1, 2)
            
            # Mark as processed
            processed_links.add(link)
            progress['processed_links'] = processed_links
            
            # Save progress periodically (every 5 downloads)
            if num % 5 == 0:
                save_progress(progress)
                save_cookies(driver)
                
        except TimeoutException:
            print(f"Timeout waiting for download button on {link}")
            continue
        except Exception as e:
            print(f"Error downloading {link}: {e}")
            continue
            
        num += 1
    
    print(f"Downloaded {num} PDFs.")
    return num

if __name__ == '__main__':
    # Create download directory if it doesn't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Load progress information
    progress = load_progress()
    batches_completed = progress['batches_completed']
    
    # Setup driver
    driver = setup_driver()
    
    try:
        total_count = 0
        yearly_dict = {}

        start_year_idx = 0
        if progress['current_year'] is not None:
            # Find the index of the year we need to continue from
            for i, year in enumerate(years):
                if year == progress['current_year']:
                    start_year_idx = i
                    break

        for year_idx, year in enumerate(years[start_year_idx:], start_year_idx):
            progress['current_year'] = year
            yearly_count = 0
            
            # Determine where to start in the dates dictionary
            date_items = list(dates.items())
            start_batch_idx = 0
            
            if progress['current_batch'] is not None and progress['current_year'] == year:
                for i, (from_date, to_date) in enumerate(date_items):
                    if (from_date, to_date) == progress['current_batch']:
                        start_batch_idx = i
                        break
            
            for batch_idx, (from_date, to_date) in enumerate(date_items[start_batch_idx:], start_batch_idx):
                # Skip batches already completed
                if (from_date, to_date) in batches_completed:
                    print(f"Skipping completed batch: {from_date}-{year} to {to_date}-{year}")
                    continue
                
                # Update current batch in progress
                progress['current_batch'] = (from_date, to_date)
                save_progress(progress)
                
                print(f"\nProcessing batch: {from_date}-{year} to {to_date}-{year}")
                
                # Get start page from progress if we're continuing the same batch
                start_page = progress['current_page'] if progress['current_batch'] == (from_date, to_date) else 0
                
                all_links = get_all_links(from_date, to_date, year, start_page)
                count = download_pdfs(all_links, progress['processed_links'])
                
                # Reset current page for next batch
                progress['current_page'] = 0
                
                # Mark batch as completed
                batches_completed.append((from_date, to_date))
                progress['batches_completed'] = batches_completed
                save_progress(progress)
                
                # Save batches completed after each batch
                with open("batches_completed.txt", "w") as f:
                    for batch in batches_completed:
                        f.write(f"{batch[0]}-{year} {batch[1]}-{year}\n")
                
                yearly_count += count
                total_count += count
                
                # Save cookies periodically
                save_cookies(driver)
                
            yearly_dict[year] = yearly_count
            
        # Clear current batch info after completing all batches
        progress['current_batch'] = None
        progress['current_page'] = 0
        save_progress(progress)
        
        print(f"Downloaded {total_count} PDFs in total.")
        print(yearly_dict)
        print(batches_completed)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user. Saving progress...")
        save_progress(progress)
        save_cookies(driver)
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("Saving progress...")
        save_progress(progress)
        save_cookies(driver)
        raise
        
    finally:
        # Save cookies before closing
        save_cookies(driver)
        
        # Close the driver
        driver.quit()

