#!/usr/bin/env python3

from flask import Flask, request, Response
import jsonpickle
import base64
import json
import os
import redis
import io
from minio import Minio

# Redis setup
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

# Flask app
server_host = os.getenv("FLASK_HOST", "0.0.0.0")
server_port = os.getenv("FLASK_PORT", "5000")
app = Flask(__name__)

# MinIO setup
minio_host = os.getenv("MINIO_HOST", "minio-proj.minio-ns.svc.cluster.local:9000")
minio_user = os.getenv("MINIO_USER", "rootuser")
minio_pass = os.getenv("MINIO_PASSWD", "rootpass123")

minio_client = Minio(minio_host,
                     secure=False,
                     access_key=minio_user,
                     secret_key=minio_pass)

# Define buckets
queue_bucket = "queue"
output_bucket = "output"

# Ensure buckets exist
if not minio_client.bucket_exists(queue_bucket):
    minio_client.make_bucket(queue_bucket)
if not minio_client.bucket_exists(output_bucket):
    minio_client.make_bucket(output_bucket)

@app.route('/apiv1/separate', methods=['POST'])
def separate():
    r = request
    data = json.loads(r.get_data())
    mp3_data = base64.b64decode(data['mp3'])
    data_length = len(mp3_data)

    try:
        mp3_name = data['callback']['data']['mp3']
        name_hash = hash(mp3_name)
        redis_conn.rpush('mp3_list', name_hash)
        
        minio_client.put_object(queue_bucket, str(name_hash), io.BytesIO(mp3_data), data_length, content_type="audio/mpeg")

        response = {'message': name_hash}
        return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

    except Exception as e:
        response = {'message': 'error not pushed', 'details': str(e)}
        return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

@app.route('/apiv1/queue', methods=['GET'])
def get_queue():
    contents = redis_conn.lrange('mp3_list', 0, -1)
    all_responses = [str(jsonpickle.decode(item)) for item in contents]
    
    response = {"redis_queue": all_responses}
    return Response(response=jsonpickle.encode(response), status=200, mimetype="application/json")

app.run(host=server_host, port=server_port)
