FROM xserrat/facebook-demucs:latest

WORKDIR /data

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY worker.py .

ENTRYPOINT [ "python3", "worker.py" ]
