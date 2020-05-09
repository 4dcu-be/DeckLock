from pelican import signals
from pelican.readers import BaseReader

import json
import os
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from time import sleep
import posixpath
from plugins.utils import fetch_image
from pelican.utils import slugify


def get_local_card_img_path(assets_cards_path, url):
    img_filename = Path(urlparse(url).path).name
    return posixpath.join(assets_cards_path, img_filename)


def parse_meta(line):
    stripped_line = line.lstrip("//").strip()
    tag, value = [p.strip() for p in stripped_line.split(":")]

    return tag, value


def parse_card_line(line):
    card_count, card_name = line.strip().split(" ", 1)

    return int(card_count), card_name


def parse_card_data(card_data):
    print(card_data)
    soup = BeautifulSoup(card_data, 'html.parser')

    card_attributes = soup.find_all("div", class_="card-wrap card-data")[0]
    card_name = soup.find_all("div", class_="card-name")[0]
    card_category = soup.find_all("div", class_="card-category")[0]
    card_body_ability = soup.find_all("div", class_="card-body-ability")[0]

    image_url = 'https://gwent.one/image/card/medium/aid/jpg/%d.jpg' % int(card_attributes.get('data-artid').replace('j',''))

    output = {
        'name': card_name.text,
        'art_id': card_attributes.get('data-artid'),
        'power': card_attributes.get('data-power'),
        'armor': card_attributes.get('data-armor'),
        'provision': card_attributes.get('data-provision'),
        'faction': card_attributes.get('data-faction'),
        'color': card_attributes.get('data-color'),
        'type': card_attributes.get('data-type'),
        'rarity': card_attributes.get('data-rarity'),
        'category': card_category.text,
        'body_ability': card_body_ability.text,
        'image_url': image_url
    }

    return output


def get_card_data(card_name, card_version, sleep_time=0.1):
    print(card_name, card_version)

    gwent_one_endpoint = 'https://gwent.one/search/abilities'

    post_data = {
        'q': card_name,
        'version': card_version,
        'Token': 1,
        'view': 'sCard',
        'language': 'en'
    }

    r = requests.post(gwent_one_endpoint, data=post_data)

    sleep(sleep_time)

    return parse_card_data(r.text)


def parse_card_type(type_line):
    if " — " in type_line:
        p = type_line.split(" — ")[0]
    else:
        p = type_line

    parts = p.split()

    return parts[-1].lower()


class GwentReader(BaseReader):
    enabled = True

    file_extensions = ["gwent"]

    def __init__(self, settings):
        super(GwentReader, self).__init__(settings)

        self.cached_data = {}

        if os.path.exists(self.gwent_data_path):
            with open(self.gwent_data_path, "r") as fin:
                self.cached_data = json.load(fin)

        Path(self.gwent_assets_cards_path(full=True)).mkdir(parents=True, exist_ok=True)

    @property
    def gwent_data_path(self):
        return posixpath.join(
            self.settings.get("PATH"),
            self.settings.get("GWENT_PATH"),
            "gwent.cached_cards.json",
        )

    def write_cache(self):
        with open(self.gwent_data_path, "w") as fout:
            json.dump(
                self.cached_data, fout, sort_keys=True, indent=4, separators=(",", ": ")
            )

    def gwent_assets_cards_path(self, full=False):
        if full:
            return posixpath.join(
                self.settings.get("PATH"), self.settings.get("GWENT_ASSETS_PATH"), "cards"
            )
        else:
            return posixpath.join(self.settings.get("GWENT_ASSETS_PATH"), "cards")

    def add_card_data(self, card_name, card_version):
        print('add_card_data', card_name, card_version)
        if card_version not in self.cached_data.keys():
            self.cached_data[card_version] = {}
        if card_name not in self.cached_data[card_version].keys():
            card_data = get_card_data(card_name, card_version)
            self.cached_data[card_version][card_name] = card_data
        else:
            card_data = self.cached_data[card_version][card_name]
        try:
            img_url = card_data["image_url"]
            local_path = get_local_card_img_path(
                self.gwent_assets_cards_path(full=False), img_url
            )
            self.cached_data[card_version][card_name]["image_path"] = local_path

            local_path_full = get_local_card_img_path(
                self.gwent_assets_cards_path(full=True), img_url
            )
            fetch_image(img_url, local_path_full)
        except Exception as e:
            print(f"an error occurred fetching {card_name} from version {card_version}")
            print(e)

    def read(self, filename):
        metadata = {
            "category": "Gwent_Deck",
            "date": "2020-04-13",
            "template": "gwent_deck",
        }

        deck_data = []

        with open(filename, "r") as fin:
            for line in fin:
                if line.startswith("//"):
                    tag, value = parse_meta(line)
                    metadata[tag.lower()] = value
                elif line.strip() != "":
                    card_count, card_name = parse_card_line(line)
                    card_version = metadata["gwent_version"]
                    self.add_card_data(card_name, card_version)

                    card_data = {
                        "name": card_name,
                        "count": card_count,
                        "data": self.cached_data[card_version][card_name],
                    }

                    deck_data.append(card_data)

        self.write_cache()

        metadata["title"] = metadata["name"]
        metadata["slug"] = slugify(
            metadata["title"],
            regex_subs=self.settings.get("SLUG_REGEX_SUBSTITUTIONS", []),
        )

        metadata["url"] = f"gwent/{metadata['gwent_version']}/{metadata['slug']}/"
        metadata["save_as"] = f"{metadata['url']}index.html"

        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        parsed["deck"] = deck_data

        return "", parsed


def add_reader(readers):
    readers.reader_classes["gwent"] = GwentReader


def register():
    signals.readers_init.connect(add_reader)
