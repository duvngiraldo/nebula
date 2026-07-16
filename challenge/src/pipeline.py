from dataclasses import dataclass, field
from typing import Any

import polars as pl

from src.raw import load_all
from src.clean import clean_all
from src.marts import (
    compute_daily_metrics,
    compute_agent_metrics,
    compute_conversion_summary,
    build_executive_report,
)


@dataclass
class Result:
    daily: pl.DataFrame = field(default_factory=pl.DataFrame)
    agents: pl.DataFrame = field(default_factory=pl.DataFrame)
    summary: pl.DataFrame = field(default_factory=pl.DataFrame)
    report: dict[str, Any] = field(default_factory=dict)

    @property
    def conversion_rate(self) -> float:
        if self.summary.is_empty():
            return 0.0
        return (
            self.summary.filter(pl.col("metric") == "Conversion Rate %")
            .select("value").item()
        )


class Pipeline:
    def extract(self) -> dict[str, pl.DataFrame]:
        return load_all()

    def transform(self, raw: dict[str, pl.DataFrame]) -> dict[str, pl.DataFrame]:
        return clean_all(raw)

    def load(self, clean: dict[str, pl.DataFrame]) -> Result:
        daily = compute_daily_metrics(clean["leads"])
        agents = compute_agent_metrics(clean["calls"])
        summary = compute_conversion_summary(daily)
        report = build_executive_report(daily, agents, summary)
        return Result(daily=daily, agents=agents, summary=summary, report=report)

    def run(self) -> Result:
        raw = self.extract()
        clean = self.transform(raw)
        return self.load(clean)
