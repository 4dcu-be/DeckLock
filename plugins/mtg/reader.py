from pelican import signals
from pelican.readers import BaseReader

import json
import os
import posixpath
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import quote
import requests
from time import sleep
from collections import defaultdict, Counter

from plugins.utils import fetch_image, get_last_modified
from pelican.utils import slugify

cmc_distribution_colors = {
    "B": ("rgba(186, 177, 171, 0.9)", "rgba(186, 177, 171, 1)"),
    "W": ("rgba(248, 246, 216, 0.9)", "rgba(248, 246, 216, 1)"),
    "G": ("rgba(163, 192, 149, 0.9)", "rgba(163, 192, 149, 1)"),
    "R": ("rgba(228, 153, 119, 0.9)", "rgba(228, 153, 119, 1)"),
    "U": ("rgba(193, 215, 233, 0.9)", "rgba(193, 215, 233, 1)"),
    "A": ("rgba(157, 134, 96, 0.9)", "rgba(157, 134, 96, 1)"),
    "M": ("rgba(194, 198, 107, 0.9)", "rgba(194, 198, 107, 1)"),
}


def get_local_card_img_path(assets_cards_path, url):
    img_filename = Path(urlparse(url).path).name
    return posixpath.join(assets_cards_path, img_filename)


def parse_meta(line):
    stripped_line = line.lstrip("//").strip()
    tag, value = [p.strip() for p in stripped_line.split(":")]

    return tag, value


def parse_card_line(line):
    sideboard = False

    stripped_line = line.strip()

    if stripped_line.startswith("SB:"):
        sideboard = True
        stripped_line = stripped_line.lstrip("SB:").strip()

    card_count, card_set, card_name = stripped_line.split(" ", 2)

    card_set = card_set.replace("[", "").replace("]", "")

    return sideboard, card_set, int(card_count), card_name


def get_card_data(card_set, card_name, sleep_time=0.1):
    card_name_attribute = quote(card_name)
    if card_set == "" or card_set is None:
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


def build_stacks(deck_data, stack_size=4):
    output_stacks = []
    current_stack = []
    for ix, card in enumerate(deck_data):
        for _ in range(card["count"]):
            current_stack.append(ix)
            if len(current_stack) == stack_size:
                output_stacks.append(current_stack.copy())
                current_stack = []
    output_stacks.append(current_stack.copy())
    return output_stacks


class MTGReader(BaseReader):
    enabled = True

    file_extensions = ["mwDeck"]

    def __init__(self, settings):
        super(MTGReader, self).__init__(settings)

        self.cached_data = {}

        if os.path.exists(self.mtg_data_path):
            with open(self.mtg_data_path, "r") as fin:
                self.cached_data = json.load(fin)

        Path(self.mtg_assets_cards_path(full=True)).mkdir(parents=True, exist_ok=True)

    @property
    def mtg_data_path(self):
        Path(self.settings.get("PATH"),
             self.settings.get("DECKLOCK_CACHE")).mkdir(parents=True, exist_ok=True)

        return posixpath.join(
            self.settings.get("PATH"),
            self.settings.get("DECKLOCK_CACHE"),
            "mtg.cached_cards.json",
        )

    def write_cache(self):
        with open(self.mtg_data_path, "w") as fout:
            json.dump(
                self.cached_data, fout, sort_keys=True, indent=4, separators=(",", ": ")
            )

    def mtg_assets_cards_path(self, full=False):
        if full:
            return posixpath.join(
                self.settings.get("PATH"), self.settings.get("MTG_ASSETS_PATH"), "cards"
            )
        else:
            return posixpath.join(self.settings.get("MTG_ASSETS_PATH"), "cards")

    def add_card_data(self, card_set, card_name):
        if card_set not in self.cached_data.keys():
            self.cached_data[card_set] = {}
        if card_name not in self.cached_data[card_set].keys():
            card_data = get_card_data(card_set, card_name)
            self.cached_data[card_set][card_name] = card_data
        else:
            card_data = self.cached_data[card_set][card_name]
        try:
            if "card_faces" in card_data.keys():
                card_data.update(card_data["card_faces"][0])

            img_url = card_data["image_uris"]["border_crop"]
            local_path = get_local_card_img_path(
                self.mtg_assets_cards_path(full=False), img_url
            )
            self.cached_data[card_set][card_name]["image_path"] = local_path

            local_path_full = get_local_card_img_path(
                self.mtg_assets_cards_path(full=True), img_url
            )
            if not self.settings.get("USE_EXTERNAL_LINKS", True):
                fetch_image(img_url, local_path_full)
        except:
            print(f"an error occurred fetching {card_name} from set {card_set}")

    def read(self, filename):
        metadata = {
            "category": "MTG_Deck",
            "date": get_last_modified(filename),
            "template": "mtg_deck",
        }

        deck_data = {"main": [], "sideboard": [], "colors": []}
        description = []

        cmc_per_color = defaultdict(list)

        with open(filename, "r") as fin:
            for line in fin:
                if line.startswith("//"):
                    tag, value = parse_meta(line)
                    metadata[tag.lower()] = value
                elif line.startswith("---"):
                    # This is the description, read until end of file
                    for dl in fin:
                        description.append(dl.strip())
                elif line.strip() != "":
                    sideboard, card_set, card_count, card_name = parse_card_line(line)
                    self.add_card_data(card_set, card_name)

                    card_data = {
                        "name": card_name,
                        "count": card_count,
                        "data": self.cached_data[card_set][card_name],
                        "card_type": parse_card_type(
                            self.cached_data[card_set][card_name]["type_line"]
                        ),
                    }

                    for color in self.cached_data[card_set][card_name]["colors"]:
                        if color not in deck_data["colors"]:
                            deck_data["colors"].append(color)

                    if sideboard:
                        deck_data["sideboard"].append(card_data)
                    else:
                        deck_data["main"].append(card_data)

                        if card_data["card_type"] != "land":
                            card_colors = self.cached_data[card_set][card_name][
                                "colors"
                            ]
                            num_colors = len(card_colors)
                            card_cmc = min(
                                11, int(self.cached_data[card_set][card_name]["cmc"])
                            )

                            if num_colors == 1:
                                cmc_per_color[card_colors[0]].extend(
                                    [card_cmc] * card_count
                                )
                            elif num_colors == 0:
                                # Artifact and devoid cards
                                cmc_per_color["A"].extend([card_cmc] * card_count)
                            else:
                                # Multicolor and hybrid cards
                                cmc_per_color["M"].extend([card_cmc] * card_count)

        cmc_distribution = {k: dict(Counter(v)) for k, v in cmc_per_color.items()}
        for k in cmc_distribution.keys():
            for i in range(0, 12):
                if i not in cmc_distribution[k].keys():
                    cmc_distribution[k][i] = 0

        deck_data["colors_string"] = "".join(
            ["{" + str(c).upper() + "}" for c in sorted(deck_data["colors"])]
        )
        deck_data["cmc_distribution"] = {
            k: [a[1] for a in sorted(v.items())] for k, v in cmc_distribution.items()
        }
        deck_data["cmc_distribution_colors"] = cmc_distribution_colors

        deck_data["main_stacks"] = build_stacks(deck_data["main"])
        deck_data["sideboard_stacks"] = build_stacks(deck_data["sideboard"])

        self.write_cache()

        print(f"Adding MTG {metadata['name']}")
        metadata["title"] = metadata["name"]
        metadata["slug"] = slugify(
            metadata["title"],
            regex_subs=self.settings.get("SLUG_REGEX_SUBSTITUTIONS", []),
        )

        metadata["description"] = "\n".join(description)

        metadata["url"] = f"mtg/{metadata['format']}/{metadata['slug']}/"
        metadata["save_as"] = f"{metadata['url']}index.html"

        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        parsed["deck"] = deck_data

        return "", parsed


def add_reader(readers):
    readers.reader_classes["mwDeck"] = MTGReader


def register():
    signals.readers_init.connect(add_reader)
