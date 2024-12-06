from functools import lru_cache
import json
from event_finder.config.model import Config
from event_finder.utils.path import path_relative_to_root

@lru_cache
def get_config(config_path = "") -> Config:
    if not config_path:
        config_path = path_relative_to_root("src/event_finder/config/config.json")
    with open(config_path, "r") as file:
        config_as_json = json.load(file)

    return Config(**config_as_json)
