from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), "../config/.env") # to find .env file
load_dotenv(dotenv_path)

# AWS
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

# NBA data
SEASON_TYPE = "Regular Season"
SEASON = "2024-25"
DATE_TO = "03-01-2025"

# S3 bucket
S3_STATS_OBJECT_NAME = "players_stats.csv"
S3_METADATA_OBJECT_NAME = "players_metadata.csv"
S3_STATS_SUBFOLDER = "raw_stats/"   # Must match RawStatsPrefix defined in the CloudFormation template
S3_METADATA_SUBFOLDER = "raw_metadata/" # Must match RawMetadataPrefix defined in the CloudFormation template

# Airflow
FILE_STATS_PATH = "/opt/airflow/data/players_stats.csv"
FILE_METADATA_PATH = "/opt/airflow/data/players_metadata.csv"
