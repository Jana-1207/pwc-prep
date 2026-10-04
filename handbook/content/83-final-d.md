## Project Connection: "How Have You Used This in a Project?" {: #f6 }

<p class="lead">Interviewers almost always connect theory to your own work: "You mentioned PostgreSQL. Where did you use indexes? How did you handle transactions?" This section maps every major concept onto a typical project, so you can answer with concrete, honest examples.</p>

[[fig:project_architecture | A typical student or fresher project: React frontend, Spring Boot API, PostgreSQL, plus cache, external API, queue and reporting.]]

### Where each concept lives in a real application

| Concept | Where it lives | What you can say |
|---|---|---|
| Database design and normalization | the schema (`users`, `products`, `orders`, `order_items`) | "I normalized to 3NF: order lines in their own table, linked by order_id and product_id." |
| Keys and constraints | DDL / JPA entities | "Foreign keys stop orphan orders; a UNIQUE constraint on email prevents duplicate accounts." |
| SQL and joins | repository layer, reports | "The order history page joins orders, order_items and products, with pagination." |
| Indexes | the database | "I added an index on orders(customer_id, created_at) because the history query filtered and sorted on those." |
| Transactions | service layer (`@Transactional`) | "Placing an order inserts the order and its items and decrements stock in one transaction." |
| REST API and status codes | controllers | "POST /orders returns 201 with a Location header; validation errors return 400 with field messages." |
| JSON and DTOs | request/response bodies | "I used DTOs so the API doesn't expose internal entity fields like password hashes." |
| Authentication and authorization | security filter, JWT | "Login returns a JWT; a filter validates it; admins have a role claim, and users can access only their own orders." |
| Caching | Redis / in-memory | "Product listings are cached for 5 minutes, which cut database load; we evict on product update." |
| External API integration | payment, maps, email | "The payment call has a timeout, retries with backoff and an idempotency key." |
| Asynchronous processing | queue, scheduled jobs | "Confirmation emails go through a queue so checkout stays fast." |
| Reporting / data pipeline | nightly export, warehouse | "A nightly job exports orders to a reporting database for sales dashboards." |
| NoSQL | MongoDB / Firebase | "We stored chat messages in MongoDB because each message document is self-contained and append-only." |

### Ready-to-adapt answers

These are models of *shape and detail*, not scripts. Swap in what you actually built; never claim work you didn't do, because every sentence below invites a follow-up question.

::: explain "How did you use SQL and joins in your project?"
"In my e-commerce project the order history page needed the order, its items and the product names, so the repository runs a query joining orders, order_items and products, filtered by the logged-in customer's ID, ordered by date, and paginated with LIMIT and OFFSET. For the admin dashboard I wrote a GROUP BY query for daily revenue per category, excluding cancelled orders."
:::

::: explain "Where did you use transactions?"
"Checkout was the critical part. Creating the order, inserting the order items and reducing stock had to succeed together, so that service method was annotated @Transactional. If the stock update failed, for example because of the CHECK constraint that stock can't go negative, Spring rolled back the whole thing, so we never had an order without stock or stock without an order. I kept the external payment call outside the transaction so we didn't hold locks while waiting for the gateway."
:::

::: explain "Did you use indexes? How did you decide?"
"Yes. When we loaded test data, the order history API slowed to over a second. EXPLAIN ANALYZE showed a sequential scan on orders, so I added a composite index on (customer_id, created_at), matching the filter and the sort, and the query dropped to a few milliseconds. I avoided indexing columns like status that have few distinct values, because they rarely help and they slow down inserts."
:::

::: explain "How did authentication work in your project?"
"Users log in with email and password. The password is checked against a bcrypt hash, and the server issues a JWT with the user ID, role and a short expiry. The frontend sends it in the Authorization header, and a filter verifies the signature and expiry on every request. Authorization is role-based for admin endpoints, plus an ownership check, so customers can only see their own orders. Invalid tokens get 401, and forbidden actions get 403."
:::

::: explain "How did you integrate an external API?"
"We used a payment gateway's sandbox. The backend creates a payment with an idempotency key tied to the order, with a 5-second timeout and up to three retries with exponential backoff for timeouts and 5xx errors. The gateway confirms the final status through a webhook, which we verify by signature and process idempotently, because the same event can arrive twice."
:::

### If your project didn't use something

Be honest, then bridge to understanding:

> "We didn't need a message queue in that project because the traffic was small, but if we added email notifications at scale, I'd publish an OrderPlaced event to a queue so checkout doesn't wait for the email provider, and make the consumer idempotent."

This shows judgement, which is what the interviewer is checking.

### A project story template (2 minutes)

1. **Context:** what the project does and for whom (one sentence).
2. **Your role:** what *you* built.
3. **Architecture:** the layers (frontend → API → database → integrations), in one breath.
4. **One hard problem:** a bug, a performance issue or a design decision, and how you solved it.
5. **Result:** a number if possible ("page load from 1.2 s to 200 ms", "handled 500 test users").
6. **What you'd improve:** caching, tests, monitoring, async processing. This shows growth.

### Follow-up questions to prepare for

| Question | What a good answer includes |
|---|---|
| "Why PostgreSQL and not MongoDB?" | the data was relational (orders, items, users) and needed transactions and joins; you'd consider MongoDB for flexible or document-shaped data |
| "How would it scale to a million users?" | stateless API behind a load balancer, caching, read replicas, indexes, async queues, a CDN; analytics moved to a warehouse |
| "How did you handle errors?" | global exception handler, proper status codes, validation messages, logs with request IDs |
| "How did you test it?" | unit tests for services, integration tests for repositories and APIs (Testcontainers / H2), Postman collections |
| "What was the hardest bug?" | a specific story: the symptom, how you found the cause, the fix, the lesson |
| "What would you do differently?" | one honest technical improvement and one process improvement |

## One-Day Revision Sheet {: #f7 }

<p class="lead">Read this the evening before and again on the morning of the interview. Each line is something you should be able to say from memory.</p>

### Module 1: Modern data systems

- **Data system** = sources → ingestion → storage → processing → serving, plus governance.
- **App layers:** user → frontend → backend/API → database → other services → analytics.
- **OLTP** (run the business: small ACID transactions, normalized, row store) vs **OLAP** (analyse: big scans, star schema, columnar).
- **Batch** (scheduled, cheap, simple) vs **streaming** (continuous, low latency, complex). Choose by how fresh the decision needs the data to be.
- **Polyglot persistence:** the right store for each job (PostgreSQL, Redis, MongoDB, Elasticsearch, S3, Kafka, warehouse).

### Module 2: Data modeling

- **Keys:** PK (unique + not null, one per table) · FK (references a PK, referential integrity, can be NULL) · UNIQUE (many NULLs in PostgreSQL) · composite · candidate · surrogate vs natural.
- **Relationships:** 1:N → FK on the many side · 1:1 → FK + UNIQUE · M:N → junction table.
- **Anomalies:** update, insert, delete. **1NF** atomic · **2NF** no partial dependency · **3NF** no transitive dependency · **BCNF** every determinant is a key.
- **Denormalize** deliberately for reads (derived columns, materialized views, star schemas).
- **Warehouse:** facts (measures) + dimensions (context); define the grain first; **star** (default) vs **snowflake**; **SCD Type 2** keeps history.
- **NoSQL modeling:** start from access patterns; embed what is owned and read together; reference what is shared or unbounded.

### Module 3: SQL

**Order of execution:** FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT.

| Remember | Detail |
|---|---|
| NULL | `IS NULL`; aggregates skip NULLs; `COUNT(*)` counts rows; `NOT IN` + NULL → nothing |
| WHERE vs HAVING | rows before grouping vs groups after grouping |
| Joins | INNER, LEFT (count a right-side column!), RIGHT, FULL, CROSS, SELF; ON vs WHERE in LEFT JOIN |
| Ranking | ROW_NUMBER 1,2,3,4 · RANK 1,2,2,4 · DENSE_RANK 1,2,2,3 |
| DELETE / TRUNCATE / DROP | rows (WHERE) / all rows fast / the whole table |
| Index | B-tree; fast reads, slower writes; leftmost prefix; selectivity |
| ACID | Atomicity, Consistency, Isolation, Durability |
| Anomalies | dirty (uncommitted), non-repeatable (changed row), phantom (new rows) |
| Isolation | RU, RC (PostgreSQL default), RR, Serializable |

```sql
-- second highest salary
SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);

-- Nth highest (ties count once)
SELECT * FROM (SELECT e.*, DENSE_RANK() OVER (ORDER BY salary DESC) AS r
               FROM employees e) t
WHERE r = 3;

-- duplicates
SELECT email, COUNT(*) FROM leads GROUP BY email HAVING COUNT(*) > 1;

-- rows with no match (anti-join)
SELECT c.* FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);

-- top N per group
SELECT * FROM (SELECT e.*, ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn
               FROM employees e) t
WHERE rn <= 2;

-- latest record per user
SELECT DISTINCT ON (user_id) * FROM user_logins ORDER BY user_id, login_time DESC;

-- running total
SELECT d, amt, SUM(amt) OVER (ORDER BY d) AS running_total FROM daily;

-- previous row
SELECT d, amt, amt - LAG(amt) OVER (ORDER BY d) AS change FROM daily;
```

### Module 4: Cloud databases and storage

- **Managed DB** (RDS / Cloud SQL): the provider runs it; you own schema, queries and access. **Serverless DB:** auto-scaling, pay per use.
- **Scale:** vertical vs horizontal; read replicas; partitioning (within one DB) vs sharding (across servers).
- **HA:** synchronous standby + failover; **RPO** = data loss, **RTO** = downtime; **replication ≠ backup**; PITR.
- **NoSQL families:** document (MongoDB), key-value (Redis), wide-column (Cassandra), graph (Neo4j).
- **CAP:** during a partition choose C or A (CP: MongoDB defaults, HBase · AP: Cassandra, DynamoDB defaults). **Eventual consistency.** **BASE** vs ACID.
- **MongoDB:** database → collection → document → field; BSON; `_id`; insertOne/Many, find(filter, projection), updateOne/Many with `$set`/`$inc`/`$push`, deleteOne/Many; aggregation `$match` → `$group` → `$sort`; `$lookup`, `$unwind`.
- **Storage:** structured / semi-structured / unstructured · warehouse (schema-on-write) · lake (schema-on-read, risk of a swamp) · lakehouse (Delta / Iceberg / Hudi: ACID on the lake).

### Module 5: APIs and integration

| Remember | Detail |
|---|---|
| Methods | GET read · POST create (not idempotent) · PUT replace · PATCH partial · DELETE |
| Idempotent | GET, PUT, DELETE (and HEAD, OPTIONS) |
| 2xx | 200 OK · 201 Created · 202 Accepted · 204 No Content |
| 4xx | 400 bad request · 401 unauthenticated · 403 forbidden · 404 · 409 conflict · 422 invalid · 429 rate limited |
| 5xx | 500 · 502 · 503 unavailable · 504 timeout |
| Path vs query | `/orders/42` identifies · `?status=PENDING&page=2` filters |
| AuthN vs AuthZ | who you are vs what you may do |
| JWT | header.payload.signature; signed, not encrypted; short expiry |
| OAuth 2.0 / OIDC | delegated access / login with an identity provider |
| Reliability | timeouts · retry 5xx/429 with backoff + jitter · idempotency keys · webhooks · circuit breaker |
| Integration | API, file, ETL/ELT, CDC, events; incremental + idempotent loads; data quality checks |

### Module 6: Enterprise integration

- **Styles:** file transfer · shared database · API (RPC) · messaging. Point-to-point → hub/ESB/iPaaS → API-led → event-driven.
- **API vs queue:** immediate answer and temporal coupling vs decoupled, buffered and eventual.
- **Queue** (one consumer per message, work) vs **topic** (every subscriber gets a copy, events). At-least-once → idempotent consumers. DLQ.
- **EDA:** events are past-tense facts; loose coupling; sagas with compensation; outbox pattern.
- **ETL** (transform before loading, separate engine) vs **ELT** (load raw, transform in the warehouse with SQL/dbt).
- **Kafka:** topic → partitions (ordering per partition) → offsets; consumer groups; retention and replay; windows (tumbling, sliding, session); event time vs processing time.
- **Salesforce → warehouse:** connector or Bulk API, incremental by SystemModstamp, capture deletes, mind API limits; staging → models → BI; reverse ETL.

### Module 7: Trends

- **Data mesh:** domain ownership · data as a product · self-serve platform · federated computational governance. Not for small organisations.
- **Serverless:** event-triggered functions, scale to zero, pay per use; cold starts, time limits, lock-in, cost at steady load.
- **AI + data:** garbage in, garbage out; quality, metadata, lineage, governance (DPDP Act); drift monitoring; **RAG** = retrieve relevant chunks via embeddings and a vector DB, then generate.
- **Modern systems:** real-time analytics, cloud-native (containers, Kubernetes, IaC, CI/CD), distributed systems (partitioning, consistency, consensus), the modern data stack, DataOps, data observability.

### Traps at a glance

| Trap | The truth |
|---|---|
| `WHERE col = NULL` | never true; use `IS NULL` |
| `COUNT(col)` = `COUNT(*)`? | `COUNT(col)` skips NULLs; `COUNT(*)` counts rows |
| `NOT IN (subquery)` | one NULL in the subquery returns no rows; use `NOT EXISTS` |
| Right-table filter in `WHERE` after a `LEFT JOIN` | silently becomes an inner join; put it in `ON` |
| Joining two one-to-many tables, then `SUM` | fan-out inflates totals; aggregate each side first |
| "Nth highest salary" | ties: use `DENSE_RANK`; `ROW_NUMBER` breaks ties arbitrarily |
| `5 / 2` in PostgreSQL | integer division gives 2; use `5 / 2.0` or `5::numeric / 2` |
| A `SELECT` alias in `HAVING` | error in PostgreSQL; repeat the expression |
| "TRUNCATE can never be rolled back" | it can in PostgreSQL (inside a transaction); not in MySQL/Oracle |
| "Index every column" | each index slows writes; low-selectivity columns rarely help |
| PUT vs PATCH | PUT replaces the whole resource (idempotent); PATCH changes some fields |
| 401 vs 403 | 401 = not authenticated; 403 = authenticated but not allowed |
| C in CAP vs C in ACID | CAP: every read sees the latest write; ACID: rules and constraints hold |
| "Replicas are my backup" | a bad `DELETE` replicates instantly; keep backups and PITR |
| "The queue delivers exactly once" | usually at-least-once; make consumers idempotent |
| "JWTs are encrypted" | signed, not encrypted; never put secrets in the payload |

### Last-minute reminders

- Say "it depends" **only** when you then say *on what*.
- For every "X vs Y": purpose, how it works, when to use each.
- For SQL: ask about ties, NULLs and edge cases before writing.
- Bring one project story and five STAR stories (see the next section).

## Interview Answering Strategy {: #f8 }

### The five-step answer

[[fig:answer_framework | A reliable structure for concept questions: define, why, how, example, trade-off.]]

For most concept questions, about 30–60 seconds:

1. **Define** it in one plain sentence.
2. **Why** it exists: the problem it solves.
3. **How** it works, briefly.
4. **Example:** real-world or from your project.
5. **Trade-off:** a limitation, or when not to use it.

Then **stop** and let the interviewer steer. Short, complete answers invite good follow-up questions; long monologues invite interruptions.

### By question type

| Type | Strategy |
|---|---|
| [DEFINITION] | one-sentence definition + one example; don't recite textbook wording |
| [COMPARISON] | three axes: purpose, how it works, when to use each; finish with a one-line rule of thumb |
| [WHY] | start from the problem without it ("without indexes, every lookup scans the whole table…") |
| [HOW] | walk step by step, in order; a quick sketch helps |
| [SCENARIO] | **clarify** (one or two questions) → **propose** → **justify** (trade-offs, risks, monitoring) |
| [SQL PROBLEM] | restate → define the output grain → pick the pattern → build in steps (CTEs) → test on 2–3 rows → mention indexes and edge cases |
| [DESIGN QUESTION] | requirements and scale → data model → main flows and APIs → scaling and failure handling → trade-offs |
| [TRAP QUESTION] | pause; look for the edge case (NULLs, ties, idempotency, CAP vs ACID consistency) before answering |

### Thinking aloud during SQL questions

Interviewers grade your reasoning as much as your final query.

For example, asked *"Find the employees with the second-highest salary in each department"*:

> "So for each department I need the people at the second salary level. If two people tie, they share one level, so DENSE_RANK, partitioned by department. I can't filter a window function in WHERE, so I'll compute the rank in a CTE first and keep rank 2 outside it. Let me check Finance: 110000 is rank 1, and the two 70000 rows are both rank 2, so both appear. That's right."

If you get stuck, write a simpler version first ("Let me get salaries per department working, then add the ranking"). Partial, correct progress beats silence.

### When you don't know

- Be honest: "I haven't used Kafka Streams directly."
- Reason from fundamentals: "…but I understand stream processing needs state per key, so I'd expect it to partition by key and keep local state, with changelogs for recovery."
- Offer what you *would* do: "I'd check the documentation for how it handles exactly-once."

Interviewers respect honesty plus reasoning; bluffing is usually obvious.

### Behavioural questions: STAR and the PwC Professional

Use **STAR**: **S**ituation (context), **T**ask (your goal), **A**ction (what *you* did, the longest part), **R**esult (the outcome, with a number if possible, and what you learned).

PwC publicly describes the **PwC Professional** framework (five dimensions). Prepare one story for each:

| Dimension | What it means | Story prompt to prepare |
|---|---|---|
| Whole leadership | leading yourself and others, resilience, ownership | a time you took ownership of a failing task or led a team |
| Business acumen | understanding the business value of your work | a time you connected a technical decision to a user or business outcome |
| Technical and digital | applying technical skills, learning new tools | a time you learned a technology quickly to deliver something |
| Global and inclusive | working across differences, valuing perspectives | a time you worked with a diverse team or resolved a misunderstanding |
| Relationships | building trust, communicating, handling conflict | a time you handled a disagreement or difficult stakeholder |

**"Tell me about yourself"** (60–90 seconds): present (degree, focus, strongest skills) → past (one or two relevant projects or internships, with impact) → future (why this role and PwC fits your direction).

**"Why PwC?"** Research the actual business unit and role you applied to (technology consulting, the Acceleration Centers, data and analytics, cyber), and connect it to your interests and what you've built. Specific beats generic: name the kind of work, not just the brand.

### Questions to ask the interviewer

- "What does a typical first project look like for someone joining this team?"
- "Which technologies and data platforms does the team use most?"
- "How do new joiners learn: training programmes, mentors, certifications?"
- "What distinguishes people who do really well in their first year here?"

### Day-before and on-the-day checklist

- [ ] Re-read the One-Day Revision Sheet
- [ ] Practise your project story aloud (2 minutes)
- [ ] Prepare five STAR stories mapped to the PwC Professional dimensions
- [ ] Revise SQL patterns 1–22 (write three from memory)
- [ ] Check your resume: be able to explain every line
- [ ] Online: test camera, microphone and internet; quiet room; charger
- [ ] In person: printed resume copies, ID, arrive early
- [ ] Have water, paper and a pen ready for SQL and sketches
- [ ] Sleep well; a rested brain answers better than a crammed one

### Common interview mistakes

| Mistake | Better |
|---|---|
| Memorized textbook definitions | plain-language definition + example |
| Writing SQL silently | think aloud, build in steps, test on sample rows |
| Not clarifying ambiguous questions | ask about ties, NULLs, scale and freshness |
| "It depends" with nothing after it | say what it depends on, then commit to a choice |
| Claiming skills you can't defend | list only what you can explain in depth |
| Ignoring trade-offs | always mention one limitation or alternative |
| Overlong answers | about 60 seconds, then pause |
| Speaking negatively about past teams | focus on what you learned and did |
