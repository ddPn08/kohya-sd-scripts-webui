import gradio as gr

from scripts import presets, ui
from scripts.runner import initialize_runner
from scripts.utilities import load_args_template, options_to_gradio


def title():
    return "Prepare latents"


def create_ui():
    options = {}
    templates, script_file = load_args_template(
        "finetune", "prepare_buckets_latents.py"
    )

    with gr.Column():
        init_runner = initialize_runner(script_file, templates, options)
        with gr.Box():
            with gr.Row():
                init_ui = presets.create_ui(
                    "finetune.prepare_buckets_latents", templates, options
                )
        with gr.Box():
            ui.title("Options")
            with gr.Column():
                options_to_gradio(templates, options)

    init_runner()
    init_ui()
