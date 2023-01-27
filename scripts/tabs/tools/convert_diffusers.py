import gradio as gr

from scripts import presets, ui
from scripts.utils import load_args_template, options_to_gradio, run_python

TEMPLATES, script_file = load_args_template(
    "tools", "convert_diffusers20_original_sd.py"
)


def title():
    return "Convert Diffusers"


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
        with gr.Box():
            with gr.Row():
                init = presets.create_ui(
                    "convert_diffusers20_original_sd", templates, options
                )
        with gr.Box():
            ui.title("Options")
            with gr.Column():
                options_to_gradio(TEMPLATES, options)
        start.click(run, set(options.values()), status)
    init()
