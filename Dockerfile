FROM python:3.10-slim

WORKDIR /app

COPY setup.py /app/
COPY src /app/src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install .

CMD ["python", "-m", "event_finder.start"]
