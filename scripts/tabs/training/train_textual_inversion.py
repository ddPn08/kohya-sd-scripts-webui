import argparse

import gradio as gr

from kohya_ss.library import train_util
from scripts import presets, ui
from scripts.runner import initialize_runner
from scripts.utilities import args_to_gradio, load_args_template, options_to_gradio


def title():
    return "Train textual inversion"


def create_ui():
    sd_models_arguments = argparse.ArgumentParser()
    dataset_arguments = argparse.ArgumentParser()
    training_arguments = argparse.ArgumentParser()
    train_util.add_sd_models_arguments(sd_models_arguments)
    train_util.add_dataset_arguments(dataset_arguments, True, True, False)
    train_util.add_training_arguments(training_arguments, True)
    sd_models_options = {}
    dataset_options = {}
    training_options = {}
    ti_options = {}

    templates, script_file = load_args_template("train_textual_inversion.py")

    get_options = lambda: {
        **sd_models_options,
        **dataset_options,
        **training_options,
        **ti_options,
    }

    get_templates = lambda: {
        **sd_models_arguments.__dict__["_option_string_actions"],
        **dataset_arguments.__dict__["_option_string_actions"],
        **training_arguments.__dict__["_option_string_actions"],
        **templates,
    }

    with gr.Column():
        init_runner = initialize_runner(script_file, get_templates, get_options)
        with gr.Box():
            with gr.Row():
                init_ui = presets.create_ui(
                    "train_textual_inversion", get_templates, get_options
                )
        with gr.Row():
            with gr.Group():
                with gr.Box():
                    ui.title("Textual inversion options")
                    options_to_gradio(templates, ti_options)
                with gr.Box():
                    ui.title("Model options")
                    args_to_gradio(sd_models_arguments, sd_models_options)
                with gr.Box():
                    ui.title("Dataset options")
                    args_to_gradio(dataset_arguments, dataset_options)
            with gr.Box():
                ui.title("Trianing options")
                args_to_gradio(training_arguments, training_options)

    init_runner()
    init_ui()
