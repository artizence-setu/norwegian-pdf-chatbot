from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests

scrape_status = {}

def scrape(link, conversation_id):
    # Set up Chrome options to run headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Initialize the WebDriver with the headless options
    driver = webdriver.Chrome(service=Service(r"chromedriver.exe"), options=chrome_options)

    driver.get(link)

    # Locate all <div> elements by their class name
    div_elements = driver.find_elements(By.CLASS_NAME, 'pb-16.mt-40.border-b')

    try:
        # Get the fourth <div> element
        fourth_div_element = div_elements[3]

        # Find the <a> tag within the fourth <div> element
        a_tag = fourth_div_element.find_element(By.TAG_NAME, 'a')

        # Extract the href attribute (the link)
        link = a_tag.get_attribute('href')

        driver.get(link)

        a_element = driver.find_elements(By.CSS_SELECTOR, 'a.dnb-button.dnb-button--primary.dnb-button--has-text.theme-dark__button__secondary.dnb-anchor--no-style.dnb-a')

        # Extract the href attribute (the link)
        pdf = a_element[1].get_attribute('href')

        response = requests.get(pdf)

        # Save the PDF to a file
        pdf_filename = 'document.pdf'  # Specify the desired filename
        with open(pdf_filename, 'wb') as file:
            file.write(response.content)

        print(f"PDF downloaded and saved as {pdf_filename}")
        scrape_status[conversation_id] = "completed"
    except Exception:
        print("House Already Sold.")
        scrape_status[conversation_id] = "error"

    # Close the WebDriver
    driver.quit()


    #URL = 'https://www.finn.no/realestate/homes/ad.html?finnkode=358548133'

# URL = 'https://www.finn.no/realestate/homes/ad.html?finnkode=357923689'
