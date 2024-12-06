import asyncio
import json
import threading
import websockets
from queue import Queue
from event_finder.data.model import ChatRecord
from event_finder.config import loader
from event_finder.logging.loader import get_logger


class WebSocketListener:
    def __init__(self, config):
        self.logger = get_logger()
        self.config = config
        self.incoming_queue = Queue(self.config.max_incoming_queue_size)
        self.is_websocket_closed = threading.Event()

    async def listen(self):
        try:
            async with websockets.connect(self.config.url) as websocket:
                while not self.is_websocket_closed.is_set():
                    message = await websocket.recv()
                    message_as_json = json.loads(message)
                    data = ChatRecord(**message_as_json)
                    try:
                        self.incoming_queue.put_nowait(data)
                    except Queue.Full:
                        print("Incoming queue is full, dropping the message.")
                        print(message)
        except websockets.exceptions.ConnectionClosedOK:
            self.logger.info("Connection closed gracefully.")
        except Exception as e:
            self.logger.info(f"Error in receiving messages: {e}")
            print(f"Error in receiving messages: {e}")
        finally:
            self.is_websocket_closed.set()
            self.logger.info("Closed the socket")

    def run(self):
        asyncio.run(self.listen())

    def get_incoming_queue(self):
        return self.incoming_queue
    
    def is_done_listening(self):
        return self.is_websocket_closed.is_set()