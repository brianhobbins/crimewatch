# CRIMEWATCH WARRANT SCRAPER AND ANALYSIS
# Author: @brianhobbins

import os
import json
from selenium import webdriver
import google.generativeai as gem
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException,TimeoutException

# Set up the Chrome WebDriver
headless = Options()
headless.add_argument("--headless")
browser = webdriver.Chrome(options=headless)

# Open the page
browser.get('https://www.crimewatchpa.com/warrants')

# init click counter
click_counter = 0

# Loop to expand the page by clicking "Show More" until the button is no longer active or present
while click_counter < 26:
    try:
        wait = WebDriverWait(browser, 5)
        show_more_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Show more')]")))
        # Scroll to the element
        browser.execute_script("arguments[0].scrollIntoView();", show_more_button)
        print('\rClick Count:',str(click_counter), end='')
        # Click the button
        if show_more_button.is_displayed() and show_more_button.is_enabled():
            show_more_button.send_keys(Keys.RETURN)
            click_counter += 1
        else:
            print("button not clickable")
            break
    except (ElementClickInterceptedException, TimeoutException) as e:
        # Close the browser
        browser.quit()
        if e == ElementClickInterceptedException:
            print("intercepted!")
        elif e == TimeoutException:
            print("timeout!")
        else:
            print(e)
        break

# Get the HTML
html = browser.page_source
browser.quit()

# Parse the HTML
soup = bs(html, "html.parser")

# grab all cards and store them in a newline seperated string
card_bodies = soup.find_all('div', class_='card-body')
user_input = ""
for card in card_bodies:
    card_text = card.get_text(strip=True)
    user_input += f'{card_text}\n'

print(f'\nNumber of Pages:{click_counter}')

# Grab the system prompt from system.prompt file
with open('system.prompt', 'r', encoding='utf-8') as file:
    sys_prompt = file.read()

# Set the API Key, Load Gemini Model and set system prompt
gem.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = gem.GenerativeModel(model_name='gemini-1.5-flash',system_instruction=[sys_prompt])
print("Ready for raw data")

# Send the raw data to Gemini. Return the response
response = model.generate_content(user_input)

# Write the response to warrants.json
with open('warrants.json', 'w', encoding='utf-8') as file:
    json.dump(response.text, file)

print("json file created")


# # print(response.text)
