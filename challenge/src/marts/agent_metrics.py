import logging

import polars as pl

logger = logging.getLogger(__name__)


def compute_agent_metrics(df: pl.DataFrame) -> pl.DataFrame:
    agents = (
        df.group_by("id_usuario")
        .agg(
            total_calls=pl.col("id").count(),
            valid_calls=pl.col("is_valid").sum(),
            avg_duration=pl.col("duration_minutes").mean(),
            inbound_calls=pl.col("is_inbound").sum(),
        )
        .sort("id_usuario")
    )

    agents = agents.with_columns(
        (pl.col("valid_calls") / pl.col("total_calls") * 100)
        .round(2).alias("success_rate"),
        (pl.col("inbound_calls") / pl.col("total_calls") * 100)
        .round(2).alias("inbound_rate"),
    )

    agents = agents.with_columns(
        (pl.col("valid_calls") / pl.col("avg_duration"))
        .fill_nan(0.0).alias("duration_efficiency"),
        (pl.col("valid_calls") / pl.col("total_calls"))
        .round(3).alias("effectiveness_rate"),
    ).sort("id_usuario")

    logger.info(
        "Agent metrics: %d agent(s), avg success rate %.1f%%",
        len(agents), agents["success_rate"].mean(),
    )
    return agents
