# a script for creating the apworld
# (This is not a module for Archipelago. This is a stand-alone script.)

# run from working directory subversion - working directory will be changed to ..

# directory "SubversionRando" (with the correct version) needs to be a sibling to "Archipelago"
# This does not verify the version.
# TODO: This script could download the correct version from github based on information in requirements.txt

import os
from shutil import copytree, make_archive, rmtree

ORIG = "subversion"
TEMP = "subversion_temp"
MOVE = "subversion_move"

if os.getcwd().endswith("Archipelago"):
    os.chdir("worlds")
else:
    os.chdir("..")
assert os.getcwd().endswith("worlds"), f"incorrect directory: {os.getcwd()=}"

assert os.path.exists(ORIG), f"{ORIG} doesn't exist"
assert not os.path.exists(TEMP), f"{TEMP} exists"
assert not os.path.exists(MOVE), f"{MOVE} exists"

subversion_rando_dir = os.path.join("..", "..", "SubversionRando", "src", "subversion_rando")
assert os.path.exists(subversion_rando_dir), f"{subversion_rando_dir} doesn't exist"

destination = os.path.join("subversion.apworld")
if os.path.exists(destination):
    os.unlink(destination)
assert not os.path.exists(destination)

copytree(ORIG, TEMP)

if os.path.exists(os.path.join(TEMP, "__pycache__")):
    rmtree(os.path.join(TEMP, "__pycache__"))

copytree(subversion_rando_dir, os.path.join(TEMP, "subversion_rando"))

if os.path.exists(os.path.join(TEMP, "subversion_rando", "__pycache__")):
    rmtree(os.path.join(TEMP, "subversion_rando", "__pycache__"))

os.rename(ORIG, MOVE)
os.rename(TEMP, ORIG)

zip_file_name = make_archive("subversion", "zip", ".", ORIG)
print(f"{zip_file_name} -> {destination}")
os.rename(zip_file_name, destination)

rmtree(ORIG)
os.rename(MOVE, ORIG)

assert os.path.exists(ORIG), f"{ORIG} doesn't exist at end"
assert not os.path.exists(TEMP), f"{TEMP} exists at end"
assert not os.path.exists(MOVE), f"{MOVE} exists at end"
