import sys

def append_to_sys_path(path):
    if path not in sys.path:
        sys.path.append(path)
