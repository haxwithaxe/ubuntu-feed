#!/usr/bin/env python3
"""Debian installer RSS feed generator."""

import json
import logging
import os
import re
import sys

import bs4
from feedgen.feed import FeedGenerator
import feedparser
import requests


log = logging.getLogger('debian-feed')


def add_entry(feed, filename, url):
    """Populate a feedgen.entry.FeedEntry given the filename and source URL."""
    entry = feed.add_entry()
    entry.title(filename)
    file_url = os.path.join(url, filename)
    entry.content(file_url)
    entry.description(filename)
    entry.link(href=file_url)


def get_version_files(config, source, path):
    if path.startswith('/'):
        path.pop(0)
    if source.endswith('/'):
        source.pop(-1)
    url = '{}/{}'.format(source, path)
    page = _get_page(url)
    if page is False:  # Got error from server, ignoring this url
        return
    if page is None:  # Error connecting, try again
        page = _get_page(url)
    if not page:  # Too many errors, skip to the next url
        log.error('Failed to connect to the server for "%s" twice.', url)
        return
    soup = bs4.BeautifulSoup(page.content, features='lxml')
    for a in soup.findAll('a'):
        if a.attrs.get('href', '').endswith(config.get('file_extension')):
            yield '{}/{}{}'.format(source, path, a.attrs['href'])


def find_new_files(config, source):
    page = _get_page(source)
    if page is False:  # Got error from server, ignoring this url
        return
    if page is None:  # Error connecting, try again
        page = _get_page(source)
    if not page:  # Too many errors, skip to the next url
        log.error('Failed to connect to the server for "%s" twice.', source)
        return
    soup = bs4.BeautifulSoup(page.content, features='lxml')
    for a in soup.findAll('a'):
        if (a.attrs.get('href') == a.text and
                re.match(r'\d+\.\d+(\.\d+)?/', a.text)):
            yield from get_version_files(config, source, a.attrs['href'])


def _get_page(url):
    log.debug('Getting %s', url)
    try:
        page = requests.get(url)
    except requests.exceptions.ConnectionError as err:
        # Warning since it's not fatal to the workflow unless it happens again.
        log.warning('Error Connectiong to the server "%s": %s', url, err)
        return None
    if not page or not page.ok:
        log.error('Could not get "%s" for this reason: %s', url, page.reason)
        return False
    log.debug('Got: %s %s', url, page.reason)
    return page


def _init_feed():
    feed = FeedGenerator()
    feed.title('Ubuntu Release Feed')
    feed.description('A feed of Ubuntu installer torrent files.')
    feed.link(href='http://localhost')
    return feed


def load_rss(config):
    """Load the previously generated RSS file.

    Returns:
        A tuple of the populated FeedGenerator and a list of the entry links.
    """
    parsed = feedparser.parse(config.get('rss_file'))
    feed = _init_feed()
    for item in parsed.entries:
        entry = feed.add_entry()
        entry.title(item.title)
        entry.description(item.description)
        entry.content(item.content[0]['value'])
        entry.link(href=item.link)
    return feed, [e.link for e in parsed.entries]


def main(config):
    if os.path.exists(config.get('rss_file')):
        feed, entries = load_rss(config)
    else:
        entries = []
        feed = _init_feed()
    for url in config['sources']:
        for torrent in find_new_files(config, url):
            log.debug('Found torrent: %s', torrent)
            if os.path.join(url, torrent) not in entries:
                add_entry(feed, torrent, url)
    feed.rss_file(config.get('rss_file'), pretty=True)


if __name__ == '__main__':
    log.setLevel(logging.ERROR)
    try:
        app_config = json.load(open(sys.argv[1], 'r'))
    except IndexError:
        print('Usage: {} /path/to/config.json'.format(sys.argv[0]))
        sys.exit(1)
    except FileNotFoundError:
        print('The configuration file "{}" does not exist.'.format(
            sys.argv[1]
        ))
        sys.exit(1)
    try:
        # Fail early if the input/output file/dir isn't accessible
        os.makedirs(os.path.dirname(app_config.get('rss_file')), exist_ok=True)
    except PermissionError:
        print('''Couldn't create the output directory "{}"'''.format(
            os.path.dirname(app_config.get('rss_file'))
        ))
        sys.exit(1)
    try:
        main(app_config)
    except PermissionError:
        print('''Couldn't write the RSS output to "{}"'''.format(
            app_config.get('rss_file')
        ))
        sys.exit(1)
