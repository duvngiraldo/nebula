import logging

import polars as pl

logger = logging.getLogger(__name__)


def clean_calls(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns(
        pl.col("timestamp_connection").str.to_datetime(format="%Y-%m-%d %H:%M:%S"),
        pl.col("timestamp_call_end").str.to_datetime(format="%Y-%m-%d %H:%M:%S"),
    )

    df = df.with_columns(
        ((pl.col("timestamp_call_end") - pl.col("timestamp_connection"))
         .dt.total_seconds() / 60.0).alias("duration_minutes"),
        (~pl.col("is_soft_delete")).alias("is_valid"),
        (pl.col("tipo_de_llamada") == "inbound").alias("is_inbound"),
    )

    logger.info(
        "Calls cleaned: %d records, avg duration %.1f min",
        df.height, df["duration_minutes"].mean(),
    )
    return df
