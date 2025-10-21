# Arquitetura: Pipeline de Dados SST Moçambique

## Visão Geral
Sistema de coleta, processamento e análise de dados de Segurança e Saúde no Trabalho em Moçambique.

## Fontes de Dados

### Fontes Nacionais
- **INE Moçambique**: Estatísticas oficiais
- **MITESS**: Ministério do Trabalho
- **MISAU**: Ministério da Saúde

### Fontes Internacionais
- **ILO**: Organização Internacional do Trabalho
- **WHO**: Organização Mundial da Saúde

## Arquitetura Cloud

### BigQuery (Camada Raw)
- Armazenamento dados brutos
- Schema flexível
- Processamento inicial

### Redshift (Camada Processed)
- Modelo dimensional
- Otimizado para analytics
- Dashboards e relatórios

## Modelo de Dados

### Tabelas Fato
- fact_work_accidents (Acidentes de trabalho)
- fact_health_incidents (Incidentes saúde)

### Tabelas Dimensão
- dim_date (Datas)
- dim_location (Localizações)
- dim_company (Empresas)
- dim_accident_type (Tipos de acidente)

## KPIs Principais
- Taxa de acidentes por setor
- Dias perdidos por acidentes
- Severidade dos acidentes
- Cumprimento legislação SST
