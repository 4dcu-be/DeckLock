import os
import requests
from datetime import datetime


def fetch_image(img_url, img_file_path):
    if not os.path.exists(img_file_path):
        print(f"Fetching image {img_url}")
        r = requests.get(img_url, allow_redirects=True)
        open(img_file_path, "wb").write(r.content)
    else:
        # print(f"Using cached image {img_file_path}")
        pass


def get_last_modified(path):
    last_modification = datetime.utcfromtimestamp(os.path.getmtime(path))

    return last_modification.strftime("%Y-%m-%d")