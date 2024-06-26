import logging
import re
import os
import urllib.parse as urlparse

import pyinputplus as pyip

from utils.webpages import get_webpage, get_url_path_parts
from utils.outputs import write_output

URLs = {}


def get_recipe_urls(url, thread_id=1):
    logging.debug(f"Thread-{thread_id}: Fetching Recipes from {url}")
    recipes = []
    soup = get_webpage(url)
    titles = soup.find_all("h3", id=re.compile("[0-9]+"))
    for title in titles:
        a = title.find('a')
        if a is not None:
            recipe_url = urlparse.urljoin(url, a['href'])
            logging.debug(f"Thread-{thread_id}: Found Recipe: {recipe_url}")
            recipes.append(recipe_url)
            if recipe_url not in URLs[url]:
                URLs[url].append(recipe_url)
    logging.debug(f"Thread-{thread_id}: Found {len(recipes)} recipes")
    return recipes


def main():
    url = pyip.inputURL("Enter a BBC Good Food URL: ", limit=3)
    logging.info(f"Fetching Recipes from {url}")
    URLs[url] = []
    get_recipe_urls(url)
    write_output(f"{get_url_path_parts(url)[-1]}.txt", "\n".join(URLs[url]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
