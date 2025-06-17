import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import current_date, round, col, when
from pyspark.sql.window import Window
from pyspark.sql import functions as F


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
        ("NICKNAME", "string", "NICKNAME", "string"),
        ("TEAM_ID", "string", "TEAM_ID", "bigint"),
        ("TEAM_ABBREVIATION", "string", "TEAM_ABBREVIATION", "string"),
        ("AGE", "string", "AGE", "double"),
        ("GP", "string", "GP", "int"),
        ("W", "string", "W", "int"),
        ("L", "string", "L", "int"),
        ("W_PCT", "string", "W_PCT", "double"),
        ("MIN", "string", "MIN", "double"),
        ("FGM", "string", "FGM", "int"),
        ("FGA", "string", "FGA", "int"),
        ("FG_PCT", "string", "FG_PCT", "double"),
        ("FG3M", "string", "FG3M", "int"),
        ("FG3A", "string", "FG3A", "int"),
        ("FG3_PCT", "string", "FG3_PCT", "double"),
        ("FTM", "string", "FTM", "int"),
        ("FTA", "string", "FTA", "int"),
        ("FT_PCT", "string", "FT_PCT", "double"),
        ("OREB", "string", "OREB", "int"),
        ("DREB", "string", "DREB", "int"),
        ("REB", "string", "REB", "int"),
        ("AST", "string", "AST", "int"),
        ("TOV", "string", "TOV", "int"),
        ("STL", "string", "STL", "int"),
        ("BLK", "string", "BLK", "int"),
        ("BLKA", "string", "BLKA", "int"),
        ("PF", "string", "PF", "int"),
        ("PFD", "string", "PFD", "int"),
        ("PTS", "string", "PTS", "int"),
        ("PLUS_MINUS", "string", "PLUS_MINUS", "int"),
        ("NBA_FANTASY_PTS", "string", "NBA_FANTASY_PTS", "double"),
        ("DD2", "string", "DD2", "int"),
        ("TD3", "string", "TD3", "int"),
        
        # *_RANK fields
        ("GP_RANK", "string", "GP_RANK", "int"),
        ("W_RANK", "string", "W_RANK", "int"),
        ("L_RANK", "string", "L_RANK", "int"),
        ("W_PCT_RANK", "string", "W_PCT_RANK", "int"),
        ("MIN_RANK", "string", "MIN_RANK", "int"),
        ("FGM_RANK", "string", "FGM_RANK", "int"),
        ("FGA_RANK", "string", "FGA_RANK", "int"),
        ("FG_PCT_RANK", "string", "FG_PCT_RANK", "int"),
        ("FG3M_RANK", "string", "FG3M_RANK", "int"),
        ("FG3A_RANK", "string", "FG3A_RANK", "int"),
        ("FG3_PCT_RANK", "string", "FG3_PCT_RANK", "int"),
        ("FTM_RANK", "string", "FTM_RANK", "int"),
        ("FTA_RANK", "string", "FTA_RANK", "int"),
        ("FT_PCT_RANK", "string", "FT_PCT_RANK", "int"),
        ("OREB_RANK", "string", "OREB_RANK", "int"),
        ("DREB_RANK", "string", "DREB_RANK", "int"),
        ("REB_RANK", "string", "REB_RANK", "int"),
        ("AST_RANK", "string", "AST_RANK", "int"),
        ("TOV_RANK", "string", "TOV_RANK", "int"),
        ("STL_RANK", "string", "STL_RANK", "int"),
        ("BLK_RANK", "string", "BLK_RANK", "int"),
        ("BLKA_RANK", "string", "BLKA_RANK", "int"),
        ("PF_RANK", "string", "PF_RANK", "int"),
        ("PFD_RANK", "string", "PFD_RANK", "int"),
        ("PTS_RANK", "string", "PTS_RANK", "int"),
        ("PLUS_MINUS_RANK", "string", "PLUS_MINUS_RANK", "int"),
        ("NBA_FANTASY_PTS_RANK", "string", "NBA_FANTASY_PTS_RANK", "int"),
        ("DD2_RANK", "string", "DD2_RANK", "int"),
        ("TD3_RANK", "string", "TD3_RANK", "int")
    ],
    transformation_ctx="mapped_dyf"
)

df = mapped_dyf.toDF()

df = df.withColumn("ingestion_date", current_date())

df = df.withColumn("PTS_PER_GAME", round(when(col("GP") > 0, col("PTS") / col("GP")), 1)) \
       .withColumn("REB_PER_GAME", round(when(col("GP") > 0, col("REB") / col("GP")), 1)) \
       .withColumn("AST_PER_GAME", round(when(col("GP") > 0, col("AST") / col("GP")), 1)) \
       .withColumn("TOV_PER_GAME", round(when(col("GP") > 0, col("TOV") / col("GP")), 1)) \
       .withColumn("STL_PER_GAME", round(when(col("GP") > 0, col("STL") / col("GP")), 1)) \
       .withColumn("BLK_PER_GAME", round(when(col("GP") > 0, col("BLK") / col("GP")), 1)) \
       .withColumn("MIN_PER_GAME", round(when(col("GP") > 0, col("MIN") / col("GP")), 1)) \
       .withColumn("PTS_PER_SHOT", round(when(col("FGA") > 0, col("PTS") / col("FGA")), 2))
       
w_pts = Window.orderBy(col("PTS_PER_GAME").desc())
w_reb = Window.orderBy(col("REB_PER_GAME").desc())
w_ast = Window.orderBy(col("AST_PER_GAME").desc())
w_tov = Window.orderBy(col("TOV_PER_GAME").asc())  # turnovers: less - better
w_stl = Window.orderBy(col("STL_PER_GAME").desc())
w_blk = Window.orderBy(col("BLK_PER_GAME").desc())
w_min = Window.orderBy(col("MIN_PER_GAME").desc())
w_pts_per_shot = Window.orderBy(col("PTS_PER_SHOT").desc())

df = df \
    .withColumn("PTS_PER_GAME_RANK", F.rank().over(w_pts)) \
    .withColumn("REB_PER_GAME_RANK", F.rank().over(w_reb)) \
    .withColumn("AST_PER_GAME_RANK", F.rank().over(w_ast)) \
    .withColumn("TOV_PER_GAME_RANK", F.rank().over(w_tov)) \
    .withColumn("STL_PER_GAME_RANK", F.rank().over(w_stl)) \
    .withColumn("BLK_PER_GAME_RANK", F.rank().over(w_blk)) \
    .withColumn("MIN_PER_GAME_RANK", F.rank().over(w_min)) \
    .withColumn("PTS_PER_SHOT_RANK", F.rank().over(w_pts_per_shot))

df.createOrReplaceTempView("tmp_player_totals_view")
    
spark.sql(f"""
    MERGE INTO {iceberg_catalog}.{glue_database}.{glue_table} t
    USING tmp_player_totals_view s
        ON t.player_id = s.player_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")


job.commit()