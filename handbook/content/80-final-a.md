# Final Interview Revision {: .part #final data-label="FINAL REVISION KIT" }

<p class="lead">Everything you need in the last days before the interview: the 100 most important questions across the whole course, a 50-question SQL bank with verified solutions, the top database and scenario questions, rapid-fire drills, how to connect concepts to your project, a one-day revision sheet, and a strategy for answering well.</p>

| Section | Use it for | Time |
|---|---|---|
| 100 Most Important Questions | a full sweep of the course; say each answer aloud | 2–3 hours |
| SQL Question Bank (Top 50) | hands-on practice; try each before reading the solution | 3–4 hours |
| Top Database Questions | DBMS theory drill | 45 minutes |
| Top Scenario Questions | design and trade-off thinking | 1 hour |
| Rapid-Fire Questions | quick recall; good for the commute | 20 minutes |
| Project Connection | preparing "how did you use this?" answers | 45 minutes |
| One-Day Revision Sheet | the night before and the morning of the interview | 30 minutes |
| Interview Answering Strategy | how to structure and deliver answers | 20 minutes |

## 100 Most Important Questions {: #f1 }

<p class="lead">Short model answers. If you can say each of these clearly in your own words, you have covered the course. Category order: SQL, DBMS, data modeling, NoSQL, MongoDB, APIs, cloud, data engineering, system design, modern data systems.</p>

::: questions The 100 Questions
#### SQL (1–15)
Q: What is the logical order of execution of a SELECT query?
A: FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT/OFFSET. That's why aliases work in ORDER BY but not in WHERE.

Q: What is the difference between WHERE and HAVING?
A: WHERE filters rows before grouping and cannot use aggregates; HAVING filters groups after GROUP BY and can use aggregates.

Q: Explain INNER, LEFT, RIGHT, FULL OUTER, CROSS and SELF joins.
A: INNER: only matches. LEFT/RIGHT: all rows of one side plus matches. FULL: all rows of both sides. CROSS: every combination. SELF: a table joined to itself (employee–manager).

Q: How do you find the second-highest salary?
A: `SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);` or DENSE_RANK = 2.

Q: How do you find the Nth highest salary?
A: DENSE_RANK() OVER (ORDER BY salary DESC) in a subquery and keep rank = N; or `SELECT DISTINCT salary … ORDER BY salary DESC OFFSET N-1 LIMIT 1`.

Q: ROW_NUMBER vs RANK vs DENSE_RANK?
A: For ties: ROW_NUMBER gives 1, 2, 3, 4; RANK gives 1, 2, 2, 4; DENSE_RANK gives 1, 2, 2, 3.

Q: How do you find duplicate records?
A: `GROUP BY` the duplicate-defining columns `HAVING COUNT(*) > 1`; to see the full rows, use `COUNT(*) OVER (PARTITION BY …)`.

Q: How do you delete duplicates but keep one row?
A: Number the rows with ROW_NUMBER() OVER (PARTITION BY key ORDER BY id) and delete rows with rn > 1 (or use DELETE … USING a self join).

Q: How do you find customers who never placed an order?
A: LEFT JOIN orders and keep `o.order_id IS NULL`, or `NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)`.

Q: What is a correlated subquery?
A: A subquery that references the outer query's row, so it is conceptually evaluated per row, e.g. salary above the employee's own department average.

Q: What is a CTE and why use one?
A: A named temporary result defined with WITH; it makes multi-step queries readable and reusable within the statement, and recursive CTEs handle hierarchies.

Q: What is a window function?
A: A function computed over related rows with OVER(PARTITION BY … ORDER BY …) that keeps every row, used for ranking, running totals, LAG/LEAD and group comparisons.

Q: Why does `WHERE col = NULL` return nothing?
A: NULL means unknown, so comparing with NULL gives UNKNOWN, never TRUE. Use `IS NULL`.

Q: COUNT(*) vs COUNT(column) vs COUNT(DISTINCT column)?
A: All rows; non-NULL values of the column; distinct non-NULL values.

Q: Why is `NOT IN` with a subquery dangerous?
A: If the subquery returns any NULL, `NOT IN` returns no rows. Use `NOT EXISTS`.

#### DBMS (16–30)
Q: What is a DBMS and what is an RDBMS?
A: A DBMS is software that stores, retrieves and protects data; an RDBMS stores data in related tables with keys and SQL (PostgreSQL, MySQL, Oracle).

Q: What are DDL, DML, DCL and TCL?
A: DDL defines structure (CREATE, ALTER, DROP, TRUNCATE); DML changes data (INSERT, UPDATE, DELETE); DCL handles permissions (GRANT, REVOKE); TCL controls transactions (COMMIT, ROLLBACK, SAVEPOINT).

Q: DELETE vs TRUNCATE vs DROP?
A: DELETE removes chosen rows (WHERE allowed, slower, triggers fire); TRUNCATE removes all rows fast and keeps the table; DROP removes the table entirely.

Q: Primary key vs unique key vs foreign key?
A: Primary key: unique + not null, one per table. Unique key: no duplicates, NULLs allowed, many per table. Foreign key: references another table's key to enforce referential integrity.

Q: What is referential integrity?
A: The guarantee, enforced by foreign keys, that a referenced row exists, so there are no orphan records.

Q: What is a transaction?
A: A unit of work of one or more operations that either all commit or all roll back.

Q: What does ACID stand for?
A: Atomicity (all or nothing), Consistency (valid state to valid state), Isolation (concurrent transactions don't interfere), Durability (committed data survives crashes).

Q: Explain dirty reads, non-repeatable reads and phantom reads.
A: Dirty: reading uncommitted data. Non-repeatable: the same row gives different values within a transaction. Phantom: the same range query returns new or missing rows.

Q: What are the isolation levels?
A: Read Uncommitted, Read Committed (PostgreSQL's default), Repeatable Read and Serializable, each preventing more anomalies at some cost to concurrency.

Q: What is an index and why can it slow down writes?
A: A sorted structure (usually a B-tree) that finds rows fast without a full scan; every insert, update and delete must also maintain each index.

Q: Clustered vs non-clustered index?
A: Clustered: the table's rows are stored in index order (one per table). Non-clustered: a separate structure pointing to rows (many allowed). PostgreSQL tables are heaps; all its indexes are non-clustered.

Q: What is a composite index and the leftmost-prefix rule?
A: An index on several columns; it helps queries that filter on its leading column(s), not on later columns alone.

Q: When will the database not use an index?
A: When the condition matches many rows, the table is small, the column is wrapped in a function, the LIKE starts with a wildcard, or statistics are stale.

Q: What is a view vs a materialized view?
A: A view is a saved query that runs on each read; a materialized view stores the result and must be refreshed.

Q: What is a deadlock?
A: Two transactions each waiting for a lock the other holds; the database aborts one. Prevent it with a consistent lock order and short transactions.

#### Data Modeling (31–40)
Q: What is normalization and why do we do it?
A: Splitting data into related tables so each fact is stored once, preventing update, insert and delete anomalies.

Q: Explain 1NF, 2NF and 3NF.
A: 1NF: atomic values, no repeating groups. 2NF: no partial dependency on part of a composite key. 3NF: no transitive dependency (non-key columns depend only on the key).

Q: What is BCNF?
A: A stricter 3NF: for every functional dependency X → Y, X must be a super key.

Q: What is a functional dependency?
A: X → Y: a value of X determines exactly one value of Y (customer_id → customer_name).

Q: What is denormalization and when do you use it?
A: Deliberately adding redundancy (derived columns, summary tables, star schemas) for faster or simpler reads; used in read-heavy paths, reporting and NoSQL.

Q: How do you model a many-to-many relationship?
A: With a junction table holding foreign keys to both tables, usually as a composite primary key (enrollments(student_id, course_id)).

Q: What is an ER diagram?
A: A diagram of entities (boxes), their attributes and relationships with cardinality (1:1, 1:N, M:N).

Q: Fact table vs dimension table?
A: Facts hold measures of business events plus foreign keys; dimensions hold descriptive context (date, product, customer).

Q: Star vs snowflake schema?
A: Star: denormalized dimensions joined directly to the fact (fewer joins, faster). Snowflake: dimensions normalized into sub-tables (less redundancy, more joins).

Q: What is a slowly changing dimension Type 2?
A: Keeping history by adding a new dimension row with validity dates when an attribute changes, instead of overwriting it.

#### NoSQL (41–48)
Q: SQL vs NoSQL?
A: SQL: relational tables, fixed schema, joins, strong ACID. NoSQL: document, key-value, wide-column or graph models, flexible schema, horizontal scale, often tunable consistency.

Q: Name the four NoSQL types with examples.
A: Document (MongoDB), key-value (Redis), wide-column (Cassandra), graph (Neo4j).

Q: When would you choose NoSQL over SQL?
A: Flexible or rapidly changing structure, massive scale or write volume, simple key-based access patterns, or relationship-heavy graph queries.

Q: What is the CAP theorem?
A: During a network partition, a distributed system must choose consistency or availability; partition tolerance is required in practice.

Q: What is eventual consistency?
A: Replicas may briefly differ, but they converge to the same value once updates stop.

Q: ACID vs BASE?
A: ACID prioritises correctness and strong consistency; BASE (Basically Available, Soft state, Eventually consistent) prioritises availability and scale.

Q: Sharding vs replication?
A: Sharding splits data across nodes for scale; replication copies the same data to several nodes for availability and read capacity.

Q: Column-family database vs columnar database?
A: Column-family (Cassandra) is an operational NoSQL store with flexible columns per row; columnar (Redshift, BigQuery) stores columns contiguously for analytics.

#### MongoDB (49–56)
Q: What are database, collection, document and field in MongoDB?
A: Database ≈ database, collection ≈ table, document ≈ row (a JSON-like record), field ≈ column.

Q: What is BSON?
A: Binary JSON, MongoDB's storage format, with extra types like ObjectId, Date, Int64 and Decimal128.

Q: What is `_id` / ObjectId?
A: The unique identifier of every document; by default a 12-byte ObjectId containing a timestamp, a random value and a counter.

Q: updateOne vs updateMany?
A: updateOne changes the first matching document; updateMany changes all matching documents.

Q: deleteOne vs deleteMany?
A: deleteOne removes the first match; deleteMany removes all matches (an empty filter deletes everything).

Q: $set vs replaceOne?
A: $set changes only the named fields; replaceOne replaces the whole document except `_id`.

Q: What is the aggregation pipeline?
A: A sequence of stages ($match, $group, $sort, $project, $unwind, $lookup) that filter, group and transform documents.

Q: Embedding vs referencing?
A: Embed data owned by and read with the parent (order items); reference data that is shared, unbounded or updated independently (customers, comments).

#### APIs (57–68)
Q: What is an API?
A: A contract that lets software request data or actions from another system without knowing its internals.

Q: What is REST?
A: An architectural style using resources identified by URLs, standard HTTP methods, stateless requests and representations like JSON.

Q: Explain GET, POST, PUT, PATCH and DELETE.
A: Read, create, replace entirely, partially update, remove.

Q: PUT vs PATCH?
A: PUT sends the full resource and replaces it (idempotent); PATCH sends only the changes.

Q: What does idempotent mean? Which methods are idempotent?
A: Repeating a request has the same effect as doing it once: GET, PUT, DELETE (and HEAD, OPTIONS). POST is not.

Q: Name important HTTP status codes.
A: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 429 Too Many Requests, 500 Internal Server Error, 503 Service Unavailable.

Q: 401 vs 403?
A: 401: not authenticated (missing or invalid credentials). 403: authenticated but not permitted.

Q: Authentication vs authorization?
A: Authentication proves who you are; authorization decides what you're allowed to do.

Q: How does JWT authentication work?
A: After login the server issues a signed token with claims (user ID, role, expiry); the client sends it as a Bearer token; the server verifies the signature and expiry on each request.

Q: Path parameter vs query parameter?
A: A path parameter identifies a resource (`/orders/42`); query parameters filter, sort or paginate (`?status=PENDING&page=2`).

Q: How do you handle a failing external API?
A: Timeouts, retries with exponential backoff and jitter for transient errors (5xx, 429), idempotency keys for non-idempotent calls, circuit breakers and fallbacks.

Q: What are pagination, rate limiting and versioning?
A: Returning results in pages; capping requests per client (429 when exceeded); managing breaking changes (e.g. `/v1/`, `/v2/`).

#### Cloud (69–76)
Q: What is a managed database?
A: A cloud service where the provider runs the database (patching, backups, replication, failover) while you manage schema, queries and access.

Q: Vertical vs horizontal scaling?
A: Vertical: a bigger machine (simple, limited). Horizontal: more machines (scalable, more complex).

Q: What is a read replica?
A: A read-only copy kept in sync by replication, used to offload read queries from the primary.

Q: Synchronous vs asynchronous replication?
A: Synchronous waits for replicas to confirm (no data loss, slower writes); asynchronous doesn't wait (faster, possible lag and loss).

Q: What is failover?
A: Automatically promoting a standby to primary when the primary fails, with clients reconnecting to the same endpoint.

Q: What are RPO and RTO?
A: RPO: maximum acceptable data loss (in time). RTO: maximum acceptable downtime.

Q: Is replication a backup?
A: No. Replication copies mistakes instantly; backups and point-in-time recovery let you go back in time.

Q: What is a serverless database?
A: A managed database that scales capacity automatically (even to zero) and bills by usage, e.g. Aurora Serverless or DynamoDB on-demand.

#### Data Engineering (77–88)
Q: What is data integration?
A: Combining data from multiple systems into a consistent, usable form, or keeping systems in sync.

Q: ETL vs ELT?
A: ETL transforms before loading on a separate engine; ELT loads raw data first and transforms inside the warehouse (SQL/dbt).

Q: Batch vs streaming?
A: Batch processes bounded data on a schedule (simple, higher latency); streaming processes events continuously (low latency, more complex).

Q: What is a data pipeline?
A: An automated, repeatable flow that ingests, transforms and delivers data, usually orchestrated (Airflow) and monitored.

Q: What is CDC?
A: Change Data Capture: streaming inserts, updates and deletes from a database's log to other systems in near real time.

Q: What is a data warehouse?
A: A central, integrated, historical store of cleaned, modelled data for analytics (schema-on-write).

Q: What is a data lake?
A: Cheap object storage holding raw data of any type in native formats (schema-on-read).

Q: What is a data lakehouse?
A: A lake plus an open table format (Delta/Iceberg/Hudi) that adds ACID transactions, schemas and performance, so BI and ML share one copy of data.

Q: Structured vs semi-structured vs unstructured data?
A: Fixed tables; flexible self-describing formats (JSON, XML, logs); no predefined model (images, PDFs, audio).

Q: What is an incremental load and why make loads idempotent?
A: Loading only changed data (via a watermark or CDC); idempotent loads (upserts) can be re-run safely after failures.

Q: Name the data quality dimensions.
A: Accuracy, completeness, consistency, validity, uniqueness, timeliness.

Q: What is a Kafka partition and a consumer group?
A: A partition is an ordered log segment of a topic (ordering per partition); a consumer group shares partitions among its consumers to process in parallel.

#### System Design (89–94)
Q: Walk through what happens when a user places an order in a web app.
A: Frontend sends POST /orders (JSON + token) → API authenticates and validates → service applies rules → DB transaction saves the order and items → payment API is called with an idempotency key → events trigger email and inventory → the order is copied to the warehouse for analytics.

Q: How would you handle a read-heavy system?
A: Caching (Redis), read replicas, proper indexes, denormalized read models or materialized views, a CDN for static content, pagination.

Q: When would you use a message queue instead of a direct API call?
A: For background or long-running work, to absorb spikes, to decouple systems so the receiver can be down, and to fan out to many consumers (pub/sub).

Q: How do you prevent duplicate payments when a client retries?
A: An idempotency key per payment attempt, stored with a unique constraint; the server returns the saved result for repeats.

Q: How would you design the database for an e-commerce app?
A: Normalized OLTP tables: customers, addresses, products, categories, orders, order_items, payments, with PK/FK constraints and indexes on FKs and common filters; a cache for hot reads; analytics in a warehouse via ELT/CDC.

Q: What is caching and what is the main difficulty?
A: Storing frequently read data in fast memory (Redis) to reduce latency and load; the hard part is invalidation, keeping the cache consistent with the source.

#### Modern Data Systems (95–100)
Q: What is data mesh?
A: Decentralised data ownership where domains publish data products on a self-serve platform with federated governance.

Q: What is serverless?
A: Running code and services without managing servers; event-driven, auto-scaling to zero, pay per use.

Q: What is a cold start?
A: Extra latency when a serverless function runs in a newly created environment that must initialise first.

Q: Why does AI depend on good data?
A: Models learn from data, so inaccuracy, gaps, bias or staleness in the data become errors in predictions: garbage in, garbage out.

Q: What is event-driven architecture?
A: Services communicate by publishing and consuming events through a broker instead of calling each other directly, which gives loose coupling at the cost of eventual consistency.

Q: What is RAG?
A: Retrieval-Augmented Generation: retrieving relevant company content via embeddings and a vector database and passing it to an LLM so answers are grounded in that content.
:::
