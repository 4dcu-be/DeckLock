# Fork and Customization Guide

This guide helps you create your own customized version of DeckLock while maintaining the ability to easily sync with upstream updates.

## Quick Start

### 1. Fork and Set Up

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/DeckLock.git
cd DeckLock

# Add upstream remote for future updates
git remote add upstream https://github.com/4dcu-be/DeckLock.git

# Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 2. Create Your Custom Content Structure

```bash
# Create your own content folder
mkdir mycontent
cp -r content/data mycontent/
cp -r content/assets mycontent/
```

### 3. Configure Your Installation

Update these three files:

#### Makefile (line 6)
```makefile
INPUTDIR=$(BASEDIR)/mycontent
```

#### pelicanconf.py (lines 24-25)
```python
PATH = "mycontent"
DECKLOCK_CACHE = "dl_cache"
```

#### publishconf.py (line 15)
```python
SITEURL = "https://YOUR-USERNAME.github.io/DeckLock"
```

### 4. Customize and Build

```bash
# Remove demo decks and add your own in mycontent/data/
rm mycontent/data/*.json
rm mycontent/data/*.gwent
rm mycontent/data/*.fab
# ... add your deck files

# Test locally
make html
make serve  # Visit http://localhost:8000
```

### 5. Deploy to GitHub Pages

```bash
# Build and push to gh-pages branch
make github

# Then on GitHub.com:
# Settings → Pages → Source: gh-pages branch
```

### 6. Set Up GitHub Actions (Optional)

To enable automatic builds on every push:

1. Go to your repo: **Settings → Secrets and variables → Actions**
2. Add secret: `DOK_API_KEY` with your API key from [Decks of KeyForge](https://decksofkeyforge.com/)

## Staying Up-to-Date with Upstream

### Syncing with the Original Repository

```bash
# Fetch latest changes
git fetch upstream

# Switch to your main branch
git checkout main

# Rebase your changes on top of upstream
git rebase upstream/main

# Resolve any conflicts if needed
# git add <resolved-files>
# git rebase --continue

# Push to your fork
git push origin main --force-with-lease
```

### Best Practices to Minimize Conflicts

✅ **Do:**
- Keep all your content in `mycontent/` folder
- Only modify configuration values (URLs, paths, welcome message)
- Regularly sync with upstream (monthly or quarterly)
- Create feature branches for experimental changes

❌ **Don't:**
- Modify plugin code unless absolutely necessary
- Change core template files
- Commit large binary files or images to git
- Wait too long between upstream syncs

## File Structure for Forks

```
DeckLock/
├── content/              # Demo content (don't modify)
│   └── dl_demo_cache/   # Demo cache (committed to repo)
├── mycontent/            # YOUR content (commit this!)
│   ├── data/            # Your deck files (commit these)
│   └── assets/          # Your local images (gitignored - redownloaded as needed)
├── dl_cache/            # Your cache (commit this for faster CI builds!)
├── pelicanconf.py       # MODIFY: paths and welcome message
├── publishconf.py       # MODIFY: your site URL
├── Makefile             # MODIFY: input directory path
└── plugins/             # Don't modify unless needed
```

**Important**: Cache folders should be committed to your repository! They contain API responses and metadata that speed up builds, especially in GitHub Actions. Only the `assets/` folders (containing downloaded images) are gitignored.

## Troubleshooting

### Build fails with "no module named..."
```bash
pip install -r requirements.txt
```

### GitHub Pages shows 404
- Check that GitHub Pages is enabled from the **gh-pages branch**
- Wait 5-10 minutes for GitHub to build
- Check the Actions tab for build errors

### Images not showing
- Production build uses external CDN links by default (`USE_EXTERNAL_LINKS = True`)
- For local testing with `make html`, images download to `mycontent/assets/` (these are gitignored as they're large files)
- Images are re-downloaded automatically when needed, so it's safe to gitignore them
- The cache folders (`dl_cache/`, `dl_demo_cache/`) should be committed - they contain metadata, not images

### Merge conflicts when syncing
- Most conflicts will be in configuration files
- Keep your version of `PATH`, `DECKLOCK_CACHE`, and `SITEURL`
- Accept upstream changes for everything else
- When in doubt, check the diff carefully

## Getting Help

- **Issues with DeckLock itself**: [Original repo issues](https://github.com/4dcu-be/DeckLock/issues)
- **Questions about forking**: Check [GitHub's fork documentation](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
- **Pelican documentation**: [Pelican docs](https://docs.getpelican.com/)

## Example Deck Files

See the `content/data/` folder for example deck formats:
- `keyforge.json` - KeyForge deck IDs
- `*.gwent` - Gwent deck format
- `*.fab` - Flesh and Blood format
- `mtg_decks/**/*.mwDeck` - Magic: The Gathering format
