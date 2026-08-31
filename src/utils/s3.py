import os
from typing import Any
import boto3
import pandas as pd
from src.utils.config import CONFIG

#create the s3 client here
def get_s3_client():
    kwargs : {"region_name":CONFIG.s3.region}

    if CONFIG.s3.endpoint_url:
        kwargs["endpoint_url"] = CONFIG.s3.endpoint_url
    
    return boto3.client("s3" , **kwargs)

#ensure the bucket here

def ensure_bucket_exist():
    s3 = get_s3_client()
    existing = {b["Name"] for b in s3.list_buckets().get("Buckets", [])}

    if CONFIG.s3.bucket not in existing:
        s3.create_bucket(Bucket=CONFIG.s3.bucket)

#Upload the bucket here
def upload_bytes(data:bytes , key:str)->str:
    s3 = get_s3_client()
    s3.put_object(Bucket=CONFIG.s3.bucket, Key=key, Body=data)
    return f"s3://{CONFIG.s3.bucket}/{key}"


#upload the file 
def upload_file(local_path:str , key:str)->str:
    s3 = get_s3_client()
    s3.upload_file(local_path, CONFIG.s3.bucket, key)
    return f"s3://{CONFIG.s3.bucket}/{key}"


def download_byte(key:str)->bytes:
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=CONFIG.s3.bucket, Key=key)
    return obj["Body"].read()

def write_csv(dataframe , key):
    buffer = io.StringIO()
    df.to_csv(buffer , index=False)
    
    return upload_bytes(buffer.getvalue().encode("utf-8"), key)
    
