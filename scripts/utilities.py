import ast
import importlib
import os
import subprocess
import sys

import gradio as gr

import scripts.shared as shared
from scripts.shared import ROOT_DIR

python = sys.executable


def path_to_module(filepath):
    return (
        os.path.relpath(filepath, ROOT_DIR).replace(os.path.sep, ".").replace(".py", "")
    )


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def literal_eval(v, module=None):
    if v == "str":
        return str
    elif v == "int":
        return int
    elif v == "float":
        return float
    elif v == list:
        return list
    else:
        if module:
            try:
                m = importlib.import_module(module)
                if hasattr(m, v):
                    return getattr(m, v)
            except:
                ()

        return ast.literal_eval(v)


def compile_arg_parser(txt, module_path=None):
    in_parser = False
    parsers = {}
    args = []
    arg = ""
    in_list = False
    in_str = None

    def compile(arg):
        arg = arg.strip()
        matches = arg.split("=")

        if len(matches) > 1:
            k = "".join(matches[:1])
            v = literal_eval("".join(matches[1:]), module_path)
            return (k, v)
        else:
            return literal_eval(arg, module_path)

    for line in txt.split("\n"):
        line = line.split("#")[0]

        if "parser.add_argument(" in line:
            in_parser = True
            line = line.replace("parser.add_argument(", "")

        if not in_parser:
            continue

        for c in line:

            if in_str is None and c == ")":
                if arg.strip():
                    args.append(compile(arg))
                in_parser = False
                [dest, *others] = args
                parsers[dest] = {"dest": dest.replace("--", ""), **dict(others)}
                arg = ""
                args = []
                break

            if c == "[":
                in_list = True
            elif c == "]":
                in_list = False
            if c == '"' or c == "'":
                if in_str is not None and in_str == c:
                    in_str = None
                elif in_str is None:
                    in_str = c

            if c == "," and not in_list and in_str is None:
                args.append(compile(arg))
                arg = ""
                continue

            arg += c

    if arg.strip():
        args.append(compile(arg))
    return parsers


def load_args_template(*filename):
    repo_dir = os.path.join(ROOT_DIR, "kohya_ss")
    filepath = os.path.join(repo_dir, *filename)
    with open(filepath, mode="r", encoding="utf-8_sig") as f:
        lines = f.readlines()
        add = False
        txt = ""
        for line in lines:
            if add == True:
                txt += line
            if "def setup_parser()" in line:
                add = True
                continue
    return compile_arg_parser(txt, path_to_module(filepath)), filepath


def check_key(d, k):
    return k in d and d[k] is not None


def get_arg_type(d):
    if check_key(d, "choices"):
        return list
    if check_key(d, "type"):
        return d["type"]
    if check_key(d, "action") and (
        d["action"] == "store_true" or d["action"] == "store_false"
    ):
        return bool
    if check_key(d, "const") and type(d["const"]) == bool:
        return bool
    return str


def options_to_gradio(options, out, overrides={}):
    for _, item in options.items():
        item = item.__dict__ if hasattr(item, "__dict__") else item
        key = item["dest"]
        if key == "help":
            continue
        override = overrides[key] if key in overrides else {}
        component = None

        help = item["help"] if "help" in item else ""
        id = f"kohya_sd_webui__{shared.current_tab.replace('.', '_')}_{key}"
        type = override["type"] if "type" in override else get_arg_type(item)
        if type == list:
            choices = [
                c if c is not None else "None"
                for c in (
                    override["choices"] if "choices" in override else item["choices"]
                )
            ]
            component = gr.Radio(
                choices=choices,
                value=item["default"] if check_key(item, "default") else choices[0],
                label=key,
                elem_id=id,
                interactive=True,
            )
        elif type == bool:
            component = gr.Checkbox(
                value=item["default"] if check_key(item, "default") else False,
                label=key,
                elem_id=id,
                interactive=True,
            )
        else:
            component = gr.Textbox(
                value=item["default"] if check_key(item, "default") else "",
                label=key,
                elem_id=id,
                interactive=True,
            ).style()

        shared.help_title_map[id] = help
        out[key] = component


def args_to_gradio(args, out, overrides={}):
    options_to_gradio(args.__dict__["_option_string_actions"], out, overrides)


def gradio_to_args(arguments, options, args, strarg=False):
    def find_arg(key):
        for k, arg in arguments.items():
            arg = arg.__dict__ if hasattr(arg, "__dict__") else arg
            if arg["dest"] == key:
                return k, arg
        return None, None

    def get_value(key):
        item = args[options[key]]
        raw_key, arg = find_arg(key)
        arg_type = get_arg_type(arg)
        multiple = "nargs" in arg and arg["nargs"] == "*"

        def set_type(x):
            if x is None or x == "None":
                return None
            elif arg_type is None:
                return x
            elif arg_type == list:
                return x
            return arg_type(x)

        if multiple and item is None or item == "":
            return raw_key, None

        return raw_key, (
            [set_type(x) for x in item.split(" ")] if multiple else set_type(item)
        )

    if strarg:
        main = []
        optional = {}

        for k in options:
            key, v = get_value(k)
            if key.startswith("--"):
                key = k.replace("--", "")
                optional[key] = v
            else:
                main.append(v)

        main = [x for x in main if x is not None]

        return main, optional
    else:
        result = {}
        for k in options:
            _, v = get_value(k)
            result[k] = v
        return result


def make_args(d):
    arguments = []
    for k, v in d.items():
        if type(v) == bool:
            arguments.append(f"--{k}" if v else "")
        elif type(v) == list and len(v) > 0:
            arguments.extend([f"--{k}", *v])
        elif type(v) == str and v:
            arguments.extend([f"--{k}", f"{v}"])
        elif v:
            arguments.extend([f"--{k}", f"{v}"])
    return arguments


def run_python(script, templates, options, args):
    main, optional = gradio_to_args(templates, options, args, strarg=True)
    args = [x for x in [*main, *make_args(optional)] if x]
    proc_args = [python, "-u", script, *args]
    print("Start process: ", " ".join(proc_args))

    ps = subprocess.Popen(
        proc_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=os.path.join(ROOT_DIR, "kohya_ss"),
    )
    return ps
