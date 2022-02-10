#!/usr/bin/env python3
"""Debian installer RSS feed generator."""

import io
import json
import logging
import os
import re
import sys
import xml.dom.minidom

import bs4
import feedgenerator
import feedparser
import requests


log = logging.getLogger('debian-feed')


class Version:

    def __init__(self, config, source, path):
        self._config = config
        self._source = source
        self._page_url = os.path.join(source, path)

    @property
    def files(self):
        page = _get_page(self._page_url)
        if not page:
            return
        soup = bs4.BeautifulSoup(page.content, features='lxml')
        for a in soup.findAll('a'):
            if a.attrs.get('href', '').endswith(self._config.get('file_extension')):
                yield a.attrs['href'], os.path.join(self._page_url,
                                                    a.attrs['href'])


class Source:

    def __init__(self, config, url):
        self._config = config
        self._url = url

    @property
    def files(self):
        page = _get_page(self._url)
        if not page:
            return
        soup = bs4.BeautifulSoup(page.content, features='lxml')
        for a in soup.findAll('a'):
            if (a.attrs.get('href') == a.text and
                    re.match(r'\d+\.\d+(\.\d+)?/', a.text)):
                yield from Version(self._config, self._url,
                                   a.attrs['href']).files


class Feed:

    def __init__(self, config):
        self._config = config
        self._entries = []

    def __enter__(self):
        if os.path.exists(self._config.get('rss_file')):
            self._entries = self._load_rss()
        else:
            self._init_feed()
        return self

    def __exit__(self, *args):
        ugly_io = io.BytesIO()
        self._feed.write(ugly_io, encoding='utf-8')
        ugly_io.seek(0)
        parsed = xml.dom.minidom.parse(ugly_io)
        with open(self._config.get('rss_file'), 'w') as rss_file:
            rss_file.write(parsed.toprettyxml())

    def _init_feed(self):
        self._feed = feedgenerator.Rss201rev2Feed(
            title='Ubuntu Release Feed',
            description='A feed of Ubuntu installer torrent files.',
            link='http://localhost'
        )

    def _load_rss(self):
        """Load the previously generated RSS file.

        Returns:
            A tuple of the populated FeedGenerator and a list of the entry links.
        """
        parsed = feedparser.parse(self._config.get('rss_file'))
        self._init_feed()
        for item in parsed.entries:
            self._feed.add_item(
                title=item.title,
                description=item.description,
                link=item.link
            )
        return [e.link for e in parsed.entries]

    def add_entry(self, filename, url):
        """Populate a feedgen.entry.FeedEntry given the filename and source URL."""
        if url in self._entries:
            return
        self._entries.append(url)
        self._feed.add_item(
            title=filename,
            description=filename,
            link=url
        )


def _get_page(url):
    log.debug('Getting %s', url)
    try:
        page = requests.get(url)
    except requests.exceptions.ConnectionError as err:
        # Warning since it's not fatal to the workflow unless it happens again.
        log.warning('Error Connectiong to the server "%s": %s', url, err)
        return _get_page(url)
    if not page or not page.ok:
        log.error('Could not get "%s" for this reason: %s', url, page.reason)
        return False
    log.debug('Got: %s %s', url, page.reason)
    return page


def main(config):
    with Feed(config) as feed:
        for source in config['sources']:
            for torrent, url in Source(config, source).files:
                log.debug('Found torrent: %s', torrent)
                feed.add_entry(torrent, url)


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
