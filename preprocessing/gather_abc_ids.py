# -*- coding: utf-8 -*-
# gather_abc_ids.py
# Defines helper for scraping ABC article IDs
#
#   Copyright (C) 2016 Andrew Donnellan, Benjamin Roberts
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import argparse
import feedparser
import requests
from bs4 import BeautifulSoup

TOPIC_INDEX = "http://www.abc.net.au/news/topics/"
DEFAULT_OUTFILE = None


def main():
    args = parse_arguments()
    topic_urls = gather_topic_pages()
    print("Gathered {} topic pages".format(len(topic_urls)))

    feed_urls = gather_feed_urls(topic_urls)
    print("Gathered {} feeds".format(len(feed_urls)))

    ids = set()
    for feed_url in feed_urls:
        ids = ids.union(gather_ids(feed_url))

    save_ids(ids, args)


def gather_topic_pages():
    topic_pages = []
    alphabet = map(chr, range(ord('a'), ord('z')+1))
    for letter in alphabet:
        print("Gathering topics starting with " + letter)
        index_page = requests.get(TOPIC_INDEX + letter)
        page = BeautifulSoup(index_page.content, 'html.parser')
        for a in page.find_all('a'):
            if("/news/topic/" in a.get('href')):
                topic_pages.append("http://www.abc.net.au" + a.get('href'))

    return topic_pages


def gather_feed_urls(topic_urls):
    feed_urls = []
    for topic_url in topic_urls:
        print("Gathering feed URL from topic " + topic_url)
        topic_page = requests.get(topic_url)
        page = BeautifulSoup(topic_page.content, 'html.parser')
        for a in page.find_all('a'):
            if("rss.xml" in a.get('href')):
                feed_urls.append("http://www.abc.net.au" + a.get('href'))
                break


    return feed_urls


def gather_ids(feed_url):
    """

    :param feed: URL of feed to fetch
    :param depth: number of pages to scrape
    :return:
    """
    ids = set()
    print("Gathering IDs from feed " + feed_url)

    feed = feedparser.parse(feed_url)
    for article in feed['entries']:
        ids.add(article['link'].split('/')[-1])

    return ids


def save_ids(ids, args):
    if args['out'] is None:
        for id in ids:
            print(id)
    else:
        f = open(args['out'], "w")
        for id in ids:
            f.write("{}\n".format(id))
        f.close()


def parse_arguments():
    """
    parses the command line arguments
    :return: dictionary containing the arguments
    :rtype: dict
    """

    parser = argparse.ArgumentParser(description="farms abc documentIDs for their govhack API")
    parser.add_argument("--out", default=DEFAULT_OUTFILE, help="save IDs to file")

    return vars(parser.parse_args())



if __name__ == '__main__':
    main()