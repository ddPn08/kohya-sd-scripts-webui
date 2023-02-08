import json
import os
import time

import gradio.routes

import scripts.runner as runner
import scripts.shared as shared
from scripts.shared import ROOT_DIR, is_webui_extension
from scripts.ui import create_ui


def create_js():
    jsfile = os.path.join(ROOT_DIR, "script.js")
    with open(jsfile, mode="r") as f:
        js = f.read()

    js = js.replace("kohya_sd_webui__help_map", json.dumps(shared.help_title_map))
    js = js.replace(
        "kohya_sd_webui__all_tabs",
        json.dumps(shared.loaded_tabs),
    )
    return js


def create_head():
    head = f'<script type="text/javascript">{create_js()}</script>'

    def template_response_for_webui(*args, **kwargs):
        res = shared.gradio_template_response_original(*args, **kwargs)
        res.body = res.body.replace(b"</head>", f"{head}</head>".encode("utf8"))
        return res

    def template_response(*args, **kwargs):
        res = template_response_for_webui(*args, **kwargs)
        res.init_headers()
        return res

    if is_webui_extension():
        import modules.shared

        modules.shared.GradioTemplateResponseOriginal = template_response_for_webui
    else:
        gradio.routes.templates.TemplateResponse = template_response


def wait_on_server():
    while 1:
        time.sleep(0.5)


def on_ui_tabs():
    cssfile = os.path.join(ROOT_DIR, "style.css")
    with open(cssfile, mode="r") as f:
        css = f.read()
    sd_scripts = create_ui(css)
    create_head()
    return [(sd_scripts, "Kohya sd-scripts", "kohya_sd_scripts")]


def launch():
    block, _, _ = on_ui_tabs()[0]
    if shared.cmd_opts.ngrok is not None:
        import scripts.ngrok as ngrok

        address = ngrok.connect(
            shared.cmd_opts.ngrok,
            shared.cmd_opts.port if shared.cmd_opts.port is not None else 7860,
            shared.cmd_opts.ngrok_region,
        )
        print("Running on ngrok URL: " + address)

    app, local_url, share_url = block.launch(
        share=shared.cmd_opts.share,
        server_port=shared.cmd_opts.port,
        server_name=shared.cmd_opts.host,
        prevent_thread_lock=True,
    )

    runner.initialize_api(app)

    wait_on_server()


if not hasattr(shared, "gradio_template_response_original"):
    shared.gradio_template_response_original = gradio.routes.templates.TemplateResponse

if is_webui_extension():
    from modules import script_callbacks

    def initialize_api(_, app):
        runner.initialize_api(app)

    script_callbacks.on_ui_tabs(on_ui_tabs)
    script_callbacks.on_app_started(initialize_api)

if __name__ == "__main__":
    launch()
