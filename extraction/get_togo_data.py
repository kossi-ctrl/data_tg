"""
Extrait des indicateurs de développement pour le Togo depuis l'API de la Banque mondiale,
et les sauvegarde en CSV.

API Banque mondiale (gratuite, sans clé) :
    https://api.worldbank.org/v2/country/{code_pays}/indicator/{code_indicateur}

Indicateurs utilisés :
    NY.GDP.MKTP.CD     -> PIB (US$ courants)
    SP.POP.TOTL        -> Population totale
    EG.ELC.ACCS.ZS     -> Accès à l'électricité (% de la population)

Usage :
    python3 fetch_worldbank_data.py
"""

import csv
from pathlib import Path

import requests

COUNTRY_CODE = "TGO"  # Togo

INDICATORS = {
    "NY.GDP.MKTP.CD": "pib_usd",
    "SP.POP.TOTL": "population_totale",
    "EG.ELC.ACCS.ZS": "acces_electricite_pct",
}

OUTPUT_DIR = Path("../extraction_output")  # ajuste selon où tu veux stocker les CSV bruts


def fetch_indicator(indicator_code: str) -> list[dict]:
    """Récupère toutes les années disponibles pour un indicateur donné."""
    url = f"https://api.worldbank.org/v2/country/{COUNTRY_CODE}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": 1000}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    # La réponse de l'API Banque mondiale est une liste : [métadonnées_pagination, données]
    if len(data) < 2 or data[1] is None:
        print(f"  Aucune donnée trouvée pour {indicator_code}")
        return []

    return data[1]


def save_to_csv(records: list[dict], column_name: str, output_path: Path) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pays", "code_pays", "annee", column_name])

        for record in records:
            writer.writerow(
                [
                    record.get("country", {}).get("value"),
                    record.get("countryiso3code"),
                    record.get("date"),
                    record.get("value"),
                ]
            )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for indicator_code, column_name in INDICATORS.items():
        print(f"Extraction de {indicator_code} ({column_name})...")
        records = fetch_indicator(indicator_code)

        output_path = OUTPUT_DIR / f"{column_name}.csv"
        save_to_csv(records, column_name, output_path)

        print(f"   -> {len(records)} lignes écrites dans {output_path}")

    print("✅ Extraction terminée.")


if __name__ == "__main__":
    main()
