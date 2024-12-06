from event_finder.config import loader
from event_finder.utils import path

def test_config():
    file_name = "sample_config.json"
    relative_path_from_root = f"tests/config/{file_name}"
    file_path = path.path_relative_to_root(relative_path_from_root)

    config  = loader.get_config(file_path)
    assert config.max_incoming_queue_size == 16
    assert config.max_processing_queue_size == 17
