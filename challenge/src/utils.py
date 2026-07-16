import logging

import polars as pl

logger = logging.getLogger(__name__)


def clean(df: pl.DataFrame) -> pl.DataFrame:
    before = len(df)
    df = (
        df.unique()
        .with_columns(pl.col(pl.Utf8).str.strip_chars())
    )
    after = len(df)
    if before != after:
        logger.info("Removed %d duplicate records", before - after)
    return df
