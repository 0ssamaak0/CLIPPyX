import subprocess
import argparse
import shutil
import os
import platform

# if it gets the flag --settings, open settings.py
parser = argparse.ArgumentParser()
parser.add_argument("--settings", action="store_true", help="Open CLIPPyX settings")
parser.add_argument(
    "--delete-index", action="store_true", help="delete the index (Vector database)"
)
parser.add_argument("--get-index", action="store_true", help="get the index path")
parser.add_argument("--open-config-file", action="store_true", help="open config.yaml")
args = parser.parse_args()

if args.settings:
    subprocess.run(["python3", "settings.py"])
    exit()

if args.delete_index:
    if os.path.exists("db/"):
        shutil.rmtree("db/")
        print("Index deleted successfully")
    else:
        print("Index does not exist")
    exit()

if args.get_index:
    if os.path.exists("db/"):
        print(os.path.abspath("db/"))
    else:
        print("Index does not exist")
    exit()

if args.open_config_file:
    if platform.system() == "Windows":
        os.system("start config.yaml")
    elif platform.system() == "Darwin":
        os.system("open config.yaml")
    else:
        os.system("xdg-open config.yaml")
    exit()

subprocess.run(["python", "create_index.py"])
subprocess.run(["python", "server.py"])
