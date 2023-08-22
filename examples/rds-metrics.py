import boto3
from prometheus_client import Gauge, start_http_server
import time
from datetime import datetime,timedelta
import os
import logging
from pythonjsonlogger import jsonlogger

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

logger.info({"state": "starting"})

# Create a CloudWatch client
cloudwatch = boto3.client('cloudwatch', region_name=os.environ.get('AWS_REGION'))

# Create Prometheus metrics
cpu_utilization_gauge = Gauge('AWS_RDS_CPUUtilization', 'CPU Utilization of RDS instance', ['DBInstanceIdentifier'])
database_connections_gauge = Gauge('AWS_RDS_DatabaseConnections', 'Database Connections of RDS instance', ['DBInstanceIdentifier'])
volume_bytes_used_gauge = Gauge('AWS_RDS_VolumeBytesUsed', 'Volume Bytes Used of RDS instance', ['DBInstanceIdentifier'])
cpu_credits_gauge = Gauge('AWS_RDS_CPUcredits', 'CPU credits of RDS instance', ['DBInstanceIdentifier'])
freeable_memory_gauge = Gauge('AWS_RDS_FreeableMemory', 'Freeable Memory of RDS instance', ['DBInstanceIdentifier'])

# Start the HTTP server to expose the metrics
start_http_server(8000)

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


def get_metric_value(metric_name, db_instance_id):
    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'm1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/RDS',
                        'MetricName': metric_name,
                        'Dimensions': [
                            {
                                'Name': 'DBInstanceIdentifier',
                                'Value': db_instance_id
                            },
                        ]
                    },
                    'Period': 300,
                    'Stat': 'Average',
                },
                'ReturnData': True,
            },
        ],
        StartTime=(datetime.now() - parse_time_string(os.environ.get('METRICS_SCRAPE_INTERVAL'))).timestamp(),
        EndTime=datetime.now().timestamp(),
    )

    return response['MetricDataResults'][0]['Values'][0] if response['MetricDataResults'][0]['Values'] else None

def collect_metrics():
    rds_client = boto3.client('rds', region_name=os.environ.get('AWS_REGION'))
    instances = rds_client.describe_db_instances()

    for instance in instances['DBInstances']:
        db_instance_id = instance['DBInstanceIdentifier']
        logger.info({"state": "processing", "db_instance_id": db_instance_id, "message": "Processing rds instance"})

        cpu_utilization = get_metric_value('CPUUtilization', db_instance_id)
        if cpu_utilization is not None:
            cpu_utilization_gauge.labels(DBInstanceIdentifier=db_instance_id).set(cpu_utilization)

        database_connections = get_metric_value('DatabaseConnections', db_instance_id)
        if database_connections is not None:
            database_connections_gauge.labels(DBInstanceIdentifier=db_instance_id).set(database_connections)

        volume_bytes_used = get_metric_value('VolumeBytesUsed', db_instance_id)
        if volume_bytes_used is not None:
            volume_bytes_used_gauge.labels(DBInstanceIdentifier=db_instance_id).set(volume_bytes_used)

        cpu_credits = get_metric_value('CPUCreditBalance', db_instance_id)
        if cpu_credits is not None:
            cpu_credits_gauge.labels(DBInstanceIdentifier=db_instance_id).set(cpu_credits)

        freeable_memory = get_metric_value('FreeableMemory', db_instance_id)
        if freeable_memory is not None:
            freeable_memory_gauge.labels(DBInstanceIdentifier=db_instance_id).set(freeable_memory)
while True:
    collect_metrics()
    time.sleep(parse_time_string(os.environ.get('METRICS_SCRAPE_INTERVAL')).seconds)
