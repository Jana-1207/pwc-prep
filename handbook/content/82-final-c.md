## Top Database Questions {: #f3 }

<p class="lead">Conceptual DBMS questions that go one level deeper than the 100 above, including a few classic topics outside the course (marked [INTERVIEW EXTENSION]) that interviewers still like to ask.</p>

::: questions Database Theory Drill
#### Keys, constraints and design
Q: [DEFINITION] What is a candidate key? Can a table have several?
A: A minimal set of columns that uniquely identifies rows. Yes: e.g. emp_id, email and PAN can all be candidate keys; one becomes the primary key, the others alternate keys.

Q: [DEFINITION] What is a self-referencing foreign key?
A: A foreign key pointing to the same table's primary key, e.g. `employees.manager_id → employees.emp_id`, used for hierarchies.

Q: [HOW] What happens if you update a primary key value that other tables reference?
A: By default the update is rejected while references exist. With `ON UPDATE CASCADE` the change propagates to the foreign keys. Stable surrogate keys avoid the issue altogether.

Q: [COMPARISON] UNIQUE constraint vs unique index?
A: A UNIQUE constraint is a declared rule (part of the table's design) that the database enforces using a unique index it creates. You can also create unique indexes directly, including partial or expression ones, e.g. `UNIQUE (LOWER(email))`.

Q: [WHY] Why use a composite primary key in a junction table instead of a surrogate ID?
A: The pair (student_id, course_id) is the natural identity and prevents duplicate enrollments automatically. Some teams add a surrogate ID anyway (for ORMs) plus a UNIQUE constraint on the pair.

#### Querying
Q: [COMPARISON] UNION vs UNION ALL?
A: Both stack the rows of two queries with the same columns. UNION removes duplicate rows (an extra sort or hash step); UNION ALL keeps all rows and is faster. Use UNION ALL unless you need de-duplication. Session 3.6 shows both, with INTERSECT and EXCEPT.

Q: [COMPARISON] JOIN vs UNION?
A: A JOIN combines columns from tables side by side, matching rows; a UNION stacks rows from compatible queries one under the other.

Q: [COMPARISON] COALESCE vs NVL / ISNULL / IFNULL?
A: All replace NULLs. COALESCE is standard SQL and takes any number of arguments; NVL (Oracle), ISNULL (SQL Server) and IFNULL (MySQL) are vendor versions with two arguments.

Q: [DEFINITION] What is an execution plan?
A: The optimizer's chosen strategy for a query (scan types, join methods, order), shown by `EXPLAIN`; `EXPLAIN ANALYZE` runs the query and shows actual rows and timings.

Q: [DEFINITION] What is the N+1 query problem?
A: Loading a list (1 query) and then running one extra query per item (N queries) to fetch related data, typical with ORMs. Fix it with joins or batch fetching (JOIN FETCH, eager loading, IN lists).

#### Programs inside the database [INTERVIEW EXTENSION]
Q: [COMPARISON] Stored procedure vs function?
A: Both are code stored in the database. A function returns a value (or a table) and can be used inside SELECT; a procedure is called on its own (`CALL`), can manage transactions (in PostgreSQL 11+), and doesn't have to return anything.

Q: [DEFINITION] What is a trigger, and when is it risky?
A: Code that runs automatically on INSERT, UPDATE or DELETE (before or after). It is useful for audit logs and keeping derived data in sync, but risky because it hides logic, can slow writes, and can cascade unexpectedly.

Q: [DEFINITION] What is a cursor?
A: A database object for processing a query's result row by row. It is usually slower than set-based SQL; prefer single set-based statements where possible.

#### Internals
Q: [DEFINITION] What is the write-ahead log (WAL)?
A: A sequential log where changes are recorded before they are applied to data files; it provides durability and crash recovery and feeds replication and point-in-time recovery.

Q: [DEFINITION] What is MVCC and why does PostgreSQL need VACUUM?
A: Multi-Version Concurrency Control keeps old row versions so readers see a consistent snapshot without blocking writers. VACUUM removes versions no transaction can see any more and reclaims space (autovacuum does this automatically).

Q: [COMPARISON] Optimistic vs pessimistic locking?
A: Pessimistic locks data before changing it (`SELECT … FOR UPDATE`), which suits high contention. Optimistic checks at write time that nothing changed (a version column), which suits low contention and web apps.

Q: [COMPARISON] Row-level vs table-level locks?
A: Row locks block only the affected rows, allowing high concurrency; table locks block the whole table (some DDL, LOCK TABLE) and should be rare and short.

Q: [DEFINITION] What is table partitioning?
A: Splitting one logical table into physical pieces (by range, list or hash), e.g. orders per month, so queries scan fewer rows and old data can be dropped or archived cheaply.

Q: [DEFINITION] What is connection pooling and why is it needed?
A: Reusing a set of open database connections across requests (HikariCP, PgBouncer), because opening connections is slow and databases support only a limited number.

Q: [DEFINITION] What is the system catalog / information_schema?
A: Built-in tables and views describing the database itself (tables, columns, types, constraints, indexes), queried for metadata.
:::

The trigger idea from Session 2.6, keeping a denormalized total in sync, as a working PostgreSQL example:

```sql run
CREATE FUNCTION refresh_order_total() RETURNS trigger AS $$
BEGIN
    UPDATE orders
    SET total_amount = (SELECT COALESCE(SUM(quantity * unit_price), 0)
                        FROM order_items
                        WHERE order_id = NEW.order_id)
    WHERE order_id = NEW.order_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_items_total
AFTER INSERT OR UPDATE ON order_items
FOR EACH ROW EXECUTE FUNCTION refresh_order_total();

INSERT INTO order_items VALUES (102, 7, 2, 149.00);    -- add two pens to order 102

SELECT order_id, total_amount FROM orders WHERE order_id = 102;
```

::: linebyline
| Part | What it does |
|---|---|
| `CREATE FUNCTION refresh_order_total() RETURNS trigger` | a PL/pgSQL function meant to be called by a trigger |
| `UPDATE orders SET total_amount = (SELECT … SUM(quantity * unit_price) …)` | recompute the order's total from its lines |
| `NEW.order_id` | the order_items row being inserted or updated |
| `CREATE TRIGGER … AFTER INSERT OR UPDATE ON order_items FOR EACH ROW` | run the function after every inserted or changed line |
| `INSERT … (102, 7, 2, 149.00)` | adds 2 × ₹149 to order 102, so its total goes from 3499 to 3797 automatically |
:::

A complete version would also handle DELETE (using `OLD.order_id`). In many teams this logic lives in the application instead, which is easier to test and see.

## Top Scenario Questions {: #f4 }

<p class="lead">Scenario questions test judgement. A strong answer has three parts: <strong>clarify</strong> (ask one or two key questions), <strong>propose</strong> (a concrete design), and <strong>justify</strong> (trade-offs and what you would watch). The answers below follow that shape.</p>

::: questions Scenario Drill
Q: [SCENARIO] You have 10 million customer records. How would you design the database?
A: *Clarify:* read/write mix, query patterns (lookup by email? search by city?), growth, retention needs.

*Propose:* a relational table with a surrogate `BIGINT` primary key; UNIQUE on email (normalized to lower case); a separate `customer_addresses` table (1:N); correct types (`TIMESTAMPTZ`, `NUMERIC` for money); indexes on the columns used in filters and joins; audit columns.

*Justify:* 10 million rows is comfortable for PostgreSQL on a single primary with indexes. Add read replicas or caching for heavy reads, partition only if there is a natural key (e.g. by region or date) and very large growth, and move analytics to a warehouse.

Q: [SCENARIO] Reads are much more frequent than writes. What would you consider?
A: Caching (Redis, cache-aside) for hot data; read replicas for read-only queries; covering and composite indexes for the top queries; denormalized read models or materialized views for expensive aggregations; a CDN for static content; pagination. Watch for replication lag and cache invalidation, and keep writes on the primary.

Q: [SCENARIO] You need real-time processing. What architecture would you consider?
A: *Clarify:* how real-time (seconds? sub-second?), volume, and what action follows.

*Propose:* producers publish events to Kafka, Kinesis or Event Hubs (partitioned by entity key); a stream processor (Flink or Spark Structured Streaming) does windowed or stateful computations; results go to a low-latency store (Redis, a real-time OLAP store) and alerts to a topic; raw events go to the lake for replay and analytics.

*Justify:* it decouples producers, scales horizontally and replays history. The costs are complexity and always-on infrastructure, so I'd confirm that micro-batch every few minutes isn't enough first.

Q: [SCENARIO] You need flexible schemas. Would you use SQL or NoSQL?
A: It depends on how much of the data is flexible. If most entities are relational (orders, payments) and only some attributes vary (product specs), use PostgreSQL with a JSONB column: you keep ACID and joins and gain flexibility. If the whole domain is document-shaped, read by key and needs scale-out (catalogue, content), MongoDB fits. Either way, validate the schema in the application or with JSON schema rules.

Q: [SCENARIO] A query that used to take 1 second now takes 30 seconds. How do you troubleshoot?
A: Reproduce it with `EXPLAIN ANALYZE`; compare the plan with the old one (seq scan instead of index? bad row estimates?); check data growth and stale statistics (`ANALYZE`); check for missing or unused indexes, functions on indexed columns and implicit casts; look for locks or blocking sessions and resource saturation (CPU, I/O); check recent deployments or parameter changes. Fix the root cause (index, rewrite, statistics, partitioning) and add monitoring.

Q: [DESIGN QUESTION] Design the core tables for a food-delivery app.
A: `customers`, `addresses` (1:N), `restaurants`, `menu_items` (N:1 restaurant), `orders` (customer, restaurant, address, status, timestamps, totals), `order_items` (order, menu item, qty, price at the time of order), `riders`, `deliveries` (order, rider, pickup/drop times, status), `payments` (order, amount, provider reference, idempotency key UNIQUE). Index the FKs and status/time columns; keep live rider locations in Redis; send events to Kafka; analytics in a warehouse.

Q: [SCENARIO] Prevent overselling the last item during a flash sale.
A: Make the stock decrement atomic and conditional: `UPDATE inventory SET stock = stock - 1 WHERE product_id = ? AND stock > 0` and treat 0 rows updated as sold out. Alternatively, reserve stock in Redis with atomic decrements and confirm in the database. Use a queue to smooth the order burst, idempotency keys for retries, and a CHECK (stock >= 0) as the safety net.

Q: [DESIGN QUESTION] Design a hospital appointment booking API.
A: Endpoints: `GET /doctors?speciality=…`, `GET /doctors/{id}/slots?date=…`, `POST /appointments` (patient, slot), `PATCH /appointments/{id}` (reschedule), `DELETE /appointments/{id}` (cancel). Data: doctors, slots (doctor_id, start_time, UNIQUE(doctor_id, start_time)), appointments (slot_id UNIQUE, patient_id, status). Concurrency: the unique constraint on slot_id, or a conditional update, prevents double booking (409 Conflict). Auth: patients see only their own appointments (ownership check). Notifications run asynchronously through a queue.

Q: [SCENARIO] Sales numbers differ between the CRM and the warehouse. How do you reconcile?
A: Define the metric precisely on both sides (filters, stages, currency, time zone); compare counts and sums by day to find where they diverge; check incremental-load watermarks, deleted or merged records and duplicates; fix the pipeline or the definitions; then add an automated reconciliation check with alerts.

Q: [SCENARIO] A payment gateway fails intermittently. What do you do?
A: Timeouts on every call; retries with exponential backoff and jitter on transient errors only; an idempotency key per payment attempt; a circuit breaker to fail fast during outages; show "payment pending" instead of encouraging double clicks; confirm final status via webhook or status polling; a nightly reconciliation with the gateway's settlement report.

Q: [DESIGN QUESTION] Daily sales from 5 regional databases must appear in one report by 8 AM.
A: A nightly orchestrated ELT: incremental extracts by `updated_at` (or CDC) from each region into warehouse staging tables tagged with region; transform with SQL/dbt into a unified fact table (standard currency and time zone); quality checks (row counts per region, totals); refresh BI by 7:30; alert on late or failed regions, and show "data as of" on the report.

Q: [SCENARIO] You must keep 7 years of transactions cheaply but query the last 3 months fast.
A: Partition by month; keep recent partitions on fast storage with indexes; archive older partitions to cheaper storage or the data lake (Parquet) while keeping them queryable through the warehouse or an external table; drop or archive by partition instead of running massive DELETEs; apply retention policies that meet regulatory requirements.

Q: [SCENARIO] A customer requests deletion of their personal data under privacy law (India's DPDP Act / GDPR).
A: Find the data through the catalogue and lineage (operational DBs, warehouse, lake, backups, third parties); delete or anonymise according to the retention rules (some financial records must be kept); propagate deletes through pipelines (CDC handles deletes); record the action for audit; design for this up front with customer IDs, PII tagging and masking.

Q: [SCENARIO] The nightly ETL failed halfway. How do you recover?
A: Check logs to find the failed step and cause; fix it; re-run from the failed step. This is safe only if the steps are idempotent (upserts or partition overwrite, watermark advanced only after success). Validate row counts and totals afterwards, communicate any delay, and add alerts or tests to catch the cause next time.

Q: [SCENARIO] A dashboard must show data no older than 5 minutes.
A: CDC or event streaming from the source into a micro-batch (1–5 minute) pipeline or a streaming table; incremental models; a fast serving layer; freshness monitoring with alerts; and a "last updated" timestamp shown on the dashboard.

Q: [DESIGN QUESTION] Choose a database for a chat application.
A: Messages are huge in volume, append-heavy and read by conversation and time, which suits a wide-column store (Cassandra/ScyllaDB) partitioned by conversation_id and sorted by time, or a well-partitioned relational design at smaller scale. Users, contacts and billing stay relational; online presence in Redis; media in object storage.

Q: [SCENARIO] A table has grown to 1 billion rows and queries are slow. What can you do?
A: Make sure queries use selective indexes; partition by time or key so queries prune partitions; archive cold data; pre-aggregate with summary tables or materialized views; move analytics to a columnar warehouse; consider sharding or distributed SQL only if a single node truly can't cope.

Q: [SCENARIO] A client says "we want to use AI on our data". What are your first steps?
A: Clarify the business problem and the success metric; inventory the relevant data, its quality and ownership; check privacy, consent and access rules; establish a governed, documented data foundation (catalogue, lineage, quality checks); start with a small pilot (a RAG assistant on a curated document set, or one predictive use case) with an evaluation plan, then iterate.

Q: [DESIGN QUESTION] Design login for a new web and mobile app.
A: Use an identity provider (Cognito, Azure Entra ID, Auth0) or OAuth 2.0 / OpenID Connect with social logins; MFA or OTP; short-lived access tokens (JWT) plus refresh tokens; HTTPS only; passwords hashed with bcrypt or Argon2 if you store them; rate limiting and lockouts; RBAC claims in the token; ownership checks in every API.
:::

## Rapid-Fire Questions {: #f5 }

<p class="lead">One-line answers for quick recall. Cover the right column and test yourself.</p>

<p class="tablecap">SQL</p>

| Question | Answer |
|---|---|
| What does SQL stand for? | Structured Query Language |
| Clause to filter groups? | HAVING |
| Clause to filter rows? | WHERE |
| Remove duplicate rows from a result? | DISTINCT |
| Default sort order? | ascending (ASC) |
| Is `BETWEEN` inclusive? | yes, at both ends |
| Wildcard for any number of characters in LIKE? | `%` |
| Wildcard for exactly one character? | `_` |
| Test for missing values? | `IS NULL` / `IS NOT NULL` |
| First non-NULL value? | `COALESCE()` |
| Count rows including NULLs? | `COUNT(*)` |
| Join that returns every combination? | CROSS JOIN |
| Join keeping all rows of the left table? | LEFT JOIN |
| UNION vs UNION ALL? | UNION removes duplicates; UNION ALL keeps them (faster) |
| Ranking with no gaps after ties? | DENSE_RANK |
| Previous row's value? | LAG |
| Next row's value? | LEAD |
| Keyword to define a CTE? | WITH |
| Can a window function be used in WHERE? | no; use a subquery or CTE |
| `5/2` in PostgreSQL? | 2 (integer division) |

<p class="tablecap">DBMS and data modeling</p>

| Question | Answer |
|---|---|
| ACID? | Atomicity, Consistency, Isolation, Durability |
| PostgreSQL's default isolation level? | Read Committed |
| How many primary keys per table? | one (can be composite) |
| Can a foreign key be NULL? | yes, unless declared NOT NULL |
| Does UNIQUE allow NULLs (PostgreSQL)? | yes, multiple |
| Default index type? | B-tree |
| Does PostgreSQL auto-index foreign keys? | no |
| Is TRUNCATE DDL or DML? | DDL |
| Which removes the table structure? | DROP |
| 1NF in four words? | one value per cell |
| 2NF removes? | partial dependencies |
| 3NF removes? | transitive dependencies |
| Junction table is used for? | many-to-many relationships |
| Fact table holds? | measures + foreign keys |
| Dimension table holds? | descriptive context |
| Schema with normalized dimensions? | snowflake |
| SCD type that keeps full history? | Type 2 |
| OLTP or OLAP: monthly revenue report? | OLAP |

<p class="tablecap">NoSQL and MongoDB</p>

| Question | Answer |
|---|---|
| NoSQL stands for? | "Not only SQL" |
| Example key-value store? | Redis |
| Example wide-column store? | Cassandra |
| Example graph database? | Neo4j |
| CAP letters? | Consistency, Availability, Partition tolerance |
| BASE? | Basically Available, Soft state, Eventually consistent |
| MongoDB's storage format? | BSON |
| MongoDB equivalent of a table? | collection |
| MongoDB equivalent of a row? | document |
| Default primary key field in MongoDB? | `_id` |
| Update all matching documents? | `updateMany()` |
| Operator to increment a number? | `$inc` |
| Add to an array only if absent? | `$addToSet` |
| Join in MongoDB? | `$lookup` |
| Flatten an array in the pipeline? | `$unwind` |
| Maximum MongoDB document size? | 16 MB |

<p class="tablecap">APIs and integration</p>

| Question | Answer |
|---|---|
| REST stands for? | Representational State Transfer |
| Method to create a resource? | POST |
| Method for partial update? | PATCH |
| Is POST idempotent? | no |
| Is DELETE idempotent? | yes |
| Status for "created"? | 201 |
| Status for "no content"? | 204 |
| Not authenticated? | 401 |
| Authenticated but not allowed? | 403 |
| Rate limit exceeded? | 429 |
| Service temporarily unavailable? | 503 |
| JWT has how many parts? | three: header, payload, signature |
| Is a JWT encrypted? | no, signed (payload is readable) |
| OAuth 2.0 is mainly for? | delegated authorization |
| Retry strategy with growing waits? | exponential backoff (+ jitter) |
| Key that makes POST retries safe? | idempotency key |
| Server calling you when an event happens? | webhook |
| Queue vs topic? | one consumer per message vs every subscriber |
| Undeliverable messages go to? | a dead-letter queue |
| CDC stands for? | Change Data Capture |

<p class="tablecap">Cloud, data engineering and trends</p>

| Question | Answer |
|---|---|
| ETL order? | Extract → Transform → Load |
| ELT transforms where? | inside the warehouse |
| Batch or streaming for fraud detection? | streaming |
| Kafka ordering is guaranteed within? | a partition |
| Raw data, any format, schema-on-read? | data lake |
| Curated, modelled, schema-on-write? | data warehouse |
| Lake + ACID tables? | lakehouse (Delta / Iceberg / Hudi) |
| Columnar file format for lakes? | Parquet |
| RPO measures? | acceptable data loss |
| RTO measures? | acceptable downtime |
| Is replication a backup? | no |
| Scale up = ? | vertical scaling |
| Scale out = ? | horizontal scaling |
| Delay when a serverless function starts fresh? | cold start |
| Four data mesh principles? | domain ownership, data as a product, self-serve platform, federated governance |
| "Garbage in, garbage out" applies to? | AI and analytics: output quality depends on data quality |
| RAG stands for? | Retrieval-Augmented Generation |
