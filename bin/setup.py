import time
from urllib.request import urlopen
import re
from bs4 import BeautifulSoup
from bs4 import NavigableString
import json


# Inject project-specific lists
def Config_Importer():
    with open('../config.json') as json_data_file:
        return json.load(json_data_file)


# Create a new soup object and then return all visible text that matches a pattern.
def Grab_Hits():
    soup = BeautifulSoup(urlopen(
        "http://chiorinotechnology.com/index_en.html").read(), "html.parser") # todo Crawl entire website sitemap
    visibleText = soup.findAll(text=True)
    for text in visibleText:
        if re.search('energ(y)?(ies)?', text, re.IGNORECASE): # todo Change this to a recursive list
            # print(text) # todo Make output look nicer and output to a file
            continue

def main():
    Grab_Hits()
    json = Config_Importer()
    print(json)


main()
