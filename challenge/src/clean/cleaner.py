import polars as pl


def clean_leads(raw: pl.LazyFrame) -> pl.LazyFrame:
    """Filter out soft-deleted and invisible leads, normalise timestamps to dates and estado to lowercase."""
    return (
        raw
        .filter(pl.col("is_soft_delete") == False)
        .filter(pl.col("visible_tabla") == True)
        .with_columns(
            pl.col("fecha_de_creacion").dt.date().alias("fecha_creacion"),
            pl.col("fecha_de_cierre").dt.date().alias("fecha_cierre"),
            pl.col("estado").str.to_lowercase().alias("estado"),
        )
    )


def clean_calls(raw: pl.LazyFrame) -> pl.LazyFrame:
    """Remove soft-deleted calls, extract call date and compute duration in seconds."""
    return (
        raw
        .filter(pl.col("is_soft_delete") == False)
        .with_columns(
            pl.col("timestamp_connection").dt.date().alias("fecha_llamada"),
            (pl.col("timestamp_call_end") - pl.col("timestamp_connection"))
            .dt.total_seconds().alias("duracion_segundos"),
        )
    )
