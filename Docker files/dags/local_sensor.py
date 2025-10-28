from airflow.sdk import dag, task
from airflow.providers.standard.sensors.filesystem import FileSensor
from airflow.operators.bash import BashOperator
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

    file_ingestion = BashOperator(
        task_id="processing_file",
        bash_command="python3 scripts/ingestion_pipeline.py"
    )

    file_sensor >> file_ingestion

dag = local_sensor()