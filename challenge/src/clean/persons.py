import logging

import polars as pl

logger = logging.getLogger(__name__)


def clean_persons(df: pl.DataFrame) -> pl.DataFrame:
    before = df.height
    df = df.filter(pl.col("telefono_movil").str.contains(r"^\+?\d{9,15}$"))
    dropped = before - df.height
    if dropped:
        logger.warning("Dropped %d record(s) with invalid phone", dropped)

    df = df.with_columns(
        pl.col("email").str.split("@").list.last().alias("email_domain"),
        pl.col("dni").str.contains(r"^\d+X?$", literal=False).alias("valid_dni"),
    )

    digit = pl.col("dni").str.slice(-2, 2).cast(pl.Int64, strict=False)
    df = df.with_columns(
        pl.when(digit < 33).then(pl.lit("A"))
        .when(digit < 66).then(pl.lit("B"))
        .otherwise(pl.lit("C"))
        .alias("customer_category"),
    )

    logger.info(
        "Persons cleaned: %d records, %d with valid DNI",
        df.height, df["valid_dni"].sum(),
    )
    return df
