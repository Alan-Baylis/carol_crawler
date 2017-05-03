import time
import httplib2
import re
from bs4 import BeautifulSoup, SoupStrainer
import json
import csv

http = httplib2.Http()
# Import JSON config
configJson = ''
# Track which pages we've already looked at
crawledPages = []
# Store the root URL to make sure we don't follow external links
parentSite = ''
# Store the output as a list
hits = []


# Inject project-specific lists
def config_importer():
    with open('../config.json') as json_data_file:
        return json.load(json_data_file)


# Get the sites from config and run grab_hits_for_a_site function
def grab_sites(configJson):
    global parentSite
    for site in configJson['sites']:
        parentSite = site
        grab_hits_for_a_site(site)
    return


# Create a new soup object and then return all visible text that matches a pattern.
def grab_hits_for_a_site(url):
    global crawledPages
    status, response = http.request(url)
    soup = BeautifulSoup(response, "html.parser")
    for link in BeautifulSoup(response, "html.parser", parse_only=SoupStrainer('a')):
        if link.has_attr('href'):
            grab_hits_for_sub_site(link['href'])
            crawledPages.append(link['href'])
    visibleText = soup.findAll(text=True)
    text_hits_by_keyword(visibleText, url)
    return


# Grab hits for all the linked pages from a root URL
def grab_hits_for_sub_site(url):
    global crawledPages, parentSite
    if url in crawledPages:
        return
    if url is '#':
        return
    if url[0:1] is '/':
        grab_hits_for_a_site(parentSite + url)
        return
    if url[0:len(parentSite)] is not parentSite:
        return
    grab_hits_for_a_site(url)
    return


# Search for each of the supplied keywords in the text and add them to a list
def text_hits_by_keyword(visibleText, url):
    global configJson, parentSite, hits
    for text in visibleText:
        for keyword in configJson['keywords']:
            if re.search(keyword, text, re.IGNORECASE):
                hits.append([url, text, parentSite])
                continue
    return


def make_a_csv():
    global hits
    with open("../output/crawl-" + str(int(time.time())) + ".csv", 'w+') as outputFile:
        wr = csv.writer(outputFile, dialect='excel')
        wr.writerow(['Website', 'Hit text', 'Url'])
        for hit in hits:
            wr.writerow([hit[0], hit[1], hit[2]])
        return


def main():
    global configJson, crawledPages
    configJson = config_importer()
    grab_sites(configJson)
    print(hits)
    make_a_csv()
    exit(200)


main()
