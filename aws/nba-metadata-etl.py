import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.sql.functions import current_date, to_date, substring, when, col, udf
from pyspark.sql.types import DoubleType

## @params: [JOB_NAME]
params = [
    'JOB_NAME',
    'catalog_name',
    'database_name',
    'table_name',
    's3_bucket_name',
    'input_prefix'
]

args = getResolvedOptions(sys.argv, params)

prefix = args['input_prefix']
bucket = args['s3_bucket_name']

s3_input_path = f"s3://{bucket}/{prefix}/"  
iceberg_catalog = args['catalog_name']
glue_database = args['database_name']
glue_table = args['table_name']

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

raw_dyf = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    format="csv",
    format_options={"withHeader": True, "separator": ","},
    connection_options={"paths": [s3_input_path], "recurse": True},
    transformation_ctx="read_csv"
)

mapped_dyf = ApplyMapping.apply(
    frame=raw_dyf,
    mappings=[
        ("PLAYER_ID", "string", "PLAYER_ID", "bigint"),
        ("PLAYER_NAME", "string", "PLAYER_NAME", "string"),
        ("TEAM_NAME", "string", "TEAM_NAME", "string"),
        ("POSITION", "string", "POSITION", "string"),
        ("HEIGHT", "string", "HEIGHT", "string"),
        ("WEIGHT", "string", "WEIGHT", "int"),
        ("COUNTRY", "string", "COUNTRY", "string"),
        ("BIRTHDATE", "string", "BIRTHDATE", "string"),
        ("DRAFT_YEAR", "string", "DRAFT_YEAR", "string"),
        ("DRAFT_NUMBER", "string", "DRAFT_NUMBER", "string"),
        ("FROM_YEAR", "string", "FROM_YEAR", "int"),
        ("TO_YEAR", "string", "TO_YEAR", "int")
    ],
    transformation_ctx="mapped_dyf"
)

df = mapped_dyf.toDF()

# birthdate
df = df.withColumn("BIRTHDATE", to_date(substring(col("BIRTHDATE"), 1, 10), "yyyy-MM-dd"))

# "undrafted"
df = df.withColumn("DRAFT_YEAR", when(col("DRAFT_YEAR") == "Undrafted", None).otherwise(col("DRAFT_YEAR").cast("int")))
df = df.withColumn("DRAFT_NUMBER", when(col("DRAFT_NUMBER") == "Undrafted", None).otherwise(col("DRAFT_NUMBER").cast("int")))

# height to cm
def parse_height(height_str):
    try:
        feet, inches = height_str.split('-')
        return round((int(feet) * 12 + int(inches)) * 2.54, 1)
    except:
        return None

# weight to kg
def parse_weight(weight_lbs):
    try:
        return round(int(weight_lbs) * 0.453592, 1)
    except:
        return None

parse_height_udf = udf(parse_height, DoubleType())
df = df.withColumn("HEIGHT_CM", parse_height_udf(col("HEIGHT")))

parse_weight_udf = udf(parse_weight, DoubleType())
df = df.withColumn("WEIGHT_KG", parse_weight_udf(col("WEIGHT")))

# ingestion date
df = df.withColumn("ingestion_date", current_date())
  
df.createOrReplaceTempView("tmp_player_metadata_view")
    
spark.sql(f"""
    MERGE INTO {iceberg_catalog}.{glue_database}.{glue_table} t
    USING tmp_player_metadata_view s
        ON t.player_id = s.player_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")

job.commit()