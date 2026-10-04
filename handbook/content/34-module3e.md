## Session 3.8 — Window Functions & Indexing (A): Window Functions {: #s3-8 }

[HIGH PRIORITY] Window functions separate strong SQL candidates from average ones. They solve ranking, "top N per group", running totals and "compare with the previous row" problems cleanly.

### Simple meaning

**A window function calculates a value across a set of rows related to the current row, without collapsing those rows.** GROUP BY squeezes each group into one row; a window function keeps every row and *adds* a column computed over its "window".

[[fig:groupby_vs_window | GROUP BY returns one row per group; a window function keeps every row and adds the group's value to each one.]]

### The syntax

```sql
function_name(...) OVER (
    PARTITION BY column     -- optional: restart the calculation for each group
    ORDER BY column         -- optional: order rows inside each partition
    ROWS BETWEEN ...        -- optional: the exact frame of rows to use
)
```

- `OVER ()` with nothing inside: the window is the **whole result set**.
- `PARTITION BY`: splits rows into groups, like GROUP BY, but **without collapsing** them.
- `ORDER BY` inside OVER: gives an order for ranking, LAG/LEAD and running totals.
- **Frame** (`ROWS BETWEEN …`): which rows around the current row are included (moving averages).

### OVER (): compare each row with the whole table

```sql run
SELECT emp_name,
       salary,
       ROUND(AVG(salary) OVER (), 2)                AS company_avg,
       ROUND(100.0 * salary / SUM(salary) OVER (), 2) AS pct_of_payroll
FROM employees
ORDER BY salary DESC
LIMIT 5;
```

Every row keeps its own data and also "sees" the totals. With GROUP BY, the employee rows would have disappeared.

### PARTITION BY: per-group values on every row

```sql run
SELECT emp_name,
       dept_id,
       salary,
       ROUND(AVG(salary) OVER (PARTITION BY dept_id), 2) AS dept_avg,
       COUNT(*)          OVER (PARTITION BY dept_id)     AS dept_size
FROM employees
WHERE dept_id IN (2, 3, 4)
ORDER BY dept_id, salary DESC;
```

::: linebyline
| Part | What it does |
|---|---|
| `AVG(salary) OVER (PARTITION BY dept_id)` | for each row, the average salary of that row's department |
| `COUNT(*) OVER (PARTITION BY dept_id)` | how many employees are in that row's department |
| `WHERE dept_id IN (2, 3, 4)` | runs **before** the window functions, so windows only see these rows |
:::

### Ranking: ROW_NUMBER, RANK and DENSE_RANK

The three ranking functions differ **only in how they treat ties**. In Engineering, Rahul and Sneha both earn 95000:

```sql run
SELECT emp_name,
       salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC, emp_id) AS row_number,
       RANK()       OVER (ORDER BY salary DESC)         AS rank,
       DENSE_RANK() OVER (ORDER BY salary DESC)         AS dense_rank
FROM employees
WHERE dept_id = 1
ORDER BY salary DESC, emp_id;
```

| Function | Ties get… | After a tie… | Sequence here |
|---|---|---|---|
| `ROW_NUMBER()` | different numbers (arbitrary unless you add a tie-breaker) | continues normally | 1, 2, 3, 4, 5, 6 |
| `RANK()` | the same number | **skips** numbers (gaps) | 1, 2, 3, 3, **5**, 6 |
| `DENSE_RANK()` | the same number | **no gaps** | 1, 2, 3, 3, **4**, 5 |

**Which one to use:**

- "Exactly one row per group" (latest order per customer, de-duplication) → `ROW_NUMBER`.
- "Nth highest *value*" (third-highest salary, counting ties once) → `DENSE_RANK`.
- "Competition ranking", like sports, where two people tied for 3rd place mean nobody is 4th → `RANK`.

The `emp_id` in ROW_NUMBER's ORDER BY is a **tie-breaker**: without it, which of Rahul and Sneha gets 3 and which gets 4 is not guaranteed.

### Ranking within groups: PARTITION BY + ORDER BY

```sql run
SELECT dept_id,
       emp_name,
       salary,
       DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rank_in_dept
FROM employees
WHERE dept_id IS NOT NULL
ORDER BY dept_id, rank_in_dept;
```

The ranking restarts at 1 for every department. This is the heart of "top N per group".

### Filtering on a window result

Window functions are computed **after** WHERE, GROUP BY and HAVING, so they cannot appear in WHERE:

```sql run error
SELECT emp_name, salary
FROM employees
WHERE DENSE_RANK() OVER (ORDER BY salary DESC) <= 3;
```

Compute the window in a subquery or CTE first, then filter in the outer query. Here are the top 2 earners per department:

```sql run
WITH ranked AS (
    SELECT dept_id, emp_name, salary,
           DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk
    FROM employees
    WHERE dept_id IS NOT NULL
)
SELECT dept_id, emp_name, salary, rnk
FROM ranked
WHERE rnk <= 2
ORDER BY dept_id, rnk;
```

::: extension QUALIFY
Snowflake, BigQuery and Databricks support `QUALIFY`, a WHERE clause for window results: `… QUALIFY DENSE_RANK() OVER (…) <= 2`. PostgreSQL does not, so use a CTE or subquery.
:::

### LAG and LEAD: the previous and next row

`LAG(col, n, default)` reads the value from **n rows before** the current row (default n = 1); `LEAD` reads **n rows after**. They need an `ORDER BY` inside OVER to define "before" and "after".

```sql run
SELECT sale_date,
       amount,
       LAG(amount)  OVER (ORDER BY sale_date) AS prev_day,
       amount - LAG(amount) OVER (ORDER BY sale_date) AS change,
       LEAD(amount) OVER (ORDER BY sale_date) AS next_day
FROM daily_sales
WHERE region = 'North'
ORDER BY sale_date;
```

::: linebyline
| Part | What it does |
|---|---|
| `LAG(amount) OVER (ORDER BY sale_date)` | the amount from the previous date; NULL for the first row |
| `amount - LAG(amount) …` | day-over-day change |
| `LEAD(amount) OVER (ORDER BY sale_date)` | the next date's amount; NULL for the last row |
:::

Add `PARTITION BY region` to compare within each region separately, and use the third argument for a default: `LAG(amount, 1, 0)` returns 0 instead of NULL on the first row.

### Running totals and moving averages

With `ORDER BY` inside OVER, aggregate functions become **cumulative**:

```sql run
SELECT region,
       sale_date,
       amount,
       SUM(amount) OVER (PARTITION BY region ORDER BY sale_date) AS running_total,
       ROUND(AVG(amount) OVER (PARTITION BY region ORDER BY sale_date
                               ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg_3d
FROM daily_sales
ORDER BY region, sale_date;
```

[[fig:window_frame | Window frames for the North region on 5 March: running total, 3-row moving average, and LAG/LEAD.]]

| Frame clause | Rows included |
|---|---|
| (default with ORDER BY) `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | from the first row of the partition up to the current row, **including rows tied with it** |
| `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | same, but counts physical rows (ties not grouped) |
| `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` | current row + 2 before it (a 3-row moving window) |
| `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING` | previous, current and next row (centred window) |
| `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` | the whole partition |

::: trap RANGE vs ROWS when the order has ties
With the default `RANGE` frame, rows that tie on the ORDER BY value are added to the running total **together**, so two orders on the same date both show the total *including each other*. If you want a strictly row-by-row running total, write `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` and add a tie-breaker to the ORDER BY.
:::

### Other useful window functions [INTERVIEW EXTENSION]

| Function | Returns |
|---|---|
| `NTILE(4)` | splits ordered rows into 4 nearly equal buckets (quartiles) |
| `FIRST_VALUE(col)` | first value in the window (e.g. the top salary in the department) |
| `LAST_VALUE(col)` | last value in the frame. With the default frame this is the current row, a common surprise; use `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` |
| `NTH_VALUE(col, n)` | the n-th value in the frame |
| `PERCENT_RANK()`, `CUME_DIST()` | relative rank as a fraction between 0 and 1 |

```sql run
SELECT emp_name,
       salary,
       NTILE(4) OVER (ORDER BY salary DESC)                            AS salary_quartile,
       FIRST_VALUE(emp_name) OVER (PARTITION BY dept_id ORDER BY salary DESC) AS top_earner_in_dept
FROM employees
WHERE dept_id IN (1, 2)
ORDER BY salary DESC;
```

### Window function vs GROUP BY

| | GROUP BY | Window function |
|---|---|---|
| Output rows | one per group | one per input row |
| Detail columns | lost (unless grouped) | kept |
| Typical use | totals, counts per group | ranking, running totals, comparing a row with its group or neighbours |
| Can filter on the result | with HAVING | in an outer query (or QUALIFY in some warehouses) |
| Runs | before SELECT | during SELECT, after WHERE / GROUP BY / HAVING |

::: explain
"Window functions compute values over a set of related rows without collapsing them, unlike GROUP BY. I use OVER with PARTITION BY to define the groups and ORDER BY to define the order inside each group. For ranking there are three options that differ only on ties: ROW_NUMBER gives every row a unique number, RANK gives ties the same rank and then skips numbers, and DENSE_RANK gives ties the same rank without gaps. So for the Nth highest salary I use DENSE_RANK, and for latest record per customer I use ROW_NUMBER. LAG and LEAD read the previous or next row, which is great for day-over-day changes, and SUM with ORDER BY inside OVER gives running totals. Since windows are calculated after WHERE, I filter on them in an outer query or CTE."
:::

::: trap
- Using a window function in WHERE: not allowed; wrap the query in a CTE or subquery.
- Using ROW_NUMBER when ties should share a rank (Nth highest *salary*): use DENSE_RANK.
- ROW_NUMBER without a deterministic ORDER BY: tied rows get arbitrary numbers.
- Forgetting ORDER BY inside OVER for LAG/LEAD or running totals.
- Expecting LAST_VALUE to return the partition's last row with the default frame.
- Forgetting that WHERE runs first: filtering rows changes what the window sees.
:::

::: questions
#### Basic
Q: [DEFINITION] What is a window function?
A: A function that computes a value over a set of rows related to the current row, defined with OVER(), while still returning every row.

Q: [COMPARISON] ROW_NUMBER vs RANK vs DENSE_RANK?
A: ROW_NUMBER numbers rows uniquely (1, 2, 3, 4). RANK gives ties the same rank and leaves gaps (1, 2, 2, 4). DENSE_RANK gives ties the same rank without gaps (1, 2, 2, 3).

Q: [DEFINITION] What does PARTITION BY do?
A: It divides rows into groups for the window calculation; the function restarts for each partition, but no rows are collapsed.

Q: [DEFINITION] What do LAG and LEAD do?
A: LAG returns a value from a previous row and LEAD from a following row, in the order given inside OVER.

#### Intermediate
Q: [COMPARISON] Window function vs GROUP BY?
A: GROUP BY returns one row per group and loses detail; window functions keep every row and add group-level or ordered calculations alongside.

Q: [SQL PROBLEM] How do you compute a running total of sales by date?
A: `SUM(amount) OVER (ORDER BY sale_date)` (add `PARTITION BY region` for one running total per region).

Q: [WHY] Why can't you filter on ROW_NUMBER() in the WHERE clause?
A: Window functions are evaluated after WHERE (and GROUP BY/HAVING). Compute them in a subquery or CTE, then filter in the outer query.

Q: [DEFINITION] What is a window frame?
A: The subset of rows within the partition used for the current row's calculation, e.g. `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` for a 3-row moving average.

Q: [HOW] How would you calculate each employee's salary as a percentage of their department's total?
A: `100.0 * salary / SUM(salary) OVER (PARTITION BY dept_id)`.

#### Scenario-based
Q: [SQL PROBLEM] Find the second-highest salary in each department.
A: Use `DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC)` in a CTE and keep rows where the rank = 2.

Q: [SQL PROBLEM] Show each day's sales and the percentage change from the previous day.
A: `ROUND(100.0 * (amount - LAG(amount) OVER (ORDER BY sale_date)) / LAG(amount) OVER (ORDER BY sale_date), 2)`. Optionally use `NULLIF` on the denominator to avoid division by zero.

Q: [SCENARIO] A "latest order per customer" report sometimes shows two orders for the same customer. Why, and how do you fix it?
A: Probably RANK/DENSE_RANK on order_date, so ties on the same date share rank 1. Use ROW_NUMBER with a tie-breaker (`ORDER BY order_date DESC, order_id DESC`).

#### Follow-up / Trap
Q: [TRAP QUESTION] With the default frame, what does a running SUM do for rows with the same ORDER BY value?
A: The default frame is RANGE, so peer rows (ties) are included together and get the same running total. Use ROWS for row-by-row accumulation.

Q: [TRAP QUESTION] Can window functions be used with GROUP BY in the same query?
A: Yes. The window is applied to the grouped result, e.g. `RANK() OVER (ORDER BY SUM(sales) DESC)` ranks groups by their totals.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Number all products from cheapest to most expensive with ROW_NUMBER.

**P2.** What will DENSE_RANK return for the salaries 100, 90, 90, 80 (highest first)?

**P3.** Show each order with the previous order's date for the same customer.

#### Level 2 — Interview application
**P4.** For each region in `daily_sales`, show each day's amount and the region's total for the week on every row.

**P5.** Rank customers by total revenue (excluding cancelled orders) using RANK.

#### Level 3 — Scenario / problem solving
**P6.** Find, for each customer, their most expensive order, using a window function (one row per customer).

**P7.** Find days where North's sales were higher than on both the previous and the next day (a "local peak").
:::

::: answers
**P1.**

```sql run
SELECT ROW_NUMBER() OVER (ORDER BY price, product_id) AS rn,
       product_name, price
FROM products;
```

**P2.** 1, 2, 2, 3 (RANK would give 1, 2, 2, 4).

**P3.**

```sql run
SELECT customer_id, order_id, order_date,
       LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS prev_order_date
FROM orders
ORDER BY customer_id, order_date
LIMIT 7;
```

**P4.**

```sql run
SELECT region, sale_date, amount,
       SUM(amount) OVER (PARTITION BY region) AS region_week_total
FROM daily_sales
ORDER BY region, sale_date
LIMIT 8;
```

Without ORDER BY inside OVER, the window is the whole partition, so every row shows the full total.

**P5.**

```sql run
SELECT c.customer_name,
       SUM(o.total_amount) AS revenue,
       RANK() OVER (ORDER BY SUM(o.total_amount) DESC) AS revenue_rank
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status <> 'CANCELLED'
GROUP BY c.customer_name
ORDER BY revenue_rank;
```

The window runs after GROUP BY, so it can rank by `SUM(…)`.

**P6.**

```sql run
WITH ranked AS (
    SELECT customer_id, order_id, total_amount,
           ROW_NUMBER() OVER (PARTITION BY customer_id
                              ORDER BY total_amount DESC, order_id) AS rn
    FROM orders
)
SELECT customer_id, order_id, total_amount
FROM ranked
WHERE rn = 1
ORDER BY customer_id;
```

**P7.**

```sql run
WITH n AS (
    SELECT sale_date, amount,
           LAG(amount)  OVER (ORDER BY sale_date) AS prev_amt,
           LEAD(amount) OVER (ORDER BY sale_date) AS next_amt
    FROM daily_sales
    WHERE region = 'North'
)
SELECT sale_date, amount
FROM n
WHERE amount > prev_amt AND amount > next_amt;
```

The first and last days are excluded automatically: their `prev_amt` or `next_amt` is NULL, and a comparison with NULL is not TRUE.
:::

## Session 3.9 — Window Functions & Indexing (B): Indexing {: #s3-9 }

[HIGH PRIORITY] "What is an index? Why not index every column?" is a top-10 DBMS question.

### Simple meaning

**An index is a separate, sorted data structure that helps the database find rows quickly without reading the whole table.**

::: analogy The index at the back of a book
To find "normalization" in a 600-page book you don't read every page; you check the index, which lists the topic alphabetically with page numbers, and jump straight there. A database index does the same: it stores column values in sorted order with pointers to the rows. And like a book index, it takes extra pages and must be updated whenever the content changes.
:::

### Why indexes exist

Without an index, a query like `WHERE customer_id = 4242` forces a **full table (sequential) scan**: read every row and test it. That is fine for 14 rows and painful for 200 million. An index turns it into a few page reads.

Indexes speed up:

- `WHERE` filters on selective columns (`email = …`, `customer_id = …`);
- `JOIN`s on foreign keys;
- `ORDER BY … LIMIT` (rows are already sorted in the index);
- uniqueness checks: PRIMARY KEY and UNIQUE constraints automatically create an index.

### How a B-tree index works

The default index type in PostgreSQL (and most databases) is the **B-tree** (balanced tree). Values are kept sorted in a shallow tree of pages. Searching starts at the root and moves down one level at a time. Even a billion values need only around 4–5 levels, so the search cost grows **logarithmically**, not linearly. The leaf pages are linked to each other, which makes range scans (`BETWEEN`, `>`, `ORDER BY`) efficient.

[[fig:btree_index | Searching a B-tree index: three short hops lead to the matching rows instead of scanning the whole table.]]

### Seeing it for real: a 200,000-row table

The block below creates a larger table with deterministic data. Each customer has exactly 4 orders, and the status values are deliberately skewed: 70% DELIVERED and 10% for each other status.

```sql run keep quiet
CREATE TABLE orders_big AS
SELECT g                                      AS order_id,
       (g * 7919) % 50000 + 1                 AS customer_id,
       DATE '2023-01-01' + (g % 730)          AS order_date,
       ROUND(((g * 37) % 50000) / 100.0 + 100, 2) AS amount,
       CASE WHEN g % 10 < 7 THEN 'DELIVERED'
            WHEN g % 10 = 7 THEN 'PENDING'
            WHEN g % 10 = 8 THEN 'SHIPPED'
            ELSE 'CANCELLED' END              AS status
FROM generate_series(1, 200000) AS g;

ALTER TABLE orders_big ADD PRIMARY KEY (order_id);
ANALYZE orders_big;
```

**Before indexing**, look up one customer's orders. `EXPLAIN ANALYZE` shows how PostgreSQL actually executed the query (parallelism is switched off so the plan stays simple):

```sql run plan
SET LOCAL max_parallel_workers_per_gather = 0;
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF, SUMMARY OFF)
SELECT * FROM orders_big WHERE customer_id = 4242;
```

`Seq Scan … Rows Removed by Filter: 199996`: PostgreSQL read all 200,000 rows to find 4.

Now create an index and run the same query:

```sql run keep quiet
CREATE INDEX idx_orders_big_customer ON orders_big (customer_id);
ANALYZE orders_big;
```

```sql run plan
SET LOCAL max_parallel_workers_per_gather = 0;
EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF, SUMMARY OFF)
SELECT * FROM orders_big WHERE customer_id = 4242;
```

`Bitmap Index Scan on idx_orders_big_customer` found the 4 matching rows directly, and only 4 table pages were visited (`Heap Blocks: exact=4`) instead of the whole table.

::: linebyline
| Plan line | Meaning |
|---|---|
| `Seq Scan on orders_big` | read the table from start to end |
| `Rows Removed by Filter: 199996` | rows read and thrown away; the cost of having no index |
| `Bitmap Index Scan on idx_orders_big_customer` | use the index to collect the locations of matching rows |
| `Bitmap Heap Scan … Heap Blocks: exact=4` | then fetch just those table pages |
| `Index Cond` / `Recheck Cond` | the condition applied through the index |
:::

### Why indexes slow down writes

An index is a second copy of some data, kept sorted. Every `INSERT`, every `DELETE` and every `UPDATE` of an indexed column must also update **every index** on the table. A table with ten indexes does roughly ten extra pieces of work per insert. Indexes also use disk and memory.

| | Without an index | With an index |
|---|---|---|
| Lookup of a few rows in a big table | slow: full scan | fast: a few page reads |
| Range queries and `ORDER BY` on the column | sort or scan everything | read in order from the index |
| INSERT / UPDATE / DELETE | faster | slower: index maintenance |
| Storage | less | more (each index is extra pages) |
| Small tables | fine | little or no benefit |

### Selectivity: when the database ignores your index

An index helps when the condition picks a **small fraction** of rows. If a value matches a large share of the table, reading the whole table sequentially is cheaper than jumping between index and table thousands of times. The optimizer decides using statistics:

```sql run keep quiet
CREATE INDEX idx_orders_big_status ON orders_big (status);
ANALYZE orders_big;
```

```sql run plan
SET LOCAL max_parallel_workers_per_gather = 0;
EXPLAIN (COSTS OFF)
SELECT * FROM orders_big WHERE status = 'DELIVERED';    -- 70% of rows
```

```sql run plan
SET LOCAL max_parallel_workers_per_gather = 0;
EXPLAIN (COSTS OFF)
SELECT * FROM orders_big WHERE status = 'CANCELLED';    -- 10% of rows
```

Same index, two different plans: a sequential scan for the common value, the index for the rarer one. That is why indexing a low-variety column (status, gender, a true/false flag) on its own often brings little benefit.

### Composite indexes and the leftmost-prefix rule

A **composite (multi-column) index** sorts by the first column, then by the second within each first value, like a phone book sorted by surname, then first name.

```sql run keep quiet
DROP INDEX idx_orders_big_customer;      -- replaced by the composite index below
CREATE INDEX idx_orders_big_cust_date ON orders_big (customer_id, order_date);
ANALYZE orders_big;
```

```sql run plan
SET LOCAL max_parallel_workers_per_gather = 0;
EXPLAIN (COSTS OFF)
SELECT * FROM orders_big
WHERE customer_id = 4242 AND order_date >= '2024-01-01';
```

```sql run plan
SET LOCAL max_parallel_workers_per_gather = 0;
EXPLAIN (COSTS OFF)
SELECT * FROM orders_big WHERE order_date = '2024-01-01';
```

The composite index serves queries on `customer_id`, or on `customer_id` **and** `order_date`. It cannot efficiently serve a query on **only** `order_date`, the second column, just as a phone book sorted by surname cannot quickly find everyone named "Priya". This is the **leftmost-prefix rule**:

| Index on `(a, b, c)` helps with… | Does not help (efficiently) with… |
|---|---|
| `WHERE a = ?` | `WHERE b = ?` |
| `WHERE a = ? AND b = ?` | `WHERE c = ?` |
| `WHERE a = ? AND b = ? AND c = ?` | `WHERE b = ? AND c = ?` |
| `WHERE a = ? ORDER BY b` | |

**Column order matters:** put the column used in equality filters (and the most frequently filtered one) first, and range or sort columns after it.

### Clustered vs non-clustered indexes

| | Clustered index | Non-clustered (secondary) index |
|---|---|---|
| What it is | the table's rows are **physically stored in the index order**; the index *is* the table | a separate structure holding keys plus pointers to the rows |
| How many per table | one (rows can be sorted only one way) | many |
| Lookup | finds the row directly | finds the pointer, then fetches the row |
| Examples | SQL Server clustered index; MySQL InnoDB's primary key | most other indexes |
| Analogy | a dictionary: the content itself is in order | the index at the back of a textbook |

**PostgreSQL specifics:** PostgreSQL stores tables as an unordered **heap**, so *all* its indexes are non-clustered (secondary), including the primary key. The `CLUSTER` command physically reorders a table by an index **once**, but the order is not maintained for new rows. Saying this in an interview shows real depth.

### PostgreSQL index types [INTERVIEW EXTENSION]

| Type | Good for |
|---|---|
| B-tree (default) | equality and range on sortable data: numbers, text, dates |
| Hash | equality only |
| GIN | "contains" queries: JSONB keys, arrays, full-text search |
| GiST / SP-GiST | geometric, location and range data; nearest-neighbour searches |
| BRIN | very large tables whose values follow physical order (time-series logs); tiny index size |

Also useful: **unique indexes**, **partial indexes** (`CREATE INDEX … WHERE status = 'PENDING'` indexes only the rows you query), **expression indexes** (`CREATE INDEX ON customers (LOWER(email))`), and **covering indexes** (`INCLUDE (amount)`) that let PostgreSQL answer from the index alone ("index-only scan").

### When indexes help and when they hurt

| Indexes help when… | Indexes hurt or are wasted when… |
|---|---|
| the column is used often in WHERE, JOIN or ORDER BY | the table is small (a scan is already cheap) |
| the filter is selective (few matching rows) | the column has few distinct values and is queried on common values |
| the column is a foreign key used in joins | the table is write-heavy and rarely read |
| queries need sorted output with LIMIT | the query wraps the column in a function (`WHERE UPPER(email) = …`) without an expression index |
| you need to enforce uniqueness | `LIKE '%text'` with a leading wildcard (B-tree can't help) |
| | there are too many overlapping indexes (slower writes, more storage) |

**Practical checklist:** index foreign keys that you join on; check slow queries with `EXPLAIN ANALYZE`; prefer one well-designed composite index over several single-column ones; remove unused indexes (`pg_stat_user_indexes` shows usage counts).

::: explain
"An index is a separate data structure, usually a B-tree, that keeps a column's values sorted with pointers to the rows, so the database can find matching rows in a few steps instead of scanning the whole table, like the index at the back of a book. It speeds up selective WHERE filters, joins and ORDER BY. The cost is that every insert, update and delete must also update the indexes, and they take extra storage, so I index the columns that are filtered or joined on frequently, not every column. With a composite index, column order matters because of the leftmost-prefix rule. And the optimizer may still choose a full scan if a condition matches a large part of the table."
:::

::: trap
- "Indexes always make queries faster." Not for small tables, low-selectivity conditions or write-heavy workloads.
- "Index every column." Each index slows writes and uses storage.
- Expecting an index on `(a, b)` to help a query on `b` alone.
- Wrapping an indexed column in a function or casting it in WHERE, which prevents normal index use.
- Saying the primary key is a clustered index in PostgreSQL. It isn't; PostgreSQL tables are heaps.
- Forgetting that PRIMARY KEY and UNIQUE create indexes automatically, while foreign keys do **not** in PostgreSQL.
:::

::: questions
#### Basic
Q: [DEFINITION] What is an index?
A: A data structure (usually a B-tree) that stores column values in sorted order with pointers to rows, so the database can find rows without scanning the whole table.

Q: [WHY] Why do indexes slow down inserts and updates?
A: Every index on the table must be updated whenever a row is inserted, deleted, or has an indexed column changed, which adds extra work per write.

Q: [DEFINITION] What is a composite index?
A: An index on two or more columns, sorted by the first column, then the second, and so on.

#### Intermediate
Q: [COMPARISON] Clustered vs non-clustered index?
A: A clustered index stores the table rows themselves in index order (only one per table, e.g. the InnoDB primary key); a non-clustered index is a separate structure with pointers to rows (many allowed). PostgreSQL has only non-clustered indexes; its tables are heaps.

Q: [DEFINITION] What is the leftmost-prefix rule?
A: A composite index on (a, b, c) can be used for conditions on a, on a and b, or on a, b and c, but not efficiently for b or c alone.

Q: [WHY] Why might the database not use an index that exists?
A: The condition matches too many rows (low selectivity), the table is small, the column is wrapped in a function or cast, the condition is a leading-wildcard LIKE, statistics are outdated, or the query does not use the index's leading column.

Q: [HOW] How do you check whether a query uses an index?
A: Run `EXPLAIN` (or `EXPLAIN ANALYZE` for the actual execution) and look for Index Scan, Bitmap Index Scan or Index Only Scan instead of Seq Scan.

Q: [DEFINITION] What is a covering index?
A: An index that contains all the columns a query needs (in PostgreSQL via `INCLUDE`), so the query is answered from the index alone without visiting the table.

#### Scenario-based
Q: [SCENARIO] A query `SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC LIMIT 10` is slow on 50 million rows. What index would you create?
A: A composite index on `(customer_id, order_date DESC)`. It filters by customer and returns rows already sorted, so the LIMIT can stop after 10.

Q: [SCENARIO] Reads are fast but bulk inserts became very slow after the team added 12 indexes. What would you do?
A: Review index usage (`pg_stat_user_indexes`), drop unused or redundant indexes, merge overlapping ones into composites, and for big loads consider dropping and recreating non-essential indexes around the load.

Q: [SCENARIO] Users search customers by email in any case ("Aarav@Mail.com"). How do you make that fast?
A: Store emails consistently, or create an expression index `CREATE INDEX ON customers (LOWER(email))` and query `WHERE LOWER(email) = LOWER(:input)`.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does PostgreSQL automatically index foreign keys?
A: No. Primary keys and unique constraints get indexes automatically; foreign key columns do not, and should usually be indexed manually for joins and for deletes on the parent table.

Q: [TRAP QUESTION] Will an index on `gender` speed up `WHERE gender = 'F'`?
A: Usually not much: about half the table matches, so a sequential scan is cheaper and the optimizer will likely ignore the index.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Write the SQL to create an index on `employees(city)`.

**P2.** Name two operations that become slower because of indexes.

**P3.** Which index does PostgreSQL create automatically when you declare a PRIMARY KEY?

#### Level 2 — Interview application
**P4.** You have an index on `(last_name, first_name)`. Which of these can use it efficiently: (a) `WHERE last_name = 'Rao'`, (b) `WHERE first_name = 'Asha'`, (c) `WHERE last_name = 'Rao' AND first_name = 'Asha'`?

**P5.** Explain why `WHERE EXTRACT(YEAR FROM order_date) = 2024` may not use an index on `order_date`, and rewrite it.

#### Level 3 — Scenario / problem solving
**P6.** An `orders` table receives 5,000 inserts per second and is queried mainly by `order_id` and occasionally by `customer_id` for a support screen. Which indexes would you create, and which would you avoid?

**P7.** A dashboard query filters `status = 'PENDING'` (2% of rows) on a 100-million-row table. Suggest an index that stays small.
:::

::: answers
**P1.** `CREATE INDEX idx_employees_city ON employees (city);`

**P2.** INSERTs and DELETEs (plus UPDATEs of indexed columns). Bulk loads are hit hardest.

**P3.** A unique B-tree index on the primary key column(s).

**P4.** (a) yes, (c) yes, (b) not efficiently, because `first_name` is not the leftmost column.

**P5.** The function is applied to every row's `order_date`, so the plain index on `order_date` can't be searched directly. Use a range instead: `WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01'`, or create an expression index on `EXTRACT(YEAR FROM order_date)`.

**P6.** Keep the primary key index on `order_id` (it is automatic). Add one index on `customer_id`, because the support screen needs it and it is a foreign key. Avoid indexes on low-selectivity or rarely queried columns such as status or amount: each extra index costs work on all 5,000 inserts per second.

**P7.** A partial index: `CREATE INDEX idx_orders_pending ON orders (order_date) WHERE status = 'PENDING';` It contains only the 2% of rows the dashboard reads, so it stays small and fast, and it does not grow with delivered orders.
:::
