import polars as pl

from src.clean.cleaner import clean_leads, clean_calls


class TestCleanLeads:

    def test_filters_soft_deletes(self, raw_leads):
        result = clean_leads(raw_leads).collect()
        ids = set(result["id"].to_list())
        assert 1003 not in ids

    def test_filters_invisible(self, raw_leads):
        result = clean_leads(raw_leads).collect()
        ids = set(result["id"].to_list())
        assert 1004 not in ids

    def test_lowercases_estado(self, raw_leads):
        result = clean_leads(raw_leads).collect()
        for e in result["estado"]:
            assert e == e.lower()

    def test_fecha_creacion_is_date(self, raw_leads):
        result = clean_leads(raw_leads).collect()
        assert result.schema["fecha_creacion"] == pl.Date


class TestCleanCalls:

    def test_filters_soft_deletes(self, raw_calls):
        result = clean_calls(raw_calls).collect()
        ids = set(result["id"].to_list())
        assert 5002 not in ids

    def test_fecha_llamada_is_date(self, raw_calls):
        result = clean_calls(raw_calls).collect()
        assert result.schema["fecha_llamada"] == pl.Date

    def test_computes_duration(self, raw_calls):
        result = clean_calls(raw_calls).collect()
        row_5000 = result.filter(pl.col("id") == 5000)["duracion_segundos"].item()
        assert row_5000 == 10
