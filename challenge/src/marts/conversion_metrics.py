import logging

import polars as pl

logger = logging.getLogger(__name__)


def compute_conversion_summary(daily: pl.DataFrame) -> pl.DataFrame:
    if daily.is_empty():
        return pl.DataFrame()

    total_leads = daily["total_leads"].sum()
    contracted = daily["contracted"].sum()
    rate = round(contracted / total_leads * 100, 2) if total_leads else 0.0
    avg_val = round(daily["contract_value"].sum() / total_leads, 2) if total_leads else 0.0

    logger.info(
        "Global conversion: %d leads, %d contracted (%.2f%%)",
        total_leads, contracted, rate,
    )
    return pl.DataFrame({
        "metric": [
            "Total Leads", "Contracted",
            "Conversion Rate %", "Avg Contract Value",
        ],
        "value": [float(v) for v in (total_leads, contracted, rate, avg_val)],
    })
