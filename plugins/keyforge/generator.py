import json
import os
from pathlib import Path
from urllib.parse import urlparse

from pelican import generators


def get_local_card_img_path(settings, url):
    img_filename = Path(urlparse(url).path).name
    return os.path.join(settings["KEYFORGE_ASSETS_PATH"], "cards", img_filename)


def get_local_house_img_path(settings, url):
    img_filename = Path(urlparse(url).path).name
    return os.path.join(settings["KEYFORGE_ASSETS_PATH"], "houses", img_filename)


class KeyForgeGenerator(generators.Generator):
    """ Generator Class to produce pages based on keyforge.cache.json """

    template_overview = "keyforge_overview.html"
    template_deck = "keyforge_deck.html"

    def __init__(self, context, settings, path, theme, output_path, **kwargs):

        self.keyforge_data_path = os.path.join(
            settings.get("PATH"), settings.get("KEYFORGE_PATH"), "keyforge.cache.json"
        )

        with open(self.keyforge_data_path) as fin:
            self.keyforge_data = json.load(fin)

        for k, v in self.keyforge_data.items():
            v["path"] = settings["KEYFORGE_DECK_SAVE_AS"].replace("{slug}", k)
            for card in v["vault_data"]["_linked"]["cards"]:

                card["count"] = v["vault_data"]["data"]["_links"]["cards"].count(
                    card["id"]
                )

                card["image_path"] = get_local_card_img_path(
                    settings, card["front_image"]
                )

            for house in v["vault_data"]["_linked"]["houses"]:
                house["image_path"] = get_local_house_img_path(settings, house["image"])

        super(KeyForgeGenerator, self).__init__(
            context, settings, path, theme, output_path, **kwargs
        )

    def generate_output(self, writer):
        self.generate_keyforge_overview_page(writer, self.keyforge_data)

        for k, v in self.keyforge_data.items():
            self.generate_keyforge_deck_page(writer, k, v)

    def generate_keyforge_deck_page(self, writer, deck_id, data):
        print(f"Generating KeyForge deck : {deck_id}")
        self.context["keyforge_data"] = data
        template = self.env.get_template(self.template_deck)
        rurls = self.settings["RELATIVE_URLS"]
        path = data["path"]
        writer.write_file(path, template, self.context, rurls, override_output=True)
        del self.context["keyforge_data"]

    def generate_keyforge_overview_page(self, writer, data):
        print(f"Generating KeyForge overview...", end='')
        self.context["keyforge_data"] = data
        template = self.env.get_template(self.template_overview)
        rurls = self.settings["RELATIVE_URLS"]
        path = self.settings["KEYFORGE_DECKS_SAVE_AS"]
        writer.write_file(path, template, self.context, rurls, override_output=True)
        del self.context["keyforge_data"]
        print(f"Done!")
