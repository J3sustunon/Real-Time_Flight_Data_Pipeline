import sys
import boto3

QUERY_RESULTS_BUCKET = 's3://query-results-athena-2026/'
MY_DATABASE = 'de_project_database'
DQ_SOURCE_TABLE = 'mia-table-parquet'
PROD_TABLE_NAME = 'mia_prod_table_parquet'
PROD_TABLE_S3_BUCKET = 'mia-prod-parquet-bucket'

athena = boto3.client('athena')
s3 = boto3.resource('s3')

# Wipe existing data from the prod table's S3 location
bucket = s3.Bucket(PROD_TABLE_S3_BUCKET)
deleted = bucket.objects.all().delete()
print(f"Deleted {len(deleted[0].get('Deleted', []) if deleted else [])} object(s).")

# Copy DQ-validated data into the prod table
queryStart = athena.start_query_execution(
    QueryString=f"""
    INSERT INTO "{MY_DATABASE}"."{PROD_TABLE_NAME}"
    SELECT
        row_ts,
        flight_n,
        airline_name,
        arriving_from,
        arriving_apt_code,
        actual_arrival,
        scheduled_arrival,
        flight_status,
        delay_minutes,
        ts_partition
    FROM "{MY_DATABASE}"."{DQ_SOURCE_TABLE}"
    ;
    """,
    QueryExecutionContext={'Database': MY_DATABASE},
    ResultConfiguration={'OutputLocation': QUERY_RESULTS_BUCKET}
)


terminal_states = ["FAILED", "SUCCEEDED", "CANCELLED"]
response = athena.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])
while response["QueryExecution"]["Status"]["State"] not in terminal_states:
    response = athena.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])

final_state = response["QueryExecution"]["Status"]["State"]
print(f"Query finished with state: {final_state}")
if final_state == 'FAILED':
    sys.exit(response["QueryExecution"]["Status"]["StateChangeReason"])

print(f"'{PROD_TABLE_NAME}' successfully refreshed.")