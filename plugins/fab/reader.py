from pelican import signals
from pelican.readers import BaseReader

import json
import os
import posixpath
import re
from pathlib import Path
from urllib.parse import urlparse
import requests

from plugins.utils import fetch_image, get_last_modified
from pelican.utils import slugify


class FABCardDatabase:
    """Card database manager for the-fab-cube API"""

    def __init__(self, cache_path):
        self.base_url = (
            "https://the-fab-cube.github.io/flesh-and-blood-cards/json/english"
        )
        self.cache_path = cache_path
        self.cards = None
        self.cards_by_name = {}

    def load_cards(self):
        """Load card data from cache or download from API"""
        if self.cards is not None:
            return

        # Try loading from cache first
        if os.path.exists(self.cache_path):
            print(f"Loading FAB card database from cache: {self.cache_path}")
            with open(self.cache_path, "r") as fin:
                self.cards = json.load(fin)
        else:
            # Download from API
            print(f"Downloading FAB card database from {self.base_url}/card.json")
            response = requests.get(f"{self.base_url}/card.json")
            response.raise_for_status()
            self.cards = response.json()

            # Save to cache
            Path(self.cache_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "w") as fout:
                json.dump(self.cards, fout, indent=2)
            print(f"Cached {len(self.cards)} cards to {self.cache_path}")

        # Build lookup index by normalized name
        self._build_name_index()

    def _build_name_index(self):
        """Build name-based lookup index for quick searches"""
        self.cards_by_name = {}
        for card in self.cards:
            name_key = self._normalize_card_name(card["name"])
            # Store as list to handle multiple cards with same normalized name
            if name_key not in self.cards_by_name:
                self.cards_by_name[name_key] = []
            self.cards_by_name[name_key].append(card)

    def _normalize_card_name(self, name):
        """Convert card name to lookup key format"""
        return name.lower().strip()

    def get_card(self, card_name_with_color):
        """
        Get card by name with color suffix.
        Handles format: "Card Name (red)", "Card Name (blue)", "Card Name (yellow)"
        Also handles cards without color suffix.
        """
        if not self.cards:
            self.load_cards()

        # Parse card name and color from input
        card_name = card_name_with_color.strip()
        requested_color = None

        # Extract color from parentheses
        color_match = re.search(r"\((\w+)\)$", card_name)
        if color_match:
            requested_color = color_match.group(1).lower()
            card_name = card_name[: color_match.start()].strip()

        # Normalize the base card name for lookup
        normalized = self._normalize_card_name(card_name)

        # Find matching cards
        candidate_cards = self.cards_by_name.get(normalized, [])

        if not candidate_cards:
            print(f"Warning: Card '{card_name_with_color}' not found in database")
            return None

        # If color was specified, find the card with matching pitch value
        if requested_color:
            pitch_map = {"red": "1", "yellow": "2", "blue": "3"}
            target_pitch = pitch_map.get(requested_color)

            for card in candidate_cards:
                card_pitch = str(card.get("pitch", ""))
                if card_pitch == target_pitch:
                    return card

            print(
                f"Warning: Card '{card_name}' found but no {requested_color} variant (pitch {target_pitch})"
            )
            # Return first match as fallback
            if candidate_cards:
                return candidate_cards[0]
            return None

        # No color specified, return first match
        return candidate_cards[0]

    def convert_to_fabdb_format(self, card):
        """
        Convert the-fab-cube card format to fabdb.net-compatible format
        for backward compatibility with existing templates.
        """
        if card is None:
            return None

        # Map pitch value to color
        pitch_to_color = {"1": "red", "2": "yellow", "3": "blue"}
        pitch = card.get("pitch", "")

        # Get image URL from printings (use last printing, not first)
        image_url = None
        printings = card.get("printings", [])
        if printings:
            image_url = printings[-1].get("image_url")

        # Build fabdb-compatible structure
        return {
            "name": card.get("name"),
            "pitch": pitch,
            "color": pitch_to_color.get(pitch),
            "image": image_url,
            "stats": {
                "resource": pitch,  # Map pitch to resource for template compatibility
                "cost": card.get("cost"),
                "attack": card.get("power"),  # Map power to attack
                "defense": card.get("defense"),
                "health": card.get("health"),
                "intelligence": card.get("intelligence"),
            },
            "keywords": card.get("types", []),
            "card_keywords": card.get("card_keywords", []),
            "functional_text": card.get("functional_text", ""),
            "type_text": card.get("type_text", ""),
            "blitz_legal": card.get("blitz_legal", False),
            "cc_legal": card.get("cc_legal", False),
        }


def get_local_card_img_path(assets_cards_path, url):
    if not url:
        return None
    img_filename = Path(urlparse(url).path).name
    return posixpath.join(assets_cards_path, img_filename)


def load_decklist(filename):
    output = {
        "title": "Unnamed Deck",
        "class": "",
        "hero": "",
        "weapons": [],
        "equipment": [],
        "cards": [],
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

        # Initialize card database with cache path
        db_cache_path = posixpath.join(
            self.settings.get("PATH"),
            self.settings.get("DECKLOCK_CACHE"),
            "fab.card_database.json",
        )
        self.card_db = FABCardDatabase(db_cache_path)

        # Load legacy cached data if exists
        if os.path.exists(self.fab_data_path):
            with open(self.fab_data_path, "r") as fin:
                self.cached_data = json.load(fin)

        Path(self.fab_assets_cards_path(full=True)).mkdir(parents=True, exist_ok=True)

    @property
    def fab_data_path(self):
        Path(self.settings.get("PATH"), self.settings.get("DECKLOCK_CACHE")).mkdir(
            parents=True, exist_ok=True
        )

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
                # Fetch card from database and convert to fabdb format
                raw_card = self.card_db.get_card(card_name)
                card_data = self.card_db.convert_to_fabdb_format(raw_card)

                if card_data is None:
                    print(f"Error: Could not find card '{card_name}' in database")
                    return

                self.cached_data[card_name] = card_data
            else:
                card_data = self.cached_data[card_name]

            img_url = card_data.get("image")
            if img_url:
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

            # Only set color if resource/pitch value exists and is not empty
            resource = parsed_card.get("stats", {}).get("resource", "")
            if resource and str(resource) in pitch_to_color:
                parsed_card["color"] = pitch_to_color[str(resource)]

            parsed_cards.append(parsed_card)

        return {
            "name": decklist["title"],
            "hero": self.cached_data[decklist["hero"]],
            "weapons": [self.cached_data[w] for w in decklist["weapons"]],
            "equipment": [self.cached_data[e] for e in decklist["equipment"]],
            "cards": parsed_cards,
            "format": "Blitz" if total_count == 40 else "Classic Constructed",
            "class": decklist["class"]
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
