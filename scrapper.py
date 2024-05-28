
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
import time
import schedule # type: ignore

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(message):
    msg = MIMEMultipart()
    msg['From'] = 'from email'
    msg['To'] = 'to email'
    msg['Subject'] = 'DL Test Availability'

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('add login details', 'add password here')
        server.sendmail('from mail', 'to mail', msg.as_string())
    except Exception as e:
        print("Error: ", e)
    finally:
        server.quit()

class scrapper:
    def __init__(self, headless = True) -> None:
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()
        self.driver.get('https://onlineservices.dps.mn.gov/EServices/_/')

    def wait_and_click(self, by, locator):
        element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((by, locator))
        )
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        element.click()

    def wait_and_send_keys(self, by, locator, keys):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, locator))
        )
        element.send_keys(keys)

    def click_checkbox(self, by, locator):
        checkbox = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by, locator))
        )
        self.driver.execute_script("arguments[0].scrollIntoView();", checkbox)
        checkbox.click()
    
    def click_dialog_box(self,by, dialog_box_locator, ok_button_locator):
        dialog_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((by,dialog_box_locator))
        )
        ok_button = dialog_box.find_element(by,ok_button_locator)
        ok_button.click()

    def get_availability(self, location_id):
        availability = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, f'caption2_Df-51-{location_id}'))
        ).text
        return availability

    def run_scrapper(self):
        self.wait_and_click(By.ID, 'c_Df-9-1')
        self.wait_and_click(By.ID, 'caption2_Dd-a-2')
        self.wait_and_click(By.ID, 'caption2_Dg-c-3')
        self.wait_and_send_keys(By.ID, 'Dk-e', 'Permit Number')
        self.wait_and_send_keys(By.ID, 'Dk-h', 'DOB')
        self.click_checkbox(By.ID, 'Dk-s')
        self.wait_and_click(By.ID, 'action_3')
        self.click_dialog_box(By.CLASS_NAME, 'ui-dialog','FastMessageBoxButtonOk')
        time.sleep(1)
        self.wait_and_send_keys(By.ID, 'Df-c', 'zip code')
        self.wait_and_click(By.ID, 'Df-d')
        locations = {
            'Arden Hill': 1,
            'Eagan': 2,
            'Plymouth': 3
        }
        availability = {}
        for location, location_id in locations.items():
            availability[location] = self.get_availability(location_id)
        return availability
    
    def close_scrapper(self):
        self.driver.quit()

def job():
    scrapper_obj = scrapper(headless=True)
    availability = scrapper_obj.run_scrapper()
    scrapper_obj.close_scrapper()
    message = ""
    expected_status = "No Availability"
    is_available = False
    for location, availability_status in availability.items():
        if availability_status != expected_status:
            is_available = True
            message += f"Availability at {location}: {availability_status}\n"
    if is_available:
        send_email(message)

schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)