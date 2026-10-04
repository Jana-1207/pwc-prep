# Cloud Databases & Storage Systems {: .part #m4 data-label="PART IV · MODULE 4" }

<p class="lead">Modern data rarely lives on a single server in an office. This module explains managed cloud databases, how databases scale and stay available, the different families of databases (relational, document, key-value, wide-column, graph), the CAP theorem, MongoDB from scratch, and the storage layers used for analytics: warehouses, lakes and lakehouses.</p>

::: coverage
- Cloud databases: what they are, managed databases, RDS / Cloud SQL concepts, serverless databases, analytical databases, scalability, availability, backups, replication, failover † → Session 4.1
- SQL vs NoSQL: relational, document, key-value, graph, column-family and columnar; when to choose each † → Session 4.2
- NoSQL: what and why, CAP theorem (consistency, availability, partition tolerance), eventual consistency † → Session 4.3
- MongoDB: database, collection, document, field, BSON † → Session 4.4
- MongoDB CRUD: insert, find, update, delete, updateMany, deleteMany † → Session 4.5
- MongoDB indexing, aggregation, embedding vs referencing † → Session 4.6
- Data storage: database, data warehouse, data lake, data lakehouse; structured, semi-structured and unstructured data † → Session 4.7
- Module quiz concepts → interview questions in each session and Session 4.8
:::

| Topic | Priority | Typical question |
|---|---|---|
| SQL vs NoSQL, choosing a database | [HIGH PRIORITY] | "Would you use SQL or NoSQL for X, and why?" |
| MongoDB basics and CRUD | [HIGH PRIORITY] | "How do you update many documents?" "What is BSON?" |
| CAP theorem, eventual consistency | [MEDIUM PRIORITY] | "Explain CAP with an example." |
| Managed databases, replication, failover, backups | [MEDIUM PRIORITY] | "What happens when the primary fails?" |
| Warehouse vs lake vs lakehouse | [MEDIUM PRIORITY] | "Compare a data lake and a data warehouse." |

::: pwc PwC angle
Cloud migration and data-platform modernization are large consulting service lines, so candidates are often asked to reason about trade-offs ("managed vs self-hosted", "lake vs warehouse", "why NoSQL here?") rather than to recite vendor commands. This module focuses on those concepts; product names appear only as examples.
:::

## Session 4.1 — Introduction to Cloud Databases {: #s4-1 }

### What is a cloud database?

**Simple meaning:** a cloud database is a database that runs on a cloud provider's infrastructure (AWS, Microsoft Azure, Google Cloud…) and is used over the network, instead of on servers your company buys and runs itself.

There are three main ways to run a database in the cloud:

| Option | What you get | Who does the hard work | Example |
|---|---|---|---|
| **Self-managed on a VM** (IaaS) | a virtual machine; you install the database yourself | you: installation, patches, backups, replication | PostgreSQL installed on an EC2 or Azure VM |
| **Managed database** (DBaaS / PaaS) | a ready database endpoint | the provider runs the servers; you design and use the database | Amazon RDS, Google Cloud SQL, Azure Database for PostgreSQL |
| **Serverless database** | a database that scales (even to zero) automatically; pay per use | the provider handles capacity too | Aurora Serverless, Azure SQL serverless, DynamoDB on-demand, Neon |

### Managed databases and the shared responsibility model

A **managed database** means the cloud provider takes over the operational chores: provisioning hardware, installing and patching the database, automated backups, replication, failover and monitoring. You still own the **data**: schema design, queries, indexes, users and permissions.

[[fig:cloud_responsibility | Who manages what. Moving right, the provider takes over more of the operational work.]]

**Why managed databases exist:** running a database well is hard work that does not differentiate most businesses. A managed service gives you, in minutes, what used to take a DBA team weeks: high availability, backups, encryption and monitoring.

| Benefits | Trade-offs |
|---|---|
| Fast setup (minutes) | Can cost more than self-managed at very large scale |
| Automated backups and point-in-time recovery | Less control: no OS access; some extensions or settings restricted |
| Built-in high availability and failover | Some vendor lock-in (proprietary features, migration effort) |
| Easy scaling (bigger instance, read replicas) | Network latency if the app runs elsewhere |
| Patching and upgrades handled | Maintenance windows are on the provider's schedule |

### RDS and Cloud SQL, conceptually

- **Amazon RDS (Relational Database Service):** managed PostgreSQL, MySQL, MariaDB, Oracle and SQL Server. **Amazon Aurora** is AWS's cloud-native engine, compatible with MySQL and PostgreSQL, with storage replicated across availability zones.
- **Google Cloud SQL:** managed MySQL, PostgreSQL and SQL Server. **AlloyDB** and **Spanner** are Google's higher-end options.
- **Azure SQL Database / Azure Database for PostgreSQL or MySQL:** Microsoft's managed equivalents.

In an interview you rarely need commands. Say what the service does for you: "RDS runs PostgreSQL for us, with automated backups, Multi-AZ failover and read replicas; we just connect to an endpoint."

### Serverless databases

A **serverless** database automatically adds and removes compute capacity as load changes, can pause when idle, and bills for what is actually used.

- **Good for:** spiky or unpredictable traffic, development and test environments, new products with unknown load.
- **Watch out for:** cold-start or resume delays after idle periods, cost surprises under constant heavy load, and limits on connections or features.

### Analytical (cloud data warehouse) databases

Analytical databases are built for OLAP (Module 1): scanning and aggregating huge tables.

| Product | Notable idea |
|---|---|
| Google BigQuery | serverless: no servers to size; pay per data scanned or reserved capacity |
| Amazon Redshift | MPP (massively parallel processing) columnar warehouse |
| Snowflake | storage and compute separated; many independent compute "warehouses" on the same data |
| Azure Synapse / Microsoft Fabric | warehouse plus lake integration in Microsoft's ecosystem |

They store data in **columns** rather than rows, compress it heavily, and split each query across many machines.

### Scalability: handling more load

[[fig:scaling | Vertical scaling makes one machine bigger; horizontal scaling adds more machines.]]

| | Vertical scaling (scale up) | Horizontal scaling (scale out) |
|---|---|---|
| How | bigger machine: more CPU, RAM, faster disk | more machines sharing the load |
| Code changes | none | often needed (routing, sharding) |
| Limit | the biggest machine available | very high |
| Downtime | often a restart | can be done online |
| Typical for | relational databases, first step for most apps | NoSQL, distributed SQL, read replicas |

Three tools for scaling relational databases:

1. **Read replicas:** copies of the database that serve read-only queries, taking load off the primary (good when reads ≫ writes).
2. **Partitioning:** splitting a big table into pieces *inside one database* (for example, orders partitioned by month). Queries that touch one month read only that partition.
3. **Sharding:** splitting data *across several database servers* by a **shard key** (customer_id 1–1M on shard 1…). Very scalable, but cross-shard joins and transactions become hard.

### Availability: staying up

**High availability (HA)** means the database keeps serving even when a component fails. Clouds offer it through **multiple availability zones** (separate data centres in one region) with automatic failover.

| SLA uptime | Allowed downtime per year (approx.) |
|---|---|
| 99.9% ("three nines") | about 8.8 hours |
| 99.95% | about 4.4 hours |
| 99.99% ("four nines") | about 53 minutes |

Two terms every interviewer likes [INTERVIEW EXTENSION]:

- **RPO (Recovery Point Objective):** how much data you can afford to lose, measured in time. "RPO 5 minutes" means losing at most the last 5 minutes of changes.
- **RTO (Recovery Time Objective):** how long you can afford to be down. "RTO 1 hour" means service is restored within an hour.

### Backups

- **Automated snapshots:** a full copy taken daily and kept for a retention period (for example 7–35 days).
- **Point-in-time recovery (PITR):** the snapshot plus the transaction logs let you restore to any second in the retention window, for example just before someone ran `DELETE` without a WHERE.
- **Test your restores.** A backup you have never restored is a hope, not a plan.

### Replication

**Replication** keeps copies of the data on other servers.

| | Synchronous replication | Asynchronous replication |
|---|---|---|
| How | the primary waits until the replica confirms each write | the primary confirms immediately; the replica catches up shortly after |
| Data loss on primary failure | none (RPO ≈ 0) | possibly the last few seconds of writes |
| Write speed | slower (waits for the network) | faster |
| Typical use | standby for failover (in the same region) | read replicas, cross-region copies |

**Replication lag** with asynchronous replicas can surprise users: someone updates their profile (on the primary), the page reloads from a replica, and the old value appears. Fixes include reading your own writes from the primary, or routing that user to the primary for a short time.

::: trap Replication is not a backup
If someone deletes a table, replication faithfully copies the delete to every replica within seconds. Only backups (and PITR) let you go back in time.
:::

### Failover

**Failover** is switching to a standby when the primary fails.

[[fig:replication_failover | With Multi-AZ, a synchronous standby is promoted when the primary fails; the application reconnects to the same endpoint.]]

1. Health checks detect the failed primary.
2. The standby (an up-to-date synchronous copy) is **promoted** to be the new primary.
3. The database endpoint (a DNS name) is pointed at the new primary.
4. Applications reconnect. This takes from seconds to a couple of minutes, so apps should **retry connections**.

::: explain
"A managed cloud database like Amazon RDS or Cloud SQL runs the database for us: the provider handles hardware, patching, backups, replication and failover, and we focus on schema, queries and access control. For scale we can move to a bigger instance, add read replicas for read-heavy traffic, partition big tables, or shard across servers. For availability we deploy a synchronous standby in another availability zone; if the primary fails, the standby is promoted and the endpoint switches over. And because replication copies mistakes too, we still rely on automated backups and point-in-time recovery."
:::

::: trap
- Treating replicas as backups.
- Assuming "managed" means "no work". Schema design, indexing, query tuning and security remain yours.
- Confusing partitioning (within one database) with sharding (across servers).
- Forgetting replication lag when reading from replicas.
- Saying serverless means "no servers exist". They exist; you just don't manage them.
:::

::: questions
#### Basic
Q: [DEFINITION] What is a managed database?
A: A cloud service where the provider operates the database (provisioning, patching, backups, replication, failover, monitoring) while the customer manages the data, schema, queries and access.

Q: [COMPARISON] Vertical vs horizontal scaling?
A: Vertical adds resources to one machine (simple, limited); horizontal adds more machines (very scalable, but more complex: sharding, routing, consistency).

Q: [DEFINITION] What is a read replica?
A: A read-only copy of the database, kept up to date by replication, used to serve read queries and reduce load on the primary.

#### Intermediate
Q: [COMPARISON] Synchronous vs asynchronous replication?
A: Synchronous waits for the replica to confirm each write (no data loss on failover, slower writes); asynchronous confirms immediately (faster, but recent writes can be lost and replicas lag).

Q: [DEFINITION] What are RPO and RTO?
A: RPO is the maximum acceptable data loss, measured in time; RTO is the maximum acceptable downtime before service is restored.

Q: [COMPARISON] Partitioning vs sharding?
A: Partitioning splits a table into parts within one database server; sharding distributes data across multiple servers by a shard key.

Q: [DEFINITION] What is point-in-time recovery?
A: Restoring a database to an exact moment by applying transaction logs on top of a base backup, for example to just before an accidental delete.

#### Scenario-based
Q: [SCENARIO] Your app's reads are 20 times higher than writes and the database CPU is maxed out. What would you consider?
A: Add read replicas and route read-only queries to them, add caching (Redis) for hot data, check indexes and slow queries, and only then scale the primary up. Watch for replication lag on read-after-write paths.

Q: [SCENARIO] The business needs at most 1 minute of data loss and 15 minutes of downtime. How would you set up the database?
A: A managed database with a synchronous Multi-AZ standby for automatic failover (meets RTO), continuous log backup with PITR (meets RPO), alerting, and regular restore tests. For regional disasters, add an asynchronous cross-region replica.

Q: [DESIGN QUESTION] Would you choose a serverless database for a college-fest registration site?
A: Yes, it's a good fit: traffic spikes around the event and is near zero otherwise, so auto-scaling and pay-per-use keep costs low. Mention possible cold starts after idle periods.

#### Follow-up / Trap
Q: [TRAP QUESTION] We have three replicas, so do we still need backups?
A: Yes. Replicas copy deletions and corruption almost instantly; backups and PITR protect against human error, bugs and ransomware.

Q: [TRAP QUESTION] Does a managed database tune your queries for you?
A: No. Some services offer recommendations, but schema design, indexing and query optimization remain the customer's responsibility.
:::

## Session 4.2 — SQL vs NoSQL: Types of Databases {: #s4-2 }

[HIGH PRIORITY] "SQL or NoSQL, and why?" is one of the most common database interview questions.

### Relational (SQL) databases, in one paragraph

Relational databases store data in **tables** with a **fixed schema**, link tables with **keys**, are queried with **SQL**, and provide **ACID transactions** and **joins**. They are the default for business data that must be correct and consistent: orders, payments, inventory, HR. Examples: PostgreSQL, MySQL, Oracle, SQL Server.

### What "NoSQL" means

**NoSQL ("Not only SQL")** is an umbrella term for databases that do **not** use the relational table model. They typically trade some relational features (fixed schemas, joins, sometimes strict consistency) for **flexible data models**, **horizontal scaling** and **high write throughput**. There are four main families:

[[fig:nosql_types | The four NoSQL families and the shape of the data each one stores.]]

| Family | Data shape | Strengths | Weaknesses | Examples | Typical uses |
|---|---|---|---|---|---|
| **Document** | JSON-like documents in collections | flexible schema, nested data, natural fit for objects | complex joins and multi-document transactions are less natural | MongoDB, Couchbase, Firestore, Cosmos DB | catalogues, content, user profiles, mobile backends |
| **Key-value** | key → value | extremely fast, simple, scales easily | query only by key; no rich querying | Redis, DynamoDB, Memcached | caching, sessions, carts, rate limiting, leaderboards |
| **Wide-column (column-family)** | rows with flexible, sparse columns grouped in families; partitioned by key | massive write volumes, linear scale-out, multi-region | queries must follow the partition key; no joins | Cassandra, HBase, Bigtable, ScyllaDB | IoT, time-series, messaging, activity feeds |
| **Graph** | nodes and relationships (edges) | traversing relationships fast (friends-of-friends) | not built for bulk aggregation | Neo4j, Amazon Neptune | social networks, recommendations, fraud rings, knowledge graphs |

### Column-family vs columnar: two different ideas

These names sound alike but mean different things, and interviewers like to check:

- **Wide-column / column-family NoSQL** (Cassandra, HBase): an operational database where each *row* can have different columns, grouped into families and distributed by partition key. Built for fast writes and key-based reads.
- **Columnar storage** (Redshift, BigQuery, Snowflake, ClickHouse, Parquet files): an analytical storage layout that stores **each column's values together** on disk, instead of each row's values together.

<p class="tablecap">The same three rows, stored two ways</p>

| Row-oriented (OLTP) | Column-oriented (OLAP) |
|---|---|
| `[101, Aarav, Mumbai, 2843]` `[102, Isha, Pune, 3499]` `[103, Aarav, Mumbai, 8999]` | `order_id: [101, 102, 103]` `customer: [Aarav, Isha, Aarav]` `city: [Mumbai, Pune, Mumbai]` `amount: [2843, 3499, 8999]` |
| fast to read or write **one whole row** (fetch order 102) | fast to scan **one column for millions of rows** (`SUM(amount)`); repeated values compress very well |

### SQL vs NoSQL

| | SQL (relational) | NoSQL |
|---|---|---|
| Data model | tables, rows, columns | documents, key-value, wide-column, graph |
| Schema | fixed, defined up front (schema-on-write) | flexible, can vary per record |
| Relationships | foreign keys and joins | embedding, references, or application-side joins (graphs: native edges) |
| Query language | standard SQL | product-specific APIs and languages (MongoDB query language, CQL, Cypher) |
| Transactions | strong ACID, multi-row and multi-table | varies: often per-record atomicity; some support multi-document ACID (MongoDB) |
| Consistency | strong by default | often tunable; many default to eventual consistency in distributed setups |
| Scaling | traditionally vertical, plus read replicas (distributed SQL also scales out) | designed for horizontal scaling |
| Best for | structured data, complex queries, integrity-critical data | huge scale, flexible or fast-changing structure, simple access patterns |
| Examples | PostgreSQL, MySQL, Oracle, SQL Server | MongoDB, Redis, Cassandra, DynamoDB, Neo4j |

### How to choose: a decision guide

| If the requirement is… | Lean towards | Because |
|---|---|---|
| Money, orders, bookings; correctness first | Relational (PostgreSQL) | ACID transactions, constraints, joins |
| Ad-hoc reporting and complex queries across entities | Relational, or a warehouse for analytics | SQL is built for this |
| Product catalogue with very different attributes per item | Document (MongoDB), or PostgreSQL JSONB | flexible schema, nested data |
| Sub-millisecond lookups, sessions, caching | Key-value (Redis) | in-memory speed |
| Millions of writes per second, time-series, multi-region | Wide-column (Cassandra) | linear scale-out, partitioned writes |
| Relationship-heavy questions ("people you may know") | Graph (Neo4j) | fast traversals |
| Unsure, small or medium app | **Start with PostgreSQL** | versatile; supports JSONB, full-text search and more |

### PostgreSQL can store documents too

The line between SQL and NoSQL is blurrier than it used to be. PostgreSQL's `JSONB` type stores binary JSON that can be indexed and queried:

```sql run
CREATE TABLE product_docs (
    id   INT PRIMARY KEY,
    doc  JSONB NOT NULL
);

INSERT INTO product_docs VALUES
  (1, '{"name": "ThinkPad E14", "category": "Laptop", "price": 62990,
        "specs": {"ram_gb": 16, "cpu": "Ryzen 5"}}'),
  (2, '{"name": "Cotton Tee", "category": "Apparel", "price": 499,
        "sizes": ["S", "M", "L"], "colour": "navy"}'),
  (3, '{"name": "Galaxy Buds", "category": "Audio", "price": 8999,
        "specs": {"battery_hrs": 6}}');

SELECT id,
       doc->>'name'             AS name,
       (doc->>'price')::numeric AS price,
       doc->'specs'->>'ram_gb'  AS ram_gb
FROM product_docs
WHERE doc ? 'specs'                       -- documents that have a "specs" key
ORDER BY price DESC;
```

::: linebyline
| Part | What it does |
|---|---|
| `doc JSONB` | a column holding a whole JSON document per row |
| `doc->>'name'` | read a key as **text** (`->` returns JSON, `->>` returns text) |
| `(doc->>'price')::numeric` | cast the text to a number for sorting and maths |
| `doc->'specs'->>'ram_gb'` | navigate into a nested object; NULL if the key is missing |
| `WHERE doc ? 'specs'` | the `?` operator tests whether a key exists |
:::

Containment queries such as `WHERE doc @> '{"category": "Apparel"}'` can use a **GIN index**. This hybrid is often the pragmatic answer: relational for core entities, JSONB for the flexible parts.

::: extension Distributed SQL ("NewSQL")
Google Spanner, CockroachDB, YugabyteDB and similar systems offer SQL and ACID transactions while scaling horizontally across regions. They show that "SQL cannot scale out" is no longer true; it is a question of trade-offs and cost.
:::

::: explain
"SQL databases store structured data in tables with a fixed schema, support joins and strong ACID transactions, so they're my default for business-critical data like orders and payments. NoSQL is a family of non-relational databases: document stores like MongoDB for flexible JSON data, key-value stores like Redis for very fast lookups and caching, wide-column stores like Cassandra for massive write volumes, and graph databases like Neo4j for relationship-heavy queries. They usually scale out horizontally and offer flexible schemas, sometimes with eventual consistency. I choose based on data shape, consistency needs, query patterns and scale, and many real systems use both."
:::

::: trap
- "NoSQL is faster than SQL." It depends entirely on the workload and access pattern.
- "NoSQL has no schema, so no design." The schema moves into the application.
- "NoSQL never supports transactions." MongoDB, for example, supports multi-document ACID transactions.
- Confusing wide-column NoSQL (Cassandra) with columnar analytical storage (Redshift, Parquet).
- Choosing NoSQL "because it's modern" for data that is highly relational and integrity-critical.
:::

::: questions
#### Basic
Q: [COMPARISON] What is the difference between SQL and NoSQL databases?
A: SQL databases are relational: tables, fixed schema, SQL, joins, strong ACID. NoSQL databases are non-relational (document, key-value, wide-column, graph), with flexible schemas, horizontal scaling and varied consistency models.

Q: [DEFINITION] Name the four main types of NoSQL databases with an example each.
A: Document (MongoDB), key-value (Redis), wide-column (Cassandra), graph (Neo4j).

Q: [DEFINITION] What is a key-value store used for?
A: Very fast lookups by key: caching, sessions, shopping carts, rate limiting, leaderboards.

#### Intermediate
Q: [COMPARISON] Wide-column store vs columnar database?
A: A wide-column store (Cassandra) is an operational NoSQL database with flexible columns per row, partitioned by key. A columnar database (Redshift, BigQuery) stores each column contiguously for fast analytical scans and compression.

Q: [WHY] When would you choose a graph database?
A: When the main queries traverse relationships of variable depth (friends-of-friends, fraud rings, recommendations), which would need many expensive self-joins in SQL.

Q: [HOW] Can a relational database store JSON?
A: Yes. PostgreSQL's JSONB stores binary JSON that can be queried with operators (`->`, `->>`, `@>`, `?`) and indexed with GIN; MySQL and SQL Server also have JSON support.

#### Scenario-based
Q: [SCENARIO] You need flexible schemas for a product catalogue. Would you use SQL or NoSQL?
A: A document database such as MongoDB fits naturally, since each product can carry its own attributes. If the rest of the system is relational, PostgreSQL with a JSONB column for the variable attributes is a strong, simpler alternative.

Q: [SCENARIO] Choose databases for a ride-sharing app.
A: PostgreSQL for users, trips and payments (ACID); Redis for live driver locations and sessions; Cassandra or a time-series store for high-volume location history; a warehouse for analytics.

Q: [DESIGN QUESTION] A bank asks whether to move its core ledger to a NoSQL database for scalability. What do you advise?
A: Be cautious. A ledger needs strict ACID transactions, constraints and auditability. Prefer a relational or distributed SQL database, scale with partitioning, replicas or distributed SQL, and use NoSQL for peripheral workloads like caching or event history.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does using MongoDB mean you can never do joins?
A: No. MongoDB has `$lookup` in its aggregation pipeline; the point is that you design to need fewer joins.

Q: [TRAP QUESTION] Is NoSQL always eventually consistent?
A: No. Many NoSQL systems offer strong consistency options (MongoDB reads from the primary; DynamoDB strongly consistent reads; Cassandra quorum reads and writes).
:::

## Session 4.3 — NoSQL Fundamentals and the CAP Theorem {: #s4-3 }

### Why NoSQL appeared

Around the late 2000s, web companies hit limits with single-server relational databases: billions of users, constant schema changes and global traffic. NoSQL systems were designed to:

- **scale horizontally** across many cheap machines (sharding by key);
- **stay available** when machines or networks fail (replication);
- **accept flexible, evolving data** (JSON documents, sparse columns);
- **serve simple access patterns extremely fast** (lookup by key).

### How distributed databases spread data

- **Partitioning / sharding:** each record's key decides which node stores it, for example `hash(user_id) mod N`. Smarter schemes (consistent hashing) avoid moving most data when nodes are added.
- **Replication:** each partition is copied to several nodes (often 3), so one node's failure loses nothing.

Once data is copied across machines connected by a network, you face the question the CAP theorem describes.

### The CAP theorem

In a **distributed** data system, you would like three properties:

| Letter | Property | Plain meaning |
|---|---|---|
| **C** | Consistency | every read sees the most recent write (all nodes agree) |
| **A** | Availability | every request to a working node gets a (non-error) response |
| **P** | Partition tolerance | the system keeps working even if the network splits nodes into groups that can't talk to each other |

**The theorem (Eric Brewer):** when a network partition happens, a distributed system must choose between **consistency** and **availability**; it cannot guarantee both at that moment.

[[fig:cap_triangle | CAP: during a network partition, a distributed system chooses consistency (CP) or availability (AP).]]

::: example A simple story
Two replicas of an account balance, one in Mumbai and one in Chennai. The network link between them breaks. A user in Chennai asks for the balance, which was just updated in Mumbai.
- **CP choice:** Chennai refuses to answer (or returns an error) until it can confirm the latest value. Correct, but unavailable.
- **AP choice:** Chennai answers with the value it has, which may be stale. Available, but possibly inconsistent.
:::

**The common misunderstanding:** CAP is often phrased as "pick any two of three". In a real distributed system network partitions *will* happen, so P is not optional; the real choice is **C or A during a partition**. "CA" systems are essentially single-node databases that never face partitions.

| Type | Behaviour during a partition | Examples (default settings) |
|---|---|---|
| CP | stays consistent; some requests fail or wait | MongoDB (writes and reads via the primary), HBase, etcd, ZooKeeper |
| AP | stays available; may return stale data, reconciles later | Cassandra, DynamoDB (default reads), CouchDB |
| CA | only possible without partitions | a single-node relational database |

These labels describe *default* behaviour. Many modern databases let you tune consistency per operation.

::: extension PACELC
CAP talks only about partitions. **PACELC** adds: *if Partitioned, choose Availability or Consistency; Else (normal operation), choose Latency or Consistency.* Even without failures, waiting for replicas to agree costs time. Cassandra is PA/EL; a typical relational primary-standby setup is PC/EC.
:::

### Consistency models

| Model | Guarantee | Example |
|---|---|---|
| **Strong consistency** | a read always returns the latest committed write | a bank balance after a transfer |
| **Eventual consistency** | if writes stop, all replicas *eventually* become identical; reads may be stale for a while | a social post's like count; DNS updates spreading worldwide |
| **Read-your-writes** | you always see your own updates, even if others may not yet | you change your profile picture and immediately see the new one |
| **Causal consistency** | related events are seen in order (a reply never appears before its question) | comment threads |

Eventual consistency is acceptable when slightly stale data harms no one (likes, view counts, recommendations) and unacceptable when it causes real damage (double-selling the last seat, overdrawing an account).

::: extension Tunable consistency with quorums
Systems like Cassandra keep N copies of each record. A write waits for W replicas to confirm and a read asks R replicas. If **R + W > N** (for example N = 3, W = 2, R = 2), every read overlaps with the latest write: strong consistency. Lower values give faster responses with weaker guarantees.
:::

### ACID vs BASE

Many NoSQL systems describe themselves with **BASE**:

| ACID (typical relational) | BASE (typical distributed NoSQL) |
|---|---|
| **A**tomicity, **C**onsistency, **I**solation, **D**urability | **B**asically **A**vailable, **S**oft state, **E**ventually consistent |
| correctness first | availability and scale first |
| strong consistency | eventual consistency (often tunable) |
| pessimistic: prevent conflicts | optimistic: resolve conflicts later |
| bank transfers, orders | social feeds, product views, IoT telemetry |

::: explain
"The CAP theorem says that in a distributed database, when a network partition happens, you have to choose between consistency, where every read returns the latest write, and availability, where every request still gets a response. Partition tolerance isn't really optional across a network, so the practical choice is CP or AP during a partition. MongoDB with default settings behaves as CP, preferring to reject writes rather than diverge, while Cassandra is AP and returns possibly stale data, then reconciles. Eventual consistency means replicas converge over time, which is fine for things like like-counts but not for bank balances."
:::

::: trap
- "Pick any two of C, A and P." In distributed systems P is a given; the trade-off is C vs A during partitions.
- Confusing CAP consistency (replicas agree) with ACID consistency (constraints hold).
- Labelling a database permanently CP or AP. Behaviour often depends on configuration and per-query settings.
- Thinking eventual consistency means "inconsistent forever". It means replicas converge after a short delay.
:::

::: questions
#### Basic
Q: [DEFINITION] What is the CAP theorem?
A: In a distributed system, during a network partition you can guarantee either consistency (latest data everywhere) or availability (every request answered), but not both.

Q: [DEFINITION] What is eventual consistency?
A: A model where replicas may be temporarily out of date, but if no new writes occur, they all converge to the same value.

Q: [DEFINITION] What does BASE stand for?
A: Basically Available, Soft state, Eventually consistent: the availability-first counterpart to ACID.

#### Intermediate
Q: [COMPARISON] CP vs AP systems: give examples.
A: CP systems (HBase, MongoDB with default primary reads, etcd) refuse or delay requests to stay consistent during partitions; AP systems (Cassandra, CouchDB, DynamoDB with default reads) keep answering with possibly stale data and reconcile later.

Q: [WHY] Why can't a distributed database simply be "CA"?
A: Because network partitions are unavoidable between machines. A system that cannot tolerate them stops working correctly when they occur; CA only really describes single-node systems.

Q: [COMPARISON] ACID consistency vs CAP consistency?
A: ACID consistency means transactions keep data valid according to rules and constraints. CAP consistency means all replicas return the same, most recent value.

Q: [HOW] How does sharding work?
A: Data is split by a shard key (for example hash(user_id)) so each node stores a subset; requests are routed to the node that owns the key.

#### Scenario-based
Q: [SCENARIO] A social app shows like counts that differ slightly between users for a few seconds. Is this a bug?
A: Probably not. It's eventual consistency, an acceptable trade-off for availability and speed in a non-critical feature.

Q: [SCENARIO] Which consistency would you require for seat booking in a cinema app, and why?
A: Strong consistency for the booking step (or a conditional, atomic write), otherwise two users could book the same seat. Browsing seat maps can tolerate slight staleness.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is MongoDB CP or AP?
A: With default settings (reads and writes through the primary, majority write concern), it behaves as CP. Reading from secondaries or relaxing write concerns moves it towards availability. Behaviour is configurable.

Q: [TRAP QUESTION] Does CAP apply to a single PostgreSQL server?
A: Not really. CAP is about distributed systems with replicas across a network. Once you add replicas, the trade-offs appear (e.g. synchronous vs asynchronous replication).
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Name the database family best suited to each: (a) user sessions, (b) a friends-of-friends query, (c) a product catalogue, (d) sensor readings at 1 million writes per second.

**P2.** What is the difference between a read replica and a standby?

**P3.** True or false: replication protects against accidental deletes.

#### Level 2 — Interview application
**P4.** Explain the CAP theorem using a two-city example in under a minute.

**P5.** Give two reasons a company might choose a managed database over running PostgreSQL on its own VM, and one reason not to.

#### Level 3 — Scenario / problem solving
**P6.** A food-delivery startup expects 10× traffic during festivals. Propose a database setup for orders, menus, sessions and analytics, with a reason for each choice.

**P7.** After moving reads to replicas, users complain that a new address "disappears" right after saving. Explain why and propose two fixes.
:::

::: answers
**P1.** (a) key-value (Redis), (b) graph (Neo4j), (c) document (MongoDB) or PostgreSQL JSONB, (d) wide-column (Cassandra) or a time-series database.

**P2.** A read replica serves read traffic (usually asynchronously updated) to reduce load. A standby exists for failover (often synchronously updated in another zone) and usually doesn't serve traffic until it is promoted.

**P3.** False. Replication copies the delete to every replica; you need backups or point-in-time recovery.

**P4.** "Imagine our data is replicated in Mumbai and Chennai and the network between them breaks. If a user in Chennai reads data that was just changed in Mumbai, the Chennai node can either refuse to answer until it can confirm the latest value, which is consistent but unavailable, or answer with what it has, which is available but possibly stale. CAP says that during such a partition you can't have both, so distributed databases choose CP or AP."

**P5.** For: automated backups, PITR and failover out of the box; less operational work (patching, monitoring). Against: less control (no OS or superuser access, some extensions unavailable) or higher cost at very large scale.

**P6.** Orders and payments: managed PostgreSQL with a Multi-AZ standby (ACID, failover) plus read replicas for order-history pages. Menus: MongoDB or PostgreSQL JSONB, because restaurant menus vary, plus a cache. Sessions and live rider location: Redis (fast, expiring keys). Analytics: a cloud warehouse such as BigQuery or Snowflake, loaded by CDC or ELT, so dashboards never touch the order database. For festivals: scale replicas and cache ahead of time, and load-test.

**P7.** Replication lag: the write went to the primary, but the next read hit an asynchronous replica that hadn't received it yet. Fixes: read-your-writes routing (send a user's reads to the primary for a short time after they write), read critical pages from the primary, or update the UI from the write response instead of re-reading immediately.
:::
