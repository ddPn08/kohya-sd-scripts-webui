import argparse

import gradio as gr

from kohya_ss import train_db
from kohya_ss.library import train_util
from scripts import presets, ui
from scripts.utils import (args_to_gradio, gradio_to_args, load_args_template,
                           options_to_gradio)

TEMPLATES = load_args_template("train_db.py")


def title():
    return "Train dreambooth"


def create_ui():
    sd_models_arguments = argparse.ArgumentParser()
    dataset_arguments = argparse.ArgumentParser()
    training_arguments = argparse.ArgumentParser()
    train_util.add_sd_models_arguments(sd_models_arguments)
    train_util.add_dataset_arguments(dataset_arguments, True, False)
    train_util.add_training_arguments(training_arguments, True)
    sd_models_options = {}
    dataset_options = {}
    training_options = {}
    dreambooth_options = {}

    options = lambda: {
        **sd_models_options,
        **dataset_options,
        **training_options,
        **dreambooth_options,
    }

    templates = lambda: {
        **sd_models_arguments.__dict__["_option_string_actions"],
        **dataset_arguments.__dict__["_option_string_actions"],
        **training_arguments.__dict__["_option_string_actions"],
        **TEMPLATES,
    }

    def train(args):
        args = gradio_to_args(templates(), options(), args)
        try:
            train_db.train(argparse.Namespace(**args))
        except Exception as e:
            return e.args
        return "Finished."

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
                    ui.title("Dataset options")
                    args_to_gradio(dataset_arguments, dataset_options)
            with gr.Box():
                ui.title("Trianing options")
                args_to_gradio(training_arguments, training_options)
        train_button.click(train, set(options().values()), status)
    init()
