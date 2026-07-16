import logging

import polars as pl

logger = logging.getLogger(__name__)


def clean_users(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns(
        pl.col("email").str.split("@").list.last().alias("email_domain"),
    )

    df = df.with_columns(
        pl.when(pl.col("nombre").str.len_chars() < 5).then(pl.lit("Junior"))
        .when(pl.col("nombre").str.len_chars() < 10).then(pl.lit("Mid"))
        .otherwise(pl.lit("Senior"))
        .alias("agent_level"),
    )

    logger.info("Users cleaned: %d records", df.height)
    return df
