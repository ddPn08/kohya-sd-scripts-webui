import gradio as gr

from scripts import presets, ui
from scripts.utils import load_args_template, options_to_gradio, run_python

TEMPLATES, script_file = load_args_template("networks", "check_lora_weights.py")


def title():
    return "Check lora wights"


def create_ui():
    options = {}

    templates = TEMPLATES

    def run(args):
        status = run_python(script_file, templates, options, args)
        if status != 0:
            return "An error has occurred Please check the output."
        return "Finished successfully."

    with gr.Column():
        status = gr.Textbox("", show_label=False, interactive=False)
        start = gr.Button("Run", variant="primary")
        init = presets.create_ui("networks.check_lora_weights", templates, options)
        with gr.Box():
            ui.title("Options")
            with gr.Column():
                options_to_gradio(TEMPLATES, options)
        start.click(run, set(options.values()), status)
    init()
