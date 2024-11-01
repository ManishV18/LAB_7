# Base image
FROM python:3.10-slim-bookworm

# Update label
LABEL MAINTAINER="your_email@example.com"

# Install dependencies
COPY requirements.txt /srv
RUN pip3 install -r /srv/requirements.txt

# Set working directory and copy application
WORKDIR /srv
COPY rest-server.py /srv

# Run the Flask app
CMD ["python3", "rest-server.py"]
