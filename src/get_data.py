#!/usr/bin/env python3
# ---
# Get Data
# Date Created: 08/10/2022
# Author: Hagen Fritz
# Last Updated: 08/10/2022
# Description: Selenium-based script that scrapes data from Carvana
# ---
import argparse
import logging
import pathlib
import os
import json

import pandas as pd

import time

from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

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

def setup_logging(log_file_name, level=logging.INFO):
    """
    Creates a logging object
    Parameters
    ----------
    log_file_name : str
        how to name the log file
    Returns
    -------
    logger : logging object
        a logger to debug
    """
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Clearing log instances
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handler
    dir_path = pathlib.Path(__file__).resolve().parent
    f_handler = logging.FileHandler(f'{dir_path}/{log_file_name}.log',mode='w')
    logging.getLogger().setLevel(level)

    # Create formatter and add it to handler
    f_format = logging.Formatter('%(asctime)s: %(name)s (%(lineno)d) - %(levelname)s - %(message)s',datefmt='%m/%d/%y %H:%M:%S')
    f_handler.setFormatter(f_format)

    # Add handler to the logger
    logger.addHandler(f_handler)

    # repeat the above steps but for a StreamHandler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(level)
    c_format = logging.Formatter('%(asctime)s: %(name)s (%(lineno)d) - %(levelname)s - %(message)s',datefmt='%m/%d/%y %H:%M:%S')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    return logger

def main(zipcode,):
    """
    
    """
    log = setup_logging("carvana_scraper",level=logging.DEBUG)
    scraper = Scraper()
    scraper.driver.get("https://www.carvana.com/cars?geolocation")
    scraper.driver.maximize_window()
    # Set Search Location
    # -------------------
    log.debug("Clicking zip code entry")
    for i in range(1):
        scraper.find_and_click("input","name","ZIP CODE")
        log.debug(f"Entering text - attempt {i}")
        scraper.enter_text(f"{zipcode}","input","name","ZIP CODE")
    log.debug("Clicking Go button")
    scraper.find_and_click("button","normalize-space()","Go",fxn=True)
    # Applying Make and Body Filters
    # ------------------------------
    with open('../data/filters_test.json') as f:
        filters = json.load(f)

    # finding cars and storing entries
    for make in filters["make"]["standard"]:
        log.info(f"Finding cars made by {make}")
        scraper.find_and_click("span","normalize-space()","MAKE & MODEL",fxn=True)
        # click make
        button = scraper.wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(),'{make}')]")))\
                    .find_element(By.XPATH, f"//div[contains(text(),'{make}')]")
        scraper.driver.execute_script("arguments[0].click();", button)
        log.debug("Select all")
        scraper.find_and_click("button","normalize-space()","Select All",fxn=True)
        scraper.find_and_click("span","normalize-space()","MAKE & MODEL",fxn=True)
        time.sleep(5)
        # setting up results
        results = {
            "make":[],
            "model":[],
            "year":[],
            "trim":[],
            "mileage":[],
            "price":[],
            "monthly_payment":[],
            "status":[],
            "link":[]
        }
        # loop through all pages
        while True:
            # get information from current page
            html = scraper.driver.page_source # get the html source
            soup = BeautifulSoup(html, 'html.parser') # save as a BS object
            # getting individual car information
            year_makes = soup.find_all("div",{"class","year-make"})
            trim_mileages = soup.find_all("div",{"class","trim-mileage"})
            prices = soup.find_all("div",{"class","price"})
            monthly_payments = soup.find_all("div",{"class","monthly-payment"})
            cars = soup.find_all("div",{"class","result-tile"})
            # looping through the available cars
            for year_make, trim_mileage, price, monthly_payment, car in zip(year_makes, trim_mileages, prices, monthly_payments, cars):
                # year, make, and model
                simplified_year_make = [item for item in year_make.contents if item != " "]
                if len(simplified_year_make) == 1: # for whatever reason sometimes this gets put as one value...
                    #log.debug(f"year_make came out as one value: {simplified_year_make}")
                    simplified_year_make = simplified_year_make[0].split(" ")
                for key, val in zip(["year","make","model"],[simplified_year_make[0],simplified_year_make[1],simplified_year_make[2]]):
                    results[key].append(val)
                # trim and mileage
                trim = trim_mileage.findChildren("span")[0].contents[0]
                mileage = trim_mileage.findChildren("span")[1].contents[0]
                for key, val in zip(["trim","mileage"],[trim,mileage]):
                    results[key].append(val)
                # price
                results["price"].append(price.contents[-1])
                # monthly payment
                payment = monthly_payment.findChildren("span")[0].contents
                if len(payment) == 1:
                    #log.debug(f"payment came out as one value: {payment}")
                    results["monthly_payment"].append(payment)
                else:
                    results["monthly_payment"].append([item for item in payment if item != " "][1])
                # link
                hrefs = car.find_all("a",href=True)
                for ref in hrefs:
                    results["link"].append(f"www.carvana.com{ref['href']}")
                # status
                status_message = car.find_all("div",{"class","days-to-delivery days-to-delivery"})
                if len(status_message) > 0:
                    results["status"].append(status_message[0].contents) # TODO: check if this actually works on another set
                else:
                    status_message = car.find_all("div",{"class","purchase-callout text-only locked"})
                    if len(status_message) > 0:
                        results["status"].append(status_message[0].contents) # TODO: pull the span out
                    else:
                        results["status"].append("None")

            # next page
            try:
                # try to get the page listing at bottom of site
                pages = soup.find_all("span",{"class":"paginationstyles__PaginationText-mpry3x-5 iXXOCI"})
                nav = pages[0].contents[0].split(" ")
                log.info(f"Page {nav[1]} of {nav[-1]}")
                # if page numbers are equal to each other, we have scraped last page so we need to break infinite loop
                if nav[1] == nav[-1]:
                    break
            except IndexError:
                if len(pages) == 0:
                    # happens sometimes
                    log.info("Navigated too quickly to catch the page number")
                else:
                    log.info(pages)

            scraper.find_and_click("button","normalize-space()","Next",fxn=True)

    # Saving Data
    # -----------
    log.info("Saving data")
    try:
        # try to convert dict to DataFrame and save as CSV
        res = pd.DataFrame(results)
        res.to_csv("../data/processed/available_cars.csv")
    except ValueError:
        # typically cannot convert to DataFrame because value lists are not equal
        log.exception("Could not convert dict to DataFrame:")
        with open("../data/processed/available_cars.json", "w") as outfile:
            json.dump(results, outfile)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-z', help="zipcode to find location", default=78750, type=int)
    args = parser.parse_args()

    main(zipcode=args.z)