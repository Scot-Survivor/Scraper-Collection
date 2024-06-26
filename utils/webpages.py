from typing import List
import requests
import bs4
import urllib3


def get_webpage(url, features='html.parser') -> bs4.BeautifulSoup:
    """
    Get the webpage from the given URL and return a BeautifulSoup object.
    :param url:  URL of the webpage
    :param features: The parser to use
    :return:
    """
    response = requests.get(url)
    response.raise_for_status()
    return bs4.BeautifulSoup(response.text, features)


def get_url_path_parts(url) -> List[str]:
    """
    Get the path parts of the URL
    :param url: URL
    :return: List of path parts
    """
    paths = urllib3.util.parse_url(url).path.split('/')
    paths = list(filter(lambda x: x != "", paths))
    paths = list(filter(lambda x: x.strip(), paths))
    return paths
