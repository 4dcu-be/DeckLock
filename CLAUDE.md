# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DeckLock is a static website generator for card game deck collections, built on Pelican. It supports Flesh and Blood, KeyForge, Gwent, and Magic: The Gathering decks. The project generates static HTML that can be hosted on GitHub Pages or any static hosting service.

## Common Development Commands

### Building the Site
- **Local development build**: `make html` or `pelican ./content -o ./_site`
- **Production build**: `make release` or `pelican ./content -o ./docs -s publishconf.py`
- **Clean build artifacts**: `make clean`

### Development Server
- **Start dev server**: `make serve` (serves on http://localhost:8000)
- **Build and serve**: `make devserver` (auto-rebuilds on changes)
- **Alternative serve**: `python -m http.server` (from `_site` directory)

### Code Quality
- **Format Python code**: `make black` (runs black formatter, excluding venv)

### Invoke Tasks (Alternative)
- **Build**: `invoke build`
- **Serve**: `invoke serve`
- **Live reload**: `invoke livereload`
- **GitHub Pages deploy**: `invoke gh-pages`

## Architecture and Plugin System

### Core Architecture
- **Pelican Framework**: Static site generator using Jinja2 templates
- **Plugin-based**: Modular system for each card game type
- **Cache System**: Downloads and caches card images and API data
- **External APIs**: Integrates with Scryfall (MTG), Decks of KeyForge, FaBDB

### Plugin Structure
Each game has its own plugin in `/plugins/[game]/`:
- **KeyForge**: Uses Decks of KeyForge API, requires DOK_API_KEY in .env
- **MTG**: Integrates with Scryfall API for card data
- **Gwent**: Parses custom deck format with patch version tracking
- **FAB**: Supports FaBDB format for Flesh and Blood decks

### Key Configuration Files
- **pelicanconf.py**: Development settings, plugin configuration, paths
- **publishconf.py**: Production settings, external image links enabled
- **Makefile**: Build commands and targets
- **tasks.py**: Invoke-based task definitions

### Content Structure
- `/content/data/`: Deck files organized by game type
- `/content/assets/`: Local card images (when USE_EXTERNAL_LINKS=False)
- `/content/dl_demo_cache/`: API response and card data cache
- `/theme/`: Jinja2 templates and static assets

### Environment Variables
- **DOK_API_KEY**: Required for KeyForge deck statistics from Decks of KeyForge
- Set in `.env` file (not committed to repo)

### Image Handling
- **Development**: USE_EXTERNAL_LINKS=False (downloads images locally)
- **Production**: USE_EXTERNAL_LINKS=True (uses external CDN links)
- Images cached in assets folders to avoid repeated downloads

### Template System
- **Base template**: `/theme/templates/base.html`
- **Game-specific templates**: Each game has overview and deck detail templates
- **Macros**: Reusable components in `/theme/templates/macros/`

## Deck File Formats

### KeyForge
- JSON file: `/content/data/keyforge.json`
- Contains deck IDs and optional adventure completion data

### Magic: The Gathering
- `.mwDeck` files in `/content/data/mtg_decks/[format]/`
- Format: `// META` comments + card lists with set codes

### Gwent
- `.gwent` files with `// NAME`, `// CREATOR`, `// GWENT_VERSION` headers
- Card lists with quantity and card names

### Flesh and Blood
- `.fab` files in FaBDB export format
- Supports hero, weapons, equipment, and card lists by pitch value

## Development Notes

- **Cache Management**: Clear `/content/dl_demo_cache/` to refresh API data
- **Testing**: Build locally with `make html` before production deployment
- **GitHub Pages**: Production builds output to `/docs/` for GitHub Pages hosting
- **Virtual Environment**: Always activate venv before development
- **Dependencies**: All requirements in `requirements.txt`, includes Pelican 4.6.0

## File Locations for Common Tasks

- **Add new game plugin**: Create `/plugins/[game]/` directory with `__init__.py` and reader
- **Modify site styling**: Edit files in `/theme/static/css/`
- **Update templates**: Modify files in `/theme/templates/`
- **Configure plugin settings**: Edit `pelicanconf.py` PLUGINS list and game-specific settings
- **Add deck data**: Place deck files in appropriate `/content/data/` subdirectories
- don't try to run the server, ask me to check things if needed