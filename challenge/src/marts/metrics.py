from pathlib import Path

import polars as pl

MARTS_DIR = Path(__file__).parents[2] / "data" / "marts"


def leads_per_day(leads: pl.LazyFrame) -> pl.DataFrame:
    return (
        leads
        .group_by("fecha_creacion")
        .agg(pl.len().alias("total_leads"))
        .sort("fecha_creacion")
        .collect()
    )


def conversion_rate(leads: pl.LazyFrame) -> pl.DataFrame:
    return (
        leads
        .group_by("fecha_creacion")
        .agg(
            pl.len().alias("total_leads"),
            pl.col("estado").str.to_lowercase().eq("contratado").sum().alias("ventas"),
        )
        .with_columns(
            (pl.col("ventas") / pl.col("total_leads")).alias("conversion_rate"),
        )
        .sort("fecha_creacion")
        .collect()
    )


def effective_calls_per_day(calls: pl.LazyFrame) -> pl.DataFrame:
    return (
        calls
        .group_by("fecha_llamada")
        .agg(pl.len().alias("total_llamadas_efectivas"))
        .sort("fecha_llamada")
        .collect()
    )


def effective_calls_per_agent(calls: pl.LazyFrame, users: pl.LazyFrame) -> pl.DataFrame:
    return (
        calls
        .group_by("id_usuario")
        .agg(pl.len().alias("total_llamadas_efectivas"))
        .join(users, left_on="id_usuario", right_on="id", how="left")
        .select("id_usuario", "nombre", "total_llamadas_efectivas")
        .sort("total_llamadas_efectivas", descending=True)
        .collect()
    )


def write_all(results: dict[str, pl.DataFrame]) -> None:
    MARTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in results.items():
        path = MARTS_DIR / f"{name}.csv"
        df.write_csv(path)
        print(f"  ✓ {path.name} ({len(df)} rows)")
