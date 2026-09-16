-- Modèle mart : combine les 3 indicateurs (PIB, population, accès électricité)
-- par année, pour faciliter l'analyse.
--
-- Dépend des 3 modèles de staging (déjà nettoyés et testés).

with pib as (
    select annee, pib_usd
    from {{ ref('stg_pib_usd') }}
),

population as (
    select annee, population_totale
    from {{ ref('stg_population_totale') }}
),

electricite as (
    select annee, acces_electricite_pct
    from {{ ref('stg_acces_electricite_pct') }}
)

select
    coalesce(pib.annee, population.annee, electricite.annee) as annee,
    pib.pib_usd,
    population.population_totale,
    electricite.acces_electricite_pct,
    -- Indicateur dérivé : PIB par habitant
    round(cast(pib.pib_usd / nullif(population.population_totale, 0) as numeric), 2) as pib_par_habitant
from pib
full outer join population on pib.annee = population.annee
full outer join electricite on coalesce(pib.annee, population.annee) = electricite.annee
order by annee desc
