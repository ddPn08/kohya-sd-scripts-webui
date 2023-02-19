import json
import os

import gradio as gr

import scripts.shared as shared
from scripts.shared import ROOT_DIR
from scripts.utilities import gradio_to_args

DEFAULT_PRESET_PATH = os.path.join(ROOT_DIR, "built-in-presets.json")
PRESET_PATH = os.path.join(ROOT_DIR, "presets.json")


def load_presets():
    if not os.path.exists(PRESET_PATH):
        save_presets({})
    if not os.path.exists(DEFAULT_PRESET_PATH):
        save_presets({}, DEFAULT_PRESET_PATH)
    if shared.cmd_opts.hide_builtin_presets:
        obj = {}
    else:
        with open(DEFAULT_PRESET_PATH, mode="r") as f:
            obj = json.loads(f.read())
    with open(PRESET_PATH, mode="r") as f:
        obj = {**obj, **json.loads(f.read())}

    return obj


def save_presets(obj, path=PRESET_PATH):
    with open(path, mode="w") as f:
        f.write(json.dumps(obj))


def load_preset(key, name):
    obj = load_presets()
    if key not in obj:
        obj[key] = {}
    if name not in obj[key]:
        obj[key][name] = {}

    return obj[key][name]


def save_preset(key, name, value):
    obj = load_presets()
    if key not in obj:
        obj[key] = {}
    obj[key][name] = value
    save_presets(obj)


def delete_preset(key, name):
    obj = load_presets()
    if key not in obj:
        obj[key] = {}

    del obj[key][name]
    save_presets(obj)


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
            result.append(preset[k])
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
