import threading

from event_finder.ingress.websocker_listener import WebSocketListener
from event_finder.processing.message_processor import MessageProcessor
from event_finder.logging.loader import get_logger


class Application:
    _instance = None
    listener = None
    processor = None
    threads = None
    logger = get_logger()

    def __new__(cls, config):
        if cls._instance is None:
            cls._instance = super(Application, cls).__new__(cls)
            cls._instance._initialize(config)

        Application.logger.info("Started initializing the application")

        return cls._instance


    def _initialize(self, config):
        Application.config = config

        Application.listener = WebSocketListener(Application.config)
        Application.processor = MessageProcessor(Application.listener, Application.config)

        Application.threads = [
            threading.Thread(target=Application.listener.run),
            threading.Thread(target=Application.processor.run),
        ]

        Application.logger.info("Finished initializing the application.")


    def run(self):
        try:
            for thread in Application.threads:
                thread.start()

            Application.logger.info("Started the threads")

            for thread in Application.threads:
                thread.join()

            Application.logger.info("Application finished.")
        except Exception as e:
            Application.logger.info(f"Encountered as error in application {e}")
            for thread in Application.threads:
                thread.terminate()

        

    

   
