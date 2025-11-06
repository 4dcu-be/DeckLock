# Beginner's Guide to DeckLock

Welcome! This guide will help you create your own deck collection website, even if you've never done anything like this before. Don't worry - we'll go step by step!

## What is DeckLock?

DeckLock creates a website that shows off your card game decks. You can share it with friends, use it as a reference, or just have a cool online collection. It works with:
- Flesh and Blood
- KeyForge
- Gwent
- Magic: The Gathering

**Example**: You tell DeckLock about your decks (by adding deck lists), and it creates a nice-looking website with card images and deck details. You can host this website for free on GitHub.

## What You'll Need

- **A computer** (Windows, Mac, or Linux)
- **About 30-60 minutes** for setup
- **Internet connection**
- **Your deck lists** (we'll explain the format later)
- **Patience!** (First time is always the trickiest)

---

## Part 1: Installing What You Need

Before we start, you need three free programs installed on your computer.

### Step 1: Install Python

Python is the programming language that runs DeckLock. Don't worry, you won't need to write code!

1. **Download Python**:
   - Go to: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - Click the big yellow "Download Python 3.x.x" button
   - Download the installer

2. **Install Python**:
   - **Windows**: Run the installer
     - ⚠️ **IMPORTANT**: Check the box that says "Add Python to PATH" at the bottom!
     - Click "Install Now"
   - **Mac**: Run the installer and follow the prompts
   - **Linux**: Python is usually already installed

3. **Check it worked**:
   - **Windows**: Open "Command Prompt" (search for it in Start menu)
   - **Mac**: Open "Terminal" (search for it in Spotlight)
   - **Linux**: Open your terminal

   Type this and press Enter:
   ```
   python --version
   ```

   You should see something like "Python 3.11.0". If you see an error, Python didn't install correctly - try again or ask for help.

### Step 2: Install Git

Git helps you save versions of your work and upload it to GitHub.

1. **Download Git**:
   - Go to: [https://git-scm.com/downloads](https://git-scm.com/downloads)
   - Download the version for your operating system

2. **Install Git**:
   - Run the installer
   - You can just click "Next" through all the options (the defaults are fine)

3. **Check it worked**:
   - Open Command Prompt (Windows) or Terminal (Mac/Linux) again
   - Type this and press Enter:
   ```
   git --version
   ```

   You should see something like "git version 2.40.0"

### Step 3: Create a GitHub Account

GitHub is where you'll store your website and host it for free.

1. Go to: [https://github.com/](https://github.com/)
2. Click "Sign up"
3. Follow the prompts to create a free account
4. Remember your username - you'll need it later!

---

## Part 2: Setting Up Your Deck Collection

Now the fun part begins!

### Step 4: Make Your Own Copy (Fork)

1. **Go to the DeckLock repository**:
   - Visit: [https://github.com/4dcu-be/DeckLock](https://github.com/4dcu-be/DeckLock)

2. **Click the "Fork" button** (top right corner of the page)
   - This makes your own copy that you can modify

3. **Wait a few seconds** while GitHub copies everything

When it's done, you'll be on YOUR copy of DeckLock. The URL will be: `https://github.com/YOUR-USERNAME/DeckLock`

### Step 5: Download Your Copy to Your Computer

Now we'll download your copy so you can work on it.

1. **On your DeckLock page on GitHub**, click the green "Code" button

2. **Copy the URL** (it looks like: `https://github.com/YOUR-USERNAME/DeckLock.git`)

3. **Open Command Prompt (Windows) or Terminal (Mac/Linux)**

4. **Navigate to where you want to store your project**:
   - **Windows example**: If you want it in your Documents folder:
     ```
     cd Documents
     ```
   - **Mac example**: If you want it in your Documents folder:
     ```
     cd ~/Documents
     ```

5. **Download your copy** (this is called "cloning"):
   ```
   git clone https://github.com/YOUR-USERNAME/DeckLock.git
   ```
   (Replace YOUR-USERNAME with your actual GitHub username)

6. **Go into the DeckLock folder**:
   ```
   cd DeckLock
   ```

**What just happened?** You now have a copy of all the DeckLock files on your computer!

### Step 6: Set Up Python Environment

This creates a special space for DeckLock's requirements, so they don't mess with other things on your computer.

1. **Create the environment**:
   ```
   python -m venv venv
   ```
   (This takes a minute - be patient!)

2. **Activate the environment**:
   - **Windows**:
     ```
     venv\Scripts\activate
     ```
   - **Mac/Linux**:
     ```
     source venv/bin/activate
     ```

   **You'll know it worked** when you see `(venv)` at the start of your command line.

3. **Install DeckLock's requirements**:
   ```
   pip install -r requirements.txt
   ```
   (This downloads everything DeckLock needs - takes 1-2 minutes)

**Tip**: Every time you open a new Command Prompt/Terminal to work on DeckLock, you'll need to:
1. Navigate to your DeckLock folder: `cd Documents/DeckLock` (or wherever you put it)
2. Activate the environment again (step 2 above)

---

## Part 3: Customizing Your Site

### Step 7: Create Your Content Folder

Let's create a folder just for YOUR decks, separate from the demo content.

**In your Command Prompt/Terminal**, type these commands:

- **Windows**:
  ```
  mkdir mycontent
  xcopy content\data mycontent\data\ /E /I
  xcopy content\assets mycontent\assets\ /E /I
  ```

- **Mac/Linux**:
  ```
  mkdir mycontent
  cp -r content/data mycontent/
  cp -r content/assets mycontent/
  ```

**What did this do?** Created a `mycontent` folder with starter subfolders where you'll put your deck information.

### Step 8: Tell DeckLock to Use Your Content

Now we need to edit three configuration files. Don't worry - it's just changing a few lines!

#### File 1: Makefile

1. **Open the file**:
   - Find the file called `Makefile` in your DeckLock folder
   - Open it with Notepad (Windows) or TextEdit (Mac)

2. **Find line 6** (it currently says: `INPUTDIR=$(BASEDIR)/content`)

3. **Change it to**:
   ```
   INPUTDIR=$(BASEDIR)/mycontent
   ```

4. **Save and close** the file

#### File 2: pelicanconf.py

1. **Open the file**: `pelicanconf.py` in Notepad/TextEdit

2. **Find line 24** (it says: `PATH = "content"`)

3. **Change it to**:
   ```
   PATH = "mycontent"
   ```

4. **Find line 25** (it says: `DECKLOCK_CACHE = "dl_demo_cache"`)

5. **Change it to**:
   ```
   DECKLOCK_CACHE = "dl_cache"
   ```

6. **Optional - Personalize your welcome message**:
   - Around lines 64-71, you'll see `WELCOME_MESSAGE = """`
   - Change the text inside to whatever you want!
   - Example:
   ```python
   WELCOME_MESSAGE = """
   #### Welcome to My Card Game Collection!

   These are all the decks I've built and played. Click on a game below to see them!
   """
   ```

7. **Save and close** the file

#### File 3: publishconf.py

1. **Open the file**: `publishconf.py` in Notepad/TextEdit

2. **Find line 15** (it says: `SITEURL = "https://4dcu.be/DeckLock"`)

3. **Change it to** (replace YOUR-USERNAME with your GitHub username):
   ```
   SITEURL = "https://YOUR-USERNAME.github.io/DeckLock"
   ```

   For example, if your GitHub username is "cardmaster99":
   ```
   SITEURL = "https://cardmaster99.github.io/DeckLock"
   ```

4. **Save and close** the file

---

## Part 4: Adding Your Decks

Now for the best part - adding your decks! The format depends on which game you play.

### Where to Put Deck Files

All your deck files go in: `mycontent/data/`

Navigate to this folder on your computer:
- **Windows**: `Documents\DeckLock\mycontent\data\` (or wherever you put DeckLock)
- **Mac**: `Documents/DeckLock/mycontent/data/`

### Option A: KeyForge Decks

1. **Get your API key** (optional, but recommended):
   - Go to: [https://decksofkeyforge.com/](https://decksofkeyforge.com/)
   - Create an account and get your API key
   - In your DeckLock folder, create a file called `.env` (note the dot at the start)
   - Open it in Notepad/TextEdit and add this line:
     ```
     DOK_API_KEY=your_api_key_here
     ```
   - Save and close

2. **Create your KeyForge deck list**:
   - In `mycontent/data/`, create a file called `keyforge.json`
   - Open it in Notepad/TextEdit
   - Add your deck IDs like this:

   ```json
   [
     {
       "deck_id": "a4268ae8-a9f6-48c7-9739-b28a3553b108"
     },
     {
       "deck_id": "bfbf6786-218c-4320-a7b1-7ed4d6eddc69"
     }
   ]
   ```

   - **Where to find deck IDs**: On Decks of KeyForge, each deck has a unique ID in its URL
   - You can add as many decks as you want - just follow the pattern above

### Option B: Magic: The Gathering Decks

1. **Create a folder for your format**:
   - Inside `mycontent/data/`, create a folder called `mtg_decks`
   - Inside `mtg_decks`, create a folder for your format (like `commander`, `standard`, `modern`, etc.)

2. **Create a deck file**:
   - Create a new file with the extension `.mwDeck` (for example: `my-cool-deck.mwDeck`)
   - Open it in Notepad/TextEdit
   - Use this format:

   ```
   // NAME : My Awesome Deck
   // CREATOR : Your Name
   // FORMAT : Commander
   1 [MH2] Ragavan, Nimble Pilferer
   1 [ZNR] Omnath, Locus of Creation
   4 [MID] Consider
   30 [ZNR] Forest
   ```

   - The format is: `quantity [SET] Card Name`
   - Get set codes from [Scryfall](https://scryfall.com/)

### Option C: Flesh and Blood Decks

1. **Create a deck file**:
   - In `mycontent/data/`, create a file ending in `.fab` (like `my-deck.fab`)
   - Open it in Notepad/TextEdit
   - Use this format:

   ```
   My Deck Name

   Class: Brute
   Hero: Rhinar
   Weapons: Romping Club
   Equipment: Scabskin Leathers, Nullrune Boots

   (2) Smash with Big Tree (red)
   (2) Barraging Beatdown (red)
   (2) Wild Ride (red)
   ```

### Option D: Gwent Decks

1. **Create a deck file**:
   - In `mycontent/data/`, create a file ending in `.gwent` (like `my-deck.gwent`)
   - Open it in Notepad/TextEdit
   - Use this format:

   ```
   // NAME : My Deck Name
   // CREATOR : Your Name
   // GWENT_VERSION : 8.2.0
   // FACTION : Scoia'tael
   1 Mystic Echo
   2 Forest Whisperer
   1 Water of Brokilon
   ```

---

## Part 5: Building and Viewing Your Site

### Step 9: Build Your Website

Time to see your hard work!

1. **Make sure you're in the DeckLock folder** in Command Prompt/Terminal

2. **Make sure the environment is activated** (you should see `(venv)` at the start of the line)

3. **Build the site**:
   ```
   pelican ./content -o ./_site -s pelicanconf.py
   ```

   **Wait a minute or two** while it builds. You'll see lots of messages - that's normal!

   **What if you get an error?**
   - If it says "pelican: command not found", your venv isn't activated - go back to Step 6, part 2
   - If it says Python errors, double-check your config files from Step 8

### Step 10: View Your Website Locally

Let's see what you created!

1. **Start a local web server**:
   ```
   pelican -l ./content -o ./_site -s pelicanconf.py
   ```

2. **Open your web browser** (Chrome, Firefox, Safari, etc.)

3. **Go to**: [http://localhost:8000](http://localhost:8000)

4. **You should see your deck collection website!** 🎉

**To stop the server**: Press `Ctrl+C` in the Command Prompt/Terminal

---

## Part 6: Publishing to the Internet

Now let's make your site available to everyone!

### Step 11: Save Your Changes

We need to save all the changes you made.

1. **In Command Prompt/Terminal, make sure you're in the DeckLock folder**

2. **Tell Git about all your new files**:
   ```
   git add .
   ```

3. **Save your changes** (this is called a "commit"):
   ```
   git commit -m "Set up my deck collection"
   ```

4. **Upload to GitHub** (this is called a "push"):
   ```
   git push
   ```

   You might need to enter your GitHub username and password.

### Step 12: Enable GitHub Pages

Almost there!

1. **Go to your repository on GitHub**: `https://github.com/YOUR-USERNAME/DeckLock`

2. **Click on "Settings"** (top menu)

3. **In the left sidebar, click "Pages"**

4. **Under "Source", you'll see two dropdowns**:
   - The first one should say "Deploy from a branch"
   - The second should say "None"

5. **Change the second dropdown to "gh-pages"**
   - If you don't see "gh-pages" yet, that's okay! We'll create it in the next step

6. **Click "Save"**

### Step 13: Deploy Your Site

Now we'll build the production version and deploy it!

1. **In Command Prompt/Terminal**, run these commands:
   ```
   pelican ./content -o ./docs -s publishconf.py
   ```

   This builds the final version.

2. **If you got the gh-pages option in Step 12**, you can use this shortcut instead:
   - **Mac/Linux**:
     ```
     make github
     ```
   - **Windows** (if you have Make installed):
     ```
     make github
     ```

3. **Wait 2-5 minutes** for GitHub to process your site

4. **Visit your website!** Go to:
   ```
   https://YOUR-USERNAME.github.io/DeckLock
   ```

**Congratulations! Your deck collection is now online!** 🎊

---

## Part 7: Making Changes Later

### Adding More Decks

1. **Add new deck files** to `mycontent/data/` (follow the formats in Part 4)

2. **Rebuild the site**:
   ```
   pelican ./content -o ./_site -s pelicanconf.py
   ```

3. **Check it looks good**: Start the local server and view at [http://localhost:8000](http://localhost:8000)

4. **Save and upload**:
   ```
   git add .
   git commit -m "Added new decks"
   git push
   ```

5. **Rebuild and deploy**:
   - **Mac/Linux**: `make github`
   - **Windows**: `pelican ./content -o ./docs -s publishconf.py` then `git add .`, `git commit -m "Deploy"`, `git push`

6. **Wait 2-5 minutes**, then check your website!

### Editing Deck Information

1. **Open the deck file** in Notepad/TextEdit
2. **Make your changes**
3. **Follow the rebuild and deploy steps** above

---

## Troubleshooting

### "Python is not recognized as a command"
- **Fix**: You need to reinstall Python and check "Add Python to PATH" during installation

### "git is not recognized as a command"
- **Fix**: Restart Command Prompt/Terminal after installing Git

### "Permission denied" when pushing to GitHub
- **Fix**: You might need to set up authentication
  - Try: `git config --global user.email "your-email@example.com"`
  - And: `git config --global user.name "Your Name"`

### My website shows a 404 error
- **Fix**:
  - Make sure GitHub Pages is enabled in Settings → Pages
  - Wait 5-10 minutes after deploying
  - Check that you pushed to the correct branch

### Cards aren't showing up
- **Fix**:
  - Check your deck file format matches the examples
  - Make sure you're using correct set codes (for MTG)
  - Make sure deck IDs are correct (for KeyForge)
  - Check for typos in card names

### Something broke and I don't know why
- **Fix**: You can always download a fresh copy and start over:
  1. Move your `mycontent` folder somewhere safe
  2. Delete the DeckLock folder
  3. Start again from Step 5
  4. Copy your `mycontent` folder back
  5. Redo the config changes from Step 8

---

## Getting Help

- **GitHub Issues**: If something isn't working, you can ask for help at: [https://github.com/4dcu-be/DeckLock/issues](https://github.com/4dcu-be/DeckLock/issues)
- **Check existing issues**: Someone might have already solved your problem!

---

## Quick Reference: Common Commands

**Activate the environment**:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

**Build and test locally**:
```
pelican ./content -o ./_site -s pelicanconf.py
pelican -l ./content -o ./_site -s pelicanconf.py
```
Then visit: http://localhost:8000

**Save and upload changes**:
```
git add .
git commit -m "Description of what you changed"
git push
```

**Deploy to GitHub Pages** (Mac/Linux):
```
make github
```

---

## You Did It!

You now have your own deck collection website! Feel free to:
- Share the link with friends
- Add more decks as you build them
- Customize the welcome message
- Show off your collection!

Enjoy your new website! 🎮🃏
