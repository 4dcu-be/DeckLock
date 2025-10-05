#!/usr/bin/env python
# -*- coding: utf-8 -*- #

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
# Don't include a / at the end
SITEURL = "https://4dcu.be/DeckLock"
RELATIVE_URLS = False

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None

DELETE_OUTPUT_DIRECTORY = False

# When set to true, external links to KeyForge/M:tG/Gwent/FaB card images will be used
# if false images will be downloaded (which could be a copyright violation if you include them)
USE_EXTERNAL_LINKS = True
STATIC_EXCLUDES = ["assets/keyforge", "assets/mtg", "assets/gwent", "assets/fab"]

# Following items are often useful when publishing

# DISQUS_SITENAME = ""
# GOOGLE_ANALYTICS = ""
