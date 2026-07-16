import logging
from datetime import datetime
from typing import Any

import polars as pl

logger = logging.getLogger(__name__)


def build_executive_report(
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

    logger.info("Executive report: %d alert(s), %d finding(s)",
                len(report["alerts"]), len(report["findings"]))
    return report
