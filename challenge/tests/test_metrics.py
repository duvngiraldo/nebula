from datetime import date

import polars as pl

from src.marts.metrics import (
    leads_per_day,
    conversion_rate,
    effective_calls_per_day,
    effective_calls_per_agent,
)


class TestLeadsPerDay:

    def test_returns_correct_dates(self, clean_leads_df):
        result = leads_per_day(clean_leads_df)
        assert result["fecha_creacion"].to_list() == [date(2026, 3, 1), date(2026, 3, 2)]

    def test_returns_correct_counts(self, clean_leads_df):
        result = leads_per_day(clean_leads_df)
        assert result["total_leads"].to_list() == [2, 1]

    def test_empty_input(self):
        empty = pl.LazyFrame({"fecha_creacion": pl.Series([], dtype=pl.Date), "estado": pl.Series([], dtype=pl.String)})
        result = leads_per_day(empty)
        assert len(result) == 0


class TestConversionRate:

    def test_global_rate(self, clean_leads_df):
        result = conversion_rate(clean_leads_df)
        assert len(result) == 1
        assert result["total_leads"].item() == 3
        assert result["ventas"].item() == 2
        assert result["conversion_rate"].item() == 2 / 3

    def test_all_contratados(self):
        df = pl.LazyFrame(
            {"fecha_creacion": [date(2026, 3, 1), date(2026, 3, 1)], "estado": ["contratado", "contratado"]},
            schema={"fecha_creacion": pl.Date, "estado": pl.String},
        )
        result = conversion_rate(df)
        assert result["conversion_rate"].item() == 1.0

    def test_no_contratados(self):
        df = pl.LazyFrame(
            {"fecha_creacion": [date(2026, 3, 1), date(2026, 3, 1)], "estado": ["perdido", "nuevo"]},
            schema={"fecha_creacion": pl.Date, "estado": pl.String},
        )
        result = conversion_rate(df)
        assert result["conversion_rate"].item() == 0.0


class TestEffectiveCallsPerDay:

    def test_filters_short_calls(self, clean_calls_df):
        result = effective_calls_per_day(clean_calls_df)
        assert result["fecha_llamada"].to_list() == [date(2026, 3, 1), date(2026, 3, 2)]
        assert result["total_llamadas_efectivas"].to_list() == [1, 1]


class TestEffectiveCallsPerAgent:

    def test_filters_short_calls(self, clean_calls_df, users):
        result = effective_calls_per_agent(clean_calls_df, users)
        names = sorted(result["nombre"].to_list())
        assert names == ["Alice", "Charlie"]
        alice = result.filter(pl.col("id_usuario") == 301)["total_llamadas_efectivas"].item()
        charlie = result.filter(pl.col("id_usuario") == 303)["total_llamadas_efectivas"].item()
        assert alice == 1
        assert charlie == 1
        assert 302 not in result["id_usuario"].to_list()

    def test_sorts_descending(self, clean_calls_df, users):
        result = effective_calls_per_agent(clean_calls_df, users)
        counts = result["total_llamadas_efectivas"].to_list()
        assert counts == sorted(counts, reverse=True)
