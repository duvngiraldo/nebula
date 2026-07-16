import logging
import sys
import traceback
from typing import Any

import polars as pl

from src.metrics.business_metrics import BusinessMetrics
from src.pipelines.call import CallPipeline
from src.pipelines.lead import LeadPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> int:
    logger.info("═══ Processing started ═══")

    pipelines: dict[str, Any] = {
        "lead": LeadPipeline(),
        "call": CallPipeline(),
    }

    try:
        results: dict[str, Any] = {}
        for name, pipe in pipelines.items():
            logger.info("▶ Processing %s …", name)
            results[name] = pipe.run()

        # Business metrics
        daily = BusinessMetrics.leads_per_day(results["lead"])
        summary = BusinessMetrics.conversion_summary(results["lead"])
        agents = BusinessMetrics.calls_per_agent(results["call"])
        report = BusinessMetrics.executive_report(daily, agents, summary)

        # Console summary
        rate = (
            summary.filter(pl.col("metric") == "Conversion Rate %")
            .select("value").item()
        )

        print("\n" + "=" * 60)
        print("  NEBULA — PROCESSING SUMMARY")
        print("=" * 60)
        print(f"  Leads processed:     {len(daily)} days")
        print(f"  Agents evaluated:    {len(agents)}")
        print(f"  Conversion rate:     {rate:.2f}%")
        print(f"  Alerts generated:    {len(report['alerts'])}")
        print("=" * 60)
        return 0

    except Exception as exc:
        logger.error("Processing failed: %s", exc)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
