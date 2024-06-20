from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import io
import requests
import time
import os

def scraper_func(link, pdf_file_name):
    try:
        print('Starting Driver')

        options = uc.ChromeOptions()
        options.add_argument('--incognito')
        options.add_argument('--disable-popup-blocking')
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--headless=new')
        options.add_argument('--ignore-certificate-errors')

        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 10)

        driver.get(link)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="show-prospectus-button"]')))
        button_link = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="show-prospectus-button"]').get_attribute('href')
        driver.get(button_link)

        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'button[class="ffe-button ffe-button--action optin-button--accept-all  optin-button--spacer"]')))
        ok_button = driver.find_element(By.CSS_SELECTOR, 'button[class="ffe-button ffe-button--action optin-button--accept-all  optin-button--spacer"]')
        ok_button.click()
        time.sleep(3)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class="ffe-button ffe-button--action style_salgsoppgave__3yBKD"]')))
        pdf_button = driver.find_element(By.CSS_SELECTOR, 'button[class="ffe-button ffe-button--action style_salgsoppgave__3yBKD"]')
        pdf_button.click()

        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'button[class="ffe-button ffe-button--primary style_download-button__R7XCj"]')))
        download_button = driver.find_element(By.CSS_SELECTOR,
                                              'button[class="ffe-button ffe-button--primary style_download-button__R7XCj"]')
        download_button.click()
        time.sleep(3)
        response = requests.get(driver.current_url)

        print(response)

        if response.status_code == 200:
            pdf_file = io.BytesIO(response.content)
            print(f"Current working directory: {os.getcwd()}")
            local_file_path = os.path.join(os.getcwd(), pdf_file_name)
            with open(local_file_path, 'wb') as f:
                f.write(pdf_file.read())
            print(f"PDF saved to {local_file_path}")
            driver.quit()
            return True
        else:
            print("Failed to retrieve the PDF.")
            driver.quit()
            return False

    except Exception as e:
        print(e)
        if 'driver' in locals():
            driver.quit()

# Example usage:
# if __name__ == '__main__':
#     links =  ['https://www.finn.no/realestate/homes/ad.html?finnkode=351952578',
#              'https://www.finn.no/realestate/project/ad.html?finnkode=296616815&location=1.20061.20511',
#              'https://www.finn.no/realestate/homes/ad.html?finnkode=352378840',
#              'https://www.finn.no/realestate/homes/ad.html?finnkode=352617896']

#     for i in links:    
#         filename = i.split("finnkode=")[-1] +".pdf"
#         status = scraper_func(i, filename)
#         print(filename, status)
