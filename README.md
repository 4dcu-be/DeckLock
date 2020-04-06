[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# DeckLock

Static web generator to generate an overview of all your favorite decks. Currently supports :

  * KeyForge

DeckLock is designed around the the static website generator Pelican and leverages GitHub's feature to host static 
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

As we are using a virtual environment with pelican installed there, the patch to the executable in
the enviroment needs to be set in the Makefile. Open the file and change the path on the line below to match your
system. The pelican executable should be in venv/bin or venv/Scripts.

```makefile
PELICAN?=d:\Git\DeckLock\venv\Scripts\pelican
```

### pelicanconf.py and publishconf.py

pelicanconf.py should be ready to go, though feel free to have a look to see if any of the
settings and paths need to be changed.

In publishconf.py however you will need to specify the final url of your site.

```python
SITEURL = "https://4dcu.be/DeckLock"
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

### Building platform

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

### Hosting locally for testing

You can use Pelican's built in webserver using the command below.

```commandline
make serve
```

Or you can build the site using *make html*, navigate to the *_site* folder and start a webserver
by running the command.

```commandline
python -m http.server
```

In both cases you can see your site by pointing your browser to [http://localhost:8000](http://localhost:8000).

### Hosting on GitHub

DeckLock includes a *make release* command which will write the final version of the website to the *./docs* folder. 
On GitHub you can specify that this folder is used for the project pages, enable this in the settings and you'll have
free hosting to show off the decks you have in your card game collection.

[Decks of KeyForge]: https://decksofkeyforge.com/