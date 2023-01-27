import json
import os

import gradio.routes

import scripts.shared as shared
from scripts.shared import ROOT_DIR, is_webui_extension
from scripts.ui import create_ui


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
    sd_scripts = create_ui(css)
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
        print("Running on ngrok URL: " + address)

    demo[0].launch(share=shared.cmd_opts.share, server_port=shared.cmd_opts.port)


if not hasattr(shared, "gradio_template_response_original"):
    shared.gradio_template_response_original = gradio.routes.templates.TemplateResponse

if is_webui_extension():
    from modules import script_callbacks

    script_callbacks.on_ui_tabs(on_ui_tabs)

if __name__ == "__main__":
    launch()
