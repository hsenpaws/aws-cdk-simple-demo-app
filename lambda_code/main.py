import json
import boto3
import pandas as pd
from io import StringIO 


def lambda_handler(event, context):
 s3 = boto3.resource('s3')
 bucket = s3.Bucket('source_bucket')

 df = pd.bucket.read_csv('*.csv')
 
 bucket = 'covid19autoupdate' # already created on S3
 csv_buffer = StringIO()
 df.to_csv(csv_buffer)
 s3_resource = boto3.resource('s3')
 s3_resource.Object(bucket, 'df.csv').put(Body=csv_buffer.getvalue())
