#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from dotenv import load_dotenv
import os
from markdown import Markdown

markdown = Markdown(extensions=["markdown.extensions.extra"])


def md(content, *args):
    return markdown.convert(content)


JINJA_FILTERS = {
    "md": md,
}

load_dotenv()

AUTHOR = "Sebastian Proost"
SITENAME = "DeckLock"
SITEURL = ""

PATH = "content"
DECKLOCK_CACHE = "dl_cache"

TIMEZONE = "Europe/Paris"

DEFAULT_LANG = "en"

THEME = "theme"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# We don't need any of these pages
AUTHORS_SAVE_AS = False
TAGS_SAVE_AS = False
CATEGORIES_SAVE_AS = False
ARCHIVES_SAVE_AS = False

AUTHOR_SAVE_AS = False
TAG_SAVE_AS = False
CATEGORY_SAVE_AS = False

ARTICLE_URL = "posts/{slug}/"
ARTICLE_SAVE_AS = "posts/{slug}/index.html"
PAGE_URL = "pages/{slug}/"
PAGE_SAVE_AS = "pages/{slug}/index.html"

# Add the assets folder to the static data
STATIC_PATHS = ["assets"]

# Configure plugins
PLUGIN_PATHS = ["plugins"]
PLUGINS = ["keyforge", "mtg", "gwent", "fab", "webassets", "jinja_filters"]


# KeyForge Section
KEYFORGE_ENABLED = True

KEYFORGE_PATH = "data"
KEYFORGE_ASSETS_PATH = "assets/keyforge"

KEYFORGE_DECK_SAVE_AS = "keyforge/{slug}.html"
KEYFORGE_DECKS_SAVE_AS = "keyforge.html"

DOK_API_KEY = os.getenv("DOK_API_KEY", None)

# Magic: The Gathering Section
MTG_ENABLED = True

MTG_PATH = "data"
MTG_ASSETS_PATH = "assets/mtg"


# Gwent Section
GWENT_ENABLED = True

GWENT_PATH = "data"
GWENT_ASSETS_PATH = "assets/gwent"
GWENT_CURRENT_VERSION = "8.2.0"

# Flesh and Blood Section
FAB_ENABLED = True

FAB_PATH = "data"
FAB_ASSETS_PATH = "assets/fab"

TEMPLATE_PAGES = {
    "gwent_overview.html": "gwent.html",
    "mtg_overview.html": "mtg.html",
    "fab_overview.html": "fab.html",
}

# When set to true, external links to KeyForge/M:tG/Gwent/FaB card images will be used
# if false images will be downloaded (which could be a copyright violation if you include them)
USE_EXTERNAL_LINKS = True
STATIC_EXCLUDES = []

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
