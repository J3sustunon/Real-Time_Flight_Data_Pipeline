import sys
import boto3

BUCKET_TO_DEL = 'mia-parquet-table-bucket'
DATABASE_TO_DEL = 'de_project_database'
TABLE_TO_DEL = 'mia-table-parquet'

s3_client = boto3.client('s3')
while True:
    objects = s3_client.list_objects(Bucket=BUCKET_TO_DEL)
    content = objects.get('Contents', [])
    if len(content) == 0:
        break
    for obj in content:
        s3_client.delete_object(Bucket=BUCKET_TO_DEL, Key=obj['Key'])

glue_client = boto3.client('glue')
try:
    glue_client.delete_table(DatabaseName=DATABASE_TO_DEL, Name=TABLE_TO_DEL)
    print(f'Table {TABLE_TO_DEL} deleted successfully.')
except glue_client.exceptions.EntityNotFoundException:
    print(f'Table {TABLE_TO_DEL} not found, skipping.')