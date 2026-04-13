import os
import json


def dump_to_file(name, data):
    """
    Dump data to a JSON file inside the `debug` folder.

    Parameters:
        name (str): Filename (e.g., 'voc-1.json').
        data (any): Data to dump (dict/list recommended for JSON).
    """

    # Ensure debug folder exists
    os.makedirs("debug", exist_ok=True)

    # Full path
    file_path = os.path.join("debug", name)

    # Dump JSON
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
