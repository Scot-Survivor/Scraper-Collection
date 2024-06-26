import os
import inspect

def get_calling_filename():
    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0])
    return os.path.basename(module.__file__).split(".")[0]