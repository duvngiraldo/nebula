import logging

import polars as pl
from src.pipelines.base import Pipeline
from src.utils import DataCleaner, SchemaValidator

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "id", "id_lead", "id_usuario", "id_persona", "numero",
    "tipo_de_llamada", "timestamp_connection", "timestamp_call_end",
    "id_call_connect", "is_soft_delete",
]


class CallPipeline(Pipeline):
    """Process calls: compute duration, classify, and aggregate by agent."""

    def __init__(self):
        super().__init__("data/raw/llamada.csv", name="Calls")

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        SchemaValidator.check(df, EXPECTED_COLUMNS, "Calls")
        df = DataCleaner.run(df)

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

        # Per-agent metrics
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

        logger.info(
            "Calls processed: %d records | %d active agents "
            "(avg success rate %.1f%%)",
            df.height, len(agents), agents["success_rate"].mean(),
        )
        return agents

    # ------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------

    def validate(self, df: pl.DataFrame) -> None:
        if df.is_empty():
            logger.warning("No agent metrics — no valid calls")
            return
        nulls = df.filter(pl.col("avg_duration").is_null()).height
        if nulls:
            logger.warning("%d agent(s) with unknown avg duration", nulls)
        logger.info("Call validation passed — %d agent(s) with data", len(df))
