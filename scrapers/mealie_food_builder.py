"""
    Connects to a Mealie Instance and tries to automatically build a food list based on confidence scores,
    from built in Ingredients Parser.
"""
import os
import logging
import tqdm
import urllib.parse as urlparse
import pyinputplus as pyip

from typing import List

from utils.cache import Cache, TTL
from utils.webpages import get_authenticated_api_data, post_authenticated_api_data
from utils.outputs import load_settings, save_settings
from concurrent.futures import ThreadPoolExecutor

SETTINGS = load_settings()
NEEDS_CHECKING = []


def get_recipe_ids():
    recipe_ids = []
    fetch = True
    page = 1
    base_url = SETTINGS['MEALIE_URL']
    token = SETTINGS['MEALIE_API_TOKEN']
    while fetch:
        url = urlparse.urljoin(base_url, f"/api/recipes?perPage=25&page={page}")
        data = get_authenticated_api_data(url, token)
        for recipe in data['items']:
            recipe_ids.append(recipe['slug'])
        if data['page'] >= data['total_pages']:
            fetch = False
        else:
            page += 1
    return recipe_ids


def get_recipe_ingredients(recipe_id):
    url = urlparse.urljoin(SETTINGS['MEALIE_URL'], f"/api/recipes/{recipe_id}")
    data = get_authenticated_api_data(url, SETTINGS['MEALIE_API_TOKEN'])
    return data['recipeIngredient']


def get_food_list_from_ingredient_parser(ingredients, thread_id=1) -> List[str]:
    logging.debug(f"Thread-{thread_id}: Fetching Foods from Ingredients")
    ingredient_strings = []
    foods = []
    for ingredient in ingredients:
        if ingredient['food'] is None:
            ingredient_strings.append(ingredient['note'])

    data = {
        "parser": "nlp",
        "ingredients": ingredient_strings
    }
    url = urlparse.urljoin(SETTINGS['MEALIE_URL'], "/api/parser/ingredients")
    resp_data = post_authenticated_api_data(url, SETTINGS['MEALIE_API_TOKEN'], data)
    for i, food_resp in enumerate(resp_data):
        if food_resp['ingredient'] is None or food_resp['ingredient']['food'] is None:
            continue
        food = food_resp['ingredient']['food']['name']
        food_conf = food_resp['confidence']['food']
        if food_conf and food_conf > 0.85:
            foods.append(food)
        else:
            NEEDS_CHECKING.append({'food': food, 'original_text': ingredient_strings[i]})
    logging.debug(f"Thread-{thread_id}: Found {len(foods)} foods")
    return foods


def get_current_food_names():
    fetch = True
    page = 1
    foods = []
    while fetch:
        logging.debug(f"Fetching Foods from Page {page}")
        data = get_authenticated_api_data(urlparse.urljoin(SETTINGS['MEALIE_URL'],
                                                           f"/api/foods?perPage=25&page={page}"),
                                          SETTINGS['MEALIE_API_TOKEN'])
        for food in data['items']:
            foods.append(food['name'])
        if data['page'] >= data['total_pages']:
            fetch = False
        else:
            page += 1
    return foods


def create_new_food(food_name):
    url = urlparse.urljoin(SETTINGS['MEALIE_URL'], "/api/foods")
    data = {
        "name": food_name
    }
    resp = post_authenticated_api_data(url, SETTINGS['MEALIE_API_TOKEN'], data)
    return resp


def filter_checking_foods():
    new_foods = []
    seen_text = []
    seen_foods = []
    for food in NEEDS_CHECKING:
        if food['original_text'] == "":
            continue
        if food['original_text'] in seen_text:
            continue
        if food['food'] in seen_foods:
            continue
        new_foods.append(food)
        seen_text.append(food['original_text'])

    NEEDS_CHECKING.clear()
    NEEDS_CHECKING.extend(new_foods)


def main():
    cache = Cache()
    token = os.getenv("MEALIE_API_TOKEN", SETTINGS.get("MEALIE_API_TOKEN"))
    if token is None:
        token = pyip.inputStr("Enter your Mealie API Token: ")
        SETTINGS["MEALIE_API_TOKEN"] = token
    url = os.getenv("MEALIE_URL", SETTINGS.get("MEALIE_URL"))
    if url is None:
        url = pyip.inputURL("Enter your Mealie URL: ")
        SETTINGS["MEALIE_URL"] = url
    save_settings(SETTINGS)
    if cache.exists("recipe_ids"):
        recipe_ids = cache.get("recipe_ids")
    else:
        recipe_ids = get_recipe_ids()
        cache.set("recipe_ids", recipe_ids, TTL.MINUTES * 5)
        cache.write_cache()
    logging.debug(f"Found {len(recipe_ids)} recipes")

    if cache.exists("ingredients"):
        ingredients = cache.get("ingredients")
    else:
        ingredients = []
        for recipe_id in tqdm.tqdm(recipe_ids, desc="Fetching Ingredients"):
            ingredients.append(get_recipe_ingredients(recipe_id))
        cache.set("ingredients", ingredients, TTL.MINUTES * 5)
        cache.write_cache()

    foods = []
    with ThreadPoolExecutor() as executor:
        for i, ingredient in enumerate(ingredients):
            foods.extend(executor.submit(get_food_list_from_ingredient_parser, ingredient, i).result())
    foods = list(set(foods))
    logging.info(f"Found {len(foods)} foods")
    filter_checking_foods()
    logging.info(f"Needs Checking: {len(NEEDS_CHECKING)}")
    check = pyip.inputYesNo("Would you like to check the foods that need checking (y/n)? ", default="n",
                            yesVal='y', noVal='n')
    if check == 'y':
        for food in NEEDS_CHECKING:
            print(f"Original Text: {food['original_text']}")
            print(f"Food: {food['food']}")
            print()
            accept = pyip.inputYesNo("Is this correct? (y/n) ", default="n",
                                     yesVal='y', noVal='n')
            if accept == 'y':
                foods.append(food['food'])
            else:
                foods.append(pyip.inputStr("Enter the correct food: "))

    current_foods = get_current_food_names()
    foods = list(set(foods) - set(current_foods))

    logging.info(f"Creating {len(foods)} new foods")
    check = pyip.inputYesNo("Would you like to create these foods (y/n)? ", default="n",
                            yesVal='y', noVal='n')
    if check == 'n':
        logging.info("Exiting")
        return
    for food in tqdm.tqdm(foods, desc="Creating Foods"):
        create_new_food(food)

    logging.info("Finished")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
