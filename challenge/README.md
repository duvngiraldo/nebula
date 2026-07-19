# Technical Challenge

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
- **Layers:** `raw` → `clean` → `marts`, each with focused, single-responsibility modules
- **Facade pattern:** `Pipeline` class orchestrates the full ETL lifecycle

## Project structure

```
challenge/
├── README.md
├── requirements.txt
src/
│
├── raw/                      # EXTRACT
│   ├── loader.py             # CSV loading with Polars
│   ├── schema.py             # Expected columns per table
│   └── validator.py          # Schema & quality validation
│
├── clean/                    # TRANSFORM
│   ├── leads.py              # Lead cleaning & enrichment
│   ├── calls.py              # Call cleaning & enrichment
│   ├── persons.py            # Person transformations
│   └── users.py              # User transformations
│
├── marts/                    # LOAD (Data Marts)
│   ├── daily_metrics.py      # Daily lead aggregation
│   ├── agent_metrics.py      # Agent call performance
│   ├── conversion_metrics.py # Global conversion summary
│   └── executive_report.py   # Executive KPI report
│
├── pipeline.py               # Facade: Pipeline class + Result dataclass
├── utils.py                  # Shared utilities (clean)
└── main.py                   # Entry point
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
- **Decoupling**: each layer manages its own schema and validation.
- **Fault tolerance**: structured logging, errors isolated per layer.
