"""
Charge les fichiers CSV extraits (dossier extraction_output/) dans PostgreSQL,
dans un schéma "raw" (données brutes, non transformées).

Usage :
    python3 load_to_postgres.py
"""

from pathlib import Path

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Charge les variables du fichier .env (à la racine du projet)
load_dotenv(Path(__file__).parent.parent / ".env")

COUNTRY_CODE = "TGO"

DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
DB_HOST = os.environ["POSTGRES_HOST"]
DB_PORT = os.environ["POSTGRES_PORT"]
DB_NAME = os.environ["POSTGRES_DB"]

CSV_DIR = Path("../extraction_output")

# Correspondance nom de fichier CSV -> nom de table dans le schéma "raw"
FILES_TO_TABLES = {
    "pib_usd.csv": "pib_usd",
    "population_totale.csv": "population_totale",
    "acces_electricite_pct.csv": "acces_electricite_pct",
}


def get_engine():
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(connection_string)


def create_schema(engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        connection.commit()


def load_csv_to_table(engine, csv_path: Path, table_name: str) -> None:
    df = pd.read_csv(csv_path)

    # On vide la table si elle existe déjà (sans la supprimer), pour ne pas casser
    # les vues dbt qui en dépendent (ex. dbt_dev.stg_pib_usd dépend de raw.pib_usd)
    with engine.connect() as connection:
        connection.execute(
            text(f"TRUNCATE TABLE raw.{table_name}")
        ) if _table_exists(connection, table_name) else None
        connection.commit()

    df.to_sql(
        table_name,
        engine,
        schema="raw",
        if_exists="append",  # la table existe déjà (ou vient d'être créée juste en dessous) ; on ajoute les lignes
        index=False,
    )
    print(f"   -> {len(df)} lignes chargées dans raw.{table_name}")


def _table_exists(connection, table_name: str) -> bool:
    result = connection.execute(
        text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'raw' AND table_name = :table_name)"
        ),
        {"table_name": table_name},
    )
    return result.scalar()


def main():
    engine = get_engine()
    create_schema(engine)

    for csv_filename, table_name in FILES_TO_TABLES.items():
        csv_path = CSV_DIR / csv_filename

        if not csv_path.exists():
            print(f" Fichier introuvable : {csv_path} (lance d'abord get_togo_data.py)")
            continue

        print(f"Chargement de {csv_filename}...")
        load_csv_to_table(engine, csv_path, table_name)

    print("Chargement terminé.")


if __name__ == "__main__":
    main()
