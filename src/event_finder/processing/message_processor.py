import threading
from queue import Queue
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from event_finder.logging.loader import get_logger
from event_finder.output.output_manager import OutputManager
from event_finder.utils import path
from event_finder.utils import graph
from event_finder.config import loader


class MessageProcessor:
    def __init__(self, websocket_listener, config):
        self.logger = get_logger()

        self.websocket_listener = websocket_listener
        self.incoming_queue = websocket_listener.get_incoming_queue()

        self.output_manager = OutputManager(config)

        self.intent_classifier = self.get_classifier()
        self.sentence_encoder = SentenceTransformer('all-MiniLM-L6-v2')

        self.processing_buffer = Queue()
        self.done_processing = threading.Event()

        self.config = config


    def get_classifier(self):
            relative_path = "src/event_finder/intent_classification/models/random_forest_model.joblib"
            abs_path = path.path_relative_to_root(relative_path)
            return joblib.load(abs_path)

    def find_related_messages(self, target_chat, buffered_chats):
        msgs = [item.message for item in buffered_chats]
        target_msg = target_chat.message

        vectors = self.sentence_encoder.encode(msgs)
        cosine_sim_matrix = cosine_similarity(vectors)
        cut_off = self.config.embedding_similarity_cutoff

        adj_matrix = [
            [1 if val >= cut_off else 0 for val in row] for row in cosine_sim_matrix
        ]

        target_index = msgs.index(target_msg)
        connected_component = graph.get_connected_component(target_index, adj_matrix)
        return [buffered_chats[index] for index in connected_component]

    def add_eject_processing_buffer(self, data_item):
        self.processing_buffer.put(data_item)
        if self.processing_buffer.qsize() > self.config.max_processing_queue_size:
            self.processing_buffer.get()

    def start_processing(self):
        self.logger.info("Started processing.")
        while True:
            if not self.incoming_queue.empty():
                current_chat = self.incoming_queue.get()
                self.add_eject_processing_buffer(current_chat)

                encoding = self.sentence_encoder.encode([current_chat.message])

                if not self.intent_classifier.predict(encoding)[0]:
                    continue

                self.logger.info("Found a message relative to event scheduling.")

                num_additional_messages = (self.config.max_processing_queue_size) / 2

                self.read_next_n_chat_records(num_additional_messages)

                related_messages = self.find_related_messages(
                    current_chat, list(self.processing_buffer.queue)
                )
                self.output_manager.save_messages(related_messages)

                self.repopulate_buffer()

            if self.incoming_queue.empty() and self.websocket_listener.is_done_listening():
                break

        self.logger.info("Finished processing.")

    def read_next_n_chat_records(self, count: int):
        while count and not self.incoming_queue.empty():
            chat = self.incoming_queue.get()
            self.add_eject_processing_buffer(chat)
            count -= 1
    
    def repopulate_buffer(self):
        self.read_next_n_chat_records(self.config.max_processing_queue_size)

    def run(self):
        self.start_processing()