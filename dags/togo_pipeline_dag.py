"""
DAG Airflow pour le pipeline de qualité de données Togo.

Enchaîne :
  1. get_togo_data.py       -> extraction API Banque mondiale
  2. load_to_postgres.py    -> chargement dans PostgreSQL (schéma raw)
  3. dbt run                -> transformation (nettoyage) vers schéma dbt_dev
  4. dbt test                -> vérification de la qualité des données
"""

from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

# Chemins du projet (ajuste si besoin selon ton installation)
PROJECT_DIR = "/home/kossi/Projets/data_tg"
EXTRACTION_DIR = f"{PROJECT_DIR}/extraction"
DBT_PROJECT_DIR = f"{PROJECT_DIR}/dbt_project/togo_pipeline"

# Interpréteur Python du venv du projet (pas celui d'Airflow)
PYTHON_BIN = f"{PROJECT_DIR}/venv/bin/python3"

# Exécutable dbt du même venv
DBT_BIN = f"{PROJECT_DIR}/venv/bin/dbt"

with DAG(
    dag_id="togo_data_quality_pipeline",
    description="Pipeline Togo : extraction Banque mondiale -> PostgreSQL -> dbt (transformation + tests qualité)",
    start_date=datetime(2026, 1, 1),
    schedule=None,  # déclenchement manuel
    catchup=False,
    tags=["togo", "data-quality", "dbt"],
) as dag:

    task_extraction = BashOperator(
        task_id="extraction_worldbank",
        bash_command=f"cd {EXTRACTION_DIR} && {PYTHON_BIN} get_togo_data.py",
    )

    task_load = BashOperator(
        task_id="load_to_postgres",
        bash_command=f"cd {EXTRACTION_DIR} && {PYTHON_BIN} load_to_postgres.py",
    )

    task_dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_BIN} run",
    )

    task_dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT_BIN} test",
    )

    task_extraction >> task_load >> task_dbt_run >> task_dbt_test
