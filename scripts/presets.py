import argparse
import inspect
import os
from pathlib import Path
import toml
from kohya_ss.library import train_util, config_util

import gradio as gr

from scripts.shared import ROOT_DIR
from scripts.utilities import gradio_to_args

PRESET_DIR = os.path.join(ROOT_DIR, "presets")
PRESET_PATH = os.path.join(ROOT_DIR, "presets.json")


def get_arg_templates(fn):
    parser = argparse.ArgumentParser()
    args = [parser]
    sig = inspect.signature(fn)
    args.extend([True] * (len(sig.parameters) - 1))
    fn(*args)
    keys = [
        x.replace("--", "") for x in parser.__dict__["_option_string_actions"].keys()
    ]
    keys = [x for x in keys if x not in ["help", "-h"]]
    return keys, fn.__name__.replace("add_", "")


arguments_functions = [
    train_util.add_dataset_arguments,
    train_util.add_optimizer_arguments,
    train_util.add_sd_models_arguments,
    train_util.add_sd_saving_arguments,
    train_util.add_training_arguments,
    config_util.add_config_arguments,
]

arg_templates = [get_arg_templates(x) for x in arguments_functions]


def load_presets():
    obj = {}
    os.makedirs(PRESET_DIR, exist_ok=True)
    preset_names = os.listdir(PRESET_DIR)
    for preset_name in preset_names:
        preset_path = os.path.join(PRESET_DIR, preset_name)
        obj[preset_name] = {}
        for key in os.listdir(preset_path):
            key = key.replace(".toml", "")
            obj[preset_name][key] = load_preset(preset_name, key)
    return obj


def load_preset(key, name):
    filepath = os.path.join(PRESET_DIR, key, name + ".toml")
    if not os.path.exists(filepath):
        return {}
    with open(filepath, mode="r") as f:
        obj = toml.load(f)

    flatten = {}
    for k, v in obj.items():
        if not isinstance(v, dict):
            flatten[k] = v
        else:
            for k2, v2 in v.items():
                flatten[k2] = v2
    return flatten


def save_preset(key, name, value):
    obj = {}
    for k, v in value.items():
        if isinstance(v, Path):
            v = str(v)
        for (template, category) in arg_templates:
            if k in template:
                if category not in obj:
                    obj[category] = {}
                obj[category][k] = v
                break
        else:
            obj[k] = v

    filepath = os.path.join(PRESET_DIR, key, name + ".toml")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode="w") as f:
        toml.dump(obj, f)


def delete_preset(key, name):
    filepath = os.path.join(PRESET_DIR, key, name + ".toml")
    if os.path.exists(filepath):
        os.remove(filepath)


def create_ui(key, tmpls, opts):
    get_templates = lambda: tmpls() if callable(tmpls) else tmpls
    get_options = lambda: opts() if callable(opts) else opts

    presets = load_presets()

    if key not in presets:
        presets[key] = {}

    with gr.Box():
        with gr.Row():
            with gr.Column() as c:
                load_preset_button = gr.Button("Load preset", variant="primary")
                delete_preset_button = gr.Button("Delete preset")
            with gr.Column() as c:
                load_preset_name = gr.Dropdown(
                    list(presets[key].keys()), show_label=False
                ).style(container=False)
                reload_presets_button = gr.Button("🔄️")
            with gr.Column() as c:
                c.scale = 0.5
                save_preset_name = gr.Textbox(
                    "", placeholder="Preset name", lines=1, show_label=False
                ).style(container=False)
                save_preset_button = gr.Button("Save preset", variant="primary")

    def update_dropdown():
        presets = load_presets()
        if key not in presets:
            presets[key] = {}
        return gr.Dropdown.update(choices=list(presets[key].keys()))

    def _save_preset(args):
        name = args[save_preset_name]
        if not name:
            return update_dropdown()
        args = gradio_to_args(get_templates(), get_options(), args)
        save_preset(key, name, args)
        return update_dropdown()

    def _load_preset(args):
        name = args[load_preset_name]
        if not name:
            return update_dropdown()
        args = gradio_to_args(get_templates(), get_options(), args)
        preset = load_preset(key, name)
        result = []
        for k, _ in args.items():
            if k == load_preset_name:
                continue
            if k not in preset:
                result.append(None)
                continue
            v = preset[k]
            if type(v) == list:
                v = " ".join(v)
            result.append(v)
        return result[0] if len(result) == 1 else result

    def _delete_preset(name):
        if not name:
            return update_dropdown()
        delete_preset(key, name)
        return update_dropdown()

    def init():
        save_preset_button.click(
            _save_preset,
            set([save_preset_name, *get_options().values()]),
            [load_preset_name],
        )
        load_preset_button.click(
            _load_preset,
            set([load_preset_name, *get_options().values()]),
            [*get_options().values()],
        )
        delete_preset_button.click(_delete_preset, load_preset_name, [load_preset_name])
        reload_presets_button.click(
            update_dropdown, inputs=[], outputs=[load_preset_name]
        )

    return init
