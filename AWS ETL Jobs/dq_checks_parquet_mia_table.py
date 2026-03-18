import sys
import awswrangler as wr


NULL_DQ_CHECK = f"""
SELECT 
    SUM(CASE WHEN flight_n IS NULL THEN 1 ELSE 0 END) AS res_col
FROM "de_project_database"."mia-table-parquet"
;
"""

# run the quality check
df = wr.athena.read_sql_query(sql=NULL_DQ_CHECK, database="de_project_database")

# exit if we get a result > 0
# else, the check was successful
if df['res_col'][0] > 0:
    sys.exit('Results returned. Quality check failed.')
else:
    print('Quality check passed.')
