import argparse
import importlib
import os
import sys


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
loaded_tabs = []
help_title_map = {}

parser = argparse.ArgumentParser()
parser.add_argument(
    "--share",
    action="store_true",
    help="use share=True for gradio and make the UI accessible through their site",
)
parser.add_argument(
    "--port",
    type=int,
    help="launch gradio with given server port, you need root/admin rights for ports < 1024, defaults to 7860 if available",
    default=None,
)
parser.add_argument(
    "--ngrok",
    type=str,
    help="ngrok authtoken, alternative to gradio --share",
    default=None,
)
parser.add_argument(
    "--ngrok-region",
    type=str,
    help="The region in which ngrok should start.",
    default="us",
)
parser.add_argument(
    "--hide-builtin-presets",
    action="store_true",
    help="Hide built-in presets",
)
parser.add_argument(
    "--enable-console-log",
    action="store_true",
    help="Print script output to console",
)
cmd_opts, _ = parser.parse_known_args(sys.argv)
