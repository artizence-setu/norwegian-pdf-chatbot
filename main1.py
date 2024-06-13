from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import io
import os
from uuid import uuid4
import time

def scarper_one(link, pdf_file_name):
    print('Starting Driver')
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--incognito')
    options.add_argument('--disable-popup-blocking')
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--headless=new')
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 3)

    driver.get(link)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="show-prospectus-button"]')))
    button_link = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="show-prospectus-button"]').get_attribute('href')
    driver.get(button_link)
    time.sleep(3)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[class*="dnb-button"]')))
    pdf_link = [element.get_attribute('href') for element in driver.find_elements(By.CSS_SELECTOR, 'a[class*="dnb-button"]') if 'prospect' in element.get_attribute('href')]
    if pdf_link[0]:
        print('downloading pdf')
        pdf_link = pdf_link[0]
        response = requests.get(pdf_link)

        if response.status_code == 200:
            pdf_file = io.BytesIO(response.content)
            local_file_path = os.path.join(os.getcwd(), pdf_file_name)
            with open(local_file_path, 'wb') as f:
                f.write(pdf_file.read())

            print(f"PDF saved to {local_file_path}")
        else:
            print("Failed to retrieve the PDF.")
    else:
        print("No PDF found.")
    driver.close()


if __name__ == '__main__':
    link = 'https://www.finn.no/realestate/homes/ad.html?finnkode=343986944'
    pdf_file_name = f"{uuid4()}.pdf"
    
    scarper_one(link, pdf_file_name)
