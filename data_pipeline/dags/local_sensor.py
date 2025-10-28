from airflow.sdk import dag, task
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash_operator import BashOperator
from pendulum import datetime

with DAG(
    schedule="10 0 * * *",
    start_date=datetime(2025,10,28),
    description="DAG to ingest events of the previous day",
    tags=["events_ingestion", "daily", "output_snowflake"],
    max_consecutive_failed_dag_runs=3
)as dag:
    
    #@task
    file_sensor = FileSensor(
        task_id="waiting_for_events_file",
        filepath="/Users/jaguilar/Desktop/Portfolio/test_folder/dropoff_folder/*.csv",
        poke_interval = 60*5,
        timeout = 60*15
    )

    file_ingestion = BashOperator(
        task_id="processing_file",
        bash_command="python3 ../ingestion_pipeline.py"
    )