import sys
import argparse
import importlib
import os


def is_webui_extension():
    try:
        importlib.import_module("webui")
        return True
    except:
        return False


ROOT_DIR = (
    importlib.import_module("modules.scripts").basedir()
    if is_webui_extension()
    else os.path.dirname(os.path.dirname(__file__))
)

current_tab = None
help_title_map = {}

parser = argparse.ArgumentParser()
parser.add_argument("--share", action="store_true")
cmd_opts, _ = parser.parse_known_args(sys.argv)
