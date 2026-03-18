import sys
import boto3
client = boto3.client('athena')

SOURCE_TABLE_NAME = 'data_ingestion_bucket_mia_final_project'
NEW_TABLE_NAME = 'mia-table-parquet'
NEW_TABLE_S3_BUCKET = 's3://mia-parquet-table-bucket/'
MY_DATABASE = 'de_project_database'
QUERY_RESULTS_S3_BUCKET = 's3://query-results-athena-2026/'

queryStart = client.start_query_execution(
    QueryString = f"""
    CREATE TABLE "{NEW_TABLE_NAME}" WITH
    (external_location='{NEW_TABLE_S3_BUCKET}',
    format='PARQUET',
    write_compression='SNAPPY',
    partitioned_by = ARRAY['ts_partition'])
    AS
    SELECT 
        row_ts,
        flight_n,
        airline_name,
        arriving_from,
        arriving_apt_code,
        delay,
        actual_arrival,
        scheduled_arrival,
        flight_status,
        ts_partition
    FROM (
        SELECT
            row_ts,
            flight_n,
            airline_name,
            arriving_from,
            arriving_apt_code,
            delay,
            actual_arrival,
            scheduled_arrival,
            flight_status,
            SUBSTRING(row_ts, 1, 7) AS ts_partition,
            ROW_NUMBER() OVER (PARTITION BY flight_n ORDER BY row_ts) AS rn
        FROM "{MY_DATABASE}"."{SOURCE_TABLE_NAME}"
    )
    WHERE rn = 1
    ;
    """,
    QueryExecutionContext = {'Database': f'{MY_DATABASE}'}, 
    ResultConfiguration = {'OutputLocation': f'{QUERY_RESULTS_S3_BUCKET}'}
)

resp = ["FAILED", "SUCCEEDED", "CANCELLED"]
response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])

while response["QueryExecution"]["Status"]["State"] not in resp:
    response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])

if response["QueryExecution"]["Status"]["State"] == 'FAILED':
    sys.exit(response["QueryExecution"]["Status"]["StateChangeReason"])
