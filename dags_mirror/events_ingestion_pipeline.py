from airflow.sdk import dag
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.docker.operators.docker import DockerOperator
import pendulum

default_args = {
"retries" : 3,
"retry_delay" : pendulum.duration(minutes=30),
"email":"ja09aguilar@gmail.com",
"email_on_failure":True
}

@dag(
    schedule="10 0 * * *",
    start_date=pendulum.datetime(2025,11,1),
    description="DAG to ingest events from the previous day",
    tags=["daily", "input_s3", "output_s3", "output_snowflake"],
    max_consecutive_failed_dag_runs=3,
    default_args=default_args
)

def s3_check_dag():

    bucket = "data-bucket-jaguilar-9",
    delivery_path = f"events_input/{pendulum.now().subtract(days=1).format('YYYY-MM-DD')}/"

    s3_sensor = S3KeySensor(
        task_id = "wait_for_s3_file",
        aws_conn_id = "amazons3",
        bucket_key="s3://data-bucket-jaguilar-9/events_input/{{ macros.ds_add(ds, -1) }}/events_*.csv",
        wildcard_match=True,
        poke_interval=60,
        timeout=60*3,
        mode="reschedule"
    )

    file_ingestion = DockerOperator(
        task_id="container_processing_file",
        image="jadolfo9/events_ingestion_image_v8:latest",
        hostname="events_ingest_container",
        auto_remove="success",
        command="python3 ingestion_pipeline.py",
        mem_limit="6g"
    )

    s3_sensor >> file_ingestion

dag = s3_check_dag()