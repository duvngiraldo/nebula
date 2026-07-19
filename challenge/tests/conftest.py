from datetime import date, datetime

import polars as pl
import pytest


@pytest.fixture
def raw_leads() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "id": [1000, 1001, 1002, 1003, 1004],
            "id_persona": [2001, 2002, 2003, 2004, 2005],
            "id_usuario": [301, 302, 303, 301, 302],
            "estado": ["Nuevo", "contratado", "Contratado", "Perdido", "Nuevo"],
            "fecha_de_creacion": [
                datetime(2026, 3, 1, 10, 0, 0),
                datetime(2026, 3, 1, 12, 0, 0),
                datetime(2026, 3, 2, 9, 0, 0),
                datetime(2026, 3, 2, 14, 0, 0),
                datetime(2026, 3, 3, 8, 0, 0),
            ],
            "fecha_de_cierre": [
                None,
                datetime(2026, 3, 5, 12, 0, 0),
                datetime(2026, 3, 6, 9, 0, 0),
                None,
                None,
            ],
            "is_soft_delete": [False, False, False, True, False],
            "visible_tabla": [True, True, True, True, False],
        },
        schema={
            "id": pl.Int64,
            "id_persona": pl.Int64,
            "id_usuario": pl.Int64,
            "estado": pl.String,
            "fecha_de_creacion": pl.Datetime,
            "fecha_de_cierre": pl.Datetime,
            "is_soft_delete": pl.Boolean,
            "visible_tabla": pl.Boolean,
        },
    )


@pytest.fixture
def clean_leads_df() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "fecha_creacion": [date(2026, 3, 1), date(2026, 3, 1), date(2026, 3, 2)],
            "estado": ["nuevo", "contratado", "contratado"],
        },
        schema={
            "fecha_creacion": pl.Date,
            "estado": pl.String,
        },
    )


@pytest.fixture
def raw_calls() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "id": [5000, 5001, 5002, 5003],
            "id_lead": [1000, 1001, 1002, 1003],
            "id_usuario": [301, 302, 301, 303],
            "id_persona": [2001, 2002, 2003, 2004],
            "timestamp_connection": [
                datetime(2026, 3, 1, 10, 0, 0),
                datetime(2026, 3, 1, 11, 0, 0),
                datetime(2026, 3, 2, 9, 0, 0),
                datetime(2026, 3, 2, 14, 0, 0),
            ],
            "timestamp_call_end": [
                datetime(2026, 3, 1, 10, 0, 10),   # 10s (> 5)
                datetime(2026, 3, 1, 11, 0, 3),    # 3s (< 5)
                datetime(2026, 3, 2, 9, 0, 30),    # 30s (> 5)
                datetime(2026, 3, 2, 14, 0, 2),    # 2s (< 5)
            ],
            "is_soft_delete": [False, False, True, False],
        },
        schema={
            "id": pl.Int64,
            "id_lead": pl.Int64,
            "id_usuario": pl.Int64,
            "id_persona": pl.Int64,
            "timestamp_connection": pl.Datetime,
            "timestamp_call_end": pl.Datetime,
            "is_soft_delete": pl.Boolean,
        },
    )


@pytest.fixture
def clean_calls_df() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "fecha_llamada": [date(2026, 3, 1), date(2026, 3, 1), date(2026, 3, 2)],
            "id_usuario": [301, 302, 303],
            "duracion_segundos": [10, 3, 30],
        },
        schema={
            "fecha_llamada": pl.Date,
            "id_usuario": pl.Int64,
            "duracion_segundos": pl.Int64,
        },
    )


@pytest.fixture
def users() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "id": [301, 302, 303],
            "nombre": ["Alice", "Bob", "Charlie"],
            "email": ["a@x.com", "b@x.com", "c@x.com"],
        },
        schema={
            "id": pl.Int64,
            "nombre": pl.String,
            "email": pl.String,
        },
    )
