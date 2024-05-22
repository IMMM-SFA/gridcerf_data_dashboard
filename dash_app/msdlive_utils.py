from datetime import date, datetime
import requests
import boto3
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=None)
def _get_annonomous_credentials() -> dict:
    """Get annonomous credentials from the API gateway

    Returns:
        dict: The annonomous credentials
    """
    print("Getting annonomous credentials")
    creds_payload = {}
    # hard coded to dev environment's auth stack
    auth_url = "https://4w5dld7rr8.execute-api.us-west-2.amazonaws.com/prod"
    creds_http_response = requests.post(
        f"{auth_url}/aws-creds",
        json=creds_payload,
    )
    creds_response = creds_http_response.json()
    return creds_response


def get_bytes(dataset_id: str, file_path: Path) -> bytes:
    print(dataset_id, file_path)
    creds_response = _get_annonomous_credentials()
    # TODO see if we can reuse with_session already impl'd in RDM extension

    # Create a session using the credentials
    session = boto3.Session(
        aws_access_key_id=creds_response["credentials"]["accessKeyId"],
        aws_secret_access_key=creds_response["credentials"]["secretKey"],
        aws_session_token=creds_response["credentials"]["sessionToken"],
    )

    # Create an S3 client using the session
    s3 = session.client("s3")

    account_id = "889772541283"

    # the ARN of the access point and file to be accessed
    access_point_arn = f"arn:aws:s3:us-west-2:{account_id}:accesspoint/{dataset_id}"

    # Get the file from S3
    obj = s3.get_object(Bucket=access_point_arn, Key=f"{dataset_id}/{file_path}")

    file_size = obj['ContentLength']
    print(f"Size of the file: {file_size} bytes")

    # Read the file content
    file_content = obj["Body"].read()

    return file_content
