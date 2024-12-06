FROM python:3.10-slim

WORKDIR /app

COPY setup.py /app/
COPY src /app/src
COPY results /app/results

RUN pip install -e .

CMD ["python", "-m", "event_finder.start"]
