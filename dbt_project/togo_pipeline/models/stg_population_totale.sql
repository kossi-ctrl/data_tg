-- Modèle de staging : nettoyage des données brutes de population
-- Source : raw.population_totale (chargée par load_to_postgres.py)

select
    pays,
    code_pays,
    cast(annee as integer) as annee,
    population_totale
from {{ source('raw', 'population_totale') }}
where population_totale is not null
