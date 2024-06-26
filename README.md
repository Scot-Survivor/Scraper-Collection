# MISC Scrapers Collection

This project is a collection of various web scrapers written in Python. It includes scrapers for different websites and generates outputs in various formats.

## Features

- Collection of various web scrapers for different websites.
- Utilizes Python's multithreading for efficient and faster data scraping.
- Outputs are generated in various formats for easy access and usage.
- Uses PyInputPlus for user input validation and PySimpleValidate for data validation.
- Custom logging format for easy debugging and tracking.

## How to Use

1. Run the `main.py` script.
2. When prompted, select a scraper to run or choose to run all.
3. The selected scraper(s) will fetch data from the respective websites and log the process.
4. The fetched data will be written to a file in the `outputs` directory.

## Dependencies

- Python 3.11
- `pip install -r requirements.txt`

## Example

An example output file `quick-lunch-ideas-work.txt` can be found in the `outputs/bbcgoodfood_lists` directory. This file contains a list of recipe URLs fetched from the corresponding BBC Good Food page.

Another example output file `recipetineats.txt` can be found in the `outputs/recipetineats` directory. This file contains a list of recipe URLs fetched from the RecipeTin Eats website.

## Note

This project is intended for educational purposes and should not be used to violate the terms of use of the websites being scraped. Always respect the website's robots.txt file and use web scraping responsibly.