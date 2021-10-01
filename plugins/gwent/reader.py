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
from plugins.utils import fetch_image, get_last_modified
from pelican.utils import slugify
from itertools import accumulate


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


def parse_card_data(card_data, card_name):
    soup = BeautifulSoup(card_data, "html.parser")

    index = -1
    results = []

    # In case there are multiple results find exact match
    for ix, result in enumerate(soup.find_all("div", class_="card-name")):
        results.append(result)
        # This character is a problem with utf-8 encoding
        # TODO: Work out a better solution or encoding to avoid this
        if card_name.lower() == str(result.text.replace("É", "E")).lower():
            index = ix

    if index < 0:
        print(f"ERROR: {card_name} not found in {results}!")
        quit()

    card_attributes = soup.find_all("div", class_="card-wrap card-data")[index]
    card_name = soup.find_all("div", class_="card-name")[index]
    card_category = soup.find_all("div", class_="card-category")[index]
    card_body_ability = soup.find_all("div", class_="card-body-ability")[index]

    image_url = "https://gwent.one/image/gwent/assets/card/art/medium/%d.jpg" % int(
        card_attributes.get("data-artid").replace("j", "")
    )

    output = {
        "name": card_name.text,
        "art_id": card_attributes.get("data-artid"),
        "power": card_attributes.get("data-power"),
        "armor": card_attributes.get("data-armor"),
        "provision": int(card_attributes.get("data-provision")),
        "faction": card_attributes.get("data-faction"),
        "color": card_attributes.get("data-color"),
        "type": card_attributes.get("data-type"),
        "rarity": card_attributes.get("data-rarity"),
        "category": card_category.text,
        "body_ability": card_body_ability.text,
        "body_ability_html": str(card_body_ability),
        "image_url": image_url,
    }

    return output


def get_card_data(card_name, card_version, sleep_time=0.1):
    gwent_one_endpoint = "https://gwent.one/search/abilities"

    post_data = {
        "q": card_name,
        "version": card_version,
        "Token": 1,
        "view": "sCard",
        "language": "en",
    }

    r = requests.post(gwent_one_endpoint, data=post_data)

    sleep(sleep_time)

    return parse_card_data(r.text, card_name)


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
            self.settings.get("DECKLOCK_CACHE"),
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
                self.settings.get("PATH"),
                self.settings.get("GWENT_ASSETS_PATH"),
                "cards",
            )
        else:
            return posixpath.join(self.settings.get("GWENT_ASSETS_PATH"), "cards")

    def add_card_data(self, card_name, card_version):
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
            if not self.settings.get("USE_EXTERNAL_LINKS"):
                fetch_image(img_url, local_path_full)
        except Exception as e:
            print(f"an error occurred fetching {card_name} from version {card_version}")
            print(e)

    def read(self, filename):
        metadata = {
            "category": "Gwent_Deck",
            "date": get_last_modified(filename),
            "template": "gwent_deck",
        }

        deck_data = []
        description = []
        leader = None
        stratagem = None

        with open(filename, "r", encoding="utf-8") as fin:
            for line in fin:
                if line.startswith("//"):
                    tag, value = parse_meta(line)
                    metadata[tag.lower()] = value
                elif line.startswith("---"):
                    # This is the description, read until end of file
                    for dl in fin:
                        description.append(dl.strip())
                elif line.strip() != "":
                    card_count, card_name = parse_card_line(line)
                    card_version = metadata["gwent_version"]
                    self.add_card_data(card_name, card_version)

                    card_data = {
                        "name": card_name,
                        "count": card_count,
                        "data": self.cached_data[card_version][card_name],
                    }

                    if (
                        self.cached_data[card_version][card_name]["category"]
                        == "Leader"
                    ):
                        leader = card_data
                    elif (
                        self.cached_data[card_version][card_name]["type"] == "stratagem"
                    ):
                        stratagem = card_data
                    else:
                        deck_data.append(card_data)

        self.write_cache()

        print(
            f"Adding Gwent {metadata['name']} (Gwent version {metadata['gwent_version']})"
        )

        metadata["title"] = metadata["name"]
        metadata["slug"] = slugify(
            metadata["title"] + "_" + metadata["gwent_version"],
            regex_subs=self.settings.get("SLUG_REGEX_SUBSTITUTIONS", []),
        )
        metadata["description"] = "\n".join(description)
        metadata["url"] = f"gwent/{metadata['gwent_version']}/{metadata['slug']}/"
        metadata["save_as"] = f"{metadata['url']}index.html"

        parsed = {
            "provisions": 0,
            "units": 0,
            "scraps": 0,
            "cards": sum([c["count"] for c in deck_data]),
        }

        for card in deck_data + [stratagem]:
            parsed["provisions"] += card["data"]["provision"] * card["count"]
            if card["data"]["type"] == "unit":
                parsed["units"] += card["count"]
            if card["data"]["rarity"] == "legendary":
                parsed["scraps"] += 800 * card["count"]
            elif card["data"]["rarity"] == "epic":
                parsed["scraps"] += 200 * card["count"]
            elif card["data"]["rarity"] == "rare":
                parsed["scraps"] += 80 * card["count"]
            else:
                parsed["scraps"] += 30 * card["count"]

        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        parsed["deck"] = deck_data
        parsed["leader"] = leader
        parsed["stratagem"] = stratagem

        parsed["stats"] = {
            "provisions": [],
            "cumulative_provisions": [],
            "card_colors": [],
            "labels": [],
        }

        for card in sorted(deck_data, key=lambda x: x["data"]["provision"]):
            for _ in range(card["count"]):
                parsed["stats"]["provisions"].append(int(card["data"]["provision"]))
                parsed["stats"]["card_colors"].append(card["data"]["color"])
                parsed["stats"]["labels"].append(card["data"]["name"])

        parsed["stats"]["cumulative_provisions"] = list(
            accumulate(parsed["stats"]["provisions"])
        )

        return "", parsed


def add_reader(readers):
    readers.reader_classes["gwent"] = GwentReader


def register():
    signals.readers_init.connect(add_reader)
