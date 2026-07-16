import logging

import polars as pl

from src.raw.schema import get_expected_columns

logger = logging.getLogger(__name__)


def check_schema(df: pl.DataFrame, table: str) -> None:
    expected = get_expected_columns(table)
    missing = set(expected) - set(df.columns)
    if missing:
        raise ValueError(f"[{table}] Missing required columns: {sorted(missing)}")
    logger.info("[%s] Schema valid — %d columns ok", table, len(expected))


def validate_raw(df: pl.DataFrame, table: str) -> None:
    check_schema(df, table)
    if df.is_empty():
        logger.warning("[%s] Empty dataset", table)
    null_count = df.null_count().sum_horizontal().item()
    if null_count > 0:
        logger.info("[%s] %d null values found", table, null_count)


def validate_users(df: pl.DataFrame) -> None:
    check_schema(df, "user")
    total = df.height
    dupes = df.filter(pl.col("email").is_duplicated()).height
    if dupes:
        logger.warning("[user] %d/%d duplicate email(s)", dupes, total)
    invalid = df.filter(~pl.col("email").str.contains(r"^[^@]+@[^@]+\.[^@]+$")).height
    if invalid:
        logger.warning("[user] %d/%d invalid email(s)", invalid, total)
    logger.info("[user] Validation passed — %d/%d ok", total - dupes - invalid, total)


def validate_persons(df: pl.DataFrame) -> None:
    check_schema(df, "person")
    total = df.height
    dupe_dnis = df.filter(pl.col("dni").is_duplicated()).height
    if dupe_dnis:
        logger.warning("[person] %d/%d duplicate DNI(s)", dupe_dnis, total)
    invalid_emails = df.filter(
        ~pl.col("email").str.contains(r"^[^@]+@[^@]+\.[^@]+$")
    ).height
    if invalid_emails:
        logger.warning("[person] %d/%d invalid email(s)", invalid_emails, total)
    invalid_phones = df.filter(
        ~pl.col("telefono_movil").str.contains(r"^\+?\d{9,15}$")
    ).height
    if invalid_phones:
        logger.warning("[person] %d/%d invalid phone(s)", invalid_phones, total)
    logger.info("[person] Validation passed — schema ok")
