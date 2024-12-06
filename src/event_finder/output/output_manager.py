import json
import os
import re

from event_finder.config import loader
from event_finder.data.model import ChatRecord
from event_finder.logging.loader import get_logger
from event_finder.utils.path import path_relative_to_root


class OutputManager:
    def __init__(self, configuration = loader.get_config):
        self.config = configuration
        self.logger = get_logger()


    def get_largest_number_in_filenames(self) -> int:
        results_folder = path_relative_to_root(self.config.results_path)
        os.chdir(results_folder)
        files = os.listdir()

        pattern = r"event_(\d+)\.json"
        numbers = [int(match.group(1)) for file in files if (match := re.search(pattern, file))]

        return max(numbers) if numbers else 0

    def save_messages(self, messages: list[ChatRecord]):
        largest_event_number = self.get_largest_number_in_filenames()
        current_event_number = largest_event_number + 1
        event_num_padded = str(current_event_number).zfill(self.config.event_file_digit_num)

        file_path = path_relative_to_root(f"{self.config.results_path}/event_{event_num_padded}.json")
        file_content = json.dumps({"lines": [msg.model_dump() for msg in messages]}, indent=4)

        self.logger.info(f"Writing event messages to file {file_path}")

        with open(file_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(file_content)
