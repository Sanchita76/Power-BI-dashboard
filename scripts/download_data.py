"""Download the Olist Brazilian E-Commerce dataset from Kaggle into data/raw.

Needs a free Kaggle account + API token (see README step 2). Alternative without any API:
download the ZIP manually from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce and unzip it into data/raw.
"""
import os, subprocess, sys

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw")
os.makedirs(RAW, exist_ok=True)
try:
    subprocess.run([sys.executable, "-m", "kaggle", "datasets", "download", "-d", "olistbr/brazilian-ecommerce",
                    "-p", RAW, "--unzip"], check=True)
    print("Downloaded to", os.path.abspath(RAW))
except Exception as e:
    sys.exit(f"\nKaggle download failed ({e}).\nFix: create an API token (Kaggle -> Settings -> API) and put kaggle.json in "
             "~/.kaggle (Windows: C:\\Users\\<you>\\.kaggle), or download the ZIP manually in your browser "
             "and unzip into data/raw.\nOr run: python scripts/make_demo_data.py  (fake data, same format)")
