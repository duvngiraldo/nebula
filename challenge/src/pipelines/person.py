import logging

import polars as pl
from src.pipelines.base import Pipeline
from src.utils import DataCleaner, SchemaValidator

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = ["id", "telefono_movil", "email", "dni", "nombre"]


class PersonPipeline(Pipeline):
    """Enrich person records with email domain and customer category."""

    def __init__(self):
        super().__init__("data/raw/persona.csv", name="Persons")

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        SchemaValidator.check(df, EXPECTED_COLUMNS, "Persons")
        df = DataCleaner.run(df)

        df = df.with_columns(
            pl.col("email").str.split("@").list.last().alias("email_domain"),
            pl.col("dni").str.contains(r"^\d+X?$", literal=False).alias("valid_dni"),
        )

        # Category A/B/C based on last two DNI digits
        digit = pl.col("dni").str.slice(-2, 2).cast(pl.Int64, strict=False)
        df = df.with_columns(
            pl.when(digit < 33).then(pl.lit("A"))
            .when(digit < 66).then(pl.lit("B"))
            .otherwise(pl.lit("C"))
            .alias("customer_category"),
        )

        logger.info(
            "Persons enriched: %d records | %d with valid DNI",
            df.height, df["valid_dni"].sum(),
        )
        return df

    # ------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------

    def validate(self, df: pl.DataFrame) -> None:
        if df.is_empty():
            logger.warning("No person records")
            return
        bad = df.filter(~pl.col("email").str.contains("@")).height
        if bad:
            logger.warning("%d record(s) with invalid email", bad)
        logger.info("Person validation passed")
