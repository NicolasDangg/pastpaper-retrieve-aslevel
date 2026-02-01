import os
import re


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\s.-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name


def menu(title, options):
    print(f"\n{title}")
    for key, value in options.items():
        if isinstance(value, tuple):
            print(f"{key}) {value[0]} ({value[1]})")
        else:
            print(f"{key}) {value}")
    return input("> ").strip()
