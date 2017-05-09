import time
import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
import json
import csv
from urllib.parse import urlparse, urlunparse

# Import JSON config
configJson = ''
# Track which pages we've already looked at
crawledPages = []
# Store the root URL to make sure we don't follow external links
parentSite = ''
# Store the output as a list
hits = []
# Store the hit counter as a dict
counter = {}


# Inject project-specific lists
def config_importer():
    with open('../config.json') as json_data_file:
        return json.load(json_data_file)


# Get the sites from config and run grab_hits_for_a_site function
def grab_sites(configJson):
    global parentSite

    for site in configJson['sites']:
        parentSite = site
        print(bcolors.OKGREEN + 'Checking site ' + bcolors.UNDERLINE + site + '...' + bcolors.ENDC)
        grab_hits_for_a_site(site)
    return


# Create a new soup object and then return all visible text that matches a pattern.
def grab_hits_for_a_site(url):
    global crawledPages

    if url in crawledPages:
        return

    try:
        r = requests.get(url, timeout=3)

    except requests.exceptions.ConnectionError:
        print(bcolors.WARNING + url + ' did not respond at all. Moving on...' + bcolors.ENDC)
        return

    except requests.exceptions.Timeout:
        print(bcolors.WARNING + url + ' did not respond in time. Moving on...' + bcolors.ENDC)
        return

    except:
        return

    print(bcolors.OKBLUE + 'Grabbed markup for ' + url + '...' + bcolors.ENDC)

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.findAll(text=True)
    visibleText = filter(visible, text)

    text_hits_by_keyword(visibleText, url)

    crawledPages.append(url)

    for link in BeautifulSoup(r.text, "html.parser", parse_only=SoupStrainer('a')):

        if link.has_attr('href'):
            grab_hits_for_sub_site(link['href'])

    return


# Filter to extract only visible text from the page.
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True


# Grab hits for all the linked pages from a root URL
def grab_hits_for_sub_site(url):
    global crawledPages, parentSite

    u = urlparse(url)
    p = urlparse(parentSite)

    if u.netloc is '' and u.path is '':
        return

    if url in crawledPages:
        return

    if u.path[-4:] == '.pdf':
        return

    if u.path[-4:] == '.jpg':
        return

    if "@" in url:
        return

    if u.netloc is '':
        unparsed_url = build_new_url(u, p)

        if unparsed_url in crawledPages:
            return

        print(bcolors.OKBLUE + 'Checking the subsite ' + unparsed_url + '...' + bcolors.ENDC)
        grab_hits_for_a_site(unparsed_url)
        return

    if u.netloc.split('.')[-2] != p.netloc.split('.')[-2]:
        print(bcolors.OKBLUE + 'Skipped external site ' + p.netloc + bcolors.ENDC)
        return

    return


# Use urlunparse to rebuild the URL before rerunning it
def build_new_url(a, b):
    unparsed_url = (b.scheme, b.netloc, a.path, a.query, '', '')
    return urlunparse(unparsed_url)


# Search for each of the supplied keywords in the text and add them to a list
def text_hits_by_keyword(visibleText, url):
    global configJson, parentSite, hits, counter

    for text in visibleText:

        for keyword in configJson['keywords']:

            if re.search(keyword, text, re.IGNORECASE):
                hits.append([url, text, parentSite])
                if keyword in counter:
                    counter[keyword] + 1
                else:
                    counter[keyword] = 1
                continue
    return


# Generate a CSV of the results
def make_a_csv():
    global hits

    with open("../output/crawl-" + str(int(time.time())) + ".csv", 'w+') as outputFile:
        wr = csv.writer(outputFile, dialect='excel')
        wr.writerow(['Website', 'Hit text', 'Url'])

        for hit in hits:
            wr.writerow([hit[0], hit[1], hit[2]])
        return


# Print some helpful console output
def print_formated_output():
    global counter

    output = bcolors.OKGREEN + 'Process complete. Here are the results (see the output folder for your CSV):\n' + bcolors.ENDC

    for keyword in counter:
        output += bcolors.OKGREEN + "Keyword: " + bcolors.ENDC + "{:s}".format(
            keyword) + bcolors.OKGREEN + " - Result Count: " + bcolors.ENDC + "{:d}\n".format(counter[keyword])
    print(output)
    return


# Quickie console formatting class
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Our main function
def main():
    global configJson, crawledPages

    configJson = config_importer()
    print(bcolors.OKBLUE + 'Imported the config file...' + bcolors.ENDC)
    grab_sites(configJson)
    print_formated_output()
    make_a_csv()
    exit(200)


main()
