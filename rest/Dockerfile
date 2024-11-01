FROM python:3.10-slim-bookworm

WORKDIR /srv

# Copy requirements.txt into the container
COPY requirements.txt /srv/

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY rest-server.py /srv/

# Command to run the application
CMD ["python3", "rest-server.py"]
