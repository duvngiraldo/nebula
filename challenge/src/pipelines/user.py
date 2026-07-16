import logging

import polars as pl
from src.pipelines.base import Pipeline
from src.utils import DataCleaner, SchemaValidator

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = ["id", "email", "nombre"]


class UserPipeline(Pipeline):
    """Enrich agent records with email domain and role level."""

    def __init__(self):
        super().__init__("data/raw/usuario.csv", name="Agents")

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        SchemaValidator.check(df, EXPECTED_COLUMNS, "Agents")
        df = DataCleaner.run(df)

        df = df.with_columns(
            pl.col("email").str.split("@").list.last().alias("email_domain"),
        )

        df = df.with_columns(
            pl.when(pl.col("nombre").str.len_chars() < 5).then(pl.lit("Junior"))
            .when(pl.col("nombre").str.len_chars() < 10).then(pl.lit("Mid"))
            .otherwise(pl.lit("Senior"))
            .alias("agent_level"),
        )

        logger.info("Agents enriched: %d active records", df.height)
        return df

    # ------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------

    def validate(self, df: pl.DataFrame) -> None:
        if df.is_empty():
            logger.warning("No agent records")
            return
        dupes = df.group_by("email").agg(pl.len()).filter(pl.col("len") > 1).height
        if dupes:
            logger.warning("Detected %d agent(s) with duplicate email", dupes)
        logger.info("Agent validation passed")
