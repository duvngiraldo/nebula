import logging
from datetime import datetime
from typing import Any

import polars as pl

logger = logging.getLogger(__name__)


class BusinessMetrics:
    """Business KPIs built from pipeline outputs."""

    # ------------------------------------------------------------------
    # Leads per day
    # ------------------------------------------------------------------

    @staticmethod
    def leads_per_day(daily: pl.DataFrame) -> pl.DataFrame:
        if daily.is_empty():
            return pl.DataFrame()
        total = daily["contracted"].sum()
        logger.info(
            "Daily metrics ready — %d days, %d contracts (avg rate %.1f%%)",
            len(daily), total, daily["conversion_rate"].mean(),
        )
        return daily

    # ------------------------------------------------------------------
    # Conversion summary
    # ------------------------------------------------------------------

    @staticmethod
    def conversion_summary(daily: pl.DataFrame) -> pl.DataFrame:
        if daily.is_empty():
            return pl.DataFrame()

        total_leads = daily["total_leads"].sum()
        contracted = daily["contracted"].sum()
        rate = round(contracted / total_leads * 100, 2) if total_leads else 0.0
        avg_val = round(daily["contract_value"].sum() / total_leads, 2) if total_leads else 0.0

        logger.info(
            "Global conversion: %d leads, %d contracted (%.2f%%) — avg value %.2f",
            total_leads, contracted, rate, avg_val,
        )
        return pl.DataFrame({
            "metric": [
                "Total Leads", "Contracted",
                "Conversion Rate %", "Avg Contract Value",
            ],
            "value": [float(v) for v in (total_leads, contracted, rate, avg_val)],
        })

    # ------------------------------------------------------------------
    # Effective calls per agent
    # ------------------------------------------------------------------

    @staticmethod
    def calls_per_agent(agents: pl.DataFrame) -> pl.DataFrame:
        if agents.is_empty():
            return pl.DataFrame()

        out = agents.with_columns(
            (pl.col("valid_calls") / pl.col("avg_duration"))
            .fill_nan(0.0).alias("duration_efficiency"),
            (pl.col("valid_calls") / pl.col("total_calls"))
            .round(3).alias("effectiveness_rate"),
        ).sort("id_usuario")

        logger.info(
            "Agent performance: %d active agent(s) (avg success rate %.1f%%)",
            len(out), out["success_rate"].mean(),
        )
        return out

    # ------------------------------------------------------------------
    # Executive report
    # ------------------------------------------------------------------

    @staticmethod
    def executive_report(
        daily: pl.DataFrame,
        agents: pl.DataFrame,
        summary: pl.DataFrame,
    ) -> dict[str, Any]:
        report: dict[str, Any] = {
            "generated_at": datetime.now().isoformat(),
            "leads": {},
            "calls": {},
            "conversion": summary.to_dicts() if not summary.is_empty() else [],
            "alerts": [],
            "findings": [],
        }

        if not daily.is_empty():
            report["leads"] = {
                "days_analyzed": len(daily),
                "daily_avg": round(daily["total_leads"].mean(), 2),
                "avg_conversion_rate": round(daily["conversion_rate"].mean(), 2),
                "best_day": int(daily["total_leads"].max()),
                "worst_conversion": round(daily["conversion_rate"].min(), 2),
            }
            if daily["conversion_rate"].std() > 20:
                report["alerts"].append(
                    f"High daily conversion volatility (σ={daily['conversion_rate'].std():.1f}%%)"
                )

        if not agents.is_empty():
            report["calls"] = {
                "active_agents": len(agents),
                "avg_success_rate": round(agents["success_rate"].mean(), 2),
                "avg_inbound_rate": round(agents["inbound_rate"].mean(), 2),
                "total_calls": int(agents["total_calls"].sum()),
            }
            if agents["success_rate"].mean() < 70:
                report["alerts"].append(
                    f"Low performance: avg success rate {agents['success_rate'].mean():.1f}%%"
                )

        report["findings"].append(
            f"Processed {report['leads'].get('days_analyzed', 'N/A')} days "
            f"across {report['calls'].get('active_agents', 'N/A')} agent(s)"
        )

        logger.info("Executive report generated with %d alert(s)", len(report["alerts"]))
        return report
