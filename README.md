# monadical_event_finder
Python package for detecting chats related to event scheduling.

The incoming messages are streamed through a websocket and we process them one at a time. See the design document for more details. 

To run as a docker container, see the commands below. 

docker build -t monadical_event_finder .
docker volume create monadical_volume

docker run -v monadical_volume:/app/results monadical_event_finder

docker run --rm -it -v monadical_volume:/data alpine sh
cd data
