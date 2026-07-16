from src.clean.leads import clean_leads
from src.clean.calls import clean_calls
from src.clean.persons import clean_persons
from src.clean.users import clean_users

import polars as pl

CLEAN_FUNCS: dict[str, callable] = {
    "leads": clean_leads,
    "calls": clean_calls,
    "persons": clean_persons,
    "users": clean_users,
}


def clean_all(raw: dict[str, pl.DataFrame]) -> dict[str, pl.DataFrame]:
    return {name: fn(raw[name]) for name, fn in CLEAN_FUNCS.items()}


__all__ = [
    "clean_leads", "clean_calls", "clean_persons", "clean_users",
    "CLEAN_FUNCS", "clean_all",
]
