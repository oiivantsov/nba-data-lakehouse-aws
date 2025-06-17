import boto3
from botocore.exceptions import ClientError
from utils.constants import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

def connect_to_s3():
    try:
        s3_client = boto3.client("s3",
                                 region_name=AWS_REGION,
                                 aws_access_key_id=AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        return s3_client
    except ClientError as e:
        print(e)


def upload_file(s3_client, bucket_name, file_name, object_name):
    try:
        s3_client.upload_file(file_name, bucket_name, object_name)
        print(f"File '{file_name}' uploaded as '{object_name}'.")
    except ClientError as e:
        print(e)
