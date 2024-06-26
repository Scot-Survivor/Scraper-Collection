import os
import logging
import inspect


OUTPUT_DIRECTORY = "./outputs"
# Check if the output directory exists, if not create it
if not os.path.exists(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)


def write_output(filename, data):
    if len(data) <= 0:
        logging.warning("No data to write")
        return
    # Preface filename with calling filename
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    calling_filename = os.path.basename(module.__file__).split(".")[0]
    filename = f"{calling_filename}-{filename}"
    with open(f"{OUTPUT_DIRECTORY}/{filename}", "w") as f:
        f.write(data)
    f.close()
    logging.info(f"Output written to {OUTPUT_DIRECTORY}/{filename}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    write_output("test.txt", "Hello World")
