# Real-Time-Flight-Data-Pipeline

In this project I implement a serverless data pipeline using AWS services to ingest, transform, and visualize hourly flight data from Miami International Airport. It pulls data from the AeroDataBox API, which then enables querying through Athena and dashboarding with Grafana.

- [Table of Contents](#table-of-contents)
  - [Architecture Overview](#architecture-overview)
  - [Data Ingestion](#data-ingestion)
    - [Historical Backfill Function](#historical-backfill-function)
    - [Daily Ingestion](#daily-ingestion)
      - [EventBridge Trigger](#eventbridge-trigger)
      - [Kinesis Firehose](#kinesis-firehose)
      - [CloudWatch Monitoring](#cloudwatch-monitoring)
  - [Data Transformation](#data-transformation)
    - [AWS Glue Crawler](#aws-glue-crawler)
    - [AWS Glue ETL Jobs](#aws-glue-etl-jobs)
    - [AWS Glue Workflows](#aws-glue-workflows-write--audit--publish--pattern)
  - [Data Visualization](#data-visualization)
    - [Analysis & Observations](#analysis--observations)
  - [Troubleshooting & Testing](#troubleshooting--testing)
  - [Design Considerations](#design-considerations)
  - [Future Improvements](#future-improvements)

## Architecture Overview

## Data Ingestion
1. S3 Bucket Setup
   - Created an S3 bucket to store raw and processed flight arrival data.
2. AeroDataBox API
3. AWS Lamda Function
   - Python script used to trigger API call 

### Historical Backfill Function

### Daily Ingestion

#### EventBridge Trigger
- Used EventBridge Trigger to invoke the lambda function every 10 mintes. In order to get fresh arrival data 

#### Kinesis Firehose

#### CloudWatch Monitoring

## Data Transformation

### AWS Glue Crawler

### AWS Glue ETL Jobs

### AWS Glue Workflows (write - audit - publish - pattern)

## Data Visualization
Grafan setup:
- Invoved generating access key that could be used by Grafana to access AWS
- 
  

### Analysis & Observations

## Troubleshooting & Testing

## Design Considerations

## Future Improvements

