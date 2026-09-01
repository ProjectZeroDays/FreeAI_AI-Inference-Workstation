---
name: data-pipeline
description: Data pipeline design, ETL processes, stream processing, data validation, and workflow orchestration. Use when the user asks about building data pipelines, ETL workflows, data transformation, stream processing, or Airflow/Dagster patterns.
---

# Data Pipeline

## Pipeline Architecture

```
Sources → Ingestion → Processing → Storage → Serving
  │          │            │          │         │
  │       Kafka/       Spark/      S3/DB    API/
  │       SQS          dbt       Warehouse  Dashboard
  │          │            │          │         │
  └────── Orchestration (Airflow/Dagster) ─────┘
```

## Python ETL Pattern

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PipelineResult:
    records_extracted: int
    records_transformed: int
    records_loaded: int
    errors: list[str]
    duration_seconds: float

class Pipeline:
    def __init__(self, name: str):
        self.name = name
        self.errors = []

    def run(self) -> PipelineResult:
        start = datetime.now()
        print(f"[{self.name}] Starting pipeline...")

        # Extract
        raw_data = self.extract()
        print(f"[{self.name}] Extracted {len(raw_data)} records")

        # Transform
        clean_data = self.transform(raw_data)
        print(f"[{self.name}] Transformed {len(clean_data)} records")

        # Load
        loaded = self.load(clean_data)
        print(f"[{self.name}] Loaded {loaded} records")

        duration = (datetime.now() - start).total_seconds()
        return PipelineResult(
            records_extracted=len(raw_data),
            records_transformed=len(clean_data),
            records_loaded=loaded,
            errors=self.errors,
            duration_seconds=duration,
        )

    @abstractmethod
    def extract(self) -> list[dict]: ...

    @abstractmethod
    def transform(self, data: list[dict]) -> list[dict]: ...

    @abstractmethod
    def load(self, data: list[dict]) -> int: ...
```

## Apache Airflow DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['alerts@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'daily_etl',
    default_args=default_args,
    description='Daily data pipeline',
    schedule_interval='0 2 * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['etl', 'daily'],
) as dag:

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
    )

    validate = PythonOperator(
        task_id='validate',
        python_callable=validate_data,
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
    )

    load = PythonOperator(
        task_id='load',
        python_callable=load_data,
    )

    extract >> validate >> transform >> load
```

## dbt (Data Build Tool)

```sql
-- models/staging/stg_users.sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'users') }}
),
renamed AS (
    SELECT
        id AS user_id,
        email,
        name,
        created_at,
        updated_at
    FROM source
)
SELECT * FROM renamed
```

```sql
-- models/marts/daily_active_users.sql
WITH users AS (
    SELECT * FROM {{ ref('stg_users') }}
),
events AS (
    SELECT * FROM {{ ref('stg_events') }}
),
daily AS (
    SELECT
        DATE(event_timestamp) AS date,
        COUNT(DISTINCT user_id) AS active_users
    FROM events
    GROUP BY 1
)
SELECT * FROM daily
```

## Data Validation

```python
from pydantic import BaseModel, Field, validator

class SalesRecord(BaseModel):
    order_id: str
    customer_id: str
    amount: float = Field(gt=0)
    currency: str = Field(pattern=r'^[A-Z]{3}$')
    order_date: datetime

    @validator('amount')
    def validate_amount(cls, v):
        if v > 1_000_000:
            raise ValueError(f'Amount {v} exceeds maximum')
        return round(v, 2)

def validate_batch(records: list[dict]) -> tuple[list[SalesRecord], list[dict]]:
    valid = []
    invalid = []
    for record in records:
        try:
            valid.append(SalesRecord(**record))
        except Exception as e:
            invalid.append({**record, '_error': str(e)})
    return valid, invalid
```

## Stream Processing (Kafka)

```python
from kafka import KafkaConsumer, KafkaProducer
import json

# Consumer
consumer = KafkaConsumer(
    'raw-events',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='processing-group',
    auto_offset_reset='earliest',
)

# Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
)

for message in consumer:
    event = message.value
    processed = transform_event(event)
    producer.send('processed-events', value=processed)
```

## Incremental Loading

```python
def incremental_extract(last_watermark: datetime) -> list[dict]:
    query = f"""
        SELECT * FROM source_table
        WHERE updated_at > '{last_watermark.isoformat()}'
        ORDER BY updated_at ASC
    """
    return db.execute(query)

def run_pipeline():
    watermark = get_last_watermark()
    new_records = incremental_extract(watermark)

    if not new_records:
        print("No new records")
        return

    transformed = transform(new_records)
    load(transformed)

    new_watermark = max(r['updated_at'] for r in new_records)
    save_watermark(new_watermark)
```

## Pipeline Best Practices

1. **Idempotency**: Same input = same output, safe to re-run
2. **Observability**: Log every step, track metrics
3. **Error handling**: Dead letter queues, retry logic
4. **Data quality**: Validate at each stage
5. **Monitoring**: Alert on failures, track latency
6. **Documentation**: Document schemas, transformations
7. **Testing**: Unit test transforms, integration test end-to-end
