import io
import sys

import fastapi
import gradio as gr
from pydantic import BaseModel, Field

import scripts.shared as shared
from scripts.utilities import run_python

proc = None
outputs = []


def alive():
    return proc is not None


def initialize_runner(script_file, tmpls, opts):
    run_button = gr.Button(
        "Run",
        variant="primary",
        elem_id=f"kohya_sd_webui__{shared.current_tab}_run_button",
    )
    stop_button = gr.Button(
        "Stop",
        variant="secondary",
        elem_id=f"kohya_sd_webui__{shared.current_tab}_stop_button",
    )
    get_templates = lambda: tmpls() if callable(tmpls) else tmpls
    get_options = lambda: opts() if callable(opts) else opts

    def run(args):
        global proc
        global outputs
        if alive():
            return
        proc = run_python(script_file, get_templates(), get_options(), args)
        reader = io.TextIOWrapper(proc.stdout, encoding="utf-8-sig")
        line = ""
        while proc is not None and proc.poll() is None:
            try:
                char = reader.read(1)
                if shared.cmd_opts.enable_console_log:
                    sys.stdout.write(char)
                if char == "\n":
                    outputs.append(line)
                    line = ""
                    continue
                line += char
            except:
                ()
        proc = None

    def stop():
        global proc
        print("killed the running process")
        proc.kill()
        proc = None

    def init():
        run_button.click(
            run,
            set(get_options().values()),
        )
        stop_button.click(stop)

    return init


class GetOutputRequest(BaseModel):
    output_index: int = Field(
        default=0, title="Index of the beginning of the log to retrieve"
    )


class GetOutputResponse(BaseModel):
    outputs: list = Field(title="List of terminal output")


class ProcessAliveResponse(BaseModel):
    alive: bool = Field(title="Whether the process is running.")


def api_get_outputs(req: GetOutputRequest):
    i = req.output_index
    out = outputs[i:] if len(outputs) > i else []
    return GetOutputResponse(outputs=out)


def api_get_isalive(req: fastapi.Request):
    return ProcessAliveResponse(alive=alive())


def initialize_api(app: fastapi.FastAPI):
    app.add_api_route(
        "/internal/extensions/kohya-sd-scripts-webui/terminal/outputs",
        api_get_outputs,
        methods=["POST"],
        response_model=GetOutputResponse,
    )
    app.add_api_route(
        "/internal/extensions/kohya-sd-scripts-webui/process/alive",
        api_get_isalive,
        methods=["GET"],
        response_model=ProcessAliveResponse,
    )
