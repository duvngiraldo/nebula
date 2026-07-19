from pathlib import Path

import polars as pl


DATA_DIR = Path(__file__).parents[2] / "data" / "raw"


def read_leads() -> pl.LazyFrame:
    return pl.scan_csv(DATA_DIR / "lead.csv", try_parse_dates=True)


def read_calls() -> pl.LazyFrame:
    return pl.scan_csv(DATA_DIR / "llamada.csv", try_parse_dates=True)


def read_persons() -> pl.LazyFrame:
    return pl.scan_csv(DATA_DIR / "persona.csv", try_parse_dates=True)


def read_users() -> pl.LazyFrame:
    return pl.scan_csv(DATA_DIR / "usuario.csv", try_parse_dates=True)
