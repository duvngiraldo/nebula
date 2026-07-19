import time

import polars as pl

from src.raw.reader import read_leads, read_calls, read_users
from src.clean.cleaner import clean_leads, clean_calls
from src.marts.metrics import (
    leads_per_day,
    conversion_rate,
    effective_calls_per_day,
    effective_calls_per_agent,
    write_all,
)


class Pipeline:

    def run(self) -> None:
        t0 = time.time()
        self._print_header()

        raw = self._phase_raw()
        clean = self._phase_clean(raw)
        self._phase_marts(clean)

        self._print_footer(t0)

    # ── phases ──────────────────────────────────────────────

    def _phase_raw(self) -> dict:
        print("── raw ───────────────────────────────────────────────")
        leads = read_leads()
        calls = read_calls()
        users = read_users()
        print(f"  leads={leads.collect().height}, "
              f"calls={calls.collect().height}, "
              f"users={users.collect().height}")
        return {"leads": leads, "calls": calls, "users": users}

    def _phase_clean(self, raw: dict) -> dict:
        print("\n── clean ──────────────────────────────────────────────")
        leads = clean_leads(raw["leads"])
        calls = clean_calls(raw["calls"])
        n_leads = leads.select(pl.len()).collect().item()
        n_calls = calls.select(pl.len()).collect().item()
        print(f"  leads={n_leads}, calls={n_calls}")
        return {"leads": leads, "calls": calls, "users": raw["users"]}

    def _phase_marts(self, clean: dict) -> dict:
        print("\n── marts ──────────────────────────────────────────────")
        results = {
            "leads_per_day": leads_per_day(clean["leads"]),
            "conversion_rate": conversion_rate(clean["leads"]),
            "effective_calls_per_day": effective_calls_per_day(clean["calls"]),
            "effective_calls_per_agent": effective_calls_per_agent(
                clean["calls"], clean["users"]
            ),
        }
        write_all(results)
        return results

    # ── helpers ──────────────────────────────────────────────

    @staticmethod
    def _print_header() -> None:
        print("=" * 48)
        print("  Pipeline ETL")
        print("=" * 48)

    @staticmethod
    def _print_footer(t0: float) -> None:
        elapsed = time.time() - t0
        print(f"\n{'=' * 48}")
        print(f"  Pipeline completado en {elapsed:.2f}s")
        print(f"{'=' * 48}")
