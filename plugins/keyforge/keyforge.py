import os
import json
import requests
from pelican import signals
from pathlib import Path
from urllib.parse import urlparse

from plugins.keyforge.generator import KeyForgeGenerator
from plugins.utils import fetch_image


def get_content_path(pelican):
    return pelican.settings.get("PATH")


def get_keyforge_data(pelican):
    keyforge_path = pelican.settings.get("KEYFORGE_PATH", None)

    if keyforge_path is None:
        return []

    content_path = get_content_path(pelican)

    input_path = os.path.join(content_path, keyforge_path, "keyforge.json")
    with open(input_path, "r") as fin:
        output = json.load(fin)

    return output


def get_keyforge_cache_path(pelican):
    cache_path = pelican.settings.get("DECKLOCK_CACHE", None)
    content_path = get_content_path(pelican)

    Path(content_path, cache_path).mkdir(parents=True, exist_ok=True)

    return os.path.join(content_path, cache_path, "keyforge.cache.json")


def get_dok_decks_cache_path(pelican):
    cache_path = pelican.settings.get("DECKLOCK_CACHE", None)
    content_path = get_content_path(pelican)

    Path(content_path, cache_path).mkdir(parents=True, exist_ok=True)

    return os.path.join(content_path, cache_path, "dok_decks.cache.json")


def get_keyforge_assets_paths(pelican):
    keyforge_assets_path = pelican.settings.get("KEYFORGE_ASSETS_PATH", None)
    content_path = get_content_path(pelican)

    keyforge_assets_house_image_directory = os.path.join(
        content_path, keyforge_assets_path, "houses"
    )
    keyforge_assets_card_image_directory = os.path.join(
        content_path, keyforge_assets_path, "cards"
    )

    Path(keyforge_assets_house_image_directory).mkdir(parents=True, exist_ok=True)
    Path(keyforge_assets_card_image_directory).mkdir(parents=True, exist_ok=True)

    return keyforge_assets_house_image_directory, keyforge_assets_card_image_directory


def get_dok_data(deck_id, api_key):
    if api_key is None:
        return {}

    api_headers = {"Api-Key": api_key}
    r = requests.get(
        f"https://decksofkeyforge.com/public-api/v3/decks/{deck_id}",
        headers=api_headers,
    )

    if r.status_code != 200:
        print(f"Warning: DoK API failed for deck {deck_id}: HTTP {r.status_code}")
        return {}

    return r.json()


def get_dok_deck_stats(api_key):
    if api_key is None:
        return {}

    api_headers = {"Api-Key": api_key}
    r = requests.get(
        "https://decksofkeyforge.com/public-api/v1/stats",
        headers=api_headers,
    )

    if r.status_code != 200:
        print(f"Warning: DoK stats API failed: HTTP {r.status_code}")
        return {}

    return r.json()


def get_vault_data(deck_id):
    r = requests.get(
        f"https://www.keyforgegame.com/api/decks/{deck_id}/?links=cards,notes"
    )

    return r.json()


def get_keyforge_assets(generator, decks_data):
    house_dir_path, card_img_dir_path = get_keyforge_assets_paths(generator)
    download_images = not generator.settings.get("USE_EXTERNAL_LINKS", True)

    for k, v in decks_data.items():
        cards = v["vault_data"]["_linked"]["cards"]

        for card in cards:
            img_url = card["front_image"]
            img_filename = Path(urlparse(img_url).path).name
            img_file_path = os.path.join(card_img_dir_path, img_filename)
            if download_images:
                fetch_image(img_url, img_file_path)

        houses = v["vault_data"]["_linked"]["houses"]
        for house in houses:
            img_url = house["image"]
            img_filename = Path(urlparse(img_url).path).name
            img_file_path = os.path.join(house_dir_path, img_filename)
            if download_images:
                fetch_image(img_url, img_file_path)


def parse_dok_stats(dok_data, dok_decks_data):
    """
    The data for a single deck, needs to be compared to summary statistics for all decks in DoK

    :param dok_data: the deck data
    :param dok_decks_data: summary statistics for all decks
    :return: dict with stats comparing the current deck to all decks in DoK
    """
    fields = [
        "expectedAmber",
        "creatureProtection",
        "amberControl",
        "artifactControl",
        "creatureControl",
        "effectivePower",
        "disruption",
        "efficiency",
        "recursion",
    ]

    output = {}

    for f in fields:
        try:
            output[f] = dok_decks_data[f + "Stats"]["percentileForValue"][
                str(round(dok_data["deck"].get(f, 0)))
            ]
        except (KeyError, ValueError, TypeError):
            output[f] = 0

    return output


def get_keyforge_external_data(generator):
    data = get_keyforge_data(generator)
    dok_api_key = generator.settings.get("DOK_API_KEY", None)

    keyforge_cache_path = get_keyforge_cache_path(generator)

    # To avoid hammering APIs relentlessly data is cached, if data is available, load here
    if os.path.exists(keyforge_cache_path):
        with open(keyforge_cache_path, "r") as fin:
            current_data = json.load(fin)
    else:
        current_data = {}

    dok_decks_cache_path = get_dok_decks_cache_path(generator)
    if os.path.exists(dok_decks_cache_path):
        with open(dok_decks_cache_path, "r") as fin:
            current_dok_deck_data = json.load(fin)
    else:
        current_dok_deck_data = get_dok_deck_stats(dok_api_key)
        with open(dok_decks_cache_path, "w") as fout:
            json.dump(
                current_dok_deck_data,
                fout,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
            )

    for deck in data:
        if deck["deck_id"] not in current_data.keys():
            print(f"Fetching data for KeyForge deck {deck['deck_id']}")
            dok_data = get_dok_data(deck["deck_id"], dok_api_key)
            vault_data = get_vault_data((deck["deck_id"]))

            current_data[deck["deck_id"]] = {
                "dok_data": dok_data if dok_data else {},
                "vault_data": vault_data,
            }

        # Add DoK Stats (percentiles) - only if we have dok_data
        if current_data[deck["deck_id"]]["dok_data"]:
            current_data[deck["deck_id"]]["dok_stats"] = parse_dok_stats(
                current_data[deck["deck_id"]]["dok_data"], current_dok_deck_data
            )
        else:
            current_data[deck["deck_id"]]["dok_stats"] = {}

        # update user data
        current_data[deck["deck_id"]]["user_data"] = deck
        current_data[deck["deck_id"]]["adventure_data"] = {
            "defeated_keyraken": deck.get("defeated_keyraken", False),
            "keyraken_difficulty": deck.get("keyraken_difficulty", False),
            "defeated_conspiracy": deck.get("defeated_conspiracy", False),
            "conspiracy_difficulty": deck.get("conspiracy_difficulty", False),
        }

    with open(keyforge_cache_path, "w") as fout:
        json.dump(current_data, fout, sort_keys=True, indent=4, separators=(",", ": "))

    # Get image data
    get_keyforge_assets(generator, current_data)

    generator.settings["KEYFORGE_DECK_COUNT"] = len(current_data.values())


def get_generators(generators):
    return KeyForgeGenerator


def register():
    """Register new functions"""
    signals.initialized.connect(get_keyforge_external_data)
    signals.get_generators.connect(get_generators)
