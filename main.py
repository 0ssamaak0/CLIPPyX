import subprocess
import sys
import argparse
import shutil
import os
import platform

# Path to the Python executable using the same interpreter that's running this script
python_executable = sys.executable


def run_script(script_name):
    result = subprocess.run([python_executable, script_name])

    if result.returncode != 0:
        print(f"Error running {script_name}: {result.stderr}")
        return False
    else:
        print(f"Successfully ran {script_name}: {result.stdout}")
        return True


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
    run_script("settings.py")
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

# Run create_index.py and check if it succeeds before running server.py
run_script(script_name="create_index.py")
run_script("server.py")
