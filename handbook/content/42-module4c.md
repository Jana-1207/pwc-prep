## Session 4.7 — Data Storage Systems: Database, Warehouse, Lake, Lakehouse {: #s4-7 }

[MEDIUM PRIORITY] "Data warehouse vs data lake" is a favourite comparison question for data roles, and "lakehouse" is now common in consulting conversations.

### First, three kinds of data

[[fig:data_shapes | Structured, semi-structured and unstructured data.]]

| Kind | Meaning | Examples | Typical storage |
|---|---|---|---|
| **Structured** | fits a fixed table: known columns and types | orders, salaries, bank transactions | relational databases, warehouses |
| **Semi-structured** | has structure, but flexible and self-describing (keys and tags travel with the data) | JSON from APIs, XML, logs, CSV with varying columns | document databases, JSONB columns, data lakes |
| **Unstructured** | no predefined data model | images, PDFs, emails, audio, video, chat text | object storage, data lakes (often with metadata in a database) |

Most enterprise data by volume is semi-structured or unstructured; most *business reporting* still runs on structured data. Modern platforms need to handle all three.

### 1. The operational database

The **database** that runs an application (OLTP, Module 1): PostgreSQL, MySQL, MongoDB. It is optimised for many small, fast, correct transactions on **current** data. It is the source of truth for the business process, but not the place for heavy analytics.

### 2. The data warehouse

A **data warehouse** (Session 2.7) is a central, integrated store of **cleaned, structured, historical** data, modelled for analysis (star schemas) and queried with SQL by BI tools.

- **Schema-on-write:** data is cleaned, validated and shaped *before* it is loaded.
- **Strengths:** fast and reliable SQL analytics, consistent business definitions, strong governance.
- **Limits:** expensive for huge raw data, poor at unstructured data, slower to add new sources (modelling comes first).
- **Examples:** Snowflake, BigQuery, Redshift, Azure Synapse, Teradata.

### 3. The data lake

A **data lake** stores **raw data of any type** (structured, semi-structured and unstructured) in its original format, in cheap **object storage** (Amazon S3, Azure Data Lake Storage, Google Cloud Storage).

- **Schema-on-read:** store first; decide the structure when you read the data.
- **Strengths:** very cheap at scale, keeps everything (useful for data science and future questions), handles any format.
- **Limits:** without governance it becomes a **data swamp**: nobody knows what is there, whether it is trustworthy, or who owns it. Classic lakes also lacked transactions, so concurrent writes and updates were painful.

[[fig:data_lake | A data lake organised into raw, cleaned and curated zones (often called bronze, silver and gold).]]

Lakes are usually organised into **zones** (the "medallion" layout):

| Zone | Also called | Contains |
|---|---|---|
| Raw | bronze | exact copies of source data, never modified, so jobs can be replayed |
| Cleaned | silver | validated, de-duplicated, standardised types and formats |
| Curated | gold | business-level tables and aggregates ready for BI and ML |

::: extension File formats in a lake
**CSV** and **JSON** are simple but slow and large. **Parquet** and **ORC** are *columnar* formats: compressed and fast for analytics, because queries read only the columns they need. **Avro** is a row format with an embedded schema, popular for streaming. Parquet is the default choice for analytical data in lakes.
:::

### 4. The data lakehouse

A **data lakehouse** combines the **cheap, open storage of a lake** with the **reliability and performance of a warehouse**, so BI, SQL analytics and machine learning all work on **one copy** of the data.

The key ingredient is an **open table format** layered on top of files in object storage:

- **Delta Lake** (Databricks), **Apache Iceberg**, **Apache Hudi**;
- they add **ACID transactions**, **schema enforcement and evolution**, **time travel** (query a table as of last Tuesday), upserts and deletes, and metadata for fast queries.

[[fig:lakehouse | The lakehouse stack: open files in object storage, an open table format adding warehouse features, and engines serving BI and ML.]]

**Why it exists:** many companies ran a lake (for data science) *and* a warehouse (for BI), copying data between them with extra pipelines, cost and inconsistencies. The lakehouse aims to remove that duplication. Platforms: Databricks, Snowflake (with Iceberg tables), Microsoft Fabric (OneLake), Google BigLake.

### The comparison tables interviewers ask for

| | Database (OLTP) | Data warehouse |
|---|---|---|
| Purpose | run the application | analyse the business |
| Data | current, operational | historical, integrated from many sources |
| Design | normalized | dimensional (star/snowflake) |
| Workload | many small reads and writes | large scans and aggregations |
| Users | applications, customers | analysts, BI tools |

| | Data warehouse | Data lake |
|---|---|---|
| Data types | structured (some semi-structured) | everything: structured, semi-structured, unstructured |
| Schema | on write (model first) | on read (store first) |
| Data state | cleaned, curated | raw and refined, in zones |
| Storage cost | higher | low (object storage) |
| Users | business analysts, BI | data engineers, data scientists |
| Performance for SQL BI | excellent | historically weaker; depends on engine and format |
| Governance | strong by default | must be built deliberately, or it becomes a swamp |
| Typical tools | Snowflake, BigQuery, Redshift | S3/ADLS/GCS + Spark, Athena, Presto/Trino |

| | Data lake | Data lakehouse |
|---|---|---|
| Storage | object storage, open files | object storage, open files + open table format |
| Transactions | none (file level) | ACID tables |
| Updates and deletes | hard (rewrite files) | supported (MERGE, UPDATE, DELETE) |
| Schema | on read only | enforced, but able to evolve |
| BI performance | limited | warehouse-like |
| Time travel and versioning | manual | built in |

<p class="tablecap">Warehouse vs lake vs lakehouse at a glance</p>

| | Warehouse | Lake | Lakehouse |
|---|---|---|---|
| Best at | trusted BI on structured data | cheap storage of everything, data science | one platform for BI + ML on open data |
| Schema | on write | on read | enforced + evolvable |
| ACID | yes | no | yes |
| Cost | $$$ | $ | $–$$ |
| Main risk | cost, rigidity | data swamp | platform maturity and skills |

### How to choose (a pragmatic view)

- **Mostly structured data and BI dashboards** → a cloud **warehouse** is the simplest and most reliable.
- **Large volumes of raw, varied data, plus ML** → a **lake** (with governance) or a **lakehouse**.
- **Want to avoid maintaining both a lake and a warehouse** → a **lakehouse**.
- Whatever you pick: a **catalogue** (what data exists), **ownership**, **quality checks** and **access control** matter more than the product.

::: explain
"A database runs the application with current, transactional data. A data warehouse stores cleaned, structured, historical data modelled for analytics; it's schema-on-write, very good for BI, but more expensive and rigid. A data lake stores raw data of any type, including JSON, logs and images, cheaply in object storage, with schema-on-read; it's flexible and great for data science, but without governance it turns into a data swamp. A lakehouse adds an open table format like Delta Lake or Iceberg on top of the lake, giving ACID transactions, schema enforcement and time travel, so BI and ML can run on the same copy of the data instead of maintaining both a lake and a warehouse."
:::

::: trap
- "A data lake is just a big database." It is file-based object storage with schema-on-read.
- "Lakes replace warehouses." Many organisations use both, or move to a lakehouse; warehouses remain excellent for BI.
- "Schema-on-read means no schema." The schema is applied when reading; someone still has to define it.
- Calling CSV files in S3 a lakehouse. Without an open table format adding ACID and metadata, it is a lake.
- Confusing **structured** with **SQL**: JSON stored in PostgreSQL is still semi-structured data.
:::

::: questions
#### Basic
Q: [COMPARISON] What is the difference between structured, semi-structured and unstructured data?
A: Structured fits fixed tables (orders); semi-structured has flexible, self-describing structure (JSON, XML, logs); unstructured has no predefined model (images, PDFs, audio).

Q: [DEFINITION] What is a data lake?
A: A central repository that stores raw data of any type in its native format, usually in cheap object storage, and applies a schema when the data is read.

Q: [COMPARISON] Data warehouse vs data lake?
A: A warehouse stores cleaned, structured, modelled data (schema-on-write) for BI; a lake stores raw data of all types cheaply (schema-on-read) for flexible analysis and data science.

#### Intermediate
Q: [DEFINITION] What is a data lakehouse?
A: An architecture that adds warehouse features (ACID transactions, schema enforcement, performance, time travel) to data-lake storage through open table formats like Delta Lake or Iceberg, serving BI and ML from one copy of the data.

Q: [COMPARISON] Schema-on-write vs schema-on-read?
A: Schema-on-write validates and shapes data before storing it (warehouses, relational databases); schema-on-read stores raw data and applies structure at query time (lakes).

Q: [DEFINITION] What is a data swamp and how do you prevent it?
A: A lake full of undocumented, untrusted, ownerless data. Prevent it with a data catalogue and metadata, clear zones, ownership, quality checks, access control and retention rules.

Q: [WHY] Why is Parquet preferred over CSV in data lakes?
A: It is columnar and compressed, so queries read only the needed columns and much less data; it also stores a schema and types.

#### Scenario-based
Q: [SCENARIO] A retailer wants sales dashboards and also to train ML models on clickstream logs and product images. What storage architecture would you propose?
A: A lakehouse (or a lake plus warehouse): land raw clickstream, images and sales extracts in object storage (bronze), clean and join them (silver), and publish curated sales tables (gold) for BI, while data scientists use the same data for ML. Add a catalogue and access controls.

Q: [SCENARIO] Analysts complain they can't find or trust data in the company's S3 lake. What would you do?
A: Introduce a catalogue with documented datasets and owners, organise raw/cleaned/curated zones, add quality checks and freshness metrics, adopt a table format (Delta/Iceberg) for reliable tables, and publish a curated, governed layer for BI.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is a lakehouse always better than a warehouse?
A: No. For mostly structured data and BI, a cloud warehouse is often simpler and cheaper to run well. A lakehouse pays off with varied data, ML workloads, or when you want to avoid duplicating data across a lake and a warehouse.

Q: [TRAP QUESTION] Is JSON stored in a relational table structured data?
A: The *data* is semi-structured; storing it in a JSONB column doesn't change its nature. The table around it is structured.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Classify as structured, semi-structured or unstructured: (a) a payroll table, (b) web server logs in JSON, (c) scanned invoices, (d) an XML feed of product prices.

**P2.** What do bronze, silver and gold zones contain?

#### Level 2 — Interview application
**P3.** In four lines, explain to a manager why a lakehouse could save money compared with "a lake plus a warehouse".

**P4.** Give two reasons Parquet makes analytical queries faster than CSV.

#### Level 3 — Scenario / problem solving
**P5.** A hospital wants to store patient records, MRI images, doctors' notes and billing data, and to run monthly financial reports plus ML research. Propose where each type of data lives and how it flows.
:::

::: answers
**P1.** (a) structured, (b) semi-structured, (c) unstructured, (d) semi-structured.

**P2.** Bronze: raw data exactly as received. Silver: cleaned, validated, de-duplicated, standardised data. Gold: curated business-level tables and aggregates for BI and ML.

**P3.** "Today we store data twice, in the lake and in the warehouse, and pay for pipelines that copy it between them. A lakehouse keeps one copy in cheap open storage and adds warehouse features on top, so BI and data science read the same tables. That cuts storage and pipeline costs and removes mismatches between the two copies."

**P4.** It is columnar, so a query reads only the columns it needs; and it is compressed, with stored statistics (min/max per block) that let engines skip irrelevant data.

**P5.** Patient records and billing (structured): an OLTP relational database for the hospital system, copied by CDC/ELT into a warehouse or lakehouse gold layer for monthly financial reporting. MRI images (unstructured): object storage, with metadata (patient, date, modality) in a database or catalogue. Doctors' notes (unstructured text): a lake, later processed (de-identified, NLP) into silver/gold tables for research. Governance across everything: access control, PII masking and de-identification for research, audit logs and a catalogue.
:::

## Session 4.8 — Module 4 Summary & Rapid Revision {: #s4-8 }

::: summary Module 4 Summary
#### Most important concepts
- **Cloud database options:** self-managed VM → managed (RDS, Cloud SQL) → serverless; shared responsibility.
- **Scaling:** vertical vs horizontal; read replicas; partitioning (inside one DB) vs sharding (across servers).
- **Availability:** Multi-AZ standby, automatic failover, SLAs, RPO/RTO; backups + PITR (replication is not a backup).
- **SQL vs NoSQL:** relational (ACID, joins, fixed schema) vs document, key-value, wide-column and graph (flexible, scale-out); column-family ≠ columnar.
- **CAP:** during a partition choose consistency or availability (CP vs AP); eventual consistency; BASE vs ACID.
- **MongoDB:** database → collection → document → field; BSON; `_id`/ObjectId; CRUD (insertOne/Many, find, updateOne/Many with `$set`, `$inc`, `$push`, deleteOne/Many); indexes; aggregation pipeline (`$match`, `$group`, `$unwind`, `$lookup`); embed vs reference.
- **Storage:** structured / semi-structured / unstructured; database vs warehouse (schema-on-write) vs lake (schema-on-read) vs lakehouse (open table formats with ACID).

#### What to memorize
- CAP letters and the CP/AP examples; RPO = data loss, RTO = downtime.
- The MongoDB ↔ SQL terminology table.
- The warehouse / lake / lakehouse comparison.

#### What to understand
- How to choose a database from requirements (data shape, consistency, scale, queries).
- Why replication lag causes "my change disappeared".
- Why lakes become swamps and how lakehouses fix reliability.

#### Most common interview questions
- SQL vs NoSQL? · When MongoDB? · Explain CAP · What is eventual consistency? · updateOne vs updateMany · What is BSON? · Embedding vs referencing · Warehouse vs lake · What is a lakehouse? · What happens on failover?

#### Common mistakes
- "Replicas are backups." · "Pick 2 of 3 in CAP." · "NoSQL = no schema = no design." · `deleteMany({})` · update without `$set` · "lakes replace warehouses".
:::

::: checklist
- [ ] I can explain managed vs self-managed vs serverless databases
- [ ] I can draw the shared responsibility split
- [ ] I can compare vertical and horizontal scaling
- [ ] I can explain read replicas, partitioning and sharding
- [ ] I can explain sync vs async replication and failover
- [ ] I can define RPO and RTO
- [ ] I know why replication is not a backup
- [ ] I can compare SQL and NoSQL in a table
- [ ] I can name the four NoSQL families with examples
- [ ] I can explain column-family vs columnar
- [ ] I can explain CAP with an example
- [ ] I can explain eventual consistency and BASE
- [ ] I know MongoDB's terminology and BSON
- [ ] I can write MongoDB CRUD commands
- [ ] I can write a simple aggregation pipeline
- [ ] I can decide between embedding and referencing
- [ ] I can classify structured, semi-structured and unstructured data
- [ ] I can compare warehouse, lake and lakehouse
:::
