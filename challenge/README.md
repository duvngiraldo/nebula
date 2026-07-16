# Nebula | Data Engineer Technical Challenge

## Context

You are a Data Engineer at Nebula, an insurtech expanding its sales channel.  
The commercial team needs visibility into lead, call, and agent performance to make data-driven decisions.

## Raw data (CSV)

| File               | Records | Description                  |
|--------------------|---------|------------------------------|
| `lead.csv`         | 61      | Leads with status, source, value |
| `llamada.csv`      | 80      | Calls with timestamps and agent  |
| `persona.csv`      | 30      | Persons / customers              |
| `usuario.csv`      | 3       | Commercial agents                |

Each lead references a person (`id_persona`) and a user/agent (`id_usuario`).

## Goal

Build an ETL pipeline that:

1. **Extracts** CSVs from `data/raw/`.
2. **Transforms** data to produce three analytical views.
3. **Validates** the quality of processed data.
4. **Outputs** results to `data/marts/`.

### Pipeline outputs

All processing is done **in‑memory**. The pipeline produces:

- **Daily lead aggregation** – leads, contracts, conversion rate per day
- **Agent call metrics** – total calls, success rate, duration per agent
- **Global conversion summary** – total leads, contracted, conversion %
- **Executive report** – JSON dict with KPIs and alerts

## Tech stack

- **Language:** Python 3.12+
- **Processing:** [Polars](https://pola.rs/) (zero‑copy, lazy by default)
- **Architecture:** Abstract pipeline (`ABC`) with `extract` / `transform` / `validate` / `run`

## Project structure

```
challenge/
├── README.md
├── requirements.txt
├── data/
│   └── raw/          ← Original CSVs (do not modify)
└── src/
    ├── __init__.py
    ├── main.py              ← Orchestrator
    ├── utils/
    │   └── __init__.py      ← SchemaValidator, DataCleaner
    ├── pipelines/
    │   ├── base.py          ← ABC Pipeline
    │   ├── lead.py          ← Lead processing
    │   ├── call.py          ← Call processing
    │   ├── person.py        ← Person enrichment
    │   └── user.py          ← Agent enrichment
    └── metrics/
        └── business_metrics.py  ← KPI calculations
```

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r challenge/requirements.txt

python3 -m src.main
```

## Design principles

- **Self‑documenting code**: expressive names + brief docstrings.
- **Immutability**: Polars avoids unnecessary copies; chained transformations.
- **Decoupling**: each pipeline manages its own schema and validation.
- **Fault tolerance**: structured logging, errors isolated per pipeline.
