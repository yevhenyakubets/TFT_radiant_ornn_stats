import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Configuration
BASE_URL = "https://raw.communitydragon.org/pbe/game/assets/characters/"
CHAMP_DEST = "champion_icons"
ABILITY_DEST = "ability_icons"

os.makedirs(CHAMP_DEST, exist_ok=True)
os.makedirs(ABILITY_DEST, exist_ok=True)

def get_links(url):
    """Returns a list of links (folders/files) from a CDragon index page."""
    try:
        r = requests.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        
        links = []
        for item in soup.find_all('a'):
            href = item.get('href')
            # Check if href exists AND doesn't go up a directory
            if href and not href.startswith('../'):
                links.append(href)
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def download_file(url, dest_folder, new_name):
    """Downloads a file and saves it with a specific name."""
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            path = os.path.join(dest_folder, new_name)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"Successfully downloaded: {new_name}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# 1. Get all champion folders
all_folders = get_links(BASE_URL)

for folder in all_folders:
    # Only look at folders starting with tft16_
    if folder.lower().startswith("tft16_"):
        champ_id = folder.strip('/')
        print(f"Processing {champ_id}...")

        # 2. Look for Champion Icon (in /hud/)
        hud_url = urllib.parse.urljoin(BASE_URL, f"{folder}hud/")
        hud_files = get_links(hud_url)
        
        for file in hud_files:
            # Look for the square icon (usually contains 'square' or the champ's name)
            if file.endswith(".png") and ("square" in file.lower() or champ_id.lower() in file.lower()):
                download_file(urllib.parse.urljoin(hud_url, file), CHAMP_DEST, f"{champ_id}.png")
                break

        # 3. Look for Ability Icons (in /hud/icons2d/)
        icons_url = urllib.parse.urljoin(hud_url, "icons2d/")
        ability_files = get_links(icons_url)
        
        for file in ability_files:
            if file.endswith(".png"):
                # Prefix with champ name to avoid "spell1.png" duplicates
                download_file(urllib.parse.urljoin(icons_url, file), ABILITY_DEST, f"{champ_id}_{file}")

print("\nAll downloads finished!")