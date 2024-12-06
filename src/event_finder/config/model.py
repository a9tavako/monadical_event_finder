from pydantic import BaseModel

class Config(BaseModel):
    embedding_similarity_cutoff: float
    max_time_gap_in_group_minutes: int
    max_incoming_queue_size: int
    max_processing_queue_size: int
    sliding_window_size: int
    url: str
    event_file_digit_num: int
    results_path: str
