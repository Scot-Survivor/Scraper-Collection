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
    output_dir = os.path.join(OUTPUT_DIRECTORY, calling_filename)
    if not os.path.exists(os.path.join(output_dir)):
        os.makedirs(output_dir)
    filename = f"{filename}"
    with open(f"{output_dir}/{filename}", "w") as f:
        f.write(data)
    f.close()
    logging.info(f"Output written to {output_dir}/{filename}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    write_output("test.txt", "Hello World")
