from pelican import signals
from pelican.readers import BaseReader

import json
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import quote
import requests
from time import sleep

from plugins.utils import fetch_image
from pelican.utils import slugify


def get_local_card_img_path(assets_cards_path, url):
    img_filename = Path(urlparse(url).path).name
    return os.path.join(assets_cards_path, img_filename)


def parse_meta(line):
    stripped_line = line.lstrip('//').strip()
    tag, value = [p.strip() for p in stripped_line.split(':')]

    return tag, value


def parse_card_line(line):
    sideboard = False

    stripped_line = line.strip()

    if stripped_line.startswith('SB:'):
        sideboard = True
        stripped_line = stripped_line.lstrip('SB:').strip()

    card_count, card_set, card_name = stripped_line.split(' ', 2)

    card_set = card_set.replace('[', '').replace(']', '')

    return sideboard, card_set, int(card_count), card_name


def get_card_data(card_set, card_name, sleep_time=0.1):
    card_name_attribute = quote(card_name)
    if card_set == '' or card_set is None:
        r = requests.get(
            f"https://api.scryfall.com/cards/named?fuzzy={card_name_attribute}"
        )
    else:
        r = requests.get(
            f"https://api.scryfall.com/cards/named?fuzzy={card_name_attribute}&set={card_set}"
        )
    sleep(sleep_time)
    return r.json()


def parse_card_type(type_line):
    if " — " in type_line:
        p = type_line.split(" — ")[0]
    else:
        p = type_line

    parts = p.split()

    return parts[-1].lower()


class MTGReader(BaseReader):
    enabled = True

    file_extensions = ['mwDeck']

    def __init__(self, settings):
        super(MTGReader, self).__init__(settings)

        self.cached_data = {}

        if os.path.exists(self.mtg_data_path):
            with open(self.mtg_data_path, 'r') as fin:
                self.cached_data = json.load(fin)

        Path(self.mtg_assets_cards_path(full=True)).mkdir(parents=True, exist_ok=True)

    @property
    def mtg_data_path(self):
        return os.path.join(
            self.settings.get("PATH"), self.settings.get("MTG_PATH"), "mtg.cached_cards.json"
        )

    def write_cache(self):
        with open(self.mtg_data_path, "w") as fout:
            json.dump(self.cached_data, fout, sort_keys=True, indent=4, separators=(",", ": "))

    def mtg_assets_cards_path(self, full=False):
        if full:
            return os.path.join(
                self.settings.get("PATH"), self.settings.get("MTG_ASSETS_PATH"), 'cards'
            )
        else:
            return os.path.join(
                self.settings.get("MTG_ASSETS_PATH"), 'cards'
            )

    def add_card_data(self, card_set, card_name):
        if card_set not in self.cached_data.keys():
            self.cached_data[card_set] = {}
        if card_name not in self.cached_data[card_set]:
            card_data = get_card_data(card_set, card_name)
            self.cached_data[card_set][card_name] = card_data
        else:
            card_data = self.cached_data[card_set][card_name]

        img_url = card_data["image_uris"]["border_crop"]
        local_path = get_local_card_img_path(self.mtg_assets_cards_path(full=False), img_url)
        self.cached_data[card_set][card_name]["image_path"] = local_path

        local_path_full = get_local_card_img_path(self.mtg_assets_cards_path(full=True), img_url)
        fetch_image(img_url, local_path_full)

    def read(self, filename):
        metadata = {'category': 'MTG_Deck',
                    'date': '2020-04-13',
                    'template': 'mtg_deck'
                    }

        deck_data = {
            'main': [],
            'sideboard': []
        }

        with open(filename, 'r') as fin:
            for line in fin:
                if line.startswith('//'):
                    tag, value = parse_meta(line)
                    metadata[tag.lower()] = value
                elif line.strip() != '':
                    sideboard, card_set, card_count, card_name = parse_card_line(line)
                    self.add_card_data(card_set, card_name)

                    card_data = {
                        'name': card_name,
                        'count': card_count,
                        'data': self.cached_data[card_set][card_name],
                        'card_type': parse_card_type(self.cached_data[card_set][card_name]['type_line'])
                    }

                    if sideboard:
                        deck_data['sideboard'].append(card_data)
                    else:
                        deck_data['main'].append(card_data)

        self.write_cache()

        metadata['title'] = metadata['name']
        metadata['slug'] = slugify(metadata['title'], regex_subs=self.settings.get('SLUG_REGEX_SUBSTITUTIONS', []))

        metadata['url'] = f"mtg/{metadata['format']}/{metadata['slug']}/"
        metadata['save_as'] = f"{metadata['url']}index.html"

        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        parsed['deck'] = deck_data

        return "", parsed


def add_reader(readers):
    readers.reader_classes['mwDeck'] = MTGReader


def register():
    signals.readers_init.connect(add_reader)
