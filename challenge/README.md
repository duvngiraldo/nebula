# Desafío Técnico

## Datos crudos

| Archivo          | Registros | Descripción                         |
|------------------|-----------|-------------------------------------|
| `lead.csv`       | 61        | Leads con estado, origen, importe   |
| `llamada.csv`    | 80        | Llamadas con timestamp y agente     |
| `persona.csv`    | 30        | Personas / clientes                 |
| `usuario.csv`    | 3         | Agentes comerciales                 |

Cada lead referencia una persona (`id_persona`) y un usuario/agente (`id_usuario`).

## Objetivo

- Leads por día
- Tasa de conversión (ventas / leads)
- Llamadas efectivas por día
- Llamadas efectivas por agente

## Tecnología

- **Lenguaje:** Python 3.12+
- **Procesamiento:** [Polars](https://pola.rs/) (zero‑copy, lazy por defecto)
- **Capas:** `raw` → `clean` → `marts`, cada capa con módulos enfocados de una sola responsabilidad
- **Patrón facade:** la clase `Pipeline` orquesta todo el ciclo ETL

## Cómo ejecutar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r challenge/requirements.txt

python3 -m src.main
```

## Pruebas

```bash
python3 -m pytest tests/ -v
```

| Clase de prueba      | Métrica                          | Casos                                       |
|----------------------|----------------------------------|---------------------------------------------|
| `TestLeadsPerDay`    | leads por día                    | fechas, conteos, entrada vacía              |
| `TestConversionRate` | tasa de conversión (global)      | valor único, 0%, 100%, conteo de ventas     |
| `TestEffectiveCallsPerDay` | llamadas efectivas por día | fechas, conteos                             |
| `TestEffectiveCallsPerAgent` | llamadas efectivas por agente | nombres, conteos, orden descendente |

## Decisiones y supuestos

### Qué se considera válido

- **Leads**: solo registros con `is_soft_delete=False` y `visible_tabla=True`. Un lead es "venta" cuando su `estado` es `contratado` (sin distinción de mayúsculas — "Contratado" y "contratado" se normalizan a minúsculas).
- **Llamadas**: solo registros con `is_soft_delete=False` y duración mayor a 5 segundos (`timestamp_call_end - timestamp_connection > 5s`).
- **Tasa de conversión**: valor único global `ventas / total_leads`, no una serie por día.

### Qué se descartó

- **`persona.csv`**: no es necesario para ninguna de las 4 métricas solicitadas (no se especificó agregación a nivel de persona). Se detectó una anomalía: las personas 2005 y 2006 comparten el mismo teléfono (`+34600000005`), lo cual no afecta las métricas actuales pero sería relevante si se requiriera validación de contacto único.
- **Registros con borrado lógico**: 2 llamadas (`id` 5042, 5066) y 6 leads con `is_soft_delete=True`. Además, leads con `visible_tabla=False` se excluyen por ser registros internos / de prueba que no deberían sesgar las métricas de negocio.

### Por qué las cifras son confiables

1. **Pipeline determinista**: la misma entrada siempre produce la misma salida — sin semillas aleatorias ni muestreo.
2. **Conteos validados cruzadamente**: la suma de `effective_calls_per_day` coincide con el total de `effective_calls_per_agent` (77 llamadas). Los conteos de leads son reproduciblemente filtrados del CSV original.
3. **Ejecución lazy con esquema forzado**: Polars valida tipos al escanear; la capa clean aplica filtros y casts explícitos antes de calcular cualquier métrica.
4. **12 pruebas unitarias cubriendo las 4 métricas**: incluyendo casos límite (entrada vacía, conversión 0% / 100%, salida ordenada).

## Principios de diseño

- **Código autodocumentado**: nombres expresivos + docstrings breves.
- **Inmutabilidad**: Polars evita copias innecesarias; transformaciones encadenadas.
- **Desacoplamiento**: cada capa gestiona su propio esquema y validación.
- **Tolerancia a fallos**: logging estructurado, errores aislados por capa.

---

# Technical Challenge

## Raw data

| File               | Records | Description                  |
|--------------------|---------|------------------------------|
| `lead.csv`         | 61      | Leads with status, source, value |
| `llamada.csv`      | 80      | Calls with timestamps and agent  |
| `persona.csv`      | 30      | Persons / customers              |
| `usuario.csv`      | 3       | Commercial agents                |

Each lead references a person (`id_persona`) and a user/agent (`id_usuario`).

## Goal

- Leads per day
- Conversion rate (ventas / leads)
- Effective calls per day
- Effective calls per agent

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

## Tests

```bash
python3 -m pytest tests/ -v
```

| Test class | Metric | Cases |
|---|---|---|
| `TestLeadsPerDay` | leads per day | dates, counts, empty input |
| `TestConversionRate` | conversion rate (global) | single value, 0%, 100%, ventas count |
| `TestEffectiveCallsPerDay` | effective calls per day | dates, counts |
| `TestEffectiveCallsPerAgent` | effective calls per agent | names, counts, descending order |

## Decisions & assumptions

### What is considered valid

- **Leads**: only records with `is_soft_delete=False` and `visible_tabla=True`. A lead is a "venta" when its `estado` is `contratado` (case-insensitive — "Contratado" and "contratado" are normalized to lowercase).
- **Calls**: only records with `is_soft_delete=False` and duration greater than 5 seconds (`timestamp_call_end - timestamp_connection > 5s`).
- **Conversion rate**: single global value `ventas / total_leads`, not a daily series.

### What was discarded

- **`persona.csv`**: not needed for any of the 4 requested metrics (no persona-level aggregation was specified).
- **Soft-deleted records**: 2 calls (`id` 5042, 5066) and 6 leads with `is_soft_delete=True`. Additionally, leads with `visible_tabla=False` are excluded — they represent internal/test records that shouldn't skew business metrics.

### Why the figures are trustworthy

1. **Deterministic pipeline**: same input always produces the same output — no random seeds, no sampling.
2. **Cross-validated counts**: `effective_calls_per_day` sums match `effective_calls_per_agent` totals (77 calls). Lead counts are independently reproducible by filtering the raw CSV.
3. **Lazy execution with schema enforcement**: Polars validates types at scan time; the clean layer applies explicit filters and casts before any metric is computed.
4. **12 unit tests covering all 4 metrics**: including edge cases (empty input, 0% / 100% conversion, sorted output).

## Design principles

- **Self‑documenting code**: expressive names + brief docstrings.
- **Immutability**: Polars avoids unnecessary copies; chained transformations.
- **Decoupling**: each layer manages its own schema and validation.
- **Fault tolerance**: structured logging, errors isolated per layer.
