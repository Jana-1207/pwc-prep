## Session 6.5 — Data Pipelines: Batch vs Real-Time Processing {: #s6-5 }

### What is a data pipeline?

**A data pipeline is an automated, repeatable series of steps that moves data from where it is produced to where it is useful, transforming it along the way.** "Every night, take yesterday's orders from the app database, clean them, join them with product data, and refresh the sales dashboard" is a pipeline.

[[fig:data_pipeline | A typical pipeline: ingest → raw storage → transform → curated storage → serve, with orchestration on top and quality checks underneath.]]

| Stage | Job | Examples |
|---|---|---|
| Ingest | bring data in from sources | API pulls, database extracts, CDC streams, file drops |
| Raw storage | keep an untouched copy, so steps can be replayed | lake bronze zone, staging tables |
| Transform | clean, validate, join, aggregate, model | SQL (dbt), Spark, Python |
| Curated storage | publish trusted, well-modelled data | warehouse star schemas, gold tables |
| Serve | deliver to consumers | dashboards, ML features, APIs, exports, reverse ETL |
| Orchestrate | run steps in order, on schedule, with retries and alerts | Apache Airflow, Azure Data Factory, Dagster, Prefect, AWS Step Functions |
| Observe | check quality, freshness, volume, lineage | dbt tests, Great Expectations, Monte Carlo, built-in monitors |

### Batch pipelines

A **batch pipeline** processes a bounded chunk of data on a schedule (hourly, nightly).

- **Strengths:** simple to build, test and re-run (re-process yesterday); efficient for big volumes; cheaper.
- **Weaknesses:** data is only as fresh as the last run; large jobs can miss their window.
- **Tools:** SQL in the warehouse, Spark, Python, scheduled by Airflow or Data Factory.

A tiny orchestration example: an Airflow DAG (a *directed acyclic graph* of tasks):

```python
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def extract(): ...
def transform(): ...
def load(): ...


with DAG(
    dag_id="daily_sales_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="0 2 * * *",            # every day at 02:00
    catchup=False,
    default_args={"retries": 2},
) as dag:
    t_extract = PythonOperator(task_id="extract", python_callable=extract)
    t_transform = PythonOperator(task_id="transform", python_callable=transform)
    t_load = PythonOperator(task_id="load", python_callable=load)

    t_extract >> t_transform >> t_load
```

::: linebyline
| Part | What it means |
|---|---|
| `with DAG(dag_id="daily_sales_pipeline", …)` | defines one pipeline with a unique name |
| `schedule="0 2 * * *"` | a cron expression: minute 0, hour 2, every day |
| `catchup=False` | don't automatically run all the missed days since start_date |
| `default_args={"retries": 2}` | each task is retried twice before the run fails |
| `PythonOperator(task_id=…, python_callable=…)` | a task that runs a Python function |
| `t_extract >> t_transform >> t_load` | dependencies: transform waits for extract, load waits for transform |
:::

### Real-time (streaming) pipelines

A **streaming pipeline** processes data continuously as events arrive, with latency from milliseconds to seconds (Session 6.7).

- **Strengths:** fresh data, immediate reactions (fraud alerts, live dashboards).
- **Weaknesses:** harder to build and test; must handle late, duplicate and out-of-order events; state management; always-on cost.
- **Tools:** Kafka / Kinesis / Event Hubs for transport; Flink, Spark Structured Streaming or Kafka Streams for processing.

### Batch vs streaming

| | Batch | Streaming |
|---|---|---|
| Data | bounded (yesterday's orders) | unbounded (an endless flow of events) |
| Latency | minutes to hours | milliseconds to seconds |
| Processing | whole chunk at once | event by event, or small windows |
| Complexity | lower | higher: windows, state, late data, exactly-once |
| Re-processing | re-run the job | replay the stream from an offset |
| Cost profile | burst compute while running | continuous compute |
| Example | nightly revenue report | real-time fraud scoring |

::: extension Lambda and Kappa architectures
The **Lambda architecture** runs two paths: a batch layer (accurate, complete, slow) and a speed layer (fast, approximate), merged at query time. It is powerful but means maintaining two codebases. The **Kappa architecture** uses **one streaming path for everything**, re-processing history by replaying the event log (e.g. Kafka). Modern engines (Spark, Flink) run the same code in batch and streaming modes, which is narrowing the gap.
:::

### Pipeline best practices

| Practice | Why |
|---|---|
| **Idempotent steps** (upserts, partition overwrite) | re-running after a failure never duplicates data |
| **Incremental processing** (watermarks, CDC) | process only what changed; faster and cheaper |
| **Keep raw data** | lets you fix a bug and re-process history (backfill) |
| **Data quality checks between stages** | stop bad data before it reaches dashboards |
| **Monitoring and alerting** on failures, freshness and row counts | you hear about problems before the business does |
| **Lineage and documentation** | you know which reports break if a source changes |
| **Parameterized, version-controlled code** | reproducible, reviewable pipelines (DataOps) |

::: explain
"A data pipeline is an automated sequence that moves data from sources to destinations, typically ingest, store raw, transform, and serve, orchestrated by a tool like Airflow that handles scheduling, dependencies, retries and alerts. Batch pipelines process bounded chunks on a schedule, which is simple, cheap and easy to re-run but only as fresh as the last run. Streaming pipelines process events continuously for low latency but must deal with late and duplicate events and state. Good pipelines are idempotent, incremental, monitored and have data quality checks between stages."
:::

::: trap
- Pipelines that duplicate data when re-run (not idempotent).
- No raw copy, so a transformation bug can't be fixed by re-processing.
- Choosing streaming when the business needs daily numbers.
- No monitoring: a silent failure shows up as a stale dashboard days later.
:::

::: questions
#### Basic
Q: [DEFINITION] What is a data pipeline?
A: An automated series of steps that extracts data from sources, transforms it and loads it into destinations, on a schedule or continuously.

Q: [COMPARISON] Batch vs streaming processing?
A: Batch processes bounded data on a schedule (higher latency, simpler, cheaper); streaming processes unbounded events continuously (low latency, more complex).

Q: [DEFINITION] What does an orchestrator like Airflow do?
A: It schedules pipeline tasks, enforces their dependencies (a DAG), retries failures, tracks runs and alerts on problems.

#### Intermediate
Q: [DEFINITION] What is a DAG in Airflow?
A: A Directed Acyclic Graph: tasks connected by dependencies with no cycles, which defines execution order.

Q: [WHY] Why should pipelines be idempotent?
A: Failures and retries are normal; idempotent steps (upserts, partition overwrites) produce the same result when re-run, with no duplicates or gaps.

Q: [COMPARISON] Lambda vs Kappa architecture?
A: Lambda runs separate batch and speed layers and merges them; Kappa uses a single streaming pipeline and re-processes by replaying the log.

Q: [DEFINITION] What is a backfill?
A: Re-running a pipeline for past periods, for example after fixing a bug or adding a new column, usually from retained raw data.

#### Scenario-based
Q: [SCENARIO] The nightly pipeline sometimes finishes after 9 AM, when managers open dashboards. What would you do?
A: Profile the slow steps; switch from full to incremental loads; parallelise independent tasks; optimise SQL and partitioning; scale compute; start earlier or trigger on source readiness; add freshness alerts and show "data as of" on dashboards.

Q: [DESIGN QUESTION] Design a pipeline that loads app orders into the warehouse every hour.
A: Hourly orchestrated job: incremental extract by `updated_at` watermark (or CDC) → land raw files or staging tables → transform with SQL/dbt (clean, de-duplicate, join dimensions) → MERGE into fact and dimension tables → quality tests (row counts, nulls, totals) → refresh BI extracts → alert on failure or staleness.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is a cron job that runs a SQL script a data pipeline?
A: Technically yes, a simple one. But without dependency handling, retries, monitoring and idempotency it is fragile; orchestrators exist to add those.
:::

## Session 6.6 — ETL vs ELT {: #s6-6 }

[HIGH PRIORITY] for data roles. "ETL vs ELT" is one of the most common data-engineering questions.

### The three letters

- **E — Extract:** read data from source systems (databases, APIs, files, SaaS apps).
- **T — Transform:** clean, standardise, de-duplicate, join, aggregate and model the data.
- **L — Load:** write it into the target (a warehouse, lake or another system).

The difference between ETL and ELT is **where and when the transformation happens**.

[[fig:etl_vs_elt | ETL transforms on a separate engine before loading; ELT loads raw data first and transforms inside the warehouse.]]

### ETL: Extract → Transform → Load

Data is transformed in a separate ETL engine or server **before** it reaches the warehouse; only clean, modelled data is loaded.

- **Grew up** in the era of expensive on-premises warehouses, where compute and storage in the warehouse were scarce.
- **Tools:** Informatica PowerCenter, IBM DataStage, SSIS, Talend, Ab Initio.
- **Good when:** strict data rules must be applied before storage; sensitive data must be masked before it lands; the target has limited compute; legacy environments.

### ELT: Extract → Load → Transform

Raw data is loaded **first**, then transformed **inside the warehouse or lakehouse**, using its scalable compute, usually with SQL.

- **Grew up** with cloud warehouses (Snowflake, BigQuery, Redshift, Databricks), where storage is cheap and compute scales on demand.
- **Tools:** Fivetran, Airbyte or Stitch for the E+L; **dbt** (SQL models + tests) for the T.
- **Good when:** you want raw history available for re-processing; requirements change often; data volumes are large; analysts work in SQL.

### ETL vs ELT

| | ETL | ELT |
|---|---|---|
| Order | extract → transform → load | extract → load → transform |
| Where the transformation runs | separate ETL server or engine | inside the target warehouse / lakehouse |
| Data loaded | cleaned and modelled only | raw first, then models built on top |
| Raw history in the target | usually not | yes, so you can re-transform anytime |
| Flexibility for new questions | lower: change the ETL job and re-extract | higher: write a new SQL model over existing raw data |
| Load speed | slower (transform first) | faster to land data |
| Compute | ETL server capacity | elastic warehouse compute (pay per use) |
| Sensitive data | can be masked before landing | must be secured or masked inside the warehouse |
| Typical era and tools | on-prem: Informatica, DataStage, SSIS | cloud: Fivetran/Airbyte + Snowflake/BigQuery + dbt |

Many real platforms mix the two: light cleaning (masking PII, format fixes) during ingestion, heavy modelling inside the warehouse.

### What "Transform" looks like in practice

Here is the T of ELT done in SQL: messy raw rows (as a source system might deliver them) become clean, typed, de-duplicated rows:

```sql run
WITH raw_orders (order_ref, cust_email, order_dt, status, amount_text) AS (
    VALUES ('A-1001', ' Aarav@Mail.com ', '2024-04-01', 'delivered', '2,843.00'),
           ('A-1002', 'isha@mail.com',    '2024-04-01', 'Shipped ',  '3499'),
           ('A-1002', 'isha@mail.com',    '2024-04-01', 'Shipped ',  '3499'),
           ('A-1003', 'kabir@mail.com',   '2024-04-02', 'CANCELLED', '15999.00'),
           ('A-1004', NULL,               '2024-04-02', 'pending',   'n/a')
)
SELECT DISTINCT
       order_ref,
       LOWER(TRIM(cust_email))  AS customer_email,
       order_dt::date           AS order_date,
       UPPER(TRIM(status))      AS status,
       CASE WHEN amount_text ~ '^[0-9,]+(\.[0-9]+)?$'
            THEN REPLACE(amount_text, ',', '')::numeric
       END                      AS amount
FROM raw_orders
WHERE cust_email IS NOT NULL
ORDER BY order_ref;
```

::: linebyline
| Part | Transformation |
|---|---|
| `WITH raw_orders … VALUES …` | stands in for a raw staging table loaded as-is from the source |
| `SELECT DISTINCT` | removes the exact duplicate row for A-1002 |
| `LOWER(TRIM(cust_email))` | standardises emails: trims spaces, lower-cases |
| `order_dt::date` | text → a real DATE |
| `UPPER(TRIM(status))` | `'Shipped '` and `'delivered'` → `SHIPPED`, `DELIVERED` |
| `CASE WHEN amount_text ~ '^[0-9,]+(\.[0-9]+)?$' THEN …` | only convert values that look like numbers (`~` is a regex match); `'n/a'` would become NULL |
| `REPLACE(amount_text, ',', '')::numeric` | `'2,843.00'` → 2843.00 |
| `WHERE cust_email IS NOT NULL` | a business rule: orders without a customer are rejected (in real life, routed to a quarantine table) |
:::

In dbt, this SELECT would be saved as a model file (`stg_orders.sql`) with tests such as `unique(order_ref)` and `not_null(customer_email)`.

::: explain
"ETL and ELT both extract data from sources and load it into a target; the difference is where the transformation happens. In ETL we transform on a separate engine, like Informatica or SSIS, before loading, so only clean data enters the warehouse. That suited on-prem warehouses with limited compute, and it's useful when sensitive data must be masked before landing. In ELT we load raw data first and transform inside a cloud warehouse like Snowflake or BigQuery, typically with SQL and dbt. That's faster to ingest, keeps raw history so we can re-transform when requirements change, and uses the warehouse's elastic compute. Most modern cloud stacks are ELT, often with some light cleaning on the way in."
:::

::: trap
- "ELT means no transformation." It means transformation happens *after* loading.
- "ETL is obsolete." It is still right for strict pre-load rules, sensitive data and legacy platforms.
- Loading raw data with PII into the warehouse without access controls or masking (an ELT risk).
- Forgetting the T must be tested and documented in both approaches.
:::

::: questions
#### Basic
Q: [DEFINITION] What is ETL?
A: Extract, Transform, Load: extracting data from sources, transforming it on a separate engine, then loading the cleaned data into the target.

Q: [COMPARISON] ETL vs ELT?
A: ETL transforms before loading, on a separate engine; ELT loads raw data first and transforms inside the target warehouse using its compute, typically with SQL.

#### Intermediate
Q: [WHY] Why has ELT become popular?
A: Cloud warehouses provide cheap storage and elastic, powerful compute, so it's faster and more flexible to land raw data and transform it in place with SQL/dbt, keeping raw history for re-processing.

Q: [HOW] When would you still choose ETL?
A: When data must be cleaned, validated or masked before it is stored (compliance, PII), when the target can't handle heavy transformations, or in established legacy environments.

Q: [DEFINITION] What is dbt?
A: A tool that lets you write transformations as version-controlled SQL SELECT models, with dependencies, tests and documentation, executed inside the warehouse: the T in ELT.

#### Scenario-based
Q: [SCENARIO] A bank must not store raw card numbers in its analytics warehouse. ETL or ELT?
A: Mask or tokenize the card numbers before loading (ETL-style for that step). The rest of the modelling can still be ELT inside the warehouse.

Q: [SCENARIO] Analysts keep asking for new metrics that need fields you didn't load. Which approach helps and why?
A: ELT. Load complete raw data into the warehouse, then new metrics are just new SQL models over data that is already there, with no re-engineering of extraction.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is ETL vs ELT about the tools you use?
A: No, it's about *where and when* the transformation happens. The same tool can support both styles.
:::

## Session 6.7 — Streaming {: #s6-7 }

### What is streaming?

**Streaming is processing data continuously while it is in motion**, event by event, instead of waiting to collect a batch. A stream is **unbounded**: card swipes, clicks, GPS pings and sensor readings never "finish".

### Apache Kafka in plain words

Kafka is the most widely used event-streaming platform; most interview questions use its vocabulary.

[[fig:kafka_partitions | A Kafka topic with three partitions; each consumer in a group reads its own partitions and tracks its offset.]]

| Term | Meaning |
|---|---|
| **Event / record** | one message: key, value (e.g. JSON), timestamp |
| **Topic** | a named stream of events, e.g. `orders` |
| **Partition** | a topic is split into ordered, append-only logs spread across brokers for parallelism; order is guaranteed **within** a partition |
| **Offset** | the position of a record in a partition (0, 1, 2…); consumers remember the last offset they processed |
| **Producer** | writes events; the **key** (e.g. customer_id) decides the partition, so one customer's events stay in order |
| **Consumer group** | a set of consumers sharing the work: each partition is read by one consumer in the group; different groups each get **all** events (pub/sub) |
| **Broker / cluster** | the Kafka servers; partitions are **replicated** across brokers for fault tolerance |
| **Retention** | events are kept for a configured time (e.g. 7 days) or forever (compacted), so consumers can **replay** |

### Stream processing concepts

- **Stateless operations:** filter, map or transform each event independently ("drop test events", "convert currency").
- **Stateful operations:** need memory across events: counts, sums, joins, deduplication, sessionization.
- **Windows** group an endless stream into finite chunks for aggregation:

| Window type | Meaning | Example |
|---|---|---|
| **Tumbling** | fixed-size, non-overlapping | orders per minute: 10:00–10:01, 10:01–10:02 … |
| **Hopping / sliding** | fixed-size, overlapping | 5-minute totals updated every minute |
| **Session** | bursts of activity separated by inactivity gaps | a user's browsing session ends after 30 minutes idle |

The window idea is easy to see with SQL on stored data. PostgreSQL's `date_bin` puts each login into a fixed 12-hour **tumbling window**:

```sql run
SELECT date_bin('12 hours', login_time, TIMESTAMP '2024-04-01 00:00') AS window_start,
       COUNT(*)                AS logins,
       COUNT(DISTINCT user_id) AS active_users
FROM user_logins
GROUP BY 1
ORDER BY 1;
```

A stream processor computes the same result **continuously**, emitting each window's counts as soon as the window closes, instead of querying stored rows afterwards.

- **Event time vs processing time:** *event time* is when the event happened (the card was swiped at 10:00:05); *processing time* is when the system saw it (10:00:09). Results should use event time.
- **Late data and watermarks:** events can arrive late (a phone was offline). A **watermark** says "we believe all events up to time T have arrived", so a window can close; later events are handled by a lateness policy.
- **Delivery semantics:** at-least-once is common; **exactly-once** processing is possible in Kafka, Flink and Spark using transactions and checkpoints, within their boundaries.

### Where streaming is used

| Use case | Why streaming |
|---|---|
| Card fraud detection | decide within milliseconds, before approving |
| Live order or delivery tracking | users expect second-by-second updates |
| Real-time dashboards (sales during a sale) | business reacts immediately |
| IoT and sensor monitoring | detect anomalies and failures quickly |
| CDC to search indexes and caches | keep read models fresh |
| Log and security analytics | detect attacks as they happen |
| Recommendations ("because you just viewed…") | personalize within the session |

**Tools:** transport with Apache Kafka (or Confluent), Amazon Kinesis, Azure Event Hubs, Google Pub/Sub; processing with Apache Flink, Spark Structured Streaming, Kafka Streams, ksqlDB, and cloud services such as Azure Stream Analytics.

::: explain
"Streaming means processing data continuously as events arrive, instead of in scheduled batches. In Kafka, events are written to topics that are split into partitions; order is guaranteed within a partition, so we key events by something like customer_id. Consumers in a consumer group share partitions, and they track offsets, so events can be replayed. Stream processors like Flink or Spark Structured Streaming do stateful work over windows, for example orders per minute, using event time and watermarks to handle late data. It's the right choice for fraud detection or live tracking, but it's more complex than batch, so I'd only use it when low latency really matters."
:::

::: trap
- Expecting global ordering across a topic: order exists only within a partition.
- More consumers than partitions in a group: the extra consumers sit idle.
- Ignoring late and out-of-order events (processing time instead of event time).
- Using streaming where hourly batch would do.
- Treating Kafka as a database for ad-hoc queries.
:::

::: questions
#### Basic
Q: [DEFINITION] What is stream processing?
A: Continuously processing unbounded data as events arrive, typically with low latency, instead of processing stored batches.

Q: [DEFINITION] What are a Kafka topic, partition and offset?
A: A topic is a named event stream; a partition is an ordered, append-only log that splits a topic for parallelism; an offset is a record's position in a partition, which consumers use to track progress.

#### Intermediate
Q: [DEFINITION] What is a consumer group?
A: A set of consumers that share a topic's partitions, each partition read by exactly one member. Different groups each receive all events independently.

Q: [COMPARISON] Tumbling vs sliding windows?
A: Tumbling windows are fixed and non-overlapping (per minute); sliding or hopping windows overlap (the last 5 minutes, updated every minute).

Q: [COMPARISON] Event time vs processing time?
A: Event time is when the event actually happened; processing time is when the system processes it. Correct analytics use event time, which requires handling late events (watermarks).

Q: [HOW] How does Kafka guarantee ordering for a customer's events?
A: By using customer_id as the message key, so all of that customer's events go to the same partition, where order is preserved.

#### Scenario-based
Q: [DESIGN QUESTION] Design a real-time fraud alert for card transactions.
A: Card swipes are published to a Kafka topic keyed by card_id; a Flink job keeps per-card state (recent locations, amounts, velocity), scores each event against rules or a model within milliseconds, and publishes alerts to an `alerts` topic consumed by the blocking and notification services. All events also flow to the lake for model training.

Q: [SCENARIO] Your consumers can't keep up during peak hours and lag grows. What can you do?
A: Add consumers, up to the number of partitions (and add partitions if needed); optimise processing; batch writes to sinks; check for slow downstream systems; monitor consumer lag and autoscale.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does Kafka delete a message once it's consumed?
A: No. Messages stay until retention expires; consumers just move their offsets, which is why replay is possible.
:::

## Session 6.8 — Salesforce and Cloud Data Warehouse Integration {: #s6-8 }

[LOWER PRIORITY] for general software roles, but common in consulting and data roles. This session explains the **architecture** of loading CRM data into a cloud warehouse; it is not a Salesforce manual.

### The business need

**Salesforce** is a cloud CRM (Customer Relationship Management) system. It holds **Accounts** (companies), **Contacts** (people), **Leads**, **Opportunities** (potential deals with stage, amount and close date) and **Cases** (support tickets).

Sales teams live in Salesforce, but the questions management asks need data from **several** systems:

- "What is our win rate by region and quarter?" (CRM)
- "Which customers bring the most revenue after the deal?" (CRM + billing/ERP)
- "How long from first contact to first payment?" (CRM + finance)
- "Customer 360: deals, orders, support cases and marketing activity in one view."

Those questions are answered in a **cloud data warehouse** (Snowflake, BigQuery, Redshift, Databricks), where CRM data is joined with everything else.

### The reference architecture

[[fig:salesforce_warehouse | Salesforce data flows into the warehouse through APIs, change events or an ELT tool; warehouse insights can flow back via reverse ETL.]]

**Ways to get data out of Salesforce (concepts):**

| Option | How it works | When to use |
|---|---|---|
| **REST API** (SOQL queries) | query records, e.g. `SELECT Id, StageName, Amount FROM Opportunity WHERE SystemModstamp > :last_run` | small to medium volumes, incremental pulls |
| **Bulk API** | submit large asynchronous query jobs; download results in batches | millions of records, initial loads |
| **Change Data Capture / Platform Events** | Salesforce publishes record changes as events | near-real-time sync |
| **Managed ELT connectors** | Fivetran, Airbyte, Informatica, MuleSoft, Azure Data Factory handle auth, incremental logic, schema changes and API limits | the most common choice: fast to set up |
| **Zero-copy / data sharing** | newer platforms let warehouse and CRM share data without copying (e.g. Salesforce Data Cloud integrations with Snowflake, BigQuery or Databricks) | when supported by both platforms |

### Design points interviewers look for

| Concern | What to do |
|---|---|
| **Incremental extraction** | use a watermark such as `SystemModstamp` / `LastModifiedDate`; never re-pull everything daily |
| **Deletes** | capture deleted records (`IsDeleted` via queryAll, or CDC events), otherwise the warehouse keeps "ghost" deals |
| **API limits** | Salesforce enforces API call quotas, so prefer the Bulk API for large volumes and schedule loads sensibly |
| **Schema changes** | admins add custom fields (`Region__c`) at any time; the pipeline must detect and handle new or changed columns |
| **Data types and time zones** | timestamps come in UTC; picklists are text codes; currencies may differ by record |
| **Relationships** | Opportunity → Account → Owner (User); keep IDs to join in the warehouse |
| **Security and PII** | an OAuth connected app with a least-privilege integration user; mask or restrict personal data |
| **Data quality** | duplicate accounts, inconsistent stage names, missing close dates: add tests |

### In the warehouse: staging → models → BI

1. **Staging (raw):** `sf_account`, `sf_opportunity`, loaded as-is (ELT).
2. **Transform (SQL / dbt):** clean, de-duplicate, filter deleted rows, standardise stages and currencies, join to other sources.
3. **Analytics models:** `dim_account`, `dim_owner`, `fact_opportunity` (one row per opportunity, with amount, stage and dates).
4. **BI:** pipeline dashboards, win rates, forecast accuracy.

A small example of the "transform" step, computing win rate and open pipeline per sales owner from staged opportunities (fictional data):

```sql run
WITH sf_opportunity (opp_id, account_name, owner, stage, amount, close_date, is_deleted) AS (
    VALUES ('0061', 'Acme Retail',    'Asha', 'Closed Won',  1200000, DATE '2024-03-28', false),
           ('0062', 'Bharat Infra',   'Asha', 'Closed Lost',  800000, DATE '2024-03-30', false),
           ('0063', 'Delta Logistics','Asha', 'Proposal',     500000, DATE '2024-06-10', false),
           ('0064', 'Metro Foods',    'Ravi', 'Closed Won',   450000, DATE '2024-04-05', false),
           ('0065', 'Orbit Telecom',  'Ravi', 'Closed Won',   600000, DATE '2024-04-18', false),
           ('0066', 'Lotus Textiles', 'Ravi', 'Closed Lost',  300000, DATE '2024-04-22', false),
           ('0067', 'Sunrise Health', 'Ravi', 'Negotiation', 2000000, DATE '2024-05-15', false),
           ('0068', 'Old Deal Co',    'Ravi', 'Closed Won',   300000, DATE '2024-02-10', true)
)
SELECT owner,
       COUNT(*) FILTER (WHERE stage = 'Closed Won')    AS won,
       COUNT(*) FILTER (WHERE stage LIKE 'Closed%')    AS closed,
       ROUND(100.0 * COUNT(*) FILTER (WHERE stage = 'Closed Won')
             / NULLIF(COUNT(*) FILTER (WHERE stage LIKE 'Closed%'), 0), 1) AS win_rate_pct,
       SUM(amount) FILTER (WHERE stage NOT LIKE 'Closed%') AS open_pipeline
FROM sf_opportunity
WHERE NOT is_deleted
GROUP BY owner
ORDER BY owner;
```

The deleted opportunity (0068) is excluded; forgetting deletes would inflate Ravi's numbers. Win rate = won ÷ closed, so open deals don't count against anyone.

### Reverse ETL: closing the loop

Insights computed in the warehouse (lead scores, churn risk, lifetime value, "next best product") are only useful if sales reps see them **inside Salesforce**. **Reverse ETL** tools (Hightouch, Census) or integration platforms push selected warehouse data **back** into CRM fields, so the warehouse becomes a source for operational systems too.

::: explain
"To integrate Salesforce with a cloud warehouse, I'd first agree the business questions, like win rate and customer 360. Then I'd extract incrementally, usually through a managed ELT connector or the Bulk API for large volumes, using SystemModstamp as a watermark, capturing deletes, and respecting API limits; for near-real-time needs, Change Data Capture events. Raw objects land in staging tables, then dbt/SQL models clean them, filter deleted records, standardise stages and join them with billing and product data into facts and dimensions for BI. Finally, reverse ETL can push scores like churn risk back into Salesforce for the sales team."
:::

::: trap
- Full extracts every day: slow, and they hit API limits.
- Ignoring deleted records (ghost opportunities) and custom-field schema changes.
- Mixing up time zones and currencies.
- Treating it as a Salesforce-specific trick: the same pattern applies to any SaaS source (HubSpot, Workday, Zendesk).
:::

::: questions
#### Basic
Q: [DEFINITION] What is Salesforce, in data terms?
A: A SaaS CRM whose objects (Accounts, Contacts, Leads, Opportunities, Cases) hold customer and sales data, accessible through APIs.

Q: [DEFINITION] What is reverse ETL?
A: Moving modelled data from the warehouse back into operational tools (CRM, marketing platforms) so business users can act on it.

#### Intermediate
Q: [HOW] How would you extract Salesforce data incrementally?
A: Query records modified since the last successful run using SystemModstamp or LastModifiedDate as a watermark (REST or Bulk API), include deleted records, or subscribe to Change Data Capture events.

Q: [COMPARISON] REST API vs Bulk API for Salesforce extraction?
A: The REST API suits smaller, frequent synchronous queries; the Bulk API runs large asynchronous jobs efficiently for millions of records and uses fewer API calls.

#### Scenario-based
Q: [DESIGN QUESTION] Finance wants yesterday's closed Salesforce deals combined with invoices from SAP in a 7 AM dashboard. Design it.
A: A nightly orchestrated ELT: extract changed opportunities and accounts (incremental, plus deletes) and SAP invoices into warehouse staging by 5 AM; dbt models join deals to invoices by account mapping; quality tests (totals, missing keys); publish `fact_deal_revenue`; refresh BI by 6:30 with freshness alerts.

Q: [SCENARIO] Dashboard revenue doesn't match Salesforce reports. What do you check?
A: Deleted or merged records, filters (stage definitions, record types), currency conversion, time zones on close dates, incremental-load gaps (watermarks), and duplicates in staging.

#### Follow-up / Trap
Q: [TRAP QUESTION] Why not let the BI tool query Salesforce directly?
A: You can for simple reports, but you hit API limits, can't easily join with other systems, have no history or snapshots, and get slow dashboards. A warehouse integrates and preserves the data.
:::

## Session 6.9 — Choosing the Right Integration Pattern {: #s6-9 }

[INTERVIEW EXTENSION] Interviewers rarely ask "define a queue"; they describe a situation and ask what you would do. This decision guide pulls the module together.

| If the requirement is… | Choose | Why |
|---|---|---|
| The user needs the answer immediately (price, payment approval, stock check) | **Synchronous API** | request/response, immediate result |
| Long-running or background work (emails, PDFs, image processing) | **Message queue** (+ 202 Accepted) | decouples, buffers, retries |
| Many systems must react to the same business event | **Publish/subscribe / event-driven** | fan-out without coupling |
| Keep another database, cache or search index in sync with low latency | **CDC** | captures every change from the log |
| Load data for reporting daily or hourly | **Batch ETL/ELT pipeline** | simple, cheap, reliable |
| React to data within seconds (fraud, live dashboards) | **Streaming** (Kafka + a stream processor) | continuous, low latency |
| Exchange data with a legacy partner system | **File transfer (SFTP)** or **API gateway** | lowest common denominator, controlled exposure |
| Connect SaaS apps quickly (Salesforce, Workday, SAP) | **iPaaS / managed connectors** | prebuilt connectors, monitoring |
| Expose capabilities to many internal teams or partners | **API-led layers + API gateway** | reuse, security, versioning |

### Anti-patterns to name in interviews

- **Shared database between teams:** hidden coupling; schema changes break other systems.
- **Distributed monolith:** microservices that must all be deployed together and call each other synchronously in long chains.
- **Chatty integrations:** dozens of fine-grained calls per screen (use aggregation or a backend-for-frontend).
- **No error path:** no retries, DLQs, alerts or reconciliation.
- **Real-time by default:** paying for streaming where daily batch suffices.

::: explain How I decide in an interview
"I start with three questions: How fresh does the data need to be? Does the caller need an immediate answer? And how many systems care about this data? If the caller needs an answer now, a synchronous API. If it's background work, a queue. If many systems react, publish an event. For analytics, batch ELT unless the business acts within minutes, in which case CDC or streaming. Then I check volume, failure handling, security and who owns each piece."
:::

::: questions
#### Scenario-based
Q: [DESIGN QUESTION] An e-commerce company wants (a) instant stock checks on product pages, (b) order data in the warehouse every hour, and (c) the CRM updated when a customer changes their address. Pick patterns.
A: (a) A synchronous API backed by a cache; (b) a batch or micro-batch ELT pipeline (or CDC into the warehouse); (c) a `CustomerAddressChanged` event consumed by a CRM integration (or iPaaS), processed idempotently.

Q: [SCENARIO] A logistics partner can only send a daily CSV. How do you integrate?
A: An SFTP or cloud-storage file drop with automated pickup, validation, a staging load, upserts into target tables, quality checks, archiving and alerting on missing or late files.

Q: [SCENARIO] You need real-time processing of 50,000 events per second from delivery bikes. What architecture would you consider?
A: Kafka (or Kinesis / Event Hubs) partitioned by bike_id, a stream processor (Flink or Spark Streaming) for windows and alerts, results to a low-latency store (Redis or a time-series DB) for live maps, and raw events to the lake for analytics.

#### Follow-up / Trap
Q: [TRAP QUESTION] Should every integration be event-driven to be "modern"?
A: No. Events add brokers, eventual consistency and debugging effort. Use them where decoupling and fan-out pay off; a simple API or a nightly batch is often the better engineering choice.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Put the letters in order for ETL and for ELT, and say where the T happens in each.

**P2.** What is a Kafka consumer group?

**P3.** Name three window types used in stream processing.

#### Level 2 — Interview application
**P4.** Explain to a client why their nightly full reload of a 500 GB table should become incremental, and how.

**P5.** Write a SQL query on `user_logins` that counts logins per device per day.

#### Level 3 — Scenario / problem solving
**P6.** A retailer wants (a) a daily sales report, (b) instant "low stock" alerts, (c) marketing emails when customers abandon carts. Design the data flows, naming the pattern for each.

**P7.** You are asked to integrate Salesforce with Snowflake. List six risks and how you would mitigate each.
:::

::: answers
**P1.** ETL: Extract → Transform → Load; the T happens on a separate engine before loading. ELT: Extract → Load → Transform; the T happens inside the target warehouse after loading.

**P2.** A set of consumers that share the partitions of a topic; each partition is read by one member, so the group processes the topic in parallel. Another group gets its own copy of all events.

**P3.** Tumbling, hopping/sliding, and session windows.

**P4.** "Each night we copy all 500 GB even though maybe 1% changed. That costs hours of compute and risks missing the morning deadline. An incremental load copies only new and changed rows, identified by an updated_at watermark or by change data capture, and merges them with upserts. It's faster, cheaper and safe to re-run."

**P5.**

```sql run
SELECT login_time::date AS day,
       device,
       COUNT(*) AS logins
FROM user_logins
GROUP BY 1, 2
ORDER BY 1, 2;
```

**P6.** (a) Batch ELT: a nightly (or hourly) pipeline loads POS and e-commerce sales into the warehouse and refreshes the report. (b) Streaming or event-driven: stock changes are published as events (or CDC from the inventory DB), and a stream job compares levels with thresholds and publishes `LowStock` alerts to store managers in seconds. (c) Event-driven with a delay: `CartUpdated` events feed a session-window or scheduled check; if there is no `OrderPlaced` within, say, 2 hours, a `CartAbandoned` event triggers the marketing platform, respecting consent rules.

**P7.** (1) API limits → Bulk API and incremental loads, schedule off-peak. (2) Missed deletes → queryAll / IsDeleted or CDC. (3) Schema changes from custom fields → a connector with schema evolution plus alerts. (4) Time zone and currency mismatches → standardise to UTC and a reporting currency in the models. (5) PII exposure → a least-privilege integration user, masking and role-based access in Snowflake. (6) Data-quality drift (duplicate accounts, inconsistent stages) → dbt tests, a mapping table, and reconciliation reports against Salesforce totals.
:::

## Session 6.10 — Module 6 Summary & Rapid Revision {: #s6-10 }

::: summary Module 6 Summary
#### Most important concepts
- **Enterprise integration** connects ERP, CRM, HR, billing and apps; four styles: file, shared DB, API, messaging; topologies: point-to-point → hub/ESB/iPaaS → API-led → event-driven.
- **Sync vs async:** APIs (immediate, temporally coupled) vs queues (decoupled, buffered, eventual).
- **Messaging:** queue = one consumer per message (work); topic = every subscriber gets a copy (events); at-least-once → idempotent consumers; DLQs.
- **EDA:** events (past-tense facts) through a broker; loose coupling; challenges: eventual consistency, tracing, duplicates; sagas, outbox.
- **Pipelines:** ingest → raw → transform → curated → serve; orchestration (Airflow); batch vs streaming; idempotent and incremental.
- **ETL vs ELT:** transform before loading (separate engine) vs after loading (in the warehouse, SQL/dbt).
- **Streaming:** Kafka topics, partitions, offsets, consumer groups; windows; event time and watermarks.
- **Salesforce → warehouse:** connectors or Bulk API, incremental by SystemModstamp, deletes, API limits, staging → models → BI, reverse ETL.

#### What to memorize
- Queue vs topic · ETL vs ELT table · tumbling, sliding and session windows · at-most/at-least/exactly-once.

#### What to understand
- How to pick a pattern from freshness, immediacy and fan-out.
- Why duplicates happen and how idempotency handles them.
- Why ELT fits cloud warehouses.

#### Most common interview questions
- ETL vs ELT? · Batch vs streaming? · API vs message queue? · Point-to-point vs pub/sub? · What is event-driven architecture? · What is a Kafka partition / consumer group? · How would you load Salesforce into Snowflake?

#### Common mistakes
- "Async is always better" · assuming exactly-once delivery · global ordering in Kafka · no DLQ · full reloads forever · ignoring deletes in CDC or SaaS loads.
:::

::: checklist
- [ ] I can explain enterprise integration with an order-to-cash example
- [ ] I can name the four integration styles and their trade-offs
- [ ] I can explain why point-to-point doesn't scale, and the alternatives
- [ ] I can compare an API call with a message queue
- [ ] I can compare point-to-point (queue) with publish/subscribe (topic)
- [ ] I can explain delivery guarantees and idempotent consumers
- [ ] I can explain event-driven architecture, its benefits and challenges
- [ ] I can explain sagas and the outbox pattern at a high level
- [ ] I can draw a data pipeline with orchestration
- [ ] I can compare batch and streaming
- [ ] I can compare ETL and ELT and say when to use each
- [ ] I can explain Kafka topics, partitions, offsets and consumer groups
- [ ] I can explain windows, event time and watermarks
- [ ] I can describe a Salesforce-to-warehouse integration
- [ ] I can pick an integration pattern for a given scenario
:::
