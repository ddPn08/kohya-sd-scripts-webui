import glob
import importlib
import json
import os
import sys

import gradio as gr
import gradio.routes

import scripts.shared as shared
from scripts.shared import ROOT_DIR, is_webui_extension
from scripts.utils import path_to_module


def register_path():
    add_module_path = [
        os.path.join(ROOT_DIR, "kohya_ss", "finetune"),
        os.path.join(ROOT_DIR, "kohya_ss", "networks"),
        os.path.join(ROOT_DIR, "kohya_ss", "library"),
        ROOT_DIR,
    ]
    remove_module_path = []
    remove_modules = {}
    if is_webui_extension():
        paths = importlib.import_module("modules.paths")
        remove_module_path.append(
            os.path.join(
                os.path.dirname(paths.script_path), "extensions-builtin", "Lora"
            )
        )
        remove_modules["lora"] = {}

    remove_module_path = [x for x in remove_module_path if x in sys.path]
    for m in remove_modules.keys():
        remove_modules[m] = sys.modules.pop(m)
    sys.path.extend(add_module_path)
    sys.path = [x for x in sys.path if x not in remove_module_path]

    def unregister():
        sys.path = [x for x in sys.path if x not in add_module_path]
        sys.path.extend(remove_module_path)
        sys.modules.update(remove_modules)

    return unregister


def create_js():
    jsfile = os.path.join(ROOT_DIR, "script.js")
    with open(jsfile, mode="r") as f:
        js = f.read()

    js = js.replace("kohya_sd_webui__help_map", json.dumps(shared.help_title_map))
    return js


def create_head():
    head = f'<script type="text/javascript">{create_js()}</script>'

    def template_response(*args, **kwargs):
        res = shared.gradio_template_response_original(*args, **kwargs)
        res.body = res.body.replace(b"</head>", f"{head}</head>".encode("utf8"))
        res.init_headers()
        return res

    def template_response_for_webui(*args, **kwargs):
        res = shared.gradio_template_response_original(*args, **kwargs)
        res.body = res.body.replace(b"</head>", f"{head}</head>".encode("utf8"))
        return res

    if is_webui_extension():
        import modules.shared

        modules.shared.GradioTemplateResponseOriginal = template_response_for_webui
    else:
        gradio.routes.templates.TemplateResponse = template_response


def on_ui_tabs():
    cssfile = os.path.join(ROOT_DIR, "style.css")
    with open(cssfile, mode="r") as f:
        css = f.read()
    with gr.Blocks(css=css, analytics_enabled=False) as sd_scripts:
        with gr.Tabs(elem_id="kohya_sd_webui__root"):
            tabs_dir = os.path.join(ROOT_DIR, "scripts", "tabs")
            unregister = register_path()
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
                            shared.current_tab = module_path
                            module = importlib.import_module(module_path)
                            with gr.TabItem(module.title()):
                                module.create_ui()
                        except Exception as e:
                            print(f"Failed to load {module_path}")
                            print(e)
                sys.path.remove(dir)
            unregister()
    create_head()
    return [(sd_scripts, "Kohya sd-scripts", "kohya_sd_scripts")]


def launch():
    [demo] = on_ui_tabs()
    if shared.cmd_opts.ngrok is not None:
        import scripts.ngrok as ngrok

        address = ngrok.connect(
            shared.cmd_opts.ngrok,
            shared.cmd_opts.port if shared.cmd_opts.port is not None else 7860,
            shared.cmd_opts.ngrok_region,
        )
        print('Running on ngrok URL: ' + address)

    demo[0].launch(share=shared.cmd_opts.share, server_port=shared.cmd_opts.port)


if not hasattr(shared, "gradio_template_response_original"):
    shared.gradio_template_response_original = gradio.routes.templates.TemplateResponse

if is_webui_extension():
    from modules import script_callbacks

    script_callbacks.on_ui_tabs(on_ui_tabs)

if __name__ == "__main__":
    launch()
