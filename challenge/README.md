# Technical Challenge / Desafío Técnico

## Raw data / Datos crudos

| File / Archivo    | Records / Registros | Description / Descripción               |
|--------------------|---------------------|------------------------------------------|
| `lead.csv`         | 61                  | Leads with status, source, value / Leads con estado, origen, importe |
| `llamada.csv`      | 80                  | Calls with timestamps and agent / Llamadas con timestamp y agente |
| `persona.csv`      | 30                  | Persons / customers / Personas / clientes |
| `usuario.csv`      | 3                   | Commercial agents / Agentes comerciales  |

Each lead references a person (`id_persona`) and a user/agent (`id_usuario`). / Cada lead referencia una persona y un usuario/agente.

## Goal / Objetivo

- Leads per day / Leads por día
- Conversion rate (ventas / leads) / Tasa de conversión (ventas / leads)
- Effective calls per day / Llamadas efectivas por día
- Effective calls per agent / Llamadas efectivas por agente

## Tech stack / Tecnología

- **Language / Lenguaje:** Python 3.12+
- **Processing / Procesamiento:** [Polars](https://pola.rs/) (zero‑copy, lazy by default)
- **Layers / Capas:** `raw` → `clean` → `marts`, each with focused, single-responsibility modules / cada capa con módulos enfocados de una sola responsabilidad
- **Facade pattern / Patrón facade:** `Pipeline` class orchestrates the full ETL lifecycle / la clase `Pipeline` orquesta todo el ciclo ETL

## How to run / Cómo ejecutar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r challenge/requirements.txt

python3 -m src.main
```

## Tests / Pruebas

```bash
python3 -m pytest tests/ -v
```

| Test class / Clase de prueba | Metric / Métrica | Cases / Casos |
|---|---|---|
| `TestLeadsPerDay` | leads per day / leads por día | dates, counts, empty input / fechas, conteos, entrada vacía |
| `TestConversionRate` | conversion rate / tasa de conversión | correct rate, 0%, 100%, ventas count / tasa correcta, 0%, 100%, conteo de ventas |
| `TestEffectiveCallsPerDay` | effective calls per day / llamadas efectivas por día | dates, counts / fechas, conteos |
| `TestEffectiveCallsPerAgent` | effective calls per agent / llamadas efectivas por agente | names, counts, descending order / nombres, conteos, orden descendente |

## Decisions & assumptions / Decisiones y supuestos

### What is considered valid / Qué se considera válido

- **Leads**: only records with `is_soft_delete=False` and `visible_tabla=True`. A lead is a "venta" when its `estado` is `contratado` (case-insensitive — "Contratado" and "contratado" are normalized to lowercase). / Solo registros sin borrado lógico y visibles. Un lead es "venta" cuando su estado es `contratado` (sin distinción de mayúsculas).
- **Calls / Llamadas**: only records with `is_soft_delete=False`. All non-deleted calls are considered "effective" — every record has a non-null `id_call_connect`, so no additional duration filter was applied. / Solo registros sin borrado lógico. Todas las llamadas no eliminadas se consideran "efectivas" — todos los registros tienen `id_call_connect` no nulo, por lo que no se aplicó filtro adicional de duración.
- **Conversion rate / Tasa de conversión**: computed per day as `ventas / total_leads` for that day, not a global rate. / Calculada por día como `ventas / total_leads` de ese día, no una tasa global.

### What was discarded / Qué se descartó

- **`persona.csv`**: not needed for any of the 4 requested metrics (no persona-level aggregation was specified). / No es necesario para ninguna de las 4 métricas solicitadas (no se especificó agregación a nivel de persona).
- **Soft-deleted records / Registros con borrado lógico**: 2 calls (`id` 5042, 5066) and 6 leads with `is_soft_delete=True`. Additionally, leads with `visible_tabla=False` are excluded — they represent internal/test records that shouldn't skew business metrics. / 2 llamadas y 6 leads con `is_soft_delete=True`; además, leads con `visible_tabla=False` se excluyen por ser registros internos/de prueba.

### Why the figures are trustworthy / Por qué las cifras son confiables

1. **Deterministic pipeline / Pipeline determinista**: same input always produces the same output — no random seeds, no sampling. / La misma entrada siempre produce la misma salida — sin semillas aleatorias ni muestreo.
2. **Cross-validated counts / Conteos validados cruzadamente**: `effective_calls_per_day` sums match `effective_calls_per_agent` totals (77 calls). Lead counts are independently reproducible by filtering the raw CSV. / La suma de `effective_calls_per_day` coincide con el total de `effective_calls_per_agent` (77 llamadas). Los conteos de leads son reproduciblemente filtrados del CSV original.
3. **Lazy execution with schema enforcement / Ejecución lazy con esquema forzado**: Polars validates types at scan time; the clean layer applies explicit filters and casts before any metric is computed. / Polars valida tipos al escanear; la capa clean aplica filtros y casts explícitos antes de calcular cualquier métrica.
4. **12 unit tests covering all 4 metrics / 12 pruebas unitarias cubriendo las 4 métricas**: including edge cases (empty input, 0% / 100% conversion, sorted output). / Incluyendo casos límite (entrada vacía, conversión 0% / 100%, salida ordenada).

## Design principles / Principios de diseño

- **Self‑documenting code / Código autodocumentado**: expressive names + brief docstrings. / Nombres expresivos + docstrings breves.
- **Immutability / Inmutabilidad**: Polars avoids unnecessary copies; chained transformations. / Polars evita copias innecesarias; transformaciones encadenadas.
- **Decoupling / Desacoplamiento**: each layer manages its own schema and validation. / Cada capa gestiona su propio esquema y validación.
- **Fault tolerance / Tolerancia a fallos**: structured logging, errors isolated per layer. / Logging estructurado, errores aislados por capa.
