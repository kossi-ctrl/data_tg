# Togo Data Quality Pipeline

An end-to-end data engineering pipeline that extracts World Bank development
indicators for Togo, loads them into PostgreSQL, transforms and tests them
with dbt, and orchestrates the whole flow with Apache Airflow.

## Why this project

Built as a hands-on exercise in **data quality and governance** — the core
theme of this pipeline is not just moving data around, but making sure it can
be trusted: automated tests catch missing values, out-of-range numbers, and
unexpected values before they reach the final tables.

## Architecture

```
World Bank API (GDP, population, electricity access)
        │
        ▼
  Extraction (Python) ──► raw schema (PostgreSQL)
        │
        ▼
  dbt staging models ──► cleaning, typing
        │
        ▼
  dbt tests ──► not_null, unique, accepted_range, accepted_values
        │
        ▼
  dbt mart model ──► combined indicators + GDP per capita
        │
        ▼
  Orchestrated end-to-end by Airflow (DAG)
```

## Stack

- **Python** — extraction (World Bank API), loading (pandas, SQLAlchemy)
- **PostgreSQL** — storage (via Docker)
- **dbt** — transformation and data quality testing
- **Apache Airflow** — orchestration

## Project structure

```
data_tg/
├── dags/
│   └── togo_pipeline_dag.py       # Airflow DAG (extraction → load → dbt run → dbt test)
├── extraction/
│   ├── get_togo_data.py           # Pulls indicators from the World Bank API
│   └── load_to_postgres.py        # Loads CSVs into PostgreSQL (raw schema)
├── dbt_project/togo_pipeline/
│   └── models/
│       ├── sources.yml            # Declares the raw tables
│       ├── stg_pib_usd.sql        # Staging: GDP
│       ├── stg_population_totale.sql
│       ├── stg_acces_electricite_pct.sql
│       ├── togo_indicateurs.sql   # Mart: combined indicators + GDP per capita
│       └── *_tests.yml            # Data quality tests
├── docker-compose.yml             # PostgreSQL container
├── .env.example                   # Environment variable template
└── .gitignore
```

## Data quality tests

Each staging model is tested for:
- **`not_null`** — no missing values on key fields
- **`unique`** — no duplicate years
- **`accepted_range`** — values within plausible bounds (e.g. 0-100% for
  electricity access)
- **`accepted_values`** — country code restricted to `TGO`

## Setup

1. Clone the repo and copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Start PostgreSQL:
   ```bash
   docker compose up -d
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run the pipeline manually:
   ```bash
   python3 extraction/get_togo_data.py
   python3 extraction/load_to_postgres.py
   cd dbt_project/togo_pipeline
   dbt run
   dbt test
   ```

Or trigger the full pipeline from Airflow using `togo_pipeline_dag.py`.

## Data source

[World Bank Open Data](https://data.worldbank.org/) — indicators used:
`NY.GDP.MKTP.CD` (GDP), `SP.POP.TOTL` (population), `EG.ELC.ACCS.ZS`
(electricity access).
