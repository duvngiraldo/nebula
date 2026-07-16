import logging

import polars as pl

logger = logging.getLogger(__name__)

TEST_SOURCES = ["test", "demo", "prueba", "prueba_qa", "pruebaqa"]


def clean_leads(df: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns(
        pl.col("fecha_de_creacion").str.to_datetime(format="%Y-%m-%d %H:%M:%S"),
        pl.col("fecha_de_cierre").str.to_datetime(format="%Y-%m-%d %H:%M:%S"),
        pl.col("importe_contrato").cast(pl.Float64, strict=False),
    )

    before = df.height
    df = df.filter(~pl.col("formulario_de_origen").str.to_lowercase().is_in(TEST_SOURCES))
    dropped = before - df.height
    if dropped:
        logger.warning("Dropped %d test lead(s): %s", dropped, TEST_SOURCES)

    df = df.with_columns(
        (pl.col("fecha_de_cierre") - pl.col("fecha_de_creacion"))
        .dt.total_hours()
        .alias("hours_to_close"),
        pl.col("fecha_de_creacion").dt.date().alias("date"),
    )

    logger.info("Leads cleaned: %d records (%d test leads discarded)", df.height, dropped)
    return df
