import os
import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

# Add the project root directory to sys.path to allow imports from 'pipelines', 'utils', etc.,
# when running the DAG from the Airflow 'dags/' folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.nba_totals_pipeline import nba_totals_pipeline
from pipelines.aws_s3_ingestion import upload_s3_pipeline
from utils.constants import SEASON, SEASON_TYPE, DATE_TO, FILE_STATS_PATH, S3_STATS_OBJECT_NAME, S3_STATS_SUBFOLDER


default_args = {
    'owner': 'Oleg I',
    'start_date': datetime(2025, 4, 6),
}

dag = DAG(
    dag_id='nba_data_totals_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['nba', 'etl', 'pipeline']
)

# extract from NBA
extract = PythonOperator(
    task_id='nba_data_extraction',
    python_callable=nba_totals_pipeline,
    op_kwargs={
        'season': SEASON,
        'season_type': SEASON_TYPE,
        'date_to': DATE_TO,
        'file_path': FILE_STATS_PATH,
    },
    dag=dag
)

# upload to s3
upload_s3 = PythonOperator(
    task_id='s3_upload',
    python_callable=upload_s3_pipeline,
    op_kwargs={
        'file_to_upload': FILE_STATS_PATH,
        's3_subfolder': S3_STATS_SUBFOLDER,
        'object_name': S3_STATS_OBJECT_NAME
    },
    dag=dag
)

extract >> upload_s3