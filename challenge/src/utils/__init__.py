import logging

import polars as pl

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Check that a DataFrame contains all expected columns."""

    @staticmethod
    def check(df: pl.DataFrame, expected: list[str], context: str) -> None:
        missing = set(expected) - set(df.columns)
        if missing:
            raise ValueError(
                f"[{context}] Missing required columns: {sorted(missing)}"
            )
        logger.info("[%s] Schema valid — %d columns ok", context, len(expected))


class DataCleaner:
    """Basic cleaning: remove duplicates and strip whitespace."""

    @staticmethod
    def run(df: pl.DataFrame) -> pl.DataFrame:
        before = len(df)
        df = (
            df.unique()
            .with_columns(pl.col(pl.Utf8).str.strip_chars())
        )
        after = len(df)
        if before != after:
            logger.info("Removed %d duplicate records", before - after)
        return df
