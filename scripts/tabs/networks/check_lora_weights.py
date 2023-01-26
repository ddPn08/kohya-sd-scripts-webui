import argparse
import logging

import gradio as gr

from kohya_ss.networks import check_lora_weights
from scripts import presets, ui
from scripts.utils import gradio_to_args, load_args_template, options_to_gradio

TEMPLATES = load_args_template("networks", "check_lora_weights.py")


def title():
    return "Check lora wights"


def create_ui():
    options = {}

    templates = TEMPLATES

    def train(args):
        args = gradio_to_args(templates, options, args)
        try:
            check_lora_weights.main(argparse.Namespace(**args).file)
        except Exception as e:
            return e.args
        return "Finished."

    with gr.Column():
        status = gr.Textbox("", show_label=False, interactive=False)
        start = gr.Button("Run", variant="primary")
        init = presets.create_ui("networks.check_lora_weights", templates, options)
        with gr.Box():
            ui.title("Options")
            with gr.Column():
                options_to_gradio(TEMPLATES, options)
        start.click(train, set(options.values()), status)
    init()
