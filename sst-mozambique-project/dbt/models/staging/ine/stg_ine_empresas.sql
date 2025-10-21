{{ config(materialized='view') }}

SELECT 
    id,
    ano,
    provincia,
    sector,
    total_empresas,
    total_trabalhadores,
    created_at
FROM {{ source('analytics', 'stg_ine_empresas') }}
WHERE ano >= 2020
