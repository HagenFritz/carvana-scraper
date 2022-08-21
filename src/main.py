#!/usr/bin/env python3
# ---
# Get Data
# Date Created: 08/10/2022
# Author: Hagen Fritz
# Last Updated: 08/20/2022
# Description: Selenium-based script that scrapes data from Carvana
# ---
import argparse
from scrape import runner

def main(zipcode):
    """
    
    """
    # get the data
    runner.execute_scrape(zipcode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-z', help="zipcode to find location", default=78750, type=int)
    args = parser.parse_args()

    main(zipcode=args.z)