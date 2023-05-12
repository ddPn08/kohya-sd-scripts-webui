import argparse

import gradio as gr

from kohya_ss.library import train_util, config_util
from scripts import presets, ui, ui_overrides
from scripts.runner import initialize_runner
from scripts.utilities import args_to_gradio, load_args_template, options_to_gradio


def title():
    return "alex lora trainer"


def create_ui():
    network_options = {}

    templates, script_file = load_args_template("Lora.py")

    get_options = lambda: {
        **network_options,
    }

    get_templates = lambda: {
        **templates,
    }

    with gr.Column():
        init_runner = initialize_runner(script_file, get_templates, get_options)
        with gr.Box():
            with gr.Row():
                init_id = presets.create_ui("alex lora trainer", get_templates, get_options)
        with gr.Row():
            with gr.Group():
                with gr.Box():
                    ui.title("Network options")
                    options_to_gradio(templates, network_options)

    init_runner()
    init_id()
