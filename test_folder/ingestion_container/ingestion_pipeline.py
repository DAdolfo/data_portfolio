import os
import logging
from itertools import chain
from datetime import datetime
import math

from pyspark.sql import SparkSession
from pyspark.logger import PySparkLogger
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, FloatType
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.getOrCreate()

logger = PySparkLogger.getLogger("spark_logger")
handler = logging.FileHandler("cleanup.log")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

events_schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("user_id", StringType(), True),
    StructField("sequence_number", IntegerType(), True),
    StructField("session_id", StringType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("ip_address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("postal_code", StringType(), True),
    StructField("browser", StringType(), True),
    StructField("traffic_source", StringType(), True),
    StructField("uri", StringType(), True),
    StructField("event_type", StringType(), True)
])

events = spark.read.csv("/app/dropoff_folder/events_table.csv", header=True, schema=events_schema).persist()
events_size = events.count()
logger.info(f"Events data loaded, there are {events_size} records on it.")

#Let's check what columns have nulls and how many of them
Events_null_dictionary = {col : events.filter(events[col].isNull()).count() for col in events.columns}
logger.info(f"The events data has the following amount of null values: {Events_null_dictionary}")

#Generate fake ids for the events that don't have one, if any
sessionids_with_null_userids = list(events.select("session_id").distinct().where(F.col("user_id").isNull()).toPandas()["session_id"])

#Only proceed if we have sessions without user_ids
if sessionids_with_null_userids:

    events.createOrReplaceTempView("events_table")
    query = """
    SELECT
        AVG(number_of_sessions) as avg_sessions_per_user
    FROM
        (SELECT
            user_id,
            COUNT(DISTINCT(session_id)) as number_of_sessions
        FROM
            events_table
        WHERE
            user_id IS NOT NULL
        GROUP BY
            user_id
    )
    """
    avg_sessions_per_user = int(round(spark.sql(query).first()[0],0))

    fake_ids = []
    value = 1
    fake_ids_amount = math.floor(len(sessionids_with_null_userids)/avg_sessions_per_user)
    for i in range(fake_ids_amount):
        fake_ids.append(f"fake_id_{value}_{datetime.now().strftime('%Y-%m-%d')}") #These are daily batches
        value += 1

    df1 = events.filter(F.col("user_id").isNull()).select("session_id")
    window = Window.orderBy("session_id")
    #Given that the window function is over the whole dataset, we persist it
    df1 = df1.withColumn("row_number", F.dense_rank().over(window)).persist() 
    df1 = df1.withColumn("fake_index", (((F.col("row_number") - 1)/avg_sessions_per_user).cast("int")))
    fake_ids_df = spark.createDataFrame([(i, fake_ids[i]) for i in range(len(fake_ids))], ["fake_index", "fake_id"])
    filled_df = df1.join(fake_ids_df, on="fake_index", how="left")

    events = (events.join(filled_df.select("session_id", "fake_id"),
                        on="session_id", how="left").withColumn("user_id", F.coalesce("user_id", filled_df["fake_id"]))
                .drop("fake_id")
    )
    events = events.drop_duplicates(subset=["id", "user_id"])
    #Check that the events have only the allowed values in the traffic and type columns
    traffic_sources = ["Organic", "YouTube", "Email", "Adwords", "Facebook"]
    event_types = ["cancel", "purchase", "cart", "cart", "department", "home", "product"]
    events = events.filter(F.col("traffic_source").isin(traffic_sources))
    events = events.filter(F.col("event_type").isin(event_types))

    events.write.parquet(f'./cleaned_data/cleaned_events_batch_{datetime.now().strftime("%Y-%m-%d")}',
                     mode = "overwrite",
                     partitionBy="event_type" #To be defined once we know what to train the model with
                     
                     )

    Events_null_dictionary = {col : events.filter(events[col].isNull()).count() for col in events.columns}
    logger.info(f"After cleanup, the events data has been written with the following amount of null values: {Events_null_dictionary}")

if not sessionids_with_null_userids:

    events.write.parquet(f'/app/cleaned_data/cleaned_events_batch_{datetime.now().strftime("%Y-%m-%d")}',
                mode = "overwrite",
                partitionBy="event_type" #To be defined once we know what to train the model with     
                )