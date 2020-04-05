[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# DeckLock

Static web generator to generate an overview of all your favorite decks. Currently supports :

  * KeyForge

DeckLock is designed around the the static website generator Pelican and leverages GitHub's feature to host static 
websites from the ./docs folder. For other hosting options, check out the official Pelican documentation.

## Setup your own DeckLock

### Get the code and setup the virtual environment

It is recommended to create a personal fork of the DeckLock repository and clone this fork. This will allow you to 
leverage GitHub's feature to host static pages from the ./docs folder.

```bash
git clone <link to your DeckLock fork>
cd DeckLock

python -m venv venv
source venv/bin/activate
pip install -r requirements
```

### Configuration

Before starting anything, have a look at the *Makefile*, and set the path to Pelican here. If you have a system wide
install set *PELICAN?=pelican*

```text
PELICAN?=pelican
```

If you are using the virtual environment the path should be set to pelican in the virtual environment. On Windows this
is in the Scripts folder under Linux/OSX in the bin folder of the virtual environment directory.

```text
PELICAN?=d:\Git\DeckLock\venv\Scripts\pelican
```

#### KeyForge

If you want to include deck statistics from [Deck of KeyForge] you'll have to create an account and get an API key from
[https://decksofkeyforge.com/](https://decksofkeyforge.com/). Create a file *.env* in the and add the line below.

A .env file, which will not be committed, is used to keep your api key secret. 

```text
DOK_API_KEY=your_api_key
```

Next, you'll have to specify where the KeyForge data can be found (folder), in pelicanconf.py. Note that this path is
relative to the content folder

```python
KEYFORGE_PATH = "./data"
```

Now, add a keyforge.json file to ./content/data, structured as followed with the identifiers of the decks to include.
A file with the KeyForge Decks I own is included as an example, the structure should be a shown below.

```json
[
  {
    "deck_id" : "a4268ae8-a9f6-48c7-9739-b28a3553b108"
  }, {
    "deck_id" : "bfbf6786-218c-4320-a7b1-7ed4d6eddc69"
  }
]
```

If you want to publish the website, specify the website's url in *publishconf.py*.

```python
SITEURL = "https://4dcu.be/DeckLock"
```

## Building platform

You can use make to build the website (if make is available on your system), use *make html* to create a local instance
to test in the *_site* directory. Use *make release* to create the version for publication in the *./docs* folder.

```commandline
make html

make release
```

alternatively you can use pelican directly, the content is in the folder ./content and the output folder should be set 
to ./_site for a local test build. Write the output to the ./docs folder with the publication settings so this can be
hosted easily on GitHub.

```commandline
pelican ./content -o ./_site

pelican ./content -o ./docs -s publishconf.py
```

[Deck of KeyForge]: https://decksofkeyforge.com/
