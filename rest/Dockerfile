FROM python:3.10-slim-bookworm

RUN pip3 install jsonpickle flask redis minio

WORKDIR /srv

COPY rest-server.py /srv
CMD ["python3", "rest-server.py"]
