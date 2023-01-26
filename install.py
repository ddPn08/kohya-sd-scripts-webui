import launch
import platform
import os
import shutil
import site
import glob
import re

dirname = os.path.dirname(__file__)
repo_dir = os.path.join(dirname, "kohya_ss")


def is_webui_extension():
    return __name__ == "__main__"


def torch_version():
    try:
        import torch

        return torch.__version__
    except Exception:
        return None


def xformers_version():
    try:
        import xformers

        return xformers.__version__
    except Exception:
        return None


def install_requirements():
    if is_webui_extension():
        with open(os.path.join(repo_dir, "requirements.txt"), "r") as f:
            txt = f.read()
            requirements = [
                re.split("==|<|>", a)[0]
                for a in txt.split("\n")
                if (not a.startswith("#") and a != ".")
            ]
            requirements = " ".join(requirements)
            launch.run_pip(
                f"install {requirements} {repo_dir}",
                "requirements for kohya sd-scripts",
            )
    else:
        launch.run(
            f"cd {repo_dir} && install -r requirements.txt",
            desc=f"Installing requirements for kohya sd-scripts",
            errdesc=f"Couldn't install requirements for kohya sd-scripts",
        )


def prepare_environment():
    launch.run(f"{launch.python} -m pip --version")
    if os.path.exists(repo_dir):
        launch.run(f"cd {repo_dir} && {launch.git} fetch --prune")
        launch.run(f"cd {repo_dir} && {launch.git} reset --hard origin/main")
    else:
        launch.run(
            f"{launch.git} clone https://github.com/kohya-ss/sd-scripts.git {repo_dir}"
        )

    install_requirements()

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
