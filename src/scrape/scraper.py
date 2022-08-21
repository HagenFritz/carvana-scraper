
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

class Scraper:

    def __init__(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')        
        #chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 7)

    def find_and_click(self, tagname, attribute, value, subtag="",fxn=False):
        """
        Clicks a button that typically throws a ElementNotInteractable exception
        Parameters
        ----------
        tagname : str
            html tag for xpath
        attribute : str
            html attribute for xpath
        value : str
            html value for xpath
        subtag : str, default ""
            subtag to look for in xpath - MUST include the starting "/"
        wait_time : int, default 2
            number of seconds to wait
        fxn : boolean, default False
            whether we are using a function in the xPath
        """
        try:
            if fxn is False:
                button = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//{tagname}[@{attribute}='{value}']{subtag}")))\
                    .find_element(By.XPATH, f"//{tagname}[@{attribute}='{value}']{subtag}")
                self.driver.execute_script("arguments[0].click();", button)
            else:
                button = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//{tagname}[{attribute}='{value}']{subtag}")))\
                    .find_element(By.XPATH, f"//{tagname}[{attribute}='{value}']{subtag}")
                self.driver.execute_script("arguments[0].click();", button)
        except TimeoutException:
            if fxn is False:
                button = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//{tagname}[@{attribute}='{value}']{subtag}")))\
                    .find_element(By.XPATH, f"//{tagname}[@{attribute}='{value}']{subtag}")
                self.driver.execute_script("arguments[0].click();", button)
            else:
                button = self.wait.until(EC.presence_of_element_located((By.XPATH, f"//{tagname}[{attribute}='{value}']{subtag}")))\
                    .find_element(By.XPATH, f"//{tagname}[{attribute}='{value}']{subtag}")
                self.driver.execute_script("arguments[0].click();", button)

        time.sleep(2)

    def enter_text(self, text, tagname, attribute, value, subtag=""):
        """
        Sends/enters text into an input
        Parameters
        ----------
        text : str
            text to send to input
        tagname : str
            html tag for xpath
        attribute : str
            html attribute for xpath
        value : str
            html value for xpath
        subtag : str, default ""
            subtag to look for in xpath - MUST include the starting "/"
        """
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//{tagname}[@{attribute}='{value}']{subtag}"))).send_keys(text)
        except TimeoutException:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//{tagname}[@{attribute}='{value}']{subtag}"))).send_keys(text)

        time.sleep(2)