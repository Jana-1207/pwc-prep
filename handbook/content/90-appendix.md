# Appendix {: .part #appendix data-label="APPENDIX" }

<p class="lead">A plain-language glossary of the terms used in this handbook, and the self-review that checks the handbook against its original brief.</p>

## Glossary {: .nobreak #glossary }

Short, plain definitions of 162 terms. The last column gives the session (and page) where each idea is taught properly, with examples and interview questions. If a definition here feels thin, that is the place to go.

::: glossary
<p class="glossletter">A</p>

| Term | Plain meaning | Session |
|---|---|---|
| **ACID** | The four guarantees of a transaction: Atomicity (all or nothing), Consistency (rules hold), Isolation (concurrent transactions don't interfere), Durability (committed data survives a crash). | 3.10 · <a class="pageref" href="#s3-10"></a> |
| **Aggregate function** | Turns many rows into one value: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. All of them skip NULLs except `COUNT(*)`. | 3.2 · <a class="pageref" href="#s3-2"></a> |
| **Aggregation pipeline** | MongoDB's way to filter, group and reshape documents through stages such as `$match`, `$group`, `$sort` and `$lookup`. | 4.6 · <a class="pageref" href="#s4-6"></a> |
| **Anomaly (data)** | An update, insert or delete problem caused by storing the same fact in more than one place. | 2.5 · <a class="pageref" href="#s2-5"></a> |
| **Anti-join** | Rows in one table with no match in another: `NOT EXISTS`, or `LEFT JOIN … WHERE right.id IS NULL`. | 3.6 · <a class="pageref" href="#s3-6"></a> |
| **API** | A contract that lets one program ask another for data or actions without knowing how it works inside. | 5.1 · <a class="pageref" href="#s5-1"></a> |
| **API gateway** | A single front door for APIs that handles authentication, rate limiting, routing and logging. | 5.3 · <a class="pageref" href="#s5-3"></a> |
| **At-least-once delivery** | Every message arrives, but some may arrive more than once, so consumers must be idempotent. | 6.3 · <a class="pageref" href="#s6-3"></a> |
| **Attribute** | A property of an entity, such as a customer's email; it usually becomes a column. | 2.2 · <a class="pageref" href="#s2-2"></a> |
| **Authentication (AuthN)** | Proving who you are: a password, a token, a certificate. | 5.4 · <a class="pageref" href="#s5-4"></a> |
| **Authorization (AuthZ)** | Deciding what an authenticated user is allowed to do. | 5.4 · <a class="pageref" href="#s5-4"></a> |
| **Availability** | The share of time a system is up and answering; 99.9% ("three nines") allows about 8.8 hours of downtime a year. | 4.1 · <a class="pageref" href="#s4-1"></a> |

<p class="glossletter">B</p>

| Term | Plain meaning | Session |
|---|---|---|
| **B-tree index** | The default index type: a balanced, sorted tree that finds a value in a few steps and also serves ranges and sorting. | 3.9 · <a class="pageref" href="#s3-9"></a> |
| **Backoff (exponential)** | Waiting longer after each failed retry (1 s, 2 s, 4 s …), plus random jitter so clients don't all retry at once. | 5.5 · <a class="pageref" href="#s5-5"></a> |
| **BASE** | Basically Available, Soft state, Eventually consistent: the relaxed model many NoSQL systems use instead of ACID. | 4.3 · <a class="pageref" href="#s4-3"></a> |
| **Batch processing** | Processing data in scheduled chunks, such as a nightly job. Simple and cheap, but the data is not fresh. | 1.3 · <a class="pageref" href="#s1-3"></a> |
| **BCNF** | Boyce–Codd Normal Form: a stricter 3NF in which every determinant is a candidate key. | 2.5 · <a class="pageref" href="#s2-5"></a> |
| **BSON** | Binary JSON: MongoDB's storage format, with extra types such as dates, decimals and ObjectId. | 4.4 · <a class="pageref" href="#s4-4"></a> |

<p class="glossletter">C</p>

| Term | Plain meaning | Session |
|---|---|---|
| **Cache** | A fast copy of frequently read data (often in Redis) that cuts database load and response time. | 1.1 · <a class="pageref" href="#s1-1"></a> |
| **CAP theorem** | When the network between nodes fails (a partition), a distributed system must choose consistency or availability. | 4.3 · <a class="pageref" href="#s4-3"></a> |
| **Cardinality** | How many of one entity relate to another: one-to-one, one-to-many or many-to-many. | 2.2 · <a class="pageref" href="#s2-2"></a> |
| **CDC (Change Data Capture)** | Reading a database's change log and streaming every insert, update and delete to other systems. | 5.6 · <a class="pageref" href="#s5-6"></a> |
| **Circuit breaker** | Stops calling a failing service for a while and fails fast, giving the service time to recover. | 5.5 · <a class="pageref" href="#s5-5"></a> |
| **Client–server** | Clients send requests; servers do the work and send back responses. | 5.1 · <a class="pageref" href="#s5-1"></a> |
| **Cloud-native** | Built for the cloud from the start: containers, Kubernetes, managed services, autoscaling, infrastructure as code, CI/CD. | 7.4 · <a class="pageref" href="#s7-4"></a> |
| **Cold start** | The extra delay when a serverless platform must start a new instance before it can handle a request. | 7.2 · <a class="pageref" href="#s7-2"></a> |
| **Columnar storage** | Storing data column by column, so analytical queries read only the columns they need and compress well. | 4.2 · <a class="pageref" href="#s4-2"></a> |
| **Composite index** | An index on several columns, usable from the leftmost column onward. | 3.9 · <a class="pageref" href="#s3-9"></a> |
| **Composite key** | A primary key made of two or more columns, such as `(order_id, product_id)`. | 2.3 · <a class="pageref" href="#s2-3"></a> |
| **Constraint** | A rule the database enforces: `NOT NULL`, `UNIQUE`, `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, `DEFAULT`. | 2.3 · <a class="pageref" href="#s2-3"></a> |
| **Consumer group** | In Kafka, consumers that share a topic's partitions, so each event is processed once per group. | 6.7 · <a class="pageref" href="#s6-7"></a> |
| **Correlated subquery** | A subquery that uses a value from the outer row, so it is evaluated once per outer row. | 3.7 · <a class="pageref" href="#s3-7"></a> |
| **CRUD** | Create, Read, Update, Delete: the four basic operations (POST, GET, PUT/PATCH, DELETE in REST). | 5.2 · <a class="pageref" href="#s5-2"></a> |
| **CTE** | Common Table Expression: a named temporary result defined with `WITH`, used to write a query in readable steps. | 3.7 · <a class="pageref" href="#s3-7"></a> |

<p class="glossletter">D</p>

| Term | Plain meaning | Session |
|---|---|---|
| **Data catalogue** | A searchable inventory of datasets with owners, descriptions, quality status and lineage. | 7.3 · <a class="pageref" href="#s7-3"></a> |
| **Data governance** | Who owns data, who may use it and how: access control, privacy, retention and legal compliance. | 7.3 · <a class="pageref" href="#s7-3"></a> |
| **Data integration** | Combining data from different systems so it can be used together. | 5.6 · <a class="pageref" href="#s5-6"></a> |
| **Data lake** | Cheap storage (such as Amazon S3) for raw data in any format; structure is applied when the data is read. | 4.7 · <a class="pageref" href="#s4-7"></a> |
| **Data lakehouse** | A data lake with warehouse features (ACID tables, schemas, fast SQL) through Delta Lake, Iceberg or Hudi. | 4.7 · <a class="pageref" href="#s4-7"></a> |
| **Data lineage** | Where data came from and every step that changed it on the way. | 7.3 · <a class="pageref" href="#s7-3"></a> |
| **Data mart** | A smaller slice of the warehouse focused on one department, such as sales or finance. | 2.7 · <a class="pageref" href="#s2-7"></a> |
| **Data mesh** | Decentralized ownership: business domains own and publish their data as products on a shared self-serve platform. | 7.1 · <a class="pageref" href="#s7-1"></a> |
| **Data model** | A description of data, its structure and relationships, at conceptual, logical and physical levels. | 2.1 · <a class="pageref" href="#s2-1"></a> |
| **Data pipeline** | An automated series of steps that moves data from sources, transforms it and delivers it to targets. | 6.5 · <a class="pageref" href="#s6-5"></a> |
| **Data quality** | How accurate, complete, consistent, timely, valid and unique the data is. | 5.6 · <a class="pageref" href="#s5-6"></a> |
| **Data warehouse** | A central analytical database, organized into facts and dimensions for reporting. | 2.7 · <a class="pageref" href="#s2-7"></a> |
| **DBMS / RDBMS** | Software that stores and manages data; an RDBMS keeps it in related tables queried with SQL. | 1.0 · <a class="pageref" href="#s1-0"></a> |
| **DCL** | Data Control Language: `GRANT` and `REVOKE` permissions. | 3.4 · <a class="pageref" href="#s3-4"></a> |
| **DDL** | Data Definition Language: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`. | 3.3 · <a class="pageref" href="#s3-3"></a> |
| **Dead-letter queue (DLQ)** | Where messages that keep failing are parked for inspection instead of blocking the queue. | 6.3 · <a class="pageref" href="#s6-3"></a> |
| **Deadlock** | Two transactions each waiting for a lock the other holds; the database aborts one of them. | 3.10 · <a class="pageref" href="#s3-10"></a> |
| **Denormalization** | Deliberately storing redundant data to make reads faster, accepting extra work on writes. | 2.6 · <a class="pageref" href="#s2-6"></a> |
| **Derived table** | A subquery in `FROM` that is used like a table. | 3.7 · <a class="pageref" href="#s3-7"></a> |
| **Dimension table** | Descriptive context in a warehouse: who, what, where and when (customer, product, date). | 2.7 · <a class="pageref" href="#s2-7"></a> |
| **DML** | Data Manipulation Language: `INSERT`, `UPDATE`, `DELETE`. | 3.4 · <a class="pageref" href="#s3-4"></a> |
| **Document database** | Stores self-contained, JSON-like documents (MongoDB). | 4.2 · <a class="pageref" href="#s4-2"></a> |

<p class="glossletter">E</p>

| Term | Plain meaning | Session |
|---|---|---|
| **ELT** | Extract, Load, Transform: load raw data first, then transform it inside the warehouse with SQL (often dbt). | 6.6 · <a class="pageref" href="#s6-6"></a> |
| **Embedding (AI)** | A list of numbers that captures the meaning of a text or image, so similar items end up close together. | 7.3 · <a class="pageref" href="#s7-3"></a> |
| **Embedding (data modeling)** | Storing related data inside the parent document so it is read in one go. The alternative is referencing. | 2.8 · <a class="pageref" href="#s2-8"></a> |
| **Entity** | A thing the business stores data about, such as a customer or an order; it usually becomes a table. | 2.2 · <a class="pageref" href="#s2-2"></a> |
| **ER diagram** | A diagram of entities, their attributes and the relationships between them. | 2.2 · <a class="pageref" href="#s2-2"></a> |
| **ESB** | Enterprise Service Bus: a central hub that routes and transforms messages between enterprise systems. | 6.1 · <a class="pageref" href="#s6-1"></a> |
| **ETL** | Extract, Transform, Load: transform data in a separate engine before loading it into the target. | 6.6 · <a class="pageref" href="#s6-6"></a> |
| **Event** | A fact that something happened, named in the past tense (`OrderPlaced`). | 6.4 · <a class="pageref" href="#s6-4"></a> |
| **Event-driven architecture** | Services publish events and others react to them, without calling each other directly. | 6.4 · <a class="pageref" href="#s6-4"></a> |
| **Eventual consistency** | Replicas may differ for a short time but converge once writes stop. | 4.3 · <a class="pageref" href="#s4-3"></a> |
| **EXPLAIN / EXPLAIN ANALYZE** | Shows the plan PostgreSQL chooses for a query (scans, joins, costs); `ANALYZE` also runs it and reports real times. | 3.9 · <a class="pageref" href="#s3-9"></a> |

<p class="glossletter">F–G</p>

| Term | Plain meaning | Session |
|---|---|---|
| **Fact table** | Numeric measures of business events at a defined grain, such as one row per order line. | 2.7 · <a class="pageref" href="#s2-7"></a> |
| **Failover** | Switching to a standby server when the primary fails. | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **Foreign key** | A column that references a primary key in another table, so every value must exist there. | 2.3 · <a class="pageref" href="#s2-3"></a> |
| **Functional dependency** | A → B: knowing A determines B (`emp_id` determines `emp_name`). | 2.5 · <a class="pageref" href="#s2-5"></a> |
| **Grain** | Exactly what one row of a fact table represents. Decide it before anything else. | 2.7 · <a class="pageref" href="#s2-7"></a> |
| **GROUP BY** | Collapses rows that share values into one row per group, for aggregation. | 3.5 · <a class="pageref" href="#s3-5"></a> |

<p class="glossletter">H</p>

| Term | Plain meaning | Session |
|---|---|---|
| **HAVING** | Filters groups after `GROUP BY`; unlike `WHERE`, it can use aggregates. | 3.5 · <a class="pageref" href="#s3-5"></a> |
| **High availability (HA)** | Keeping a service running through failures: standbys in other availability zones plus automatic failover. | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **Horizontal scaling** | Adding more machines (scaling out). | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **HTTP** | The request/response protocol of the web: a method, URL, headers and body go out; a status code and body come back. | 5.2 · <a class="pageref" href="#s5-2"></a> |

<p class="glossletter">I</p>

| Term | Plain meaning | Session |
|---|---|---|
| **Idempotency** | Repeating an operation has the same effect as doing it once (PUT, DELETE). | 5.2 · <a class="pageref" href="#s5-2"></a> |
| **Idempotency key** | A unique ID sent with a request so the server can recognize a retry and not repeat the action. | 5.5 · <a class="pageref" href="#s5-5"></a> |
| **Incremental load** | Loading only rows that are new or changed since the last run, tracked with a watermark or CDC. | 5.6 · <a class="pageref" href="#s5-6"></a> |
| **Index** | A separate, sorted structure that finds rows without scanning the whole table. Faster reads, slower writes. | 3.9 · <a class="pageref" href="#s3-9"></a> |
| **iPaaS** | Integration Platform as a Service: cloud tools with ready-made connectors (MuleSoft, Boomi, Azure Logic Apps). | 6.1 · <a class="pageref" href="#s6-1"></a> |
| **Isolation level** | How much concurrent transactions see of each other: Read Uncommitted, Read Committed, Repeatable Read, Serializable. | 3.10 · <a class="pageref" href="#s3-10"></a> |

<p class="glossletter">J–K</p>

| Term | Plain meaning | Session |
|---|---|---|
| **JOIN** | Combines rows from two tables using a related column. | 3.6 · <a class="pageref" href="#s3-6"></a> |
| **JSON** | A text format for structured data built from objects, arrays, strings, numbers, booleans and null. | 5.2 · <a class="pageref" href="#s5-2"></a> |
| **JSONB** | PostgreSQL's binary JSON type, which can be indexed and queried. | 4.2 · <a class="pageref" href="#s4-2"></a> |
| **JWT** | JSON Web Token: a signed (not encrypted) token carrying claims such as user ID, role and expiry. | 5.4 · <a class="pageref" href="#s5-4"></a> |
| **Kafka** | A distributed, durable event log: topics split into partitions, read by consumer groups at their own offsets. | 6.7 · <a class="pageref" href="#s6-7"></a> |
| **Key-value store** | Stores a value under a key and fetches it extremely fast (Redis, DynamoDB). | 4.2 · <a class="pageref" href="#s4-2"></a> |

<p class="glossletter">L</p>

| Term | Plain meaning | Session |
|---|---|---|
| **LAG / LEAD** | Window functions that read a value from the previous / next row. | 3.8 · <a class="pageref" href="#s3-8"></a> |
| **LEFT JOIN** | All rows from the left table, with the matching right rows or NULLs. | 3.6 · <a class="pageref" href="#s3-6"></a> |
| **Leftmost-prefix rule** | A composite index on `(a, b)` helps filters on `a`, or on `a` and `b`, but not on `b` alone. | 3.9 · <a class="pageref" href="#s3-9"></a> |
| **Lock** | Prevents conflicting changes to the same data at the same time; `SELECT … FOR UPDATE` locks rows. | 3.10 · <a class="pageref" href="#s3-10"></a> |

<p class="glossletter">M</p>

| Term | Plain meaning | Session |
|---|---|---|
| **Managed database** | A cloud database where the provider handles servers, patching, backups and failover (RDS, Cloud SQL). | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **Materialized view** | A query result stored like a table and refreshed when needed. | 2.6 · <a class="pageref" href="#s2-6"></a> |
| **Message broker** | The server that stores and routes messages (RabbitMQ, Kafka, Amazon SQS). | 6.3 · <a class="pageref" href="#s6-3"></a> |
| **Message queue** | Point-to-point messaging: each message is handled by one consumer. | 6.3 · <a class="pageref" href="#s6-3"></a> |
| **Microservices** | An application split into small services that each own their data and are deployed independently. | 1.1 · <a class="pageref" href="#s1-1"></a> |
| **Modern data stack** | Cloud tools that each do one job: ingestion (Fivetran), warehouse (Snowflake, BigQuery), transformation (dbt), BI. | 7.4 · <a class="pageref" href="#s7-4"></a> |
| **MVCC** | Multi-Version Concurrency Control: each transaction reads a snapshot, so readers and writers don't block each other. | 3.10 · <a class="pageref" href="#s3-10"></a> |

<p class="glossletter">N</p>

| Term | Plain meaning | Session |
|---|---|---|
| **Normal forms** | 1NF: atomic values. 2NF: no dependency on part of a composite key. 3NF: no dependency between non-key columns. | 2.5 · <a class="pageref" href="#s2-5"></a> |
| **Normalization** | Splitting data into well-structured tables so each fact is stored once, removing anomalies. | 2.5 · <a class="pageref" href="#s2-5"></a> |
| **NoSQL** | Non-relational databases: document, key-value, wide-column and graph. | 4.2 · <a class="pageref" href="#s4-2"></a> |
| **NULL** | A missing or unknown value. Not zero and not an empty string; test it with `IS NULL`. | 3.2 · <a class="pageref" href="#s3-2"></a> |

<p class="glossletter">O</p>

| Term | Plain meaning | Session |
|---|---|---|
| **OAuth 2.0** | A standard for delegated access: an app gets a limited token to act for you without seeing your password. | 5.4 · <a class="pageref" href="#s5-4"></a> |
| **ObjectId** | MongoDB's default 12-byte `_id` value, roughly ordered by creation time. | 4.4 · <a class="pageref" href="#s4-4"></a> |
| **OLAP** | Online Analytical Processing: large, read-heavy queries for analysis and reporting. | 1.3 · <a class="pageref" href="#s1-3"></a> |
| **OLTP** | Online Transaction Processing: many small, fast reads and writes that run the business. | 1.3 · <a class="pageref" href="#s1-3"></a> |
| **OpenID Connect (OIDC)** | An identity layer on top of OAuth 2.0 that powers "Log in with Google / Microsoft". | 5.4 · <a class="pageref" href="#s5-4"></a> |
| **Orchestration** | Scheduling and coordinating pipeline tasks and their dependencies as a DAG (Apache Airflow, Azure Data Factory). | 6.5 · <a class="pageref" href="#s6-5"></a> |
| **Outbox pattern** | Write the business change and the event to an outbox table in one transaction, then publish from the outbox. | 6.4 · <a class="pageref" href="#s6-4"></a> |

<p class="glossletter">P–Q</p>

| Term | Plain meaning | Session |
|---|---|---|
| **Pagination** | Returning results a page at a time: `LIMIT`/`OFFSET`, or faster keyset (cursor) pagination. | 5.3 · <a class="pageref" href="#s5-3"></a> |
| **Partition (Kafka)** | An ordered, append-only part of a topic; ordering is guaranteed only within one partition. | 6.7 · <a class="pageref" href="#s6-7"></a> |
| **Partitioning** | Splitting one large table into smaller pieces (by month, by region) inside one database. | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **PITR** | Point-in-time recovery: restoring a database to a chosen moment using backups plus logs. | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **Polyglot persistence** | Using different databases for different jobs within one system. | 1.3 · <a class="pageref" href="#s1-3"></a> |
| **Primary key** | The column(s) that uniquely identify each row: unique, not null, one per table. | 2.3 · <a class="pageref" href="#s2-3"></a> |
| **Publish/subscribe** | A publisher sends to a topic and every subscriber receives its own copy. | 6.3 · <a class="pageref" href="#s6-3"></a> |
| **PUT vs PATCH** | PUT replaces the whole resource and is idempotent; PATCH changes only the fields sent. | 5.2 · <a class="pageref" href="#s5-2"></a> |
| **Query optimizer** | The part of the database that decides how to run a query, using table statistics. | 3.9 · <a class="pageref" href="#s3-9"></a> |

<p class="glossletter">R</p>

| Term | Plain meaning | Session |
|---|---|---|
| **RAG** | Retrieval-Augmented Generation: retrieve relevant content first, then let the language model answer from it. | 7.3 · <a class="pageref" href="#s7-3"></a> |
| **Rate limiting** | Capping how many requests a client may make in a time window; extra requests get 429 Too Many Requests. | 5.3 · <a class="pageref" href="#s5-3"></a> |
| **RBAC / ABAC** | Role-based access control (permissions per role) / attribute-based (rules on user, resource and context). | 5.4 · <a class="pageref" href="#s5-4"></a> |
| **Read replica** | A copy of the database that serves read queries, spreading the read load. | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **Recursive CTE** | A CTE that refers to itself, used to walk hierarchies such as an org chart. | 3.7 · <a class="pageref" href="#s3-7"></a> |
| **Referential integrity** | Every foreign key value points to a row that exists. | 2.3 · <a class="pageref" href="#s2-3"></a> |
| **Replica set** | MongoDB's high-availability group: one primary and several secondaries, with automatic election. | 4.4 · <a class="pageref" href="#s4-4"></a> |
| **Replication** | Keeping copies of data on several servers: synchronous (no data loss) or asynchronous (faster, small lag). | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **REST** | An API style built on resources identified by URLs, standard HTTP methods and stateless requests. | 5.2 · <a class="pageref" href="#s5-2"></a> |
| **Reverse ETL** | Syncing modelled warehouse data back into operational tools such as a CRM. | 6.8 · <a class="pageref" href="#s6-8"></a> |
| **RPO / RTO** | Recovery Point Objective: how much data you can afford to lose. Recovery Time Objective: how long you can be down. | 4.1 · <a class="pageref" href="#s4-1"></a> |

<p class="glossletter">S</p>

| Term | Plain meaning | Session |
|---|---|---|
| **Saga** | A long business process made of local transactions, with compensating steps that undo earlier ones if a later step fails. | 6.4 · <a class="pageref" href="#s6-4"></a> |
| **SCD Type 2** | A slowly changing dimension that keeps history by adding a new row, with validity dates, for each change. | 2.7 · <a class="pageref" href="#s2-7"></a> |
| **Schema** | The structure of a database (tables, columns, types, constraints); in PostgreSQL also a namespace for tables. | 2.4 · <a class="pageref" href="#s2-4"></a> |
| **Schema-on-read / on-write** | Structure applied when data is read (lake) vs enforced when it is written (warehouse). | 4.7 · <a class="pageref" href="#s4-7"></a> |
| **Selectivity** | The fraction of rows a condition matches; an index helps when that fraction is small. | 3.9 · <a class="pageref" href="#s3-9"></a> |
| **Serverless** | Running code or databases without managing servers: automatic scaling, scale to zero, pay per use. | 7.2 · <a class="pageref" href="#s7-2"></a> |
| **Sharding** | Splitting data across several servers by a shard key. | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **Snowflake schema** | A star schema whose dimensions are normalized into more tables. | 2.7 · <a class="pageref" href="#s2-7"></a> |
| **SQL injection** | An attack where user input is executed as SQL; prevented with parameterized queries. | 5.4 · <a class="pageref" href="#s5-4"></a> |
| **Star schema** | One fact table surrounded by denormalized dimension tables. | 2.7 · <a class="pageref" href="#s2-7"></a> |
| **Stateless** | Each request carries everything needed; the server keeps no session memory between requests. | 5.2 · <a class="pageref" href="#s5-2"></a> |
| **Status code** | The HTTP result: 2xx success, 3xx redirect, 4xx client error, 5xx server error. | 5.2 · <a class="pageref" href="#s5-2"></a> |
| **Stream processing** | Processing events continuously as they arrive, typically within seconds. | 6.7 · <a class="pageref" href="#s6-7"></a> |
| **Subquery** | A query nested inside another query. | 3.7 · <a class="pageref" href="#s3-7"></a> |
| **Surrogate key** | An artificial key with no business meaning, such as an auto-generated ID. | 2.3 · <a class="pageref" href="#s2-3"></a> |

<p class="glossletter">T–V</p>

| Term | Plain meaning | Session |
|---|---|---|
| **TCL** | Transaction Control Language: `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`. | 3.4 · <a class="pageref" href="#s3-4"></a> |
| **Topic** | A named stream of messages or events that subscribers or consumer groups read. | 6.3 · <a class="pageref" href="#s6-3"></a> |
| **Transaction** | A group of operations that succeed or fail as one unit. | 3.10 · <a class="pageref" href="#s3-10"></a> |
| **TRUNCATE** | Removes all rows from a table at once; much faster than `DELETE`, but takes no `WHERE`. | 3.3 · <a class="pageref" href="#s3-3"></a> |
| **UNION / UNION ALL** | Stack the results of two queries; `UNION` removes duplicates, `UNION ALL` keeps them and is faster. | 3.6 · <a class="pageref" href="#s3-6"></a> |
| **UNIQUE constraint** | No two rows may share a value; NULLs are allowed (several of them, by default, in PostgreSQL). | 2.3 · <a class="pageref" href="#s2-3"></a> |
| **Upsert** | Insert a row, or update it if it already exists: `INSERT … ON CONFLICT … DO UPDATE` in PostgreSQL. | 3.4 · <a class="pageref" href="#s3-4"></a> |
| **Vector database** | Stores embeddings and quickly finds the most similar ones; used for semantic search and RAG. | 7.3 · <a class="pageref" href="#s7-3"></a> |
| **Vertical scaling** | Making one machine bigger: more CPU, memory or faster disks (scaling up). | 4.1 · <a class="pageref" href="#s4-1"></a> |
| **View** | A saved query that behaves like a virtual table. | 3.7 · <a class="pageref" href="#s3-7"></a> |

<p class="glossletter">W</p>

| Term | Plain meaning | Session |
|---|---|---|
| **Watermark** | In incremental loads, the highest `updated_at` or ID already loaded; in streaming, "all events up to time T have arrived". | 6.7 · <a class="pageref" href="#s6-7"></a> |
| **Webhook** | The provider calls your URL when an event happens, instead of you polling again and again. | 5.5 · <a class="pageref" href="#s5-5"></a> |
| **WHERE** | Filters rows before grouping; it cannot use aggregates. | 3.1 · <a class="pageref" href="#s3-1"></a> |
| **Wide-column store** | Rows with flexible columns grouped into column families, built for huge write volumes (Cassandra). | 4.2 · <a class="pageref" href="#s4-2"></a> |
| **Window (streaming)** | A time bucket for grouping events: tumbling (fixed), sliding (overlapping) or session (activity-based). | 6.7 · <a class="pageref" href="#s6-7"></a> |
| **Window function** | Computes a value across related rows (`OVER`, `PARTITION BY`) while keeping every row. | 3.8 · <a class="pageref" href="#s3-8"></a> |

:::

## Coverage Verification {: #coverage-check }

<p class="lead">Before this edition was produced, the handbook was checked against every point of the preparation brief. This table records where each requirement is met, so you can verify it yourself.</p>

::: covcheck
<p class="tablecap">Self-review against the brief</p>

| Check | Where it is met | Page |
|---|---|---|
| All 7 modules included | Parts I–VII, one per course module, each opening with a Course Coverage box | <a class="pageref" href="#m1"></a> |
| Every visible course session included | the Course Coverage Map lists every session and topic from the brief and links it to a handbook session (titles marked † were rebuilt from topic lists) | <a class="pageref" href="#coverage-map"></a> |
| Every identifiable subtopic included | each module's Course Coverage box lists its subtopics with the session that teaches them | <a class="pageref" href="#coverage-map"></a> |
| SQL covered deeply | Module 3: 13 sessions from SELECT to transactions, 22 interview patterns, every output produced by PostgreSQL | <a class="pageref" href="#m3"></a> |
| SQL interview problems | Session 3.11 (22 patterns: approach, solution, mistakes, variations) and the Top 50 SQL bank | <a class="pageref" href="#s3-11"></a> |
| Database fundamentals covered | DBMS basics (1.0), DDL/DML (3.3–3.4), indexes (3.9), transactions and ACID (3.10), Top Database Questions | <a class="pageref" href="#s1-0"></a> |
| Data modeling covered | Module 2: ER modeling, keys, normalization to BCNF, denormalization, star/snowflake, SCD, NoSQL modeling | <a class="pageref" href="#m2"></a> |
| MongoDB covered | Sessions 4.4–4.6: concepts, CRUD, indexes, aggregation, modeling, SQL-to-MongoDB translation | <a class="pageref" href="#s4-4"></a> |
| Cloud database concepts covered | Session 4.1: managed and serverless databases, scaling, replication, failover, backups, RPO/RTO | <a class="pageref" href="#s4-1"></a> |
| APIs covered | Sessions 5.1–5.5: HTTP, REST, status codes, API design, security, reliability | <a class="pageref" href="#s5-1"></a> |
| Data integration covered | Sessions 1.2 and 5.6 (approaches, CDC, incremental loads, data quality); pipelines and ETL/ELT in 6.5–6.6 | <a class="pageref" href="#s5-6"></a> |
| Enterprise integration covered | Module 6: integration styles, sync vs async, messaging, EDA, streaming, Salesforce → warehouse, pattern choice | <a class="pageref" href="#m6"></a> |
| Modern data systems covered | Module 1 (data systems, OLTP vs OLAP) and Module 7 (data mesh, serverless, AI, cloud-native, distributed systems) | <a class="pageref" href="#m7"></a> |
| Interview questions for every major session | every teaching session ends with Interview Questions in four groups (Basic, Intermediate, Scenario-based, Follow-up/Trap) with model answers | <a class="pageref" href="#session-structure"></a> |
| Practice questions at three levels | 20 Practice Question sets (Levels 1–3) at the end of the important topic groups, each followed by a separate Answer / Explanation box | <a class="pageref" href="#session-structure"></a> |
| PwC interview orientation included | PwC Interview Orientation, keeping common, reported, likely and recommended information separate; PwC Interview Angle boxes | <a class="pageref" href="#pwc"></a> |
| Common traps included | a Common Traps & Mistakes box in every teaching session (Session 3.11 lists mistakes per pattern), trap questions in every question set, Traps at a Glance | <a class="pageref" href="#f7"></a> |
| Comparison tables included | for example OLTP vs OLAP, PK vs UNIQUE, WHERE vs HAVING, SQL vs NoSQL, PUT vs PATCH, ETL vs ELT, queue vs pub/sub | <a class="pageref" href="#s1-3"></a> |
| Practical examples included | one realistic sample database used throughout, worked examples, a food-delivery case study and a project map | <a class="pageref" href="#s3-0"></a> |
| Final revision section included | 100 Most Important Questions, Top 50 SQL, database, scenario and rapid-fire questions | <a class="pageref" href="#final"></a> |
| One-day revision sheet included | One-Day Revision Sheet, with SQL templates and traps | <a class="pageref" href="#f7"></a> |
| Project connection and answering strategy | how to map concepts onto your own project; the five-step answer, STAR, PwC Professional | <a class="pageref" href="#f6"></a> |
| No major interview topic omitted | gaps in the course are filled with labelled Interview Extension material (set operations, ROLLUP, SCD, MVCC, locks, circuit breakers, RabbitMQ vs Kafka and more) | <a class="pageref" href="#labels"></a> |
| No unexplained jargon | terms are explained where they first appear and again in this Glossary | <a class="pageref" href="#glossary"></a> |
| No unnecessary filler | every session follows the same short pattern; module summaries fit on one or two pages | <a class="pageref" href="#session-structure"></a> |
:::

### How the content was verified

- **SQL:** every query with an *Output* panel was executed against PostgreSQL while the PDF was built, using the sample database from Session 3.0. The outputs are copied from the database, not typed by hand, so a query that failed would have stopped the build.
- **MongoDB:** no MongoDB server was used. The shell examples were checked for valid syntax automatically, and their outputs were traced by hand against the sample documents shown with them.
- **Python:** every Python example was compiled during the build to catch syntax errors.
- **PwC information:** only publicly available, reported information was used. It is labelled [REPORTED] and kept separate from general advice; nothing in this handbook is an official PwC question list.
- **Course structure:** see "About the Source Material". Session titles marked † were reconstructed from the module topic lists because the course screenshots were not available.
