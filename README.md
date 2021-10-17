[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# DeckLock

Static web generator to generate an overview of all your favorite decks. DeckLock currently supports :

  * Flesh and Blood
  * KeyForge
  * Gwent
  * Magic: The Gathering
  

DeckLock is designed around the static website generator Pelican and leverages GitHub's feature to host static 
websites from the ./docs folder. For other hosting options, check out the official Pelican documentation.

## Getting started

First fork this repository to create your own copy on GitHub. Next, use the commands below to clone your own repository, create a virtual environment and install all
required packages.

```bash
git clone <url to your fork of DeckLock> ./DeckLock
cd DeckLock
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On windows the line to activate the virtual environment (source venv/bin/activate) will not work, use the line below 
instead.

```bash
venv\Scripts\activate.bat
```

## Setting up DeckLock

### Configuring the Makefile

The pelican executable should be in venv/bin or venv/Scripts. Depending on how you've set up things the default (below) should work, or you might have to specify the full path.

```makefile
PELICAN?=pelican
```

### pelicanconf.py and publishconf.py

pelicanconf.py requires you to specify where the cache and content is stored. You should only change the cache folder
to something else (e.g. dl_cache)

```python
DECKLOCK_CACHE = "dl_demo_cache"
```

In publishconf.py however you will need to specify the final url of your site.

```python
SITEURL = "https://4dcu.be/DeckLock"
```
## Adding Games

Before adding a game, make sure the correct plugins are active

```python
# Configure plugins
PLUGIN_PATHS = ["plugins"]
PLUGINS = ["keyforge", "mtg", "gwent", "fab", "webassets", "jinja_filters"]
```
The sections below show how to add decks for the various games.

### Flesh and Blood

To add a Flesh and Blood deck, put a text file with the .fab extension in the content folder. These file are in
the same format as [fabdb.net](https://fabdb.net/), though cards that have only one pitch option don't need to include
the color (this will be fixed in later versions). The easiest way to get the list in the correct is to add it on fabdb,
copy it to the clipboard and paste it into a .fab file. The format is pretty self explanatory even if you don't want to 
generate it through fabdb.

```text
Deck build - via https://fabdb.net :

Prism Blitz Precon

Class: Illusionist
Hero: Prism
Weapons: Iris of Reality
Equipment: Dream Weavers, Halo of Illumination, Heartened Cross Strap, Spell Fray Leggings

(2) Herald of Protection (red)
(2) Herald of Ravages (red)
(2) Herald of Rebirth (red)
(2) Herald of Tenacity (red)
(2) Illuminate (red)
(1) Phantasmify (red)
(1) Prismatic Shield (red)
(2) Seek Enlightenment (red)
(2) Wartune Herald (red)
(2) Enigma Chimera (yellow)
(1) Herald of Judgment
(1) Merciful Retribution
(1) Ode to Wrath
(2) Rising Solartide (yellow)
(2) Enigma Chimera (blue)
(2) Herald of Protection (blue)
(2) Herald of Ravages (blue)
(2) Herald of Rebirth (blue)
(2) Herald of Tenacity (blue)
(2) Illuminate (blue)
(2) Spears of Surreality (blue)
(2) Wartune Herald (blue)
(1) The Librarian

See the full deck at: https://fabdb.net/decks/GkNKXvRA/
```

### Gwent

To add a Gwent Deck, put a text file with a .gwent extension in the content folder.
The file needs to be structured as shown below, the first sections indicate the name
of the deck, the creator and the Gwent version. Below that there should be a list
of cards preceded by the number of copies of that card.

```text
// NAME : Harmony (alt)
// CREATOR : BUSHr
// GWENT_VERSION : 6.2.0
// FACTION : Scoia'tael
1 Mystic Echo
1 Tactical Advantage
1 The Great Oak
1 Water of Brokilon
1 Call of the Forest
1 Barnabas Beckenbauer
1 Figgis Merluzzo
1 Pavko Gale
1 Toruviel
1 Fauve
1 Treant Boar
1 Weeping Willow
1 Hawker Smuggler
1 Nature's Rebuke
2 Forest Whisperer
2 Dryad Ranger
1 Dwarven Chariot
2 Trained Hawk
1 Dwarven Skirmisher
2 Dol Blathanna Bowman
1 Miner
2 Mahakam Marauder
```

### Decks of KeyForge API Key

If you want to include deck statistics from [Decks of KeyForge] you'll have to create an account and get an API key from
[https://decksofkeyforge.com/](https://decksofkeyforge.com/). Create a file *.env* in the and add the line below.

A .env file, which will not be committed, is used to keep your api key secret. 

```text
DOK_API_KEY=your_api_key
```

### KeyForge Deck IDs

Next, you'll have to specify where the KeyForge data can be found (folder), in pelicanconf.py. Note that this path is
relative to the content folder

```python
KEYFORGE_PATH = "./data"
```

Now, add a keyforge.json file to ./content/data, structured as followed with the identifiers of the decks to include.
A file with the KeyForge Decks I own is included as an example, the structure should be a shown below. Optionally,
you can include details if you tackled one of the KeyForge Adventures with the deck. Difficulties are "Easy", "Normal"
and "Hard", which is the number of cards the Keyraken or the Conspiracy draw and play each turn (resp. 1, 2 and 3)

```json
[
  {
    "deck_id" : "a4268ae8-a9f6-48c7-9739-b28a3553b108",
    "defeated_keyraken": true,
    "keyraken_difficulty": "Normal",
    "defeated_conspiracy": false,
    "conspiracy_difficulty": "Easy"
  }, {
    "deck_id" : "bfbf6786-218c-4320-a7b1-7ed4d6eddc69"
  }
]
```

### Magic: the Gathering

Magic: the Gathering decks can be added by including a mwDeck file for each deck in the content/data/mtg_decks folder. 
The mwDeck file format is rather self-explanatory, see the example below:

```text
// NAME : 9 Land Stompy
// CREATOR : Sebastian Proost
// FORMAT : Casual
9 [USG] Forest
4 [MMQ] Land Grant
4 [ALL] Elvish Spirit Guide
3 [MMQ] Vine Dryad
4 [EXO] Skyshroud Elite
4 [VIS] Quirion Ranger
2 [VIS] River Boa
4 [DKA] Strangleroot Geist
4 [ALL] Bounty of the Hunt
4 [WTH] Rogue Elephant
4 [RTR] Dryad Militant
4 [WTH] Briar Shield
4 [ULG] Rancor
4 [POR] Jungle Lion
1 [2ED] Winter Orb
1 [5ED] Winter Orb
SB:  2 [TMP] Root Maze
SB:  4 [ULG] Hidden Gibbons
SB:  3 [ONS] Naturalize
SB:  2 [MMQ] Rushwood Legate
SB:  3 [UDS] Compost
```

Do make sure that the set, included here in between square brackets, matches ScryFall's abbreviations.

## Building platform

You can use make to build the website (if make is available on your system), use ```make html``` to create a local instance
to test in the ```_site``` directory. Use ```make release``` to create the version for publication in the ```./docs``` folder.

If you are on windows, you'll have to install **make** before these commands will work. You can find it [here](http://gnuwin32.sourceforge.net/packages/make.htm), and you need
to [add the location of make.exe to your PATH](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/). 

```commandline
make html

make release
```

alternatively you can use pelican directly, the content is in the folder ```./content``` and the output folder should be set 
to ```./_site``` for a local test build. Write the output to the ```./docs``` folder with the publication settings so this can be
hosted easily on GitHub.

```commandline
pelican ./content -o ./_site

pelican ./content -o ./docs -s publishconf.py
```

## Hosting locally for testing

You can use Pelican's built in webserver using the command below.

```commandline
make serve
```

Or you can build the site using ```make html```, navigate to the ```_site``` folder and start a webserver
by running the command.

```commandline
python -m http.server
```

In both cases you can see your site by pointing your browser to [http://localhost:8000](http://localhost:8000).

## Hosting on GitHub

DeckLock includes a *make release* command which will write the final version of the website to the *./docs* folder. 
On GitHub, you can specify that this folder is used for the project pages, enable this in the settings, and you'll have
free hosting to show off the decks you have in your card game collection.

## Acknowledgements

Some icons and glyphs used require attribution:

  * Trophy by i cons from the Noun Project
  * Kraken by Pau Urquijo from the Noun Project
  * Diving helmet by Geordie Kaytes from the Noun Project

## Legal

Decklock is unofficial Fan Content. The literal and graphical information presented in this project about Flesh and Blood, Gwent, KeyForge and 
Magic: The Gathering, are copyright of Legend Story Studios, CDPR, Fantasy Flight Games and Wizards of the Coast, LLC, a subsidiary of Hasbro, 
Inc. respectively. DeckLock and 4DCu.be are not produced by, endorsed by, supported by, or affiliated with any of these
entities.

[Decks of KeyForge]: https://decksofkeyforge.com/
