from airflow.sdk import dag, task
from airflow.providers.amazon.aws.operators.s3 import S3KeySensor
from airflow.operators.bash import BashOperator
from pendulum import datetime, duration

default_args = {
    "retries" : 3,
    "retry_delay" : duration(minutes=30),
    "email":"ja@gmail.com",
    "email_on_failure":True
}

@dag(
    schedule="0 1 * * *",
    start_date=datetime(2025,10,19, tz="UTC"),
    description="This DAG triggers the events cleanup, before transformation.",
    tags=["etl", "raw_ingestion", "s3", "events_logs"],
    max_consecutive_failed_dag_runs=3,
    default_args=default_args
)

def s3_check_dag():

    bucket = "data-delivery-jaguilar"
    delivery_path = f"daily_events_delivery/{datetime.now().format('YYYY-MM-DD')}/"

    
    wait_for_file = S3KeySensor(
        task_id="wait_for_file",
        aws_conn_id="amazons3",
        bucket_key="s3://data-delivery-jaguilar/{{ ds }}/events_*.csv",
        wildcard_match=True,
        poke_interval = 60*5,
        timeout = 60*60*2,
        mode="reschedule"
    )

    @task
    def execute_cleanup = BashOperator(

    )
    

    wait_for_file >> execute_cleanup

s3_check_dag()