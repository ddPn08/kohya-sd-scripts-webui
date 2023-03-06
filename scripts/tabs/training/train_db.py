import argparse

import gradio as gr

from kohya_ss.library import train_util, config_util
from scripts import presets, ui, ui_overrides
from scripts.runner import initialize_runner
from scripts.utilities import args_to_gradio, load_args_template, options_to_gradio


def title():
    return "Train dreambooth"


def create_ui():
    sd_models_arguments = argparse.ArgumentParser()
    dataset_arguments = argparse.ArgumentParser()
    training_arguments = argparse.ArgumentParser()
    sd_saving_arguments = argparse.ArgumentParser()
    optimizer_arguments = argparse.ArgumentParser()
    config_arguments = argparse.ArgumentParser()
    train_util.add_sd_models_arguments(sd_models_arguments)
    train_util.add_dataset_arguments(dataset_arguments, True, False, True)
    train_util.add_training_arguments(training_arguments, True)
    train_util.add_sd_saving_arguments(sd_saving_arguments)
    train_util.add_optimizer_arguments(optimizer_arguments)
    config_util.add_config_arguments(config_arguments)
    sd_models_options = {}
    dataset_options = {}
    training_options = {}
    sd_saving_options = {}
    optimizer_options = {}
    config_options = {}
    dreambooth_options = {}

    templates, script_file = load_args_template("train_db.py")

    get_options = lambda: {
        **sd_models_options,
        **dataset_options,
        **training_options,
        **sd_saving_options,
        **optimizer_options,
        **config_options,
        **dreambooth_options,
    }

    get_templates = lambda: {
        **sd_models_arguments.__dict__["_option_string_actions"],
        **dataset_arguments.__dict__["_option_string_actions"],
        **training_arguments.__dict__["_option_string_actions"],
        **sd_saving_arguments.__dict__["_option_string_actions"],
        **optimizer_arguments.__dict__["_option_string_actions"],
        **config_arguments.__dict__["_option_string_actions"],
        **templates,
    }

    with gr.Column():
        init_runner = initialize_runner(script_file, get_templates, get_options)
        with gr.Box():
            with gr.Row():
                init_ui = presets.create_ui("train_db", get_templates, get_options)
        with gr.Row():
            with gr.Group():
                with gr.Box():
                    ui.title("Dreambooth options")
                    options_to_gradio(templates, dreambooth_options)
                with gr.Box():
                    ui.title("Model options")
                    args_to_gradio(sd_models_arguments, sd_models_options)
                with gr.Box():
                    ui.title("Dataset options")
                    args_to_gradio(dataset_arguments, dataset_options)
                with gr.Box():
                    ui.title("Dataset Config options")
                    args_to_gradio(config_arguments, config_options)
            with gr.Box():
                ui.title("Training options")
                args_to_gradio(training_arguments, training_options)
            with gr.Group():
                with gr.Box():
                    ui.title("Save options")
                    args_to_gradio(sd_saving_arguments, sd_saving_options)
                with gr.Box():
                    ui.title("Optimizer options")
                    args_to_gradio(
                        optimizer_arguments,
                        optimizer_options,
                        ui_overrides.OPTIMIZER_OPTIONS,
                    )

    init_runner()
    init_ui()
