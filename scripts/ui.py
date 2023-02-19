import glob
import importlib
import os
import sys

import gradio as gr

import scripts.shared as shared
from scripts.shared import ROOT_DIR
from scripts.utilities import path_to_module


def title(txt):
    gr.HTML(
        f'<h1 style="margin: 0.5rem 0; font-weight: bold; font-size: 1.5rem;">{txt}</h1>',
    )


def create_ui(css):
    PATHS = [
        os.path.join(ROOT_DIR, "kohya_ss", "library"),
        ROOT_DIR,
    ]
    sys.path.extend(PATHS)
    with gr.Blocks(css=css, analytics_enabled=False) as ui:
        with gr.Tabs(elem_id="kohya_sd_webui__root"):
            tabs_dir = os.path.join(ROOT_DIR, "scripts", "tabs")
            for category in os.listdir(tabs_dir):
                dir = os.path.join(tabs_dir, category)
                tabs = glob.glob(os.path.join(dir, "*.py"))
                sys.path.append(dir)
                if len(tabs) < 1:
                    continue
                with gr.TabItem(category):
                    for lib in tabs:
                        try:
                            module_path = path_to_module(lib)
                            module_name = module_path.replace(".", "_")

                            module = importlib.import_module(module_path)
                            shared.current_tab = module_name
                            shared.loaded_tabs.append(module_name)

                            with gr.TabItem(module.title()):
                                module.create_ui()
                        except Exception as e:
                            print(f"Failed to load {module_path}")
                            print(e)
                sys.path.remove(dir)
            with gr.TabItem("terminal"):
                gr.HTML('<div id="kohya_sd_webui__terminal_outputs"></div>')
    sys.path = [x for x in sys.path if x not in PATHS]
    return ui
