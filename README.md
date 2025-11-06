[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# DeckLock

Static web generator to generate an overview of all your favorite decks. DeckLock currently supports :

  * Flesh and Blood
  * KeyForge
  * Gwent
  * Magic: The Gathering
  

DeckLock is designed around the static website generator Pelican and leverages GitHub's feature to host static
websites from the ```gh-pages``` branch leveraging GitHub Actions for easy building your own version. For other hosting options,
check out the official Pelican documentation.

> **📖 Want to create your own fork?** Check out the [FORK_GUIDE.md](FORK_GUIDE.md) for a quick-start guide!

## Getting Started

### Option 1: Quick Start (Using Demo Content)

If you just want to try out DeckLock with the demo content:

```bash
git clone https://github.com/4dcu-be/DeckLock.git
cd DeckLock
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Option 2: Creating Your Own Fork (Recommended)

If you want to create your own deck collection website:

#### 1. Fork and Clone

1. **Fork this repository** on GitHub (click the "Fork" button)
2. **Clone your fork** to your local machine:

```bash
git clone https://github.com/YOUR-USERNAME/DeckLock.git
cd DeckLock
```

3. **Set up the upstream remote** (for syncing with updates):

```bash
git remote add upstream https://github.com/4dcu-be/DeckLock.git
git remote -v  # Verify you have both 'origin' (your fork) and 'upstream' (original repo)
```

#### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
```

#### 3. Create Your Custom Content Folder

To keep your content separate from demo content (making updates easier):

```bash
# Create your custom content folder
mkdir mycontent
cp -r content/data mycontent/
cp -r content/assets mycontent/
```

#### 4. Update Configuration Files

**Makefile** - Update the input directory (line 6):
```makefile
INPUTDIR=$(BASEDIR)/mycontent
```

**pelicanconf.py** - Update the content path and cache location (lines 24-25):
```python
PATH = "mycontent"
DECKLOCK_CACHE = "dl_cache"  # Use your own cache folder
```

**publishconf.py** - Update your site URL (line 15):
```python
SITEURL = "https://YOUR-USERNAME.github.io/DeckLock"
```

#### 5. Customize the Welcome Message

Edit **pelicanconf.py** (lines 64-71) to personalize your welcome message:

```python
WELCOME_MESSAGE = """
#### Welcome to My Deck Collection!

Your custom message here...
"""
```

#### 6. Add Your Deck Data

- Remove or replace the demo decks in `mycontent/data/`
- Add your own deck files following the format guides below

#### 7. Build and Test Locally

```bash
make html  # Build to _site folder for testing
make serve  # Start local server at http://localhost:8000
```

#### 8. Enable GitHub Pages

1. Build the production version:
   ```bash
   make github  # Builds and pushes to gh-pages branch
   ```

2. On GitHub, go to your repository **Settings → Pages**
3. Set **Source** to **gh-pages branch** and **/ (root)** folder
4. Click **Save**
5. Your site will be available at: `https://YOUR-USERNAME.github.io/DeckLock`

#### 9. Set Up GitHub Actions (Optional but Recommended)

The repository includes GitHub Actions that automatically build your site on every push.

**Important**: Add your Decks of KeyForge API key as a secret:
1. Go to your repository **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `DOK_API_KEY`
4. Value: Your API key from [Decks of KeyForge](https://decksofkeyforge.com/)

Now every push to your repository will automatically rebuild and deploy your site!

### Syncing with Upstream Updates

To pull in new features and improvements from the original repository:

```bash
# Fetch the latest changes from upstream
git fetch upstream

# Make sure you're on your main branch
git checkout main  # or master, depending on your default branch

# Rebase your changes on top of upstream
git rebase upstream/main  # or upstream/master

# If there are conflicts, resolve them, then continue:
# git add <resolved-files>
# git rebase --continue

# Force push to your fork (only safe if you're the only one using your fork)
git push origin main --force-with-lease
```

**Tips to minimize merge conflicts:**
- Keep all your custom content in `mycontent/` folder
- Only modify configuration files that need personalization
- Don't modify plugin code or core files unless necessary
- Regularly sync with upstream to avoid large divergences

**What to commit to your fork:**
- ✅ Your `mycontent/` folder (deck files and data)
- ✅ Your cache folder (e.g., `dl_cache/`) - speeds up CI builds
- ✅ Modified configuration files (Makefile, pelicanconf.py, publishconf.py)
- ❌ Downloaded images in `mycontent/assets/*` (gitignored - redownloaded automatically)
- ❌ Build output in `_site/` or `docs/` (gitignored)

## Configuration Reference

### Makefile Configuration

The pelican executable should be in venv/bin or venv/Scripts. The default should work:

```makefile
PELICAN?=pelican
```

If needed, update these paths:
```makefile
INPUTDIR=$(BASEDIR)/mycontent  # Your content folder
OUTPUTDIR=$(BASEDIR)/_site      # Test build output
DOCSDIR=$(BASEDIR)/docs         # Production build (for GitHub Pages via docs folder)
```

### Python Configuration Files

**pelicanconf.py** - Development settings:
```python
PATH = "mycontent"              # Your content folder
DECKLOCK_CACHE = "dl_cache"     # Your cache folder (avoids demo cache)
```

**publishconf.py** - Production settings:
```python
SITEURL = "https://YOUR-USERNAME.github.io/DeckLock"  # Your GitHub Pages URL
USE_EXTERNAL_LINKS = True       # Uses CDN links instead of local images
```

### Advanced: Hosting Images Locally

By default, production builds use external CDN links for card images (`USE_EXTERNAL_LINKS = True`), and local image downloads in `assets/` folders are gitignored. This keeps your repository small and avoids potential copyright issues.

However, you can choose to host images yourself for offline access or archival purposes.

#### ⚠️ Copyright Warning

**IMPORTANT**: Hosting card images may constitute copyright infringement. Card images are copyrighted by their respective publishers (Wizards of the Coast, Legend Story Studios, Fantasy Flight Games, CD Projekt Red). **Use at your own discretion and risk** for personal, non-commercial purposes only.

#### How to Enable Local Image Hosting

1. **Modify .gitignore** - Comment out or remove the lines that exclude your assets:
   ```bash
   # mycontent/assets/keyforge
   # mycontent/assets/mtg
   # mycontent/assets/gwent
   # mycontent/assets/fab
   ```

2. **Update publishconf.py**:
   ```python
   USE_EXTERNAL_LINKS = False
   STATIC_EXCLUDES = []  # Don't exclude assets from build
   ```

3. **Build, commit images, and deploy**:
   ```bash
   make html                  # Downloads images to mycontent/assets/
   git add mycontent/assets/  # Add images to git
   git commit -m "Add local card images"
   make github                # Deploy with local images
   ```

**Note**: This significantly increases repository size (potentially hundreds of MB).

## Adding Games

Before adding a game, make sure the correct plugins are active

```python
# Configure plugins
PLUGIN_PATHS = ["plugins"]
PLUGINS = ["keyforge", "mtg", "gwent", "fab", "webassets", "jinja_filters"]
```
The sections below show how to add decks for the various games.

### Flesh and Blood

To add a Flesh and Blood deck, put a text file with the .fab extension in the content folder. These files follow
a simple text format where cards that have only one pitch option don't need to include the color (this will be fixed
in later versions). The format is pretty self explanatory, see the example below.

```text
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

DeckLock supports two methods for GitHub Pages hosting:

### Method 1: Using gh-pages Branch (Recommended)

This is the easiest method with GitHub Actions:

1. Run `make github` to build and push to the gh-pages branch
2. Enable GitHub Pages from the **gh-pages branch** in your repository settings
3. GitHub Actions will automatically rebuild on every push (see `.github/workflows/autobuild.yml`)

### Method 2: Using docs/ Folder

Alternatively, you can use the docs folder:

1. Run `make release` to build the site to the `./docs` folder
2. Commit and push the `./docs` folder to your repository
3. In GitHub Settings → Pages, select the `main` branch and `/docs` folder
4. Your site will be hosted from the docs folder

**Note**: The gh-pages branch method is recommended as it keeps your source code separate from build artifacts.

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
