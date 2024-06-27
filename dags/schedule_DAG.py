from dags.main import *
from datetime import timedelta,datetime
from airflow.decorators import dag, task


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=60)
}


@dag(
    schedule_interval="0 0 * * 0",  # Runs every Sunday at midnight
    start_date=datetime(2024, 6, 1),  # Start date of the DAG
    catchup=False,  # Prevents backfilling of old DAG runs
    tags=['Schedule_Weekly_Pipeline'],  # Tags for easier identification
    default_args=default_args  # Default arguments for tasks
)
def Schedule_Weekly_Pipeline():
    @task()
    def Scheduled_Task():
        schedule_func = send_data_to_s3()
    Scheduled_Task()
Schedule_Weekly_Pipeline()