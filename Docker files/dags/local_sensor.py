from airflow.sdk import dag, task
from airflow.providers.standard.sensors.filesystem import FileSensor
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from pendulum import datetime

@dag(
    schedule="10 0 * * *",
    start_date=datetime(2025,10,28),
    description="DAG to ingest events of the previous day",
    tags=["events_ingestion", "daily", "output_snowflake"],
    max_consecutive_failed_dag_runs=3
)

def local_sensor():
    
    file_sensor = FileSensor(
        task_id="waiting_for_events_file",
        filepath="/dropoff_folder/events_table.csv",
        poke_interval = 60*5,
        timeout = 60*15
    )

    file_ingestion = DockerOperator(
        task_id="container_to_process_file",
        image="events_ingestion_image_3",
        hostname="events_ingest_container",
        auto_remove="success",
        command="python3 ingestion_pipeline.py",
        network_mode="bridge",
        mem_limit="6g",
        mounts=[Mount(source="/Users/jaguilar/Desktop/Portfolio/test_folder/cleaned_data", 
                      target="/app/cleaned_data", type="bind"),
                Mount(source="/Users/jaguilar/Desktop/Portfolio/test_folder/dropoff_folder", 
                      target="/app/dropoff_folder", type="bind")]
    )

    file_sensor >> file_ingestion

dag = local_sensor()