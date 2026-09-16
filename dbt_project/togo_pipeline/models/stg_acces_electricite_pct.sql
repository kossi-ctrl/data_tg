-- Modèle de staging : nettoyage des données brutes d'accès à l'électricité
-- Source : raw.acces_electricite_pct (chargée par load_to_postgres.py)

select
    pays,
    code_pays,
    cast(annee as integer) as annee,
    acces_electricite_pct
from {{ source('raw', 'acces_electricite_pct') }}
where acces_electricite_pct is not null
