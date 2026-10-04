## Session 2.6 — Denormalization: When and Why {: #s2-6 }

### Simple meaning

**Denormalization means deliberately storing some data more than once, or storing pre-calculated results, so that reading becomes faster or simpler.** It is a conscious trade: you accept extra storage and extra work on writes in exchange for quicker reads.

Normalization is the default for transactional systems. Denormalization is a targeted exception, applied where the reads justify it.

### Why we denormalize

- **Joins cost time at scale.** Joining five large tables for every page view adds up.
- **Read-heavy workloads.** If a value is read a million times and changed once a day, pre-computing it makes sense.
- **Reporting and analytics.** Analysts want wide, simple tables (Session 2.7).
- **Distributed and NoSQL databases** often cannot join efficiently, so related data is stored together (Session 2.8).

### Common denormalization techniques

| Technique | Example | Cost you accept |
|---|---|---|
| Store a derived value | `orders.total_amount` instead of summing `order_items` every time | must be kept in sync when items change |
| Copy a column into another table | store `customer_name` on the invoice | name can drift from the customer table, which is sometimes *wanted*: the invoice should show the name at the time of sale |
| Summary (aggregate) table | `daily_sales(date, revenue)` | refresh jobs, possible staleness |
| Materialized view | a stored, refreshable query result | refresh cost; data only as fresh as the last refresh |
| Star schema | wide dimension tables in a warehouse | duplication inside dimensions |

### Example 1: a derived column in the sample database

The sample database itself is slightly denormalized: `orders.total_amount` repeats information that could be computed from `order_items`. That makes listing orders fast, but now we must check that the two never disagree. This query looks for any order whose stored total differs from its items:

```sql run
SELECT o.order_id,
       o.total_amount,
       SUM(i.quantity * i.unit_price) AS items_total
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
GROUP BY o.order_id, o.total_amount
HAVING o.total_amount <> SUM(i.quantity * i.unit_price);
```

Zero rows means the copies are consistent. In production this check (or a trigger that recalculates the total) is part of the price of denormalizing.

### Example 2: a materialized view

A **view** is a saved query that runs every time you read it. A **materialized view** stores the query's *result*, so reading it is as cheap as reading a table, until you refresh it.

```sql run
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT date_trunc('month', order_date)::date AS month,
       COUNT(*)                              AS orders,
       SUM(total_amount)                     AS revenue
FROM orders
WHERE status <> 'CANCELLED'
GROUP BY 1;

SELECT * FROM monthly_sales ORDER BY month;
```

::: linebyline
| Line | What it does |
|---|---|
| `CREATE MATERIALIZED VIEW monthly_sales AS` | saves the result of the query below as a stored object |
| `date_trunc('month', order_date)::date AS month` | cuts each date down to the first day of its month, e.g. 2024-01-28 → 2024-01-01 |
| `COUNT(*) AS orders, SUM(total_amount) AS revenue` | number of orders and revenue per month |
| `WHERE status <> 'CANCELLED'` | cancelled orders are not revenue |
| `GROUP BY 1` | group by the first column in the SELECT list (the month) |
| `SELECT * FROM monthly_sales` | reading it now costs no aggregation at all |
:::

When new orders arrive, `REFRESH MATERIALIZED VIEW monthly_sales;` recomputes it, typically on a schedule.

### Normalize or denormalize? A decision table

| Situation | Lean towards | Why |
|---|---|---|
| OLTP: orders, payments, bookings | **Normalize** (3NF) | correctness and cheap updates matter most |
| Write-heavy data | **Normalize** | each write touches one place |
| Read-heavy pages with stable data (product listing) | **Denormalize selectively** | fewer joins per page view |
| Data warehouse / BI | **Denormalize** (star schema) | simple, fast analytical queries |
| NoSQL document store | **Denormalize** (embed) | joins are limited; read patterns drive design |
| Legal or historical snapshot (invoice) | **Copy on purpose** | the value at that moment must be preserved |

| | Normalization | Denormalization |
|---|---|---|
| Goal | remove redundancy, protect consistency | speed up reads, simplify queries |
| Number of tables | more | fewer / wider |
| Writes | simple and cheap | more work: several copies to update |
| Reads | may need many joins | fewer joins |
| Risk | slower complex reads | inconsistent copies, more storage |
| Typical home | OLTP | OLAP, caches, NoSQL |

::: explain
"Denormalization is intentionally adding redundancy, like storing an order total or copying a customer's name, to make reads faster or simpler. It is the opposite trade-off to normalization: reads get cheaper, but writes get more expensive and we risk copies going out of sync, so we need triggers, refresh jobs or checks. I'd normalize transactional data to 3NF first, and then denormalize specific read-heavy paths, use materialized views or summary tables, or use a star schema in the warehouse."
:::

::: trap
- Treating denormalization as "not knowing normalization". A good answer says you normalize first, then denormalize *on purpose*, with a reason.
- Forgetting the cost: someone must keep the copies in sync.
- Confusing a view (re-runs every time) with a materialized view (stored result, needs refresh).
:::

::: questions
#### Basic
Q: [DEFINITION] What is denormalization?
A: Deliberately adding redundant or pre-computed data to a design to make reads faster or simpler, at the cost of extra storage and more complex writes.

Q: [COMPARISON] View vs materialized view?
A: A view stores only the query and runs it on every read. A materialized view stores the result physically, so it is fast to read but must be refreshed to show new data.

#### Intermediate
Q: [WHY] When would you denormalize?
A: For read-heavy workloads where joins are a bottleneck, for reporting and warehouses, for NoSQL stores without efficient joins, and when a historical snapshot must be preserved (an invoice's price).

Q: [HOW] How do you keep denormalized data consistent?
A: Update all copies in the same transaction, use triggers, schedule refresh jobs for summary tables and materialized views, and run reconciliation checks that compare copies with the source.

#### Scenario-based
Q: [SCENARIO] Your product listing page joins six tables and is slow. What would you consider?
A: First check indexes and the query plan. If the joins are still the bottleneck, add a denormalized read model: a materialized view or a cached JSON document per product, refreshed when products change.

Q: [SCENARIO] Should an invoice store the product price or always look it up from the products table?
A: Store the price charged on the invoice line. Prices change; an old invoice must keep showing what was actually charged.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is denormalization the same as having no normalization?
A: No. Denormalization is a deliberate step taken *after* designing a normalized model, for a specific performance or simplicity reason.
:::

## Session 2.7 — Data Warehousing and Dimensional Modeling {: #s2-7 }

### What is a data warehouse?

**Simple meaning:** a data warehouse is a central database built for **analysis**, not for running the business. It collects data from many operational systems, cleans and integrates it, and keeps years of history, so people can answer questions like "How did sales in each region change over the last three years?"

The classic definition (Bill Inmon) describes four properties. In plain words:

| Property | Meaning |
|---|---|
| **Subject-oriented** | organised around business subjects (sales, customers, inventory), not around applications |
| **Integrated** | data from many sources made consistent (same codes, formats and definitions) |
| **Time-variant** | keeps history, so you can see how things changed over time |
| **Non-volatile** | data is loaded and read; it is not constantly updated or deleted like OLTP data |

[[fig:dw_architecture | Classic warehouse architecture: sources → ETL → warehouse → data marts → BI tools.]]

- **Staging area:** a landing zone where raw extracts are cleaned before loading.
- **Data mart:** a smaller, focused slice of the warehouse for one department, such as a sales mart or finance mart.
- **BI tools:** Power BI, Tableau or Looker read from the warehouse or the marts.

### Dimensional modeling: facts and dimensions

Warehouses are usually designed with **dimensional modeling** (Ralph Kimball's approach). Every analytical question has the same shape: *a number, sliced by some context.* "Revenue (number) by month (when), by product category (what), by city (where)."

- A **fact table** stores the **numbers** (measures) of a business event, plus foreign keys to its context. Example: `fact_sales(date_key, product_key, customer_key, quantity, sales_amount)`.
- A **dimension table** stores the **descriptive context**: who, what, where, when. Examples: `dim_date`, `dim_product`, `dim_customer`, `dim_store`.

| | Fact table | Dimension table |
|---|---|---|
| Contains | measures (amount, quantity) + foreign keys | descriptive attributes (name, category, city) |
| Shape | very many rows, few columns (long and thin) | fewer rows, many columns (short and wide) |
| Changes | new rows appended for every event | changes slowly (a customer moves city) |
| Example row | (20240105, product 1, customer 1, qty 2, ₹1598) | (product 1, Wireless Mouse, Electronics) |
| Typical question it answers | "how much / how many?" | "by what / for whom / when / where?" |

### Grain: the first decision

The **grain** is what one row of the fact table represents, for example "one row per product per order line". Decide the grain *before* anything else; it determines which dimensions and measures make sense. Mixing grains (some rows per line, some per order) produces double counting.

### Types of measures [INTERVIEW EXTENSION]

| Type | Can you SUM it across everything? | Example |
|---|---|---|
| Additive | yes | sales amount, quantity |
| Semi-additive | across some dimensions, not time | account balance (summing balances across days is meaningless) |
| Non-additive | no | ratios and percentages (profit margin): recompute from components |

### Star schema

In a **star schema**, one fact table sits in the middle and each dimension connects to it directly, like the points of a star. Dimensions are **denormalized**: `dim_product` holds the product name, category and brand together.

[[fig:star_schema | A star schema: every dimension is one join away from the fact table.]]

### Building and querying a tiny star schema for real

The sample database is an OLTP design. The block below performs a mini ETL: it reshapes the OLTP tables into a star schema. In a real warehouse, a pipeline would do this, and the keys would be generated surrogate keys. Here the source IDs are reused to keep it short.

```sql run keep quiet
CREATE TABLE dim_date AS
SELECT DISTINCT
       to_char(order_date, 'YYYYMMDD')::int  AS date_key,
       order_date                            AS full_date,
       to_char(order_date, 'Mon')            AS month_name,
       EXTRACT(MONTH FROM order_date)::int   AS month_no,
       EXTRACT(QUARTER FROM order_date)::int AS quarter,
       EXTRACT(YEAR FROM order_date)::int    AS year
FROM orders;
ALTER TABLE dim_date ADD PRIMARY KEY (date_key);

CREATE TABLE dim_product AS
SELECT product_id AS product_key, product_name, category
FROM products;
ALTER TABLE dim_product ADD PRIMARY KEY (product_key);

CREATE TABLE dim_customer AS
SELECT customer_id AS customer_key, customer_name, city
FROM customers;
ALTER TABLE dim_customer ADD PRIMARY KEY (customer_key);

CREATE TABLE fact_sales AS
SELECT to_char(o.order_date, 'YYYYMMDD')::int AS date_key,
       i.product_id                           AS product_key,
       o.customer_id                          AS customer_key,
       i.quantity,
       i.quantity * i.unit_price              AS sales_amount
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
WHERE o.status <> 'CANCELLED';
```

The grain of `fact_sales` is one row per order line (cancelled orders excluded). A typical analytical question is "revenue and units by month and category":

```sql run
SELECT d.month_name,
       p.category,
       SUM(f.sales_amount) AS revenue,
       SUM(f.quantity)     AS units
FROM fact_sales f
JOIN dim_date    d ON d.date_key    = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY d.month_no, d.month_name, p.category
ORDER BY d.month_no, revenue DESC;
```

::: linebyline
| Line | What it does |
|---|---|
| `FROM fact_sales f` | start from the numbers |
| `JOIN dim_date d ...` / `JOIN dim_product p ...` | each dimension is exactly one join away; that is the "star" |
| `SUM(f.sales_amount) AS revenue, SUM(f.quantity) AS units` | the measures, aggregated |
| `GROUP BY d.month_no, d.month_name, p.category` | slice by month and category; `month_no` is included so we can sort months correctly |
| `ORDER BY d.month_no, revenue DESC` | January first; inside each month, the biggest category first |
:::

Every star-schema query looks like this: **join the fact to the dimensions you need, filter and group by dimension attributes, aggregate the measures.**

### Snowflake schema

A **snowflake schema** normalizes the dimensions into sub-dimensions: `dim_product` → `dim_category` → `dim_department`. The diagram branches out like a snowflake.

[[fig:snowflake_schema | A snowflake schema: dimensions are split into further normalized tables.]]

| | Star schema | Snowflake schema |
|---|---|---|
| Dimensions | denormalized, one table each | normalized into several tables |
| Joins per query | fewer (one hop) | more (several hops) |
| Query speed | usually faster | usually slower |
| Storage | some duplication inside dimensions | less duplication |
| Ease of use for analysts and BI tools | simpler | more complex |
| Maintenance of dimension data | updates may touch many rows | updates touch one place |
| Most common choice | yes, the default in most warehouses | when dimensions are huge or shared hierarchies matter |

### OLTP database vs data warehouse

| | Operational database (OLTP) | Data warehouse (OLAP) |
|---|---|---|
| Purpose | run day-to-day transactions | analyse history and trends |
| Design | normalized (3NF) | dimensional (star/snowflake) |
| Data | current state | historical, time-stamped |
| Workload | many small reads and writes | few large reads and aggregations |
| Updates | constant inserts, updates, deletes | periodic loads, mostly appends |
| Users | applications, customers, staff | analysts, managers, data scientists |
| Examples | PostgreSQL, MySQL, Oracle | Snowflake, BigQuery, Redshift, Synapse |

### Slowly changing dimensions (SCD) [INTERVIEW EXTENSION]

What should happen in the warehouse when a customer moves from Mumbai to Pune? That is the **slowly changing dimension** problem.

| Type | What happens | History kept? | Example use |
|---|---|---|---|
| Type 0 | never change the value | original only | date of birth |
| Type 1 | overwrite the old value | no | fixing a spelling mistake |
| Type 2 | add a **new row** with validity dates; old row is closed | full history | customer city, for correct historical reports |
| Type 3 | keep a "previous value" column | one level | `current_city`, `previous_city` |

Type 2 is the one interviewers ask about. Each version of the customer gets its own surrogate key:

```sql run keep quiet
CREATE TABLE dim_customer_scd2 (
    customer_sk    INT PRIMARY KEY,       -- surrogate key: one per version
    customer_id    INT NOT NULL,          -- business key from the source system
    customer_name  VARCHAR(60) NOT NULL,
    city           VARCHAR(40) NOT NULL,
    valid_from     DATE NOT NULL,
    valid_to       DATE,                  -- NULL = still the current version
    is_current     BOOLEAN NOT NULL
);

INSERT INTO dim_customer_scd2 VALUES
    (1, 1, 'Aarav Patel',   'Mumbai', '2023-11-05', '2024-02-29', false),
    (2, 1, 'Aarav Patel',   'Pune',   '2024-03-01', NULL,         true),
    (3, 2, 'Isha Kulkarni', 'Pune',   '2023-12-12', NULL,         true);
```

"Which city was Aarav in on 15 January 2024?" Sales made then should still count for Mumbai:

```sql run
SELECT customer_sk, customer_name, city
FROM dim_customer_scd2
WHERE customer_id = 1
  AND DATE '2024-01-15' >= valid_from
  AND (valid_to IS NULL OR DATE '2024-01-15' <= valid_to);
```

::: explain
"A data warehouse is a central store designed for analysis. It integrates data from many operational systems and keeps history. We usually model it dimensionally: fact tables hold the measurable events, like sales amount and quantity, with foreign keys to dimension tables that describe the context, such as date, product, customer and store. In a star schema each dimension joins directly to the fact table, which keeps queries simple and fast. A snowflake schema normalizes the dimensions further, saving space but adding joins. The first design decision is the grain, what one fact row means."
:::

::: trap
- Putting descriptive text (product names) in the fact table instead of a dimension.
- Forgetting to define the grain, which leads to double counting.
- Summing a semi-additive measure such as account balance over time.
- Saying a snowflake schema is "more advanced, therefore better". The star is the usual default.
- Confusing a data warehouse (curated, modelled, schema-on-write) with a data lake (raw files, schema-on-read). See Session 4.7.
:::

::: questions
#### Basic
Q: [DEFINITION] What is a data warehouse?
A: A central, integrated, historical store of data designed for analysis and reporting, separate from the operational systems.

Q: [COMPARISON] What is the difference between a fact table and a dimension table?
A: A fact table holds measures (numbers) of business events plus foreign keys; a dimension table holds descriptive attributes (who, what, when, where) used to filter and group the facts.

Q: [DEFINITION] What is a star schema?
A: A dimensional design with one central fact table connected directly to denormalized dimension tables.

#### Intermediate
Q: [COMPARISON] Star schema vs snowflake schema?
A: In a star, dimensions are denormalized single tables, so there are fewer joins and faster, simpler queries. In a snowflake, dimensions are normalized into sub-tables, so there is less redundancy but more joins.

Q: [DEFINITION] What is the grain of a fact table?
A: The level of detail one row represents, for example one row per order line or one row per store per day.

Q: [DEFINITION] What is a data mart?
A: A subject- or department-specific subset of the warehouse, such as a sales mart.

Q: [COMPARISON] OLTP database vs data warehouse?
A: OLTP is normalized, holds current data and handles many small transactions; a warehouse is dimensional, holds history and handles large analytical queries.

#### Scenario-based
Q: [DESIGN QUESTION] Design a star schema for a food-delivery company's order analytics.
A: Fact: `fact_order_line(date_key, time_key, customer_key, restaurant_key, item_key, rider_key, quantity, item_amount, delivery_fee, delivery_minutes)` at the grain of one row per item ordered. Dimensions: date, time of day, customer (city, segment), restaurant (cuisine, area), menu item (category, veg/non-veg), rider.

Q: [SCENARIO] A customer moved from Mumbai to Pune, and old sales now show under Pune. What went wrong and how do you fix it?
A: The dimension was overwritten (SCD Type 1). Use SCD Type 2: close the old row with a valid_to date, insert a new row with a new surrogate key, and point new facts at the new key. Old facts keep pointing to the Mumbai version.

#### Follow-up / Trap
Q: [TRAP QUESTION] Why do warehouses use surrogate keys instead of source system IDs?
A: To integrate several sources whose IDs may clash, to keep multiple versions of the same entity (SCD Type 2), and to stay independent of changes in source systems.

Q: [TRAP QUESTION] Can you sum an account balance across months?
A: No. Balance is semi-additive; sum it across accounts for one day, but use the closing or average balance across time.
:::

## Session 2.8 — NoSQL Data Modeling {: #s2-8 }

### Why NoSQL exists (the modeling view)

Relational databases are excellent, but some problems push against them:

- **Huge scale:** billions of rows and very high write rates, spread across many servers.
- **Changing structure:** products with completely different attributes (a laptop has RAM; a T-shirt has a size).
- **Known, simple access patterns:** "get a user's whole cart by user ID" a million times a second.

NoSQL databases relax some relational features (fixed schemas, joins, sometimes strict consistency) to gain flexibility and horizontal scale. Session 4.2 compares the database types; here we focus on **how you model data** in them, especially in document databases such as MongoDB.

### Schema flexibility (and its catch)

- Relational: **schema-on-write**. The table structure is fixed first; every row must fit.
- Document stores: **flexible schema**. Documents in the same collection can have different fields.

```javascript
// Two products in the same "products" collection
{ "_id": 1, "name": "ThinkPad E14", "category": "Laptop",
  "price": 62990, "specs": { "ram_gb": 16, "cpu": "Ryzen 5" } }

{ "_id": 2, "name": "Cotton Tee", "category": "Apparel",
  "price": 499, "sizes": ["S", "M", "L"], "colour": "navy" }
```

The catch: **"schemaless" does not mean "no design".** The schema moves into your application code. Without discipline you get `"price": "499"` in one document and `"price": 499` in another. MongoDB supports **schema validation** rules to prevent this.

### Embedding vs referencing

The central decision in document modeling: put related data **inside** one document (embed), or keep it in a separate document and store its ID (reference)?

[[fig:embedding_vs_referencing | Embedding keeps data that is read together in one document; referencing links separate documents by ID.]]

| | Embedding | Referencing |
|---|---|---|
| How | nested object or array inside the parent | store the other document's `_id` |
| Reads | one query returns everything | two queries, or a `$lookup` (a join) |
| Writes | update one document (atomic) | update the shared document once, everywhere sees it |
| Duplication | data may be repeated across parents | no duplication |
| Growth | risky if the array grows without limit (MongoDB documents max out at 16 MB) | fine for large or unbounded sets |
| Use when | "contains" relationships, one-to-few, read together, owned by the parent | many-to-many, large or unbounded sets, data shared and updated independently |

**Rules of thumb:**

- Order and its line items → **embed** (always read together, owned by the order, bounded).
- Order and customer → **reference** the customer (customer data is shared by many orders and changes independently). Optionally copy the name and address *as of the order* (denormalization for history).
- Blog post and comments → embed the latest few comments for fast display, and keep all comments in their own collection (a hybrid).
- Students and courses (many-to-many) → reference by ID on one or both sides.

### Access-pattern-driven design

Relational modeling starts from the **data** ("what are the entities?") and normalizes. NoSQL modeling starts from the **queries** ("what will the app ask for, how often?") and shapes documents so the most frequent queries need a single read.

1. List the access patterns, for example: "show order with items" (very frequent), "list a customer's last 10 orders" (frequent), "monthly revenue report" (rare, can run in a warehouse).
2. Design documents so each frequent pattern is one read.
3. Add indexes for the filters you use (`customer_id`, `order_date`).
4. Accept some duplication where it saves joins, and decide how copies will be updated.

| | Relational mindset | Document (NoSQL) mindset |
|---|---|---|
| Starting point | entities and normalization | access patterns (queries) |
| Duplication | avoid it | acceptable when it saves reads |
| Relationships | foreign keys + joins | embedding, or references with application-side joins |
| Schema | fixed, enforced by the DB | flexible, enforced by the app (plus optional validation) |
| Changing questions later | easy: new joins | harder: may need remodeling |

::: example A food-delivery order as one MongoDB document
```javascript
{
  "_id": "ORD-9001",
  "customer": { "customer_id": 42, "name": "Diya Joshi" },   // snapshot copy
  "restaurant_id": 17,                                        // reference
  "items": [                                                  // embedded
    { "name": "Paneer Biryani", "qty": 1, "price": 249 },
    { "name": "Gulab Jamun",    "qty": 2, "price": 60 }
  ],
  "delivery": { "address": "HSR Layout, Bengaluru", "status": "OUT_FOR_DELIVERY" },
  "total": 369,
  "created_at": ISODate("2024-04-19T19:42:00Z")
}
```
One read renders the whole order screen. The restaurant is referenced because its menu and details change independently; the customer's name is copied as it was at order time.
:::

::: extension Key-value and wide-column modeling in one paragraph
In key-value and wide-column stores (DynamoDB, Cassandra), you design around a **partition key** (which server holds the data, e.g. `customer_id`) and often a **sort key** (order inside the partition, e.g. `order_date`). Queries that do not use the partition key are expensive, so the table is shaped around exactly the queries you need. Some teams even store several entity types in one table ("single-table design").
:::

::: explain
"In NoSQL, especially document databases like MongoDB, we model around access patterns instead of normalizing first. The main decision is embedding versus referencing. I embed data that belongs to the parent and is read with it, like an order's line items, because one read returns everything and the update is atomic. I reference data that is shared, large, unbounded or updated independently, like the customer or a restaurant, to avoid duplication and huge documents. Flexible schema doesn't mean no schema; the structure lives in the application, ideally backed by validation rules."
:::

::: trap
- "NoSQL means no schema, so no design is needed." The design moves into the application and the access patterns.
- Embedding arrays that grow forever (all of a user's activity logs in the user document) and hitting the 16 MB document limit.
- Using MongoDB exactly like a relational database, with every relationship as a reference and `$lookup` everywhere. You lose the main benefit.
- Forgetting that duplicated (embedded) data must be updated in several places if it changes.
:::

::: questions
#### Basic
Q: [DEFINITION] What does "schema flexibility" mean in NoSQL?
A: Records (documents) in the same collection can have different fields, and the structure can evolve without migrating a fixed table schema.

Q: [COMPARISON] Embedding vs referencing in MongoDB?
A: Embedding stores related data inside the parent document (one read, atomic updates, possible duplication); referencing stores the related document's ID (no duplication, but extra queries or `$lookup`).

#### Intermediate
Q: [HOW] How do you decide whether to embed or reference?
A: Embed when the data is owned by the parent, read together, and bounded (one-to-few). Reference when it is shared, many-to-many, large or unbounded, or updated independently.

Q: [DEFINITION] What is access-pattern-driven design?
A: Designing the data model starting from the application's most frequent queries, so each of them can be served efficiently, often with a single read.

Q: [WHY] Why is denormalization common in NoSQL?
A: Many NoSQL systems have limited or expensive joins, and they are optimised for fast single-key reads at scale, so related data is stored together.

#### Scenario-based
Q: [DESIGN QUESTION] Model a blog with posts and thousands of comments per post in MongoDB.
A: Store posts in a `posts` collection, possibly embedding the latest five comments for quick display; store all comments in a separate `comments` collection with `post_id` and an index on (post_id, created_at). Embedding every comment would make documents unbounded.

Q: [SCENARIO] A product catalogue has very different attributes per category. SQL or document model?
A: A document model fits well because each product can carry its own attributes. In PostgreSQL, a JSONB column for category-specific attributes is a good middle ground.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does MongoDB support joins?
A: Yes, the `$lookup` stage in the aggregation pipeline performs a left-outer-join-like operation, but heavy reliance on it usually means the model should embed more.

Q: [TRAP QUESTION] Is there a limit to embedding?
A: Yes. A MongoDB document can be at most 16 MB, and large, ever-growing arrays also make updates and reads slower.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Give one example each of an additive and a semi-additive measure.

**P2.** Which schema has fewer joins: star or snowflake?

**P3.** True or false: in MongoDB, two documents in the same collection must have the same fields.

#### Level 2 — Interview application
**P4.** Explain the difference between a view and a materialized view, and when you would use each.

**P5.** You must store a user and their three saved addresses in MongoDB. Embed or reference? Why?

**P6.** Name three things that go into a dimension table and three that go into a fact table for a retail store.

#### Level 3 — Scenario / problem solving
**P7.** Design a star schema for a hospital that wants to analyse "number of appointments and revenue by doctor, department, month and patient age group". State the grain.

**P8.** Write a SQL query on this chapter's `fact_sales`, `dim_customer` and `dim_date` tables that returns revenue per customer city per quarter.
:::

::: answers
**P1.** Additive: sales amount (sum across any dimension). Semi-additive: inventory level or account balance (sum across products or stores, but not across days).

**P2.** The star schema.

**P3.** False. MongoDB has a flexible schema; documents can differ unless validation rules restrict them.

**P4.** A view is a saved query that runs on every read, so it is always current but costs the full query each time; use it to simplify or secure access. A materialized view stores the result, so it is fast to read but stale until refreshed; use it for expensive aggregations read often, such as dashboard summaries.

**P5.** Embed. The addresses belong to the user, there are only a few, and they are displayed together with the user, so one read and atomic updates are ideal.

**P6.** Dimension: product name and category, store city and region, the date's month and weekday. Fact: quantity sold, sales amount, discount amount.

**P7.** Grain: one row per appointment. Fact: `fact_appointment(date_key, doctor_key, department_key, patient_key, appointment_count = 1, consultation_fee, billed_amount)`. Dimensions: `dim_date` (day, month, quarter, year), `dim_doctor` (name, specialization, seniority), `dim_department` (name, building), `dim_patient` (gender, age_group, city). If age group changes over time, either store it in the fact at appointment time or use SCD Type 2.

**P8.** One possible answer:

```sql run
SELECT c.city,
       d.year,
       d.quarter,
       SUM(f.sales_amount) AS revenue
FROM fact_sales f
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_date     d ON d.date_key     = f.date_key
GROUP BY c.city, d.year, d.quarter
ORDER BY d.year, d.quarter, revenue DESC;
```

All sample orders fall in Q1 and Q2 of 2024, so there are only two quarters.
:::

## Session 2.9 — Module 2 Summary & Rapid Revision {: #s2-9 }

::: summary Module 2 Summary
#### Most important concepts
- **Data modeling** = entities, attributes, relationships and keys; conceptual → logical → physical.
- **Keys:** primary (unique + not null, one per table), foreign (points to a PK/unique key, enforces referential integrity), unique, composite, candidate, super, surrogate vs natural.
- **Relationships:** 1:N → FK on the many side; 1:1 → FK + UNIQUE; M:N → junction table.
- **Normalization:** removes update/insert/delete anomalies. 1NF atomic values; 2NF no partial dependency; 3NF no transitive dependency; BCNF every determinant is a super key.
- **Denormalization:** deliberate redundancy for faster reads (derived columns, summary tables, materialized views, star schemas).
- **Warehousing:** facts (measures) + dimensions (context); grain first; star (default) vs snowflake; SCD Type 2 keeps history.
- **NoSQL modeling:** access-pattern-driven; embed what is owned and read together, reference what is shared or unbounded.

#### What to memorize
- "The key, the whole key, and nothing but the key" (1NF, 2NF, 3NF).
- PK vs FK vs UNIQUE differences, including NULL rules.
- Star = denormalized dimensions, fewer joins; snowflake = normalized dimensions, more joins.

#### What to understand
- *Why* anomalies happen (one table storing facts about several things).
- *When* to break normalization, and what it costs.
- *How* the grain controls a fact table's correctness.

#### Most common interview questions
- Normalize this table. · 2NF vs 3NF? · PK vs unique key? · Can a FK be NULL? · How to model many-to-many? · Star vs snowflake? · Fact vs dimension? · Embed or reference?

#### Common mistakes
- 2NF for single-column keys · FK on the wrong side · lists in a column · FLOAT for money · facts holding descriptive text · "NoSQL needs no design".
:::

::: checklist
- [ ] I can explain conceptual vs logical vs physical models
- [ ] I can identify entities and relationships from a paragraph
- [ ] I know every type of key with an example
- [ ] I can explain PK vs FK vs UNIQUE (and NULL rules)
- [ ] I know the referential actions (CASCADE, SET NULL…)
- [ ] I can model 1:1, 1:N and M:N relationships
- [ ] I can name the three anomalies with examples
- [ ] I can normalize a table to 3NF step by step
- [ ] I can explain BCNF in one sentence
- [ ] I can justify when to denormalize
- [ ] I can design a star schema and state its grain
- [ ] I can compare star and snowflake schemas
- [ ] I can explain SCD Type 2
- [ ] I can decide between embedding and referencing
:::
