import os


def root_dir_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "../../..")
    return os.path.abspath(base_dir)

def path_relative_to_root(rel_path):
    return os.path.join(root_dir_path(), rel_path)