from etls.aws_s3_etl import connect_to_s3, upload_file
from utils.constants import AWS_BUCKET_NAME

def upload_s3_pipeline(file_to_upload: str, s3_subfolder: str, object_name: str) -> None:
    """
    :param object_name: e.g., 'players_totals.csv'
    :param file_to_upload: e.g., 'players_totals.csv'
    :param s3_subfolder: e.g., 'raw_stats/'
    :return:
    """
    s3 = connect_to_s3()
    upload_file(s3, AWS_BUCKET_NAME, file_to_upload, s3_subfolder + object_name)