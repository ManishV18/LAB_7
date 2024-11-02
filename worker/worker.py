import os
import subprocess
import redis
from minio import Minio

print("Worker initialized...")

# Establish Redis connection
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_connection = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

# Configure MinIO client
minio_host = os.getenv("MINIO_HOST", "localhost:9000")
minio_user = os.getenv("MINIO_USER", "rootuser")
minio_password = os.getenv("MINIO_PASSWD", "rootpass123")

minio_client = Minio(
    minio_host,
    secure=False,
    access_key=minio_user,
    secret_key=minio_password
)

# Define queue and output bucket names
input_queue = "queue"
output_bucket = "output"

while True:
    # Wait for a new MP3 file in the Redis list
    mp3_item = redis_connection.blpop('mp3_list')
    mp3_filename = mp3_item[1]

    print(f"Processing file: {mp3_filename}")

    # Download the MP3 file from MinIO
    minio_client.fget_object(input_queue, mp3_filename, f"/data/input/{mp3_filename}")

    # Execute the Demucs separation command
    separation_command = f"python3 -m demucs -d cpu --out /data/output --mp3 /data/input/{mp3_filename}"
    execution_result = os.system(separation_command)

    # Check the result of the separation process
    if execution_result == 0:
        print("Track successfully separated.")
    else:
        print(f"Error encountered during separation: {execution_result}")

    # Upload separated tracks back to MinIO
    base_output_path = f"/data/output/mdx_extra_q/{mp3_filename}"
    minio_client.fput_object(output_bucket, f"bass_{mp3_filename}.mp3", f"{base_output_path}/bass.mp3")
    minio_client.fput_object(output_bucket, f"vocal_{mp3_filename}.mp3", f"{base_output_path}/vocals.mp3")
    minio_client.fput_object(output_bucket, f"drums_{mp3_filename}.mp3", f"{base_output_path}/drums.mp3")
    minio_client.fput_object(output_bucket, f"other_{mp3_filename}.mp3", f"{base_output_path}/other.mp3")
