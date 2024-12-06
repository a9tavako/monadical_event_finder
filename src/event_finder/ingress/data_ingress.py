import asyncio
import json
import os
import re
import threading
import queue
import time
import traceback
from typing import List
import joblib
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import websockets
import config_loader
from event_finder.data.model import ChatRecord
from event_finder.utils.graph import get_connected_component
import event_finder.utils.path as path

config = config_loader.get_config()

incoming_queue = queue.Queue(config.max_incoming_queue_size)
processing_queue = queue.Queue()
is_websocket_closed = threading.Event()
stop_receiving = threading.Event()

sentence_encoder = SentenceTransformer('all-MiniLM-L6-v2')
intent_classifier = joblib.load("/Users/namra/Documents/monadical_project/ml_meeting_finder/source_code/models/random_forest_model.joblib")


async def listen():
    try: 
        async with websockets.connect(config.url) as websocket:
            while True and not stop_receiving.is_set():
                message = await websocket.recv()
                message_as_json = json.loads(message)
                data = ChatRecord(**message_as_json)
                try:
                    incoming_queue.put_nowait(data)
                except queue.Full:
                    print("Incoming Queue is full, dropping the message")
                    print(message)
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except Exception as e:
        print(f"Error in receving messages: {e}")
        traceback.print_exc()

    is_websocket_closed.set()


def listener():
    asyncio.run(listen())


def processor():
    try:
        while True:
            while not incoming_queue.empty():
                current_data = incoming_queue.get()
                add_to_processing_queue(current_data)

                msg = current_data.message
                encoding = sentence_encoder.encode(msg)
                is_about_scheduling = intent_classifier.predict([encoding])[0]

                if not is_about_scheduling:
                    continue
                
                msg_count_to_load = config.sliding_window_size
                while msg_count_to_load and not incoming_queue.empty():
                    next_data_item = incoming_queue.get()
                    add_to_processing_queue(next_data_item)
                    msg_count_to_load -= 1
                
                related_messages = find_related_messages(current_data, list(processing_queue.queue))
                save_messages(related_messages)

            if is_websocket_closed.is_set():
                print("Finished processing")
                break
    except Exception as e:
        print(f"Exception in processing: {e}")
        traceback.print_exc()
        stop_receiving.set()

def add_to_processing_queue(data_item):
    processing_queue.put(data_item)
    if processing_queue.qsize() > config.max_processing_queue_size:
        processing_queue.get()

def find_related_messages(
        target_message: ChatRecord, 
        data_messages: ChatRecord
) -> List[ChatRecord]:
    sentence_encoder = SentenceTransformer('all-MiniLM-L6-v2')

    msgs = [item.message for item in data_messages]
    target_message = target_message.message

    vectors = sentence_encoder.encode(msgs)
    cosine_sim_matrix = cosine_similarity(vectors)
    cosine_sim_list = cosine_sim_matrix.tolist()

    cut_off = 0.3
    adj_matrix = [[1 if val >= cut_off else 0 for val in row] for row in cosine_sim_list]

    target_index = msgs.index(target_message)

    connected_component = get_connected_component(target_index, adj_matrix)
    related_messages = [data_messages[index] for index in connected_component]
    return related_messages

def get_largest_number_in_filenames() -> int:
    results_folder = path.path_relative_to_root("results")
    os.chdir(results_folder)
    files = os.listdir()

    # Extract numbers from filenames of the specified form
    pattern = r"event_(\d+)\.json"
    numbers = []

    for file in files:
        match = re.search(pattern, file)
        if match:
            numbers.append(int(match.group(1)))

    # Find the largest number
    largest_number = max(numbers) if numbers else 0

    return largest_number


def save_messages(messages: List[ChatRecord]):
    largest_event_number = get_largest_number_in_filenames()
    current_event_number = largest_event_number + 1
    event_num_pad_with_zeros = str(current_event_number).zfill(config.event_file_digit_num)

    file_path= path.path_relative_to_root(f"results/event_{event_num_pad_with_zeros}.json")
    file_content = json.dumps({"lines" : [msg.model_dump() for msg in messages]}, indent=4)
    with open(file_path, "w", encoding = "utf-8") as file_handle:
        file_handle.write(file_content)
                    

listener_thread = threading.Thread(target=listener)
listener_thread.start()

processing_thread = threading.Thread(target=processor)
processing_thread.start()

# Wait for threads to complete
listener_thread.join()
processing_thread.join()
