from . import shared

def optional_network_modules():
    if shared.cmd_opts.locon:
        yield "locon.locon_kohya"

NETWORK_OPTIONS = {
    "network_module": {
        "type": list,
        "choices": ["networks.lora", *optional_network_modules()],
    }
}

OPTIMIZER_OPTIONS = {
    "optimizer_type": {
        "type": list,
        "choices": [
            "AdamW",
            "AdamW8bit",
            "Lion",
            "SGDNesterov",
            "SGDNesterov8bit",
            "DAdaptation",
            "AdaFactor",
        ],
    },
    "lr_scheduler": {
        "type": list,
        "choices": [
            "linear",
            "cosine",
            "cosine_with_restarts",
            "polynomial",
            "constant",
            "constant_with_warmup",
            "adafactor",
        ],
    },
}
