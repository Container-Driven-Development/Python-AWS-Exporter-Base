import os
import boto3
from prometheus_client import start_http_server, Gauge
import time
from datetime import datetime,timedelta
import logging
from pythonjsonlogger import jsonlogger

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

logger.info({"state": "starting"})

# Create a Gauge metric for Prometheus
s3_bucket_folder_size = Gauge('s3_bucket_folder_size', 'Size of the S3 bucket folders', ['bucket', 'folder'])

def parse_time_string(time_string):
    value = int(time_string[:-1])
    unit = time_string[-1]

    if unit == 's':
        return timedelta(seconds=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    elif unit == 'h':
        return timedelta(hours=value)
    else:
        raise ValueError(f"Unknown time unit: {unit}")

def get_s3_bucket_folder_sizes(bucket_name):
    logger.info({"state": "processing", "bucket": bucket_name, "message": "Getting folder sizes"})
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')

    folder_sizes = {}

    for page in paginator.paginate(Bucket=bucket_name, Delimiter='/'):
        for prefix in page.get('CommonPrefixes', []):
            folder = prefix['Prefix']
            size = 0
            for obj in s3.list_objects_v2(Bucket=bucket_name, Prefix=folder)['Contents']:
                size += obj['Size']
            folder_sizes[folder.rstrip('/')] = size

    return folder_sizes

def update_metrics(bucket_names):
    for bucket in bucket_names:
        folder_sizes = get_s3_bucket_folder_sizes(bucket)
        for folder, size in folder_sizes.items():
            s3_bucket_folder_size.labels(bucket=bucket, folder=folder).set(size)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)

    # List of bucket names
    buckets = os.environ.get('S3_BUCKET_NAMES').split(',')

    # Update metrics every minute
    while True:
        update_metrics(buckets)
        time.sleep(parse_time_string(os.environ.get('METRICS_SCRAPE_INTERVAL')).seconds)
