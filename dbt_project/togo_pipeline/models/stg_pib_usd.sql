-- Modèle de staging : nettoyage des données brutes de PIB
-- Source : raw.pib_usd (chargée par load_to_postgres.py)

select
    pays,
    code_pays,
    cast(annee as integer) as annee,
    pib_usd
from {{ source('raw', 'pib_usd') }}
where pib_usd is not null  -- on élimine les années sans donnée
