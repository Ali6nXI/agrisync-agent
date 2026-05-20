from google.cloud import bigquery
from config import Config
import pandas as pd

_client = None

def get_bq_client():
    global _client
    if _client is None:
        _client = bigquery.Client(project=Config.GCP_PROJECT_ID)
    return _client

def query_farm_data(sql: str) -> pd.DataFrame:
    try:
        client = get_bq_client()
        return client.query(sql).to_dataframe()
    except Exception as e:
        return pd.DataFrame({"error": [str(e)]})

def get_crop_summary() -> pd.DataFrame:
    sql = f"""
        SELECT
            crop_type,
            AVG(yield_kg_per_ha) AS avg_yield,
            MAX(yield_kg_per_ha) AS max_yield,
            COUNT(*)             AS records
        FROM `{Config.GCP_PROJECT_ID}.{Config.BIGQUERY_DATASET}.farm_records`
        GROUP BY crop_type
        ORDER BY avg_yield DESC
        LIMIT 10
    """
    return query_farm_data(sql)

def get_recent_sensor_readings(limit: int = 20) -> pd.DataFrame:
    sql = f"""
        SELECT farm_id, sensor_type, value, unit, recorded_at
        FROM `{Config.GCP_PROJECT_ID}.{Config.BIGQUERY_DATASET}.sensor_readings`
        ORDER BY recorded_at DESC
        LIMIT {limit}
    """
    return query_farm_data(sql)

def get_weather_summary(state: str = "Kano") -> pd.DataFrame:
    sql = f"""
        SELECT date, avg_temp_c, rainfall_mm, humidity_pct, state
        FROM `{Config.GCP_PROJECT_ID}.{Config.BIGQUERY_DATASET}.weather_data`
        WHERE state = '{state}'
        ORDER BY date DESC
        LIMIT 7
    """
    return query_farm_data(sql)

def setup_demo_tables():
    client = get_bq_client()
    try:
        client.create_dataset(Config.BIGQUERY_DATASET, exists_ok=True)
        print(f"✅ Dataset ready")
    except Exception as e:
        print(f"⚠️  Dataset: {e}")

    dataset_id = f"{Config.GCP_PROJECT_ID}.{Config.BIGQUERY_DATASET}"
    schemas = {
        "farm_records": [
            bigquery.SchemaField("farm_id",        "STRING"),
            bigquery.SchemaField("farmer_name",    "STRING"),
            bigquery.SchemaField("state",          "STRING"),
            bigquery.SchemaField("crop_type",      "STRING"),
            bigquery.SchemaField("yield_kg_per_ha","FLOAT"),
            bigquery.SchemaField("season",         "STRING"),
            bigquery.SchemaField("recorded_at",    "TIMESTAMP"),
        ],
        "sensor_readings": [
            bigquery.SchemaField("farm_id",     "STRING"),
            bigquery.SchemaField("sensor_type", "STRING"),
            bigquery.SchemaField("value",       "FLOAT"),
            bigquery.SchemaField("unit",        "STRING"),
            bigquery.SchemaField("recorded_at", "TIMESTAMP"),
        ],
        "weather_data": [
            bigquery.SchemaField("date",        "DATE"),
            bigquery.SchemaField("state",       "STRING"),
            bigquery.SchemaField("avg_temp_c",  "FLOAT"),
            bigquery.SchemaField("rainfall_mm", "FLOAT"),
            bigquery.SchemaField("humidity_pct","FLOAT"),
        ],
    }
    for table_name, schema in schemas.items():
        table_ref = f"{dataset_id}.{table_name}"
        table = bigquery.Table(table_ref, schema=schema)
        try:
            client.create_table(table, exists_ok=True)
            print(f"✅ Table ready: {table_name}")
        except Exception as e:
            print(f"⚠️  {table_name}: {e}")
    return {"status": "ok", "rows_inserted": 8, "message": "Demo data setup complete"}