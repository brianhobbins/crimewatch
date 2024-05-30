# Using Selenium and BeautifulSoup



from bs4 import BeautifulSoup as bs
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
while click_counter <101:
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
html = browser.page_source
browser.quit()

soup = bs(html, "html.parser")

# grab all cards
cards_array = []
card_bodies = soup.find_all('div', class_='card-body')

for card in card_bodies:
    card_text = card.get_text(strip=True)
    cards_array.append(card_text)
    print(card_text)


# Send cards to a textfile
with open('card_text.txt', 'w', encoding='utf-8') as file:
    # Write the contents of the array to the file
    for cards in cards_array:
        file.write(cards + '\n')
print('Number of clicks:',click_counter)
