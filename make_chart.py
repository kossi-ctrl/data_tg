"""
Génère un graphique de l'évolution du PIB par habitant du Togo,
à partir du CSV exporté du mart togo_indicateurs.

Usage :
    python3 make_chart.py
"""

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("togo_indicateurs_sample.csv")
df = df.dropna(subset=["pib_par_habitant"]).sort_values("annee")

plt.figure(figsize=(10, 5))
plt.plot(df["annee"], df["pib_par_habitant"], marker="o", color="#2E86AB")
plt.title("Togo — PIB par habitant (USD courants)")
plt.xlabel("Année")
plt.ylabel("PIB par habitant (USD)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("togo_pib_par_habitant.png", dpi=150)
print(" Graphique sauvegardé : togo_pib_par_habitant.png")
