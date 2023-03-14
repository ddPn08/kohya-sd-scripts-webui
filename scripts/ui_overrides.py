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
