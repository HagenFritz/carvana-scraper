import logging
import json
import pathlib

import pandas as pd

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

from utils import logger
from scrape import scraper

PATH_TO_DATA = f"{pathlib.Path(__file__).resolve().parent.parent.parent}/data"

def save_raw(cars, subdir="raw"):
    """
    Saves the data as a .csv if possible, .json otherwise

    Parameters
    ----------
    cars : dict
        data on the available cars
    subdir : str, default "raw"
        subdirectory in data to save 

    Returns
    -------
    <message> : str
        where and what file type was saved
    """
    try:
        # try to convert dict to DataFrame and save as CSV
        res = pd.DataFrame(cars)
        res.to_csv(f"{PATH_TO_DATA}/{subdir}/available_cars.csv")
        return f"Successfuly saved raw data as .csv in {PATH_TO_DATA}/{subdir}"
    except ValueError:
        # typically cannot convert to DataFrame because value lists are not equal
        with open(f"{PATH_TO_DATA}/{subdir}/available_cars.json", "w") as outfile:
            json.dump(cars, outfile)
        return f"Could not save as .csv - saved as .json in {PATH_TO_DATA}/{subdir}"

def save_filtered(cars, subdir="processed"):
    """
    Filters and saves the available cars as .csv if possible

    Parameters
    ----------
    cars : dict
        data on the available cars
    subdir : str, default "raw"
        subdirectory in data to save 

    Returns
    -------
    <message> : str
        where and what file type was saved
    """
    try:
        res = pd.DataFrame(cars)
    except ValueError:
        assert ValueError

    # importing filters
    with open(f'{PATH_TO_DATA}/filters.json') as f:
        filters = json.load(f)

    

def execute_scrape(zipcode):
    """
    Runs the scraper

    Parameters
    ----------
    zipcode : int
        integer referencing the zip code to search for cars    
    """
    log = logger.setup("carvana_scraper",level=logging.DEBUG)
    sc = scraper.Scraper()
    sc.driver.get("https://www.carvana.com/cars?geolocation")
    sc.driver.maximize_window()
    # Set Search Location
    # -------------------
    log.debug("Clicking zip code entry")
    for i in range(1):
        sc.find_and_click("button","aria-label","Location")
        log.debug(f"Entering text - attempt {i}")
        sc.backspace_text(5,"input","id","zip code")
        sc.enter_text(f"{zipcode}","input","id","zip code")
    log.debug("Clicking Go button")
    sc.find_and_click("button","normalize-space()","GO",fxn=True)
    # Applying Make and Body Filters
    # ------------------------------
    with open(f'{PATH_TO_DATA}/filters.json') as f:
        filters = json.load(f)

    # finding cars and storing entries
    for make in filters["make"]:
        log.info(f"Finding cars made by {make}")
        sc.find_and_click("span","normalize-space()","MAKE & MODEL",fxn=True)
        # click make
        button = sc.wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(),'{make}')]")))\
                    .find_element(By.XPATH, f"//div[contains(text(),'{make}')]")
        sc.driver.execute_script("arguments[0].click();", button)
        log.debug("Select all")
        sc.find_and_click("button","normalize-space()","Select All",fxn=True) #TODO: allow for model selection
        sc.find_and_click("span","normalize-space()","MAKE & MODEL",fxn=True)
        time.sleep(2)

    # setting up results
    results = {
        "id":[],
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
        html = sc.driver.page_source # get the html source
        soup = BeautifulSoup(html, 'html.parser') # save as a BS object
        # getting individual car information
        year_makes = soup.find_all("div",{"class","year-make"})
        trim_mileages = soup.find_all("div",{"class","trim-mileage"})
        prices = soup.find_all("div",{"class","flex items-end font-bold mb-4 text-2xl"})
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
                results["monthly_payment"].append(payment[0])
            else:
                results["monthly_payment"].append([item for item in payment if item != " "][1])
            # link
            hrefs = car.find_all("a",href=True)
            for ref in hrefs:
                results["link"].append(f"www.carvana.com{ref['href']}")
                results["id"].append(ref['href'].split("/")[-1])
            # status
            status_message = car.find_all("div",{"class","days-to-delivery days-to-delivery"})
            if len(status_message) > 0:
                results["status"].append(status_message[0].contents) # TODO: check if this actually works on another set
            else:
                status_message = car.find_all("div",{"class","purchase-callout text-only locked"})
                if len(status_message) > 0:
                    results["status"].append(status_message[0].contents[0].text) # TODO: pull the span out
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

        sc.find_and_click("button","normalize-space()","Next",fxn=True)

    print(results)
    # Saving Data
    # -----------
    log.info("Saving data")
    save_message = save_raw(results)
    log.info(save_message)
