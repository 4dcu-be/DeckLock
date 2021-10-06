from pelican import signals
from pelican.readers import BaseReader

import json
import os
import posixpath
import re
from pathlib import Path
from urllib.parse import urlparse
import requests
from time import sleep

from plugins.utils import fetch_image, get_last_modified
from pelican.utils import slugify


def get_local_card_img_path(assets_cards_path, url):
    img_filename = Path(urlparse(url).path).name
    return posixpath.join(assets_cards_path, img_filename)


def name_to_url(card_name):
    output = card_name.lower().replace(" (undefined)", "")
    output = re.sub(r"[^a-z ]", "", output).replace(" ", "-")

    return output


def get_card_data(card_name, sleep_time=0.1):
    card_name_attribute = name_to_url(card_name)

    r = requests.get(f"https://fabdb.net/api/cards/{card_name_attribute}")

    sleep(sleep_time)

    print(r.text)

    return r.json()


def load_decklist(filename):
    output = {
        "title": "Unnamed Deck",
        "class": "",
        "hero": "",
        "weapons": [],
        "equipment": [],
        "cards": [],
        "url": None,
    }

    with open(filename) as fin:
        lines = [line.strip() for line in fin.readlines()]

    for line in lines:
        if line.startswith("Deck build") or line == "":
            continue
        elif line.startswith("("):
            count_str, card = line.split(" ", 1)
            output["cards"].append(
                (int(count_str.replace("(", "").replace(")", "")), card)
            )
        elif line.startswith("Class: "):
            output["class"] = line.replace("Class: ", "")
        elif line.startswith("Hero: "):
            output["hero"] = line.replace("Hero: ", "")
        elif line.startswith("Weapons: "):
            output["weapons"] = [
                w.strip() for w in line.replace("Weapons: ", "").split(",")
            ]
        elif line.startswith("Equipment: "):
            output["equipment"] = [
                w.strip() for w in line.replace("Equipment: ", "").split(",")
            ]
        elif line.startswith("See the full deck"):
            output["url"] = line.replace("See the full deck at: ", "")
        else:
            output["title"] = line

    return output


def build_stacks(deck_data, stack_size=4):
    output_stacks = []
    current_stack = []

    for ix, card in enumerate(deck_data["cards"]):
        for _ in range(card["count"]):
            current_stack.append(ix)
            if len(current_stack) == stack_size:
                output_stacks.append(current_stack.copy())
                current_stack = []

    output_stacks.append(current_stack.copy())
    return output_stacks


class FaBReader(BaseReader):
    enabled = True

    file_extensions = ["fab"]

    def __init__(self, settings):
        super(FaBReader, self).__init__(settings)

        self.cached_data = {}

        if os.path.exists(self.fab_data_path):
            with open(self.fab_data_path, "r") as fin:
                self.cached_data = json.load(fin)

        Path(self.fab_assets_cards_path(full=True)).mkdir(parents=True, exist_ok=True)

    @property
    def fab_data_path(self):
        Path(self.settings.get("PATH"),
             self.settings.get("DECKLOCK_CACHE")).mkdir(parents=True, exist_ok=True)

        return posixpath.join(
            self.settings.get("PATH"),
            self.settings.get("DECKLOCK_CACHE"),
            "fab.cached_cards.json",
        )

    def write_cache(self):
        with open(self.fab_data_path, "w") as fout:
            json.dump(
                self.cached_data, fout, sort_keys=True, indent=4, separators=(",", ": ")
            )

    def fab_assets_cards_path(self, full=False):
        if full:
            return posixpath.join(
                self.settings.get("PATH"), self.settings.get("FAB_ASSETS_PATH"), "cards"
            )
        else:
            return posixpath.join(self.settings.get("FAB_ASSETS_PATH"), "cards")

    def add_card_data(self, card_name):
        try:
            if card_name not in self.cached_data.keys():
                card_data = get_card_data(card_name)
                self.cached_data[card_name] = card_data
            else:
                card_data = self.cached_data[card_name]

            img_url = card_data["image"]
            local_path = get_local_card_img_path(
                self.fab_assets_cards_path(full=False), img_url
            )
            self.cached_data[card_name]["image_path"] = local_path

            local_path_full = get_local_card_img_path(
                self.fab_assets_cards_path(full=True), img_url
            )
            if not self.settings.get("USE_EXTERNAL_LINKS", True):
                fetch_image(img_url, local_path_full)
        except Exception as e:
            print(f"an error occurred fetching {card_name}")
            print(e)

    def add_decklist(self, decklist: dict):
        if "hero" in decklist.keys():
            self.add_card_data(decklist["hero"])
        if "weapons" in decklist.keys():
            for weapon in decklist["weapons"]:
                self.add_card_data(weapon)
        if "equipment" in decklist.keys():
            for equipment in decklist["equipment"]:
                self.add_card_data(equipment)
        if "cards" in decklist.keys():
            for _, card in decklist["cards"]:
                self.add_card_data(card)

        self.write_cache()

    def parse_decklist(self, decklist):
        parsed_cards = []

        total_count = 0

        pitch_to_color = {"1": "red", "2": "yellow", "3": "blue"}

        for count, card in decklist["cards"]:
            parsed_card = self.cached_data[card]
            parsed_card["count"] = count
            total_count += count

            if "resource" in parsed_card.get("stats", {}):
                parsed_card["color"] = pitch_to_color[parsed_card["stats"]["resource"]]

            parsed_cards.append(parsed_card)

        return {
            "name": decklist["title"],
            "hero": self.cached_data[decklist["hero"]],
            "weapons": [self.cached_data[w] for w in decklist["weapons"]],
            "equipment": [self.cached_data[e] for e in decklist["equipment"]],
            "cards": parsed_cards,
            "format": "Blitz" if total_count == 40 else "Classic Constructed",
            "fabdb_url": decklist["url"],
        }

    def read(self, filename):
        decklist = load_decklist(filename)
        self.add_decklist(decklist)

        deck_data = self.parse_decklist(decklist)
        deck_data["stacks"] = build_stacks(deck_data)

        print(f"Adding FaB {deck_data['name']}")
        deck_data["title"] = deck_data["name"]
        deck_data["slug"] = slugify(
            deck_data["title"],
            regex_subs=self.settings.get("SLUG_REGEX_SUBSTITUTIONS", []),
        )

        deck_data["url"] = f"fab/{deck_data['slug']}/"
        deck_data["save_as"] = f"{deck_data['url']}index.html"
        deck_data["category"] = "FaB_Deck"
        deck_data["date"] = get_last_modified(filename)
        deck_data["template"] = "fab_deck"

        for key, value in deck_data.items():
            deck_data[key] = self.process_metadata(key, value)

        return "", deck_data


def add_reader(readers):
    readers.reader_classes["fab"] = FaBReader


def register():
    signals.readers_init.connect(add_reader)
