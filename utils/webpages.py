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


def get_authenticated_api_data(url, bearer_token):
    """
    Make an authenticated API request
    :param url: URL
    :param bearer_token: Bearer Token
    :return: Response
    """
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Encoding': 'utf-8'
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def post_authenticated_api_data(url, bearer_token, json_data):
    """
    Make an authenticated API request
    :param url: URL
    :param bearer_token: Bearer Token
    :param json_data: JSON data
    :return: Response
    """
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Encoding': 'utf-8'
    }
    resp = requests.post(url, headers=headers, json=json_data)
    resp.raise_for_status()
    return resp.json()
