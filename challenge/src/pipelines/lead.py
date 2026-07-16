import logging

import polars as pl
from src.pipelines.base import Pipeline
from src.utils import DataCleaner, SchemaValidator

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "id", "id_persona", "id_usuario", "estado", "estado_contrato",
    "formulario_de_origen", "origen_lead", "lead_type", "importe_contrato",
    "fecha_de_creacion", "fecha_de_cierre", "is_soft_delete", "visible_tabla",
]

TEST_SOURCES = ["test", "demo", "prueba_qa"]


class LeadPipeline(Pipeline):
    """Process leads: clean, enrich, and aggregate by day."""

    def __init__(self):
        super().__init__("data/raw/lead.csv", name="Leads")

    # ------------------------------------------------------------------
    # Transform
    # ------------------------------------------------------------------

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        SchemaValidator.check(df, EXPECTED_COLUMNS, "Leads")
        df = DataCleaner.run(df)

        # Type conversions
        df = df.with_columns(
            pl.col("fecha_de_creacion").str.to_datetime(format="%Y-%m-%d %H:%M:%S"),
            pl.col("fecha_de_cierre").str.to_datetime(format="%Y-%m-%d %H:%M:%S"),
            pl.col("importe_contrato").cast(pl.Float64, strict=False),
        )

        # Derived columns
        df = df.with_columns(
            pl.col("formulario_de_origen").is_in(TEST_SOURCES).alias("is_test_lead"),
            (pl.col("fecha_de_cierre") - pl.col("fecha_de_creacion"))
            .dt.total_hours()
            .alias("hours_to_close"),
            pl.col("fecha_de_creacion").dt.date().alias("date"),
        )

        # Daily aggregation
        daily = (
            df.group_by("date")
            .agg(
                total_leads=pl.col("id").count(),
                contracted=pl.col("estado").str.to_lowercase().is_in(["contratado"]).sum(),
                contract_value=pl.col("importe_contrato").sum(),
                test_leads=pl.col("is_test_lead").sum(),
            )
            .sort("date")
        )

        daily = daily.with_columns(
            (pl.col("contracted") / pl.col("total_leads") * 100)
            .round(2).fill_nan(0.0).alias("conversion_rate"),
            (pl.col("test_leads") / pl.col("total_leads") * 100)
            .round(2).fill_nan(0.0).alias("test_pct"),
            (pl.col("contract_value") / pl.col("total_leads"))
            .round(2).fill_nan(0.0).alias("avg_value"),
        )

        contracted_total = daily["contracted"].sum()
        logger.info(
            "Leads processed: %d records across %d days | %d contracted (rate %.1f%%)",
            df.height, len(daily), contracted_total,
            daily["conversion_rate"].mean(),
        )
        return daily

    # ------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------

    def validate(self, df: pl.DataFrame) -> None:
        if df.is_empty():
            logger.warning("No daily metrics generated — no valid leads")
            return
        logger.info("Lead validation passed — %d days with data", len(df))
