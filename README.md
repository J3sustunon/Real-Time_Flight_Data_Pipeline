# Real-Time Flight Data Pipeline

In this project I implement a serverless data pipeline using AWS services to ingest, transform, and visualize hourly flight data from Miami International Airport. It pulls data from the AeroDataBox API, which then enables querying through Athena and dashboarding with Grafana.

- [Table of Contents](#table-of-contents)
  - [Architecture Overview](#architecture-overview)
  - [Data Ingestion](#data-ingestion)
    - [Daily Ingestion](#daily-ingestion)
     - [Lambda Function](lambda-function)
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
<img width="1341" height="532" alt="Architecture " src="https://github.com/user-attachments/assets/e26cd28e-4d5a-4978-b147-c1dd27cc74bc" />

## Data Ingestion
1. S3 Bucket Setup
   - Created an S3 bucket to store raw and processed flight arrival data.
     
2. AeroDataBox API
   
4. AWS Lamda Function
   - Python script used to trigger API call.

### Daily Ingestion
- Retrieves daily data from AeroDataBox API and stores JSON files in S3.
- Configured IAM role with AmazonS3FullAccess and AmazonKinesisFirehoseFullAccess.

#### Lamda Function
AWS Lambda enables serverless, event-driven compute, eiminating the need to provision or manage infrastructure. Using Python, I scripted an extraction function that pulls real-time flight arrival data from the AeroDataBox API and pushes it downstream via Kinesis Firehose. The function is triggered automatically every hour through Amazon EventBridge, ensuring a continuously refreshed data feed.

#### EventBridge Trigger
Used EventBridge Trigger to invoke the lambda function every 10 mintes. Providing up to date flight data. 
<img width="1191" height="385" alt="Screenshot 2026-03-18 at 1 19 41 PM" src="https://github.com/user-attachments/assets/833f818f-ec10-4d03-87ea-c1ea3a37c9b6" /> 

#### Kinesis Firehose
Buffers and streams data to S3 when either:
5 MiB of data is received, or 10 seconds have passed.
Configured to deliver streaming data into S3 path.

#### CloudWatch Monitoring
Incorporated real time email notification system to using CloudWatch, desinged to create an alaert in case of pipeline failure.

## Data Transformation
1. AWS Glue Crawler
   - This service was completly gamechnager. Automating the creation of my data and weaving everything together onto a table. 
3. AWS Glue ETL Jobs
   - Orchestration & Table Managemen: AWS Glue ETL Jobs are triggered automatically via Amazon EventBridge. Each run begins by dropping stale intermediate tables to prevent residual data from contaminating downstream transformations.
   - Parquet Transformation & Delay Computation:Raw JSON is converted into a partitioned Parquet table, leveraging columnar storage for optimized Athena query performance. A delay column is computed during this step by calculating the difference between scheduled and actual arrival times.
   - Data Quality & Production Publishing: The transformed table passes through a data quality check validating for null values before a wipe-and-reload publishes clean records into the production table, which serves as the single source of truth for the Grafana dashboard.
   
5. AWS Glue Workflows (clear worflow -> write -> transform -> audit -> publish -> pattern)
   
<img width="1077" height="272" alt="Screenshot 2026-03-18 at 3 07 45 PM" src="https://github.com/user-attachments/assets/23704305-90dc-4633-b2f1-ffbd17b431ea" />
<img width="1045" height="369" alt="Screenshot 2026-03-18 at 3 08 31 PM" src="https://github.com/user-attachments/assets/a2b79a27-f206-4a9d-8a60-8e936959489a" />

## Data Visualization

#### Grafan setup:
- Invoved generating access key that could be used by Grafana to access AWS.
- SQL queries were written directly in the Grafana panel editor, leveraging Athena as the query engine over the Parquet production table.

## Arrivals per hour
<img width="1137" height="671" alt="Screenshot 2026-03-18 at 3 41 00 PM" src="https://github.com/user-attachments/assets/4fb4bb79-5a9d-4515-b42a-58993e6130ec" />

## Top 10 cities
<img width="1144" height="671" alt="Screenshot 2026-03-18 at 2 56 32 PM" src="https://github.com/user-attachments/assets/69c24294-d930-4e08-92bf-c72833463d32" />

## Flights per airline
<img width="1144" height="671" alt="Screenshot 2026-03-18 at 2 48 10 PM" src="https://github.com/user-attachments/assets/c4c48f17-c4f5-43c6-8a9f-acc47e21a6eb" />

### Analysis & Observations
#### Arrivals by Interval:

- There is a high peak of arrivals around 11AM, suggesting a concentrated morning, where connecting flights are probably banked to maximize passenger transfer efficiency.

#### Airline Population:
- American Airlines dominates MIA arrivals, accounting for 56% of all tracked flights (136 of ~244 total, within a 12 hour)
- This concentration clearly shows how Miami International Airport serves as a primary hub for American Airlines, making it one of the carrier's busiest gateways for both domestic and international operations, particularly for Latin America and the Caribbean routes.
- The remaining 44% is distributed across 40+ carriers, reflecting MIA's role as a major international gateway with broad global connectivity.

#### Top 10 Origin Cities:
- The top 10 origin cities are dominated by major US Northeast and Southeast corridor hubs, with New York leading at 17 flights, followed by Washington, Atlanta, and Charlotte at 12 each.
- This distribution reinforces MIA's role as the primary southern gateway for East Coast travelers, with strong connectivity to major American Airlines hubs (Charlotte, Chicago, Washington) further reflecting the carrier's network concentration at MIA.

## Troubleshooting & Testing
- Time window direction caused empty actual_arrival fields, the initial implementation fetched the next hour forward, pulling flights that hadn't landed yet. Flipping to a backwards window (and ultimately extending it) was required to consistently capture post-touchdown runwayTime data.
-Codeshare contamination required an API swap, AviationStack returned duplicate records for alliance-shared flights with no native filter. Switching to AeroDataBox and enabling the withCodeshared=false query parameter eliminated the problem at the source, removing the need for post-ingestion deduplication logic on that specific issue.

## Design Considerations
- A wipe-and-reload INSERT INTO strategy was implemented to flush stale records before each pipeline run, guaranteeing the production table always reflects a clean, deduplicated dataset for downstream reporting.

## Future Improvements
Data Coverage
- Lambda currently pulls a 12-hour rolling window per invocation, limiting historical depth.
Could be extended to a full 24-hour window or multi-invocation strategy to capture complete daily arrival patterns.
