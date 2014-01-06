#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from __future__ import unicode_literals

import os

AUTHOR = u'Paylogic Crew'
SITENAME = u'Paylogic developer portal'
SITEURL = 'http://localhost:8000'

TIMEZONE = 'Europe/Amsterdam'

DEFAULT_DATE = 'fs'
DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  ()

# Social widget
SOCIAL = (('Our GitHub account', 'http://github.com/paylogic'),
          ("Our corporate site", 'http://paylogic.com/'),)

DEFAULT_PAGINATION = 10

STATIC_PATHS = ['images']

# Custom theme for Paylogic.
THEME = os.path.join(os.path.dirname(__file__), 'themes', 'paylogic')

DISQUS_SITENAME = 'paylogicdevportal'

PLUGINS = ('plugins.pelican_extended_authors',)

# Exclude author pages from other content.
ARTICLE_EXCLUDES = ('pages', 'authors')
PAGE_EXCLUDES = ('authors',)

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

DISPLAY_PAGES_ON_MENU = False
MENUITEMS = (
    ("Welcome", "/"),
    ("Integration", "/pages/integration.html"),
    ("Authors", "/authors.html"),
    ("About", "/pages/about.html"),
)
