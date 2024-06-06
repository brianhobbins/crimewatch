from bs4 import BeautifulSoup as bs
import google.generativeai as gem
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
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
while click_counter < 2:
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

print('\n')   
html = browser.page_source
browser.quit()

# Parse the HTML
soup = bs(html, "html.parser")

# grab all cards
cards_array = []
card_bodies = soup.find_all('div', class_='card-body')
user_input = ""
for card in card_bodies:
    card_text = card.get_text(strip=True)
    cards_array.append(card_text)
    user_input += card_text + '\n'


print(f'Number of Pages:{click_counter}')

# Grab the system prompt from system.prompt file
with open('system.prompt', 'r', encoding='utf-8') as file:
    sys_prompt = file.read()

# Send the data to llama using the openapi client
# Point to the local server
gem.configure(api_key=os.environ['GOOGLE_API_KEY'])

model = gem.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(sys_prompt)

print(response.text)

# new_message = {"role": "assistant", "content": ""}

# for chunk in completion:
#     if chunk.choices[0].delta.content:
#         print(chunk.choices[0].delta.content, end="", flush=True)
#         new_message["content"] += chunk.choices[0].delta.content

# message.append(new_message)
# print(message)
    
    # Uncomment to see chat history
    # import json
    # gray_color = "\033[90m"
    # reset_color = "\033[0m"
    # print(f"{gray_color}\n{'-'*20} History dump {'-'*20}\n")
    # print(json.dumps(history, indent=2))
    # print(f"\n{'-'*55}\n{reset_color}")

