from airflow.sdk import dag, task, Context
from airflow.providers.standard.operators.python import PythonOperator #Can be substituted by the task decorator
from pendulum import datetime

default_args = {
    "retries" : 3
}

@dag(
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    description="This DAG is just to learn",
    tags=["learning_dag", "team_css", "source_one"],
    max_consecutive_failed_dag_runs=3, #Paused after three failed tries, check more parameters
    default_args=default_args
) #The decorator decorates a function 

def dag_try(): #This should be the same name as the DAG
    
    @task
    def task_a():
        val = 42
        #context["ti"].xcom_push(key="my_key", value=val) # ti for task instance, don't forget to add context in
        #the function arguments
        return val #This is the equivalent of pushing with key="return_value"

    @task
    def task_b(val2: int):
        #val2 = context["ti"].xcom_pull(task_ids="task_a", key="my_key")

        print(f"Hi from {val2}!")

    @task
    def task_c(ti):
        print("Hi from C!")
        val = 69 #If you want to push multiple values, use a fucking dictionary
        ti.xcom_push(key="my_key", value=val)

    @task
    def task_d(ti):
        ti.xcom_pull(task_ids=["task_a", "task_c"], key="my_key") #This doesn't make chronological sense 
        # but that's the syntaxis
        print("Hi from D!")

    val = task_a()
    task_b(val) >> [task_c(), task_d()]


dag_try() #Don't forget to call it cause it won't exist without this