from dotenv import load_dotenv

load_dotenv()
import os
import logging

from utils.logs import CustomFormatter
from os import listdir
from os.path import isfile, join
from importlib import import_module

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")

logging.basicConfig(level=logging.getLevelNamesMapping().get(LOGGING_LEVEL, logging.DEBUG),
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().handlers[0].setFormatter(CustomFormatter())

# Set Requests logging to info and urllib3 to warning
logging.getLogger("requests").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_list_of_scrapers():
    scrapers_dir = "scrapers"
    scrapers = [f"{scrapers_dir}.{f[:-3]}" for f in listdir(scrapers_dir) if
            isfile(join(scrapers_dir, f)) and f.endswith(".py")]
    # Filter out __init__.py
    scrapers = [scraper for scraper in scrapers if scraper != "scrapers.__init__"]
    return scrapers


def main():
    logging.info("Starting Scraper")
    scrapers = get_list_of_scrapers()
    for scraper in scrapers:
        logging.debug(f"Starting Scraper: {scraper}")
        module = import_module(scraper)
        module.main()
        logging.debug(f"Finishing Scraper: {scraper}")
    logging.debug("Finishing Scraper")


if __name__ == "__main__":
    main()
