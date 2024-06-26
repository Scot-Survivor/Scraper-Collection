import os
import logging
import json

from utils.misc import get_calling_filename

OUTPUT_DIRECTORY = "./outputs"
# Check if the output directory exists, if not create it
if not os.path.exists(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)


def write_output(filename, data):
    if len(data) <= 0:
        logging.warning("No data to write")
        return
    # Preface filename with calling filename
    calling_filename = get_calling_filename()
    output_dir = os.path.join(OUTPUT_DIRECTORY, calling_filename)
    if not os.path.exists(os.path.join(output_dir)):
        os.makedirs(output_dir)
    filename = f"{filename}"
    with open(f"{output_dir}/{filename}", "w") as f:
        f.write(data)
    f.close()
    logging.info(f"Output written to {output_dir}/{filename}")


def save_settings(data: dict):
    logging.debug(f"Saving settings for {get_calling_filename()}: {data}")
    settings_name = get_calling_filename() + "_settings.json"
    with open(f"{OUTPUT_DIRECTORY}/{settings_name}", "w") as f:
        json.dump(data, f)
    f.close()
    logging.info(f"Settings written to {OUTPUT_DIRECTORY}/{settings_name}")


def load_settings():
    settings_name = get_calling_filename() + "_settings.json"
    try:
        with open(f"{OUTPUT_DIRECTORY}/{settings_name}", "r") as f:
            data = json.load(f)
        f.close()
        logging.debug(f"Loaded settings for {get_calling_filename()}: {data}")
        return data
    except FileNotFoundError:
        logging.warning(f"No settings found for {get_calling_filename()}")
        return {}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    write_output("test.txt", "Hello World")
