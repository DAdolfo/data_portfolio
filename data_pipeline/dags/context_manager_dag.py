from airflow.sdk import dag, task, DAG
from pendulum import datetime

with DAG(
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    description="This DAG is just to learn",
    tags=["learning_dag", "team_css", "source_one"],
    max_consecutive_failed_dag_runs=3
): #Different way to define a DAG
    @task
    def task_a():
        print("Hello A!")