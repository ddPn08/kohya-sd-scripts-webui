import argparse

import gradio as gr

from kohya_ss.finetune import merge_dd_tags_to_metadata
from scripts import presets, ui
from scripts.utils import gradio_to_args, load_args_template, options_to_gradio

TEMPLATES = load_args_template("finetune", "merge_dd_tags_to_metadata.py")


def title():
    return "Merge tags"


def create_ui():
    options = {}

    templates = TEMPLATES

    def train(args):
        args = gradio_to_args(templates, options, args)
        try:
            merge_dd_tags_to_metadata.main(argparse.Namespace(**args))
        except Exception as e:
            return e.args
        return "Finished."

    with gr.Column():
        status = gr.Textbox("", show_label=False, interactive=False)
        start = gr.Button("Run", variant="primary")
        with gr.Box():
            with gr.Row():
                init = presets.create_ui(
                    "finetune.merge_dd_tags_to_metadata", templates, options
                )
        with gr.Box():
            ui.title("Options")
            with gr.Column():
                options_to_gradio(TEMPLATES, options)
        start.click(train, set(options.values()), status)
    init()
