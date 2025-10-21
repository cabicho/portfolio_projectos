-- BigQuery Setup for SST Mozambique Data Pipeline

CREATE SCHEMA IF NOT EXISTS `sst_mozambique_raw`
OPTIONS (
  description = 'Raw SST data from multiple Mozambican sources',
  location = 'europe-west1'
);

CREATE SCHEMA IF NOT EXISTS `sst_mozambique_processed`
OPTIONS (
  description = 'Cleaned and processed SST data',
  location = 'europe-west1'
);

CREATE OR REPLACE TABLE `sst_mozambique_raw.ine_statistics` (
  record_id STRING,
  data_source STRING,
  indicator_name STRING,
  year INTEGER,
  quarter INTEGER,
  geographic_region STRING,
  sector STRING,
  value FLOAT64,
  unit STRING,
  collection_date DATE,
  raw_data JSON,
  metadata STRUCT<
    extraction_method STRING,
    confidence_level STRING,
    last_updated TIMESTAMP
  >
)
PARTITION BY DATE(collection_date)
CLUSTER BY geographic_region, sector, year;

CREATE OR REPLACE TABLE `sst_mozambique_raw.work_accidents` (
  accident_id STRING,
  reporting_entity STRING,
  accident_date DATE,
  accident_time TIME,
  province STRING,
  district STRING,
  economic_sector STRING,
  company_size STRING,
  accident_type STRING,
  severity STRING,
  fatal BOOLEAN,
  injured_count INTEGER,
  days_lost INTEGER,
  description STRING,
  raw_report JSON,
  data_quality_score FLOAT64,
  last_updated TIMESTAMP
)
PARTITION BY DATE(accident_date)
CLUSTER BY province, economic_sector, severity;

CREATE OR REPLACE VIEW `sst_mozambique_processed.data_quality_monitoring` AS
SELECT
  data_source,
  COUNT(*) as total_records,
  COUNTIF(accident_date IS NULL) as missing_dates,
  COUNTIF(province IS NULL) as missing_locations,
  AVG(data_quality_score) as avg_quality_score,
  MIN(accident_date) as earliest_record,
  MAX(accident_date) as latest_record
FROM `sst_mozambique_raw.work_accidents`
GROUP BY data_source;
