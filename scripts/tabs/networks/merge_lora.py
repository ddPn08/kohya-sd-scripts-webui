import gradio as gr

from scripts import ui
from scripts.runner import initialize_runner
from scripts.utils import load_args_template, options_to_gradio


def title():
    return "Merge lora"


def create_ui():
    options = {}
    templates, script_file = load_args_template("networks", "merge_lora.py")
    run = initialize_runner(script_file, templates, options)

    with gr.Column():
        status = gr.Textbox("", show_label=False, interactive=False)
        start = gr.Button("Run", variant="primary")
        with gr.Box():
            ui.title("Options")
            with gr.Column():
                options_to_gradio(templates, options)
        start.click(run, set(options.values()), status)
