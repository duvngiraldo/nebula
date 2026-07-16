from pathlib import Path
import logging

import polars as pl

from src.raw.validator import validate_raw, validate_users, validate_persons

logger = logging.getLogger(__name__)

DATASETS: dict[str, tuple[str, str, callable]] = {
    "leads": ("data/raw/lead.csv", "lead", validate_raw),
    "calls": ("data/raw/llamada.csv", "call", validate_raw),
    "persons": ("data/raw/persona.csv", "person", validate_persons),
    "users": ("data/raw/usuario.csv", "user", validate_users),
}


def load_csv(path: str | Path) -> pl.DataFrame:
    path = Path(path)
    df = pl.read_csv(path)
    logger.info("Loaded %s: %d records, %d columns", path.name, len(df), len(df.columns))
    return df


def load_all() -> dict[str, pl.DataFrame]:
    raw: dict[str, pl.DataFrame] = {}
    for name, (path, table, validator) in DATASETS.items():
        df = load_csv(path)
        validator(df, table) if validator is validate_raw else validator(df)
        raw[name] = df
    return raw
