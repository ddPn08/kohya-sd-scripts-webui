import sys
import launch
import platform
import os
import shutil
import site
import glob
import re

dirname = os.path.dirname(__file__)
repo_dir = os.path.join(dirname, "kohya_ss")


def prepare_environment():
    torch_command = os.environ.get(
        "TORCH_COMMAND",
        "install torch==2.0.0+cu118 torchvision==0.15.1+cu118 --extra-index-url https://download.pytorch.org/whl/cu118",
    )
    sd_scripts_repo = os.environ.get("SD_SCRIPTS_REPO", "https://github.com/kohya-ss/sd-scripts.git")
    requirements_file = os.environ.get("REQS_FILE", "requirements.txt")

    sys.argv, skip_install = launch.extract_arg(sys.argv, "--skip-install")
    if skip_install:
        return

    sys.argv, disable_strict_version = launch.extract_arg(
        sys.argv, "--disable-strict-version"
    )
    sys.argv, skip_torch_cuda_test = launch.extract_arg(
        sys.argv, "--skip-torch-cuda-test"
    )
    sys.argv, update = launch.extract_arg(sys.argv, "--update")
    sys.argv, reinstall_xformers = launch.extract_arg(sys.argv, "--reinstall-xformers")
    sys.argv, reinstall_torch = launch.extract_arg(sys.argv, "--reinstall-torch")
    xformers = "--xformers" in sys.argv
    ngrok = "--ngrok" in sys.argv

    if (
        reinstall_torch
        or not launch.is_installed("torch")
        or not launch.is_installed("torchvision")
    ) and not disable_strict_version:
        launch.run(
            f'"{launch.python}" -m {torch_command}',
            "Installing torch and torchvision",
            "Couldn't install torch",
        )

    if not skip_torch_cuda_test:
        launch.run_python(
            "import torch; assert torch.cuda.is_available(), 'Torch is not able to use GPU; add --skip-torch-cuda-test to COMMANDLINE_ARGS variable to disable this check'"
        )

    if (not launch.is_installed("xformers") or reinstall_xformers) and xformers:
        launch.run_pip("install xformers --pre", "xformers")

    if update and os.path.exists(repo_dir):
        launch.run(f'cd "{repo_dir}" && {launch.git} fetch --prune')
        launch.run(f'cd "{repo_dir}" && {launch.git} reset --hard origin/main')
    elif not os.path.exists(repo_dir):
        launch.run(
            f'{launch.git} clone {sd_scripts_repo} "{repo_dir}"'
        )

    if not launch.is_installed("gradio"):
        launch.run_pip("install gradio==3.16.2", "gradio")

    if not launch.is_installed("pyngrok") and ngrok:
        launch.run_pip("install pyngrok", "ngrok")

    if platform.system() == "Linux":
        if not launch.is_installed("triton"):
            launch.run_pip("install triton", "triton")

    if disable_strict_version:
        with open(os.path.join(repo_dir, requirements_file), "r") as f:
            txt = f.read()
            requirements = [
                re.split("==|<|>", a)[0]
                for a in txt.split("\n")
                if (not a.startswith("#") and a != ".")
            ]
            requirements = " ".join(requirements)
            launch.run_pip(
                f'install "{requirements}" "{repo_dir}"',
                "requirements for kohya sd-scripts",
            )
    else:
        launch.run(
            f'cd "{repo_dir}" && "{launch.python}" -m pip install -r requirements.txt',
            desc=f"Installing requirements for kohya sd-scripts",
            errdesc=f"Couldn't install requirements for kohya sd-scripts",
        )

    if platform.system() == "Windows":
        for file in glob.glob(os.path.join(repo_dir, "bitsandbytes_windows", "*")):
            filename = os.path.basename(file)
            for dir in site.getsitepackages():
                outfile = (
                    os.path.join(dir, "bitsandbytes", "cuda_setup", filename)
                    if filename == "main.py"
                    else os.path.join(dir, "bitsandbytes", filename)
                )
                if not os.path.exists(os.path.dirname(outfile)):
                    continue
                shutil.copy(file, outfile)


if __name__ == "__main__":
    prepare_environment()
