import logging

import polars as pl

logger = logging.getLogger(__name__)


def compute_daily_metrics(df: pl.DataFrame) -> pl.DataFrame:
    daily = (
        df.group_by("date")
        .agg(
            total_leads=pl.col("id").count(),
            contracted=pl.col("estado").str.to_lowercase().is_in(["contratado", "Contratado"]).sum(),
            contract_value=pl.col("importe_contrato").sum(),
        )
        .sort("date")
    )

    daily = daily.with_columns(
        (pl.col("contracted") / pl.col("total_leads") * 100)
        .round(2).fill_nan(0.0).alias("conversion_rate"),
        (pl.col("contract_value") / pl.col("total_leads"))
        .round(2).fill_nan(0.0).alias("avg_value"),
    )

    contracted_total = daily["contracted"].sum()
    logger.info(
        "Daily metrics: %d days, %d contracted (avg rate %.1f%%)",
        len(daily), contracted_total, daily["conversion_rate"].mean(),
    )
    return daily
