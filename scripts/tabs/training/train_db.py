import argparse

import gradio as gr

from kohya_ss import train_db
from kohya_ss.library import train_util
from scripts import presets, ui
from scripts.utils import (args_to_gradio, gradio_to_args, load_args_template,
                           make_args, options_to_gradio, run_python)

TEMPLATES, script_file = load_args_template("train_db.py")


def title():
    return "Train dreambooth"


def create_ui():
    sd_models_arguments = argparse.ArgumentParser()
    dataset_arguments = argparse.ArgumentParser()
    training_arguments = argparse.ArgumentParser()
    sd_saving_arguments = argparse.ArgumentParser()
    train_util.add_sd_models_arguments(sd_models_arguments)
    train_util.add_dataset_arguments(dataset_arguments, True, False)
    train_util.add_training_arguments(training_arguments, True)
    train_util.add_sd_saving_arguments(sd_saving_arguments)
    sd_models_options = {}
    dataset_options = {}
    training_options = {}
    sd_saving_options = {}
    dreambooth_options = {}

    options = lambda: {
        **sd_models_options,
        **dataset_options,
        **training_options,
        **sd_saving_options,
        **dreambooth_options,
    }

    templates = lambda: {
        **sd_models_arguments.__dict__["_option_string_actions"],
        **dataset_arguments.__dict__["_option_string_actions"],
        **training_arguments.__dict__["_option_string_actions"],
        **sd_saving_arguments.__dict__["_option_string_actions"],
        **TEMPLATES,
    }

    def train(args):
        args = gradio_to_args(templates(), options(), args)
        args = make_args(args)
        status = run_python(f"{script_file} {args}")
        if status != 0:
            return "An error has occurred Please check the output."
        return "Finished successfully."

    with gr.Column():
        status = gr.Textbox("", show_label=False, interactive=False)
        train_button = gr.Button("Run", variant="primary")
        with gr.Box():
            with gr.Row():
                init = presets.create_ui("train_db", templates, options)
        with gr.Row():
            with gr.Group():
                with gr.Box():
                    ui.title("Dreambooth options")
                    options_to_gradio(TEMPLATES, dreambooth_options)
                with gr.Box():
                    ui.title("Model options")
                    args_to_gradio(sd_models_arguments, sd_models_options)
                with gr.Box():
                    ui.title("Save options")
                    args_to_gradio(sd_saving_arguments, sd_saving_options)
                with gr.Box():
                    ui.title("Dataset options")
                    args_to_gradio(dataset_arguments, dataset_options)
            with gr.Box():
                ui.title("Trianing options")
                args_to_gradio(training_arguments, training_options)
        train_button.click(train, set(options().values()), status)
    init()
