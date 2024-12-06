import asyncio
import json
import websockets

from event_finder.utils.path import path_relative_to_root

port = 8000
host = "localhost"

shutdown_event = asyncio.Event()

def load_sample_data():
    file_path = path_relative_to_root("tests/monadical_data_1.txt")
    data = []
    with open(file_path, "r", encoding = "utf-8") as file_handle:
        while True:
            line = file_handle.readline()
            if not line:
                break
            msg_as_str = line.strip()
            msg_as_json = json.loads(msg_as_str)
            data.append(msg_as_json)

    return data

async def handler(websocket):
    try:
        print(f"New connection from: {websocket.remote_address}")
        msgs = load_sample_data()
        for item in msgs:
            await websocket.send(json.dumps(item))
        shutdown_event.set()  
        print("Finished sending the data")
    except websockets.ConnectionClosed:
        print("Connection closed")
        shutdown_event.set()  
    except Exception as e:
        print(f"An error occurred: {e}")
        shutdown_event.set()  

async def main():
    server = await websockets.serve(handler, host, port)
    print(f"Server is listening on {host}:{port}")
    
    async def shutdown():
        print("Shutting down server...")
        server.close()
        await server.wait_closed()

    try:
        await shutdown_event.wait()
    finally:
        await shutdown()

def start_local_server():
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
