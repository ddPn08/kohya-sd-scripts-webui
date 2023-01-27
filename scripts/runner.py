from scripts.utils import run_python


def initialize_runner(script_file, tmpls, opts):
    get_templates = lambda: tmpls() if callable(tmpls) else tmpls
    get_options = lambda: opts() if callable(opts) else opts

    def run(args):
        status = run_python(script_file, get_templates(), get_options(), args)
        if status != 0:
            return "An error has occurred Please check the output."
        return "Finished successfully."

    return run
