import argparse

import gradio as gr

from kohya_ss.networks import extract_lora_from_models
from scripts import presets, ui
from scripts.utils import gradio_to_args, load_args_template, options_to_gradio

TEMPLATES = load_args_template("networks", "extract_lora_from_models.py")


def title():
    return "Extract lora from models"


def create_ui():
    options = {}

    templates = TEMPLATES

    def train(args):
        args = gradio_to_args(templates, options, args)
        try:
            extract_lora_from_models.svd(argparse.Namespace(**args))
        except Exception as e:
            return e.args
        return "Finished."

    with gr.Column():
        status = gr.Textbox("", show_label=False, interactive=False)
        start = gr.Button("Run", variant="primary")
        with gr.Box():
            with gr.Row():
                init = presets.create_ui(
                    "networks.extract_lora_from_models", templates, options
                )
        with gr.Box():
            ui.title("Options")
            with gr.Column():
                options_to_gradio(TEMPLATES, options)
        start.click(train, set(options.values()), status)
    init()
