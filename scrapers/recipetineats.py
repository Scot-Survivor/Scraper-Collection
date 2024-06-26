import logging
import os
import tqdm

from utils.webpages import get_webpage, get_url_path_parts
from utils.outputs import write_output
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://www.recipetineats.com/"
URLs = {}


def get_recipe_urls(url, thread_id=1):
    logging.debug(f"Thread-{thread_id}: Fetching Recipes from {url}")
    recipes = []
    soup = get_webpage(url)
    articles = soup.find_all('article')
    for article in articles:
        a = article.find('a', class_='entry-title-link')
        if a is not None:
            recipe_url = a['href']
            recipes.append(recipe_url)
            if recipe_url not in URLs[url]:
                URLs[url].append(recipe_url)
    if len(articles) == 0:
        logging.warning(f"Thread-{thread_id}: No recipes found at {url}")
        return []
    logging.debug(f"Thread-{thread_id}: Found {len(recipes)} recipes")
    return recipes


def get_categories(url):
    soup = get_webpage(url)
    return [a['href'] for a in soup.select('a') if a.has_attr('href') and
            a['href'].startswith('https://www.recipetineats.com/') and "category" in get_url_path_parts(a['href'])]


def main():
    logging.info("Fetching Categories")
    for url in get_categories(BASE_URL):
        URLs[url] = []
    logging.info(f"Found {len(URLs)} categories")
    logging.info("Fetching Recipes")
    with ThreadPoolExecutor(os.cpu_count()) as executor:
        for i, url in enumerate(URLs):
            executor.submit(get_recipe_urls, url, i)

    for url in tqdm.tqdm(URLs, desc="Writing Outputs"):
        if len(URLs[url]) > 0:
            write_output(f"{get_url_path_parts(url)[-1]}.txt", "\n".join(URLs[url]))



if __name__ == "__main__":
    main()
