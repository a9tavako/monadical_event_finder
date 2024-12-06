import threading
from event_finder.application import Application
from event_finder.config.loader import get_config
from event_finder.utils.path import path_relative_to_root
from event_finder import start
from event_finder.local_server.setup_local_server import start_local_server


def test_with_local_server():
    try:
        test_config_path = path_relative_to_root("tests/config/sample_config.json")
        test_config = get_config(test_config_path)

        server_thread = threading.Thread(target=start_local_server)
        server_thread.start()


        app = Application(test_config)
        app.run()

        server_thread.join()

        print("Finished testing")
    except Exception as e:
        print(f"Encountered error {e}")
        server_thread.terminate()
        

test_with_local_server()
