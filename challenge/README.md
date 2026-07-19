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
Leads per day
Conversion rate (ventas / leads)
Effective calls per day
Effective calls per agent

## Tech stack

- **Language:** Python 3.12+
- **Processing:** [Polars](https://pola.rs/) (zero‑copy, lazy by default)
- **Layers:** `raw` → `clean` → `marts`, each with focused, single-responsibility modules
- **Facade pattern:** `Pipeline` class orchestrates the full ETL lifecycle

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
