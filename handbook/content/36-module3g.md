## Session 3.11 — SQL Interview Patterns (Practice Programs) {: #s3-11 }

<p class="lead">Interviewers reuse a small set of problem shapes. Once you recognise the shape, you know the tool. This session covers 22 patterns; each one has the idea, a tiny worked example run on the sample database, the general approach, the variations you will be asked, the difficulty, and the usual mistakes.</p>

::: tip How to attack any SQL question in an interview
1. **Restate** the question and ask about edge cases: "Should ties count once or twice? Include customers with no orders? What about NULLs?"
2. **Identify the grain** of the answer: one row per what? (customer, department, day…)
3. **Pick the pattern**: filter, aggregate, join, anti-join, rank, running total…
4. **Build it in steps** (a CTE per step), say each step out loud, then check it against a couple of rows by hand.
5. **Mention alternatives and performance** briefly: "This could also be done with a window function; an index on customer_id would help."
:::

| # | Pattern | Main tool | Difficulty |
|---|---|---|---|
| 1 | Filtering | WHERE, AND/OR, IN, BETWEEN, LIKE, NULL | [EASY] |
| 2 | Aggregation | COUNT, SUM, AVG, MIN, MAX | [EASY] |
| 3 | GROUP BY + HAVING | GROUP BY, HAVING | [EASY] |
| 4 | Joining multiple tables | JOIN chains | [EASY] – [MEDIUM] |
| 5 | Find duplicates | GROUP BY … HAVING COUNT(*) > 1 | [EASY] |
| 6 | Remove duplicates | ROW_NUMBER, DELETE … USING | [MEDIUM] |
| 7 | Nth highest salary | DENSE_RANK, OFFSET | [MEDIUM] |
| 8 | Second highest salary | MAX with subquery | [EASY] – [MEDIUM] |
| 9 | Top N per group | ROW_NUMBER / DENSE_RANK + PARTITION BY | [MEDIUM] |
| 10 | Above the group average | window AVG, join to aggregate | [MEDIUM] |
| 11 | Customers with no orders | LEFT JOIN … IS NULL, NOT EXISTS | [EASY] |
| 12 | Latest record per user | ROW_NUMBER, DISTINCT ON | [MEDIUM] |
| 13 | Finding missing records | generate_series, anti-join | [MEDIUM] |
| 14 | Ranking | RANK, DENSE_RANK | [MEDIUM] |
| 15 | Running totals | SUM() OVER (ORDER BY …) | [MEDIUM] |
| 16 | Previous / next row | LAG, LEAD | [MEDIUM] |
| 17 | Date-based analysis | DATE_TRUNC, EXTRACT, intervals | [MEDIUM] |
| 18 | Conditional aggregation | SUM(CASE…), FILTER | [MEDIUM] |
| 19 | Subquery problems | scalar / correlated subqueries | [MEDIUM] |
| 20 | CTE problems | chained WITH steps | [MEDIUM] |
| 21 | Self joins | table joined to itself | [MEDIUM] |
| 22 | Window-function problems | gaps and islands, percentages | [HARD] |

### Pattern 1 — Filtering {: .intoc }

[EASY] · asked in almost every interview, often as a warm-up

**The pattern.** Return the rows that satisfy several conditions. It looks trivial, which is exactly why mistakes with AND/OR, NULLs, ranges and case sensitivity are noticed.

**General approach.** Write each condition separately, combine them with parentheses, check NULL behaviour, and use half-open ranges for dates.

```sql run
SELECT emp_name, city, salary, hire_date
FROM employees
WHERE (city = 'Bengaluru' OR city = 'Hyderabad')
  AND salary BETWEEN 70000 AND 130000
  AND hire_date >= '2019-01-01'
ORDER BY salary DESC;
```

**Variations interviewers ask:** names starting with a letter (`LIKE 'A%'`), case-insensitive search (`ILIKE`), "not in these cities", rows with missing values (`IS NULL`), orders in the last 30 days (`order_date >= CURRENT_DATE - 30`).

**Common mistakes:** missing parentheses around OR; `= NULL`; `BETWEEN` on timestamps; `NOT IN` with NULLs; quoting numbers as strings.

### Pattern 2 — Aggregation {: .intoc }

[EASY] · "How many…?", "What is the total / average…?"

**The pattern.** Summarise many rows into a few numbers.

**General approach.** Decide which rows count (WHERE), which aggregate answers the question, and whether duplicates should be counted once (`COUNT(DISTINCT …)`).

```sql run
SELECT COUNT(*)                    AS orders,
       COUNT(DISTINCT customer_id) AS unique_customers,
       SUM(total_amount)           AS revenue,
       ROUND(AVG(total_amount), 2) AS avg_order_value,
       MAX(total_amount)           AS biggest_order
FROM orders
WHERE status <> 'CANCELLED'
  AND order_date >= '2024-01-01' AND order_date < '2024-04-01';   -- Q1 2024
```

**Variations:** average excluding zeros or NULLs, percentage of total, minimum and maximum dates, count of non-null values.

**Common mistakes:** `COUNT(column)` silently skipping NULLs; integer division in averages and percentages; forgetting to exclude cancelled or test records.

### Pattern 3 — GROUP BY + HAVING {: .intoc }

[EASY] · reported in PwC write-ups ("write a query which uses GROUP BY")

**The pattern.** One result row per group, then keep only the groups that pass a condition on an aggregate.

**General approach.** WHERE for row filters → GROUP BY the grain → aggregate → HAVING for group filters → ORDER BY.

```sql run
SELECT c.customer_name,
       COUNT(*)            AS orders,
       SUM(o.total_amount) AS spent
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status <> 'CANCELLED'
GROUP BY c.customer_name
HAVING COUNT(*) >= 2
ORDER BY spent DESC;
```

**Variations:** departments with more than N employees; categories with revenue above X; cities whose average salary exceeds the company average (HAVING with a subquery, Pattern 19).

**Common mistakes:** aggregates in WHERE; selecting non-grouped columns; using a SELECT alias in HAVING (PostgreSQL).

### Pattern 4 — Joining Multiple Tables {: .intoc }

[EASY] – [MEDIUM] · "Show X with details from Y and Z"

**The pattern.** Walk the foreign-key path between tables to bring together columns that live in different places.

**General approach.** Draw the path (customers → orders → order_items → products), join one hop at a time on the key pairs, choose INNER vs LEFT for each hop, then aggregate.

```sql run
SELECT c.city,
       p.category,
       SUM(i.quantity * i.unit_price) AS revenue
FROM customers c
JOIN orders o      ON o.customer_id = c.customer_id
JOIN order_items i ON i.order_id    = o.order_id
JOIN products p    ON p.product_id  = i.product_id
WHERE o.status NOT IN ('CANCELLED', 'RETURNED')
GROUP BY c.city, p.category
ORDER BY c.city, revenue DESC;
```

**Variations:** best-selling product per city, employees with department and manager names (two joins, one a self join), order lines with customer and product names.

**Common mistakes:** fan-out double counting (summing an order-level column after joining items); an accidental cross join from a missing condition; LEFT JOIN undone by a WHERE on the right table.

### Pattern 5 — Find Duplicates {: .intoc }

[EASY] · very common in data-quality and consulting contexts

**The pattern.** Identify values that appear more than once.

**General approach.** Group by the column(s) that define "duplicate" and keep groups with `COUNT(*) > 1`. To see the full duplicate rows, use a window count.

```sql run
SELECT email, COUNT(*) AS copies
FROM leads
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY copies DESC;
```

Show every row that belongs to a duplicate group:

```sql run
SELECT lead_id, full_name, email, created_at
FROM (SELECT l.*, COUNT(*) OVER (PARTITION BY email) AS copies
      FROM leads l) t
WHERE copies > 1
ORDER BY email, lead_id;
```

**Variations:** duplicates across several columns (`GROUP BY first_name, last_name, dob`); case-insensitive duplicates (`GROUP BY LOWER(TRIM(email))`); duplicate orders within 5 minutes (self join or LAG).

**Common mistakes:** grouping by `lead_id` (every row is unique); ignoring case and whitespace differences; not agreeing on the definition of "duplicate" first.

### Pattern 6 — Remove Duplicates {: .intoc }

[MEDIUM] · "Delete duplicate rows but keep one"

**The pattern.** Keep one row per duplicate group (usually the first or the latest) and delete or ignore the rest.

**General approach.** Number the rows inside each group with `ROW_NUMBER() OVER (PARTITION BY dup_key ORDER BY keep_rule)`; rows with `rn > 1` are the extras.

```sql run
DELETE FROM leads
WHERE lead_id IN (
    SELECT lead_id
    FROM (SELECT lead_id,
                 ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at, lead_id) AS rn
          FROM leads) ranked
    WHERE rn > 1
)
RETURNING lead_id, full_name, email;
```

::: linebyline
| Part | What it does |
|---|---|
| `ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at, lead_id)` | numbers each email's rows from oldest to newest: 1, 2, 3… |
| `WHERE rn > 1` | every row except the first per email |
| `DELETE … WHERE lead_id IN (…)` | deletes exactly those rows |
| `RETURNING …` | shows what was deleted (this example was rolled back afterwards) |
:::

**Other ways:** `DELETE … USING` with a self join (shown in Session 3.4, P7); a de-duplicated *view* without deleting anything: `SELECT DISTINCT ON (email) * FROM leads ORDER BY email, created_at;`; or `CREATE TABLE clean AS SELECT DISTINCT …` and swap the tables.

**Common mistakes:** deleting *all* copies (including the one to keep); a non-deterministic keep rule (no tie-breaker); running the DELETE without first checking the SELECT; tables with no unique ID (then use `ctid` in PostgreSQL or rebuild the table).

### Pattern 7 — Nth Highest Salary {: .intoc }

[MEDIUM] · one of the most famous SQL interview questions

**The pattern.** Find the Nth largest *distinct* value. The trick is ties: two people earning 95000 should count as **one** salary level.

**General approach (recommended):** `DENSE_RANK()` over the value descending, then keep rank = N. It handles ties and generalises to "per group".

```sql run
SELECT emp_name, salary
FROM (SELECT emp_name, salary,
             DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
      FROM employees) ranked
WHERE rnk = 4
ORDER BY emp_name;
```

The distinct salaries in order are 150000, 120000, 110000, **95000**…, so the 4th highest is 95000, and both people at that level are returned.

**Alternative 1: DISTINCT + OFFSET** (just the value):

```sql run
SELECT DISTINCT salary
FROM employees
ORDER BY salary DESC
OFFSET 3 LIMIT 1;           -- skip N-1 values
```

**Alternative 2: correlated subquery** (works in any SQL dialect, slower on big tables): the Nth highest salary is the one that has exactly N − 1 distinct salaries above it.

```sql run
SELECT DISTINCT e1.salary
FROM employees e1
WHERE 3 = (SELECT COUNT(DISTINCT e2.salary)
           FROM employees e2
           WHERE e2.salary > e1.salary);
```

**Variations:** Nth highest per department (add `PARTITION BY dept_id`); return NULL when there is no Nth value; write it as a function with N as a parameter.

**Common mistakes:** `ROW_NUMBER` or `ORDER BY … OFFSET` without `DISTINCT`, which counts ties twice and returns the wrong level; `RANK` (gaps make rank = N disappear after a tie); forgetting the "no result" case.

### Pattern 8 — Second Highest Salary {: .intoc }

[EASY] – [MEDIUM] · the classic special case of Pattern 7

**General approach.** The highest salary that is *below* the maximum:

```sql run
SELECT MAX(salary) AS second_highest
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
```

This form returns **NULL** automatically when there is no second salary (everyone earns the same), which many online judges expect. The OFFSET version returns *no row* instead; wrapping it as a scalar subquery turns that into NULL:

```sql run
SELECT (SELECT DISTINCT salary
        FROM employees
        ORDER BY salary DESC
        OFFSET 1 LIMIT 1) AS second_highest;
```

**Per department**, with ties shown:

```sql run
SELECT d.dept_name, r.emp_name, r.salary
FROM (SELECT emp_name, dept_id, salary,
             DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk
      FROM employees) r
JOIN departments d ON d.dept_id = r.dept_id
WHERE r.rnk = 2
ORDER BY d.dept_name, r.emp_name;
```

In Finance, Karan and Meera share second place at 70000, and both are returned.

**Common mistakes:** `ORDER BY salary DESC LIMIT 1 OFFSET 1` without DISTINCT (wrong when the top salary is tied); not stating what should happen with ties or with no second value.

### Pattern 9 — Top N per Group {: .intoc }

[MEDIUM] · "top 2 products in each category", "top 3 earners per department"

**The pattern.** Rank inside each group and keep the first N.

**General approach.** Aggregate if needed → `ROW_NUMBER` or `DENSE_RANK` with `PARTITION BY group ORDER BY measure DESC` → filter `<= N` in an outer query.

```sql run
WITH product_revenue AS (
    SELECT p.category, p.product_name,
           SUM(i.quantity * i.unit_price) AS revenue
    FROM order_items i
    JOIN products p ON p.product_id = i.product_id
    JOIN orders   o ON o.order_id   = i.order_id
    WHERE o.status <> 'CANCELLED'
    GROUP BY p.category, p.product_name
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn
    FROM product_revenue
)
SELECT category, product_name, revenue
FROM ranked
WHERE rn <= 2
ORDER BY category, rn;
```

**ROW_NUMBER or DENSE_RANK?** ROW_NUMBER returns exactly N rows per group; DENSE_RANK returns everyone tied at the cut-off. Ask the interviewer which they want.

::: extension LATERAL joins
PostgreSQL's `JOIN LATERAL (SELECT … ORDER BY … LIMIT 2)` runs a small "top N" subquery per row of the outer table. With the right index it is very fast for "latest 3 orders per customer".
:::

**Common mistakes:** filtering on the window result in WHERE (not allowed); forgetting PARTITION BY (gives the top N overall); missing tie-breakers.

### Pattern 10 — Rows Above Their Group's Average {: .intoc }

[MEDIUM] · "employees earning more than their department's average"

**General approach (three equivalent options):** a window `AVG() OVER (PARTITION BY …)` (Session 3.8), a correlated subquery (Session 3.7), or a join to a grouped derived table, shown here:

```sql run
SELECT e.emp_name, e.dept_id, e.salary, a.dept_avg
FROM employees e
JOIN (SELECT dept_id, ROUND(AVG(salary), 2) AS dept_avg
      FROM employees
      GROUP BY dept_id) a ON a.dept_id = e.dept_id
WHERE e.salary > a.dept_avg
ORDER BY e.dept_id, e.salary DESC;
```

**Variations:** products priced above their category's average; orders above the customer's average order; students above the class average.

**Common mistakes:** comparing with the *overall* average instead of the group's; forgetting that NULL group keys (Farhan) drop out of the join; using HAVING when you need row-level output.

### Pattern 11 — Customers With No Orders {: .intoc }

[EASY] · the anti-join; extremely common

**General approach.** Three standard ways; know at least two.

```sql run
-- 1) LEFT JOIN + IS NULL
SELECT c.customer_name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;
```

```sql run
-- 2) NOT EXISTS (NULL-safe and usually the clearest)
SELECT c.customer_name
FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
```

```sql run
-- 3) EXCEPT on the keys (set difference)
SELECT customer_id FROM customers
EXCEPT
SELECT customer_id FROM orders
ORDER BY customer_id;
```

**Variations:** products never sold, employees who are not managers, departments without employees, users who signed up but never logged in.

**Common mistakes:** `NOT IN` with a subquery that can contain NULLs (returns nothing); checking `IS NULL` on a right-table column that can be NULL for matched rows (check the right table's key instead).

### Pattern 12 — Latest Record per User {: .intoc }

[MEDIUM] · "each customer's most recent order", "latest login per user", "current address"

**General approach.** `ROW_NUMBER() OVER (PARTITION BY user ORDER BY time DESC)` and keep `rn = 1`.

```sql run
SELECT user_id, login_time, device
FROM (SELECT l.*,
             ROW_NUMBER() OVER (PARTITION BY user_id
                                ORDER BY login_time DESC, login_id DESC) AS rn
      FROM user_logins l) t
WHERE rn = 1
ORDER BY user_id;
```

**PostgreSQL shortcut, DISTINCT ON:**

```sql run
SELECT DISTINCT ON (user_id) user_id, login_time, device
FROM user_logins
ORDER BY user_id, login_time DESC;
```

**Another portable way:** join each user to their `MAX(login_time)`. It is simple, but it returns two rows if two logins share the same latest timestamp.

**Common mistakes:** `GROUP BY user_id` with `MAX(login_time)` while also selecting `device` (not allowed, or picks the wrong row in lenient databases); ties without a tie-breaker; RANK instead of ROW_NUMBER when exactly one row is required.

### Pattern 13 — Finding Missing Records {: .intoc }

[MEDIUM] · gaps in IDs, days with no sales, expected rows that never arrived

**General approach.** Generate the complete *expected* set (numbers or dates) with `generate_series`, or use a calendar table, then anti-join it with the actual data.

Missing order IDs between the smallest and largest:

```sql run
SELECT g AS missing_order_id
FROM generate_series((SELECT MIN(order_id) FROM orders),
                     (SELECT MAX(order_id) FROM orders)) AS g
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.order_id = g);
```

Days in the first week of April with no logins at all:

```sql run
SELECT d::date AS day_without_logins
FROM generate_series(DATE '2024-04-01', DATE '2024-04-07', INTERVAL '1 day') AS d
WHERE NOT EXISTS (SELECT 1
                  FROM user_logins l
                  WHERE l.login_time::date = d::date);
```

**Variations:** months with zero revenue (show 0 instead of skipping: LEFT JOIN the calendar to the data and use `COALESCE(SUM(…), 0)`); employees with no timesheet for a working day; sensors that stopped reporting.

**Common mistakes:** grouping the data directly (days with no rows simply don't appear); comparing timestamps with dates without casting; time-zone boundaries.

### Pattern 14 — Ranking {: .intoc }

[MEDIUM] · "rank customers by number of orders"

**General approach.** Aggregate first, then rank with the function whose tie behaviour matches the question.

```sql run
SELECT c.customer_name,
       COUNT(*)                              AS orders,
       RANK()       OVER (ORDER BY COUNT(*) DESC) AS rank,
       DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS dense_rank
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.customer_name
ORDER BY orders DESC, c.customer_name;
```

Isha and Kabir tie for second place with 3 orders each: RANK then jumps to 4, while DENSE_RANK continues with 3.

**Variations:** rank within groups (PARTITION BY), percentile rank (`PERCENT_RANK`), quartiles (`NTILE(4)`), "show only the top 3 ranks".

**Common mistakes:** picking the wrong ranking function for ties; ranking before filtering out irrelevant rows; forgetting that ORDER BY inside OVER and the final ORDER BY are separate.

### Pattern 15 — Running Totals {: .intoc }

[MEDIUM] · cumulative revenue, running balance, cumulative signups

**General approach.** Aggregate to the right grain (per day), then `SUM(…) OVER (ORDER BY day)`. Add PARTITION BY for one running total per group.

```sql run
WITH daily AS (
    SELECT order_date, SUM(total_amount) AS revenue
    FROM orders
    WHERE status <> 'CANCELLED'
    GROUP BY order_date
)
SELECT order_date,
       revenue,
       SUM(revenue) OVER (ORDER BY order_date
                          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue
FROM daily
ORDER BY order_date;
```

Two orders were placed on 19 April; aggregating per day first means each date appears once, so the running total is clean.

**Variations:** running total per customer (`PARTITION BY customer_id`), month-to-date totals (`PARTITION BY DATE_TRUNC('month', order_date)`), a running count, the percentage of the yearly target reached.

**Common mistakes:** forgetting ORDER BY inside OVER (gives the grand total on every row); RANGE-frame surprises with duplicate dates; mixing grains.

### Pattern 16 — Previous / Next Row (LAG and LEAD) {: .intoc }

[MEDIUM] · change since last time, gaps between events

**General approach.** `LAG(col) OVER (PARTITION BY entity ORDER BY time)` brings the previous row's value onto the current row; then subtract or compare.

Days between consecutive orders of the same customer:

```sql run
SELECT customer_id,
       order_id,
       order_date,
       order_date - LAG(order_date) OVER (PARTITION BY customer_id
                                          ORDER BY order_date, order_id) AS days_since_prev
FROM orders
WHERE customer_id IN (1, 2)
ORDER BY customer_id, order_date;
```

Date minus date gives a whole number of days in PostgreSQL. The first order of each customer has no previous row, so the gap is NULL.

**Variations:** month-over-month growth (Pattern 20), salary change between revisions, detecting a status change, comparing each stock price with the next day's (LEAD).

**Common mistakes:** missing PARTITION BY (compares different customers); no deterministic ORDER BY; dividing by a previous value that can be 0 or NULL.

### Pattern 17 — Date-Based Analysis {: .intoc }

[MEDIUM] · orders per month, busiest weekday, last N days

**General approach.** Bucket dates with `DATE_TRUNC` or `EXTRACT`/`TO_CHAR`, then aggregate. Filter with half-open ranges.

```sql run
SELECT DATE_TRUNC('month', order_date)::date AS month,
       COUNT(*)                              AS orders,
       SUM(total_amount)                     AS revenue,
       ROUND(AVG(total_amount), 2)           AS avg_order
FROM orders
WHERE status <> 'CANCELLED'
GROUP BY 1
ORDER BY 1;
```

Busiest day of the week for logins:

```sql run
SELECT TO_CHAR(login_time, 'Dy')        AS weekday,
       EXTRACT(ISODOW FROM login_time)  AS day_no,
       COUNT(*)                         AS logins
FROM user_logins
GROUP BY 1, 2
ORDER BY day_no;
```

**Variations:** last 7 or 30 days relative to today (`>= CURRENT_DATE - INTERVAL '30 days'`), year-over-year comparison, customer tenure (`AGE`), signups per week (`DATE_TRUNC('week', …)`), first purchase month cohorts.

**Common mistakes:** `BETWEEN` with timestamps; grouping by `TO_CHAR(… 'Month')` and sorting alphabetically (April before January); ignoring time zones; using `EXTRACT(MONTH …)` alone across several years (January 2023 and January 2024 merge).

### Pattern 18 — Conditional Aggregation {: .intoc }

[MEDIUM] · counts per category as columns ("pivot"), success rates

**General approach.** Put the condition **inside** the aggregate: `SUM(CASE WHEN cond THEN 1 ELSE 0 END)`, or `COUNT(*) FILTER (WHERE cond)` in PostgreSQL.

```sql run
SELECT DATE_TRUNC('month', order_date)::date                     AS month,
       COUNT(*) FILTER (WHERE status = 'DELIVERED')               AS delivered,
       COUNT(*) FILTER (WHERE status IN ('PENDING', 'SHIPPED'))   AS open,
       COUNT(*) FILTER (WHERE status IN ('CANCELLED', 'RETURNED')) AS lost,
       ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'DELIVERED') / COUNT(*), 1) AS delivered_pct
FROM orders
GROUP BY 1
ORDER BY 1;
```

The portable form of the first column is `SUM(CASE WHEN status = 'DELIVERED' THEN 1 ELSE 0 END)`.

**Variations:** revenue per category as columns, male/female headcount per department, pass/fail counts per subject, the share of mobile vs web logins.

**Common mistakes:** filtering in WHERE (removes the rows needed by the other columns); integer division in percentages; `COUNT(CASE WHEN … THEN 1 ELSE 0 END)` (counts zeros too, because 0 is not NULL; use `SUM`, or leave out the ELSE).

### Pattern 19 — Subquery Problems {: .intoc }

[MEDIUM] · comparing against a computed value

**General approach.** Compute the reference value in a subquery (scalar, in WHERE/HAVING), or per row (correlated).

Departments whose average salary is above the company average (a subquery inside HAVING):

```sql run
SELECT d.dept_name, ROUND(AVG(e.salary), 2) AS dept_avg
FROM employees e
JOIN departments d ON d.dept_id = e.dept_id
GROUP BY d.dept_name
HAVING AVG(e.salary) > (SELECT AVG(salary) FROM employees)
ORDER BY dept_avg DESC;
```

Orders larger than that customer's own average order (correlated):

```sql run
SELECT o.order_id, o.customer_id, o.total_amount
FROM orders o
WHERE o.total_amount > (SELECT AVG(x.total_amount)
                        FROM orders x
                        WHERE x.customer_id = o.customer_id)
ORDER BY o.customer_id, o.order_id;
```

**Variations:** products costing more than every Stationery item (`> ALL`), employees hired before their manager, customers whose spend exceeds the average spend.

**Common mistakes:** a scalar subquery returning several rows; `NOT IN` with NULLs; correlated subqueries on huge tables without supporting indexes.

### Pattern 20 — CTE Problems (Multi-Step Logic) {: .intoc }

[MEDIUM] · "month-over-month growth", "flag months where…"

**General approach.** One CTE per logical step: aggregate → add the comparison (LAG) → compute the metric → filter or flag. Name each step clearly.

```sql run
WITH monthly AS (
    SELECT DATE_TRUNC('month', order_date)::date AS month,
           SUM(total_amount)                     AS revenue
    FROM orders
    WHERE status <> 'CANCELLED'
    GROUP BY 1
),
with_prev AS (
    SELECT month, revenue,
           LAG(revenue) OVER (ORDER BY month) AS prev_revenue
    FROM monthly
)
SELECT month,
       revenue,
       prev_revenue,
       ROUND(100.0 * (revenue - prev_revenue) / NULLIF(prev_revenue, 0), 1) AS growth_pct,
       CASE WHEN revenue > prev_revenue THEN 'up' ELSE 'down / n.a.' END     AS trend
FROM with_prev
ORDER BY month;
```

::: linebyline
| Step | What it does |
|---|---|
| `monthly` | revenue per month (excluding cancelled orders) |
| `with_prev` | adds the previous month's revenue next to each month |
| final SELECT | computes growth %, protecting against division by zero with `NULLIF` |
:::

**Variations:** customers whose first order was in Q1 and who bought again later; top category per month; a funnel (visited → added to cart → paid) with one CTE per stage.

**Common mistakes:** one giant nested query nobody can read; recomputing the same aggregate in several places instead of reusing a CTE.

### Pattern 21 — Self Joins {: .intoc }

[MEDIUM] · employee/manager, pairs of rows, comparing rows of the same table

**The classic question:** "Find employees who earn more than their manager."

```sql run
SELECT e.emp_name AS employee, e.salary,
       m.emp_name AS manager,  m.salary AS manager_salary
FROM employees e
JOIN employees m ON m.emp_id = e.manager_id
WHERE e.salary > m.salary;
```

In this data no employee out-earns their manager, so the correct answer is **an empty result**. Say so confidently in an interview: an empty result can be right. A variation that does return rows, employees based in the same city as their manager:

```sql run
SELECT e.emp_name AS employee, m.emp_name AS manager, e.city
FROM employees e
JOIN employees m ON m.emp_id = e.manager_id
WHERE e.city = m.city
ORDER BY e.city, e.emp_name;
```

And the number of direct reports per manager:

```sql run
SELECT m.emp_name AS manager, COUNT(*) AS direct_reports
FROM employees e
JOIN employees m ON m.emp_id = e.manager_id
GROUP BY m.emp_name
ORDER BY direct_reports DESC, manager;
```

**Variations:** pairs of employees in the same department (`e1.emp_id < e2.emp_id` to avoid duplicates); flights with a connection (`f1.dest = f2.origin`); consecutive-day comparisons in older SQL without LAG.

**Common mistakes:** using the same alias for both copies; joining in the wrong direction (`e.emp_id = m.manager_id` finds reports, not managers); listing each pair twice.

### Pattern 22 — Window-Function Problems (Gaps and Islands) {: .intoc }

[HARD] · consecutive days, streaks, sessions

**The pattern.** Find runs of consecutive values, for example "users who logged in on 3 or more consecutive days".

**The trick.** For consecutive dates, `date − ROW_NUMBER()` is **constant** within a run. Group by that constant (the "island" key):

| user 1 login day | row_number | day − row_number |
|---|---|---|
| 2024-04-01 | 1 | 2024-03-31 |
| 2024-04-02 | 2 | 2024-03-31 |
| 2024-04-03 | 3 | 2024-03-31 |
| 2024-04-05 | 4 | 2024-04-01 ← a new island |

```sql run
WITH days AS (
    SELECT DISTINCT user_id, login_time::date AS day
    FROM user_logins
),
islands AS (
    SELECT user_id, day,
           day - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day))::int AS island
    FROM days
)
SELECT user_id,
       MIN(day) AS streak_start,
       MAX(day) AS streak_end,
       COUNT(*) AS streak_days
FROM islands
GROUP BY user_id, island
HAVING COUNT(*) >= 3;
```

::: linebyline
| Step | What it does |
|---|---|
| `days` | one row per user per day they logged in (two logins on one day count once) |
| `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day)` | 1, 2, 3… per user in date order |
| `day - (…)::int AS island` | constant inside a run of consecutive days; changes after a gap |
| `GROUP BY user_id, island … HAVING COUNT(*) >= 3` | each group is one streak; keep streaks of 3 days or more |
:::

Customer 1 logged in on 1, 2 and 3 April, a three-day streak.

**Other window-function problems:** each row's percentage of its group total; cumulative distribution; the first and last value in a session; median (`PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY …)`, strictly an ordered-set aggregate); sessionising events with LAG (a new session when the gap exceeds 30 minutes).

**Common mistakes:** not removing duplicate days first; forgetting PARTITION BY user; trying to filter streaks in WHERE.

::: explain How I talk through a SQL problem in an interview
"Let me make sure I understand: we want one row per department with its second-highest salary, and if two people share that salary we show both? … OK. I'll first rank salaries inside each department with DENSE_RANK, because ties should share a rank and I don't want gaps. That goes in a CTE, since I can't filter on a window function in WHERE. Then I select the rows where the rank is 2 and join to departments for the name. If the table were large, an index on (dept_id, salary) would help. Let me quickly check it against Finance: 110000 is first, and both 70000 rows are second. Good."
:::

::: questions
#### Basic
Q: [SQL PROBLEM] Find duplicate emails in a table.
A: `SELECT email, COUNT(*) FROM leads GROUP BY email HAVING COUNT(*) > 1;`

Q: [SQL PROBLEM] Find the second-highest salary.
A: `SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);` (returns NULL if there is none).

Q: [SQL PROBLEM] List customers who never placed an order.
A: `SELECT c.* FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);`

#### Intermediate
Q: [SQL PROBLEM] Find the Nth highest salary.
A: DENSE_RANK over salary descending in a subquery, keeping rank = N; or `SELECT DISTINCT salary … ORDER BY salary DESC OFFSET N-1 LIMIT 1`.

Q: [SQL PROBLEM] Delete duplicate rows, keeping the earliest.
A: `DELETE FROM t WHERE id IN (SELECT id FROM (SELECT id, ROW_NUMBER() OVER (PARTITION BY dup_key ORDER BY created_at, id) rn FROM t) x WHERE rn > 1);`

Q: [SQL PROBLEM] Get each user's latest login.
A: ROW_NUMBER partitioned by user and ordered by login_time DESC, keeping rn = 1; or `DISTINCT ON (user_id) … ORDER BY user_id, login_time DESC` in PostgreSQL.

Q: [SQL PROBLEM] Compute a running total of daily revenue.
A: Aggregate per day in a CTE, then `SUM(revenue) OVER (ORDER BY day)`.

#### Scenario-based
Q: [SQL PROBLEM] Show monthly revenue and month-over-month growth percentage.
A: A CTE for monthly revenue, `LAG(revenue) OVER (ORDER BY month)` for the previous month, and growth = `100.0 * (rev - prev) / NULLIF(prev, 0)`.

Q: [SQL PROBLEM] Find users who logged in on at least 3 consecutive days.
A: Distinct user-days, then `day - ROW_NUMBER() OVER (PARTITION BY user ORDER BY day)` as an island key, then GROUP BY user and island with `HAVING COUNT(*) >= 3`.

Q: [SQL PROBLEM] Top 3 products by revenue in each category.
A: Aggregate revenue per product, then ROW_NUMBER (or DENSE_RANK for ties) partitioned by category ordered by revenue DESC, keeping rank ≤ 3.

#### Follow-up / Trap
Q: [TRAP QUESTION] Why might `ORDER BY salary DESC LIMIT 1 OFFSET 1` give the wrong second-highest salary?
A: If the top salary is shared by two people, the second row has the same top salary. Use DISTINCT or DENSE_RANK.

Q: [TRAP QUESTION] Your "employees earning more than their manager" query returns no rows. Is it wrong?
A: Not necessarily: verify the join direction and the data. An empty result is correct when no such employee exists.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Find all products whose name contains "Desk" or "Chair" (case-insensitive).

**P2.** Count orders per customer, including customers with zero orders.

**P3.** Return the third-highest product price.

#### Level 2 — Interview application
**P4.** For each department, show the highest-paid employee (all of them if tied).

**P5.** Show each customer's first-ever order (id and date).

**P6.** Produce one row per product category with three columns: units sold in January, February and March 2024 (exclude cancelled orders).

#### Level 3 — Scenario / problem solving
**P7.** For each month, show revenue and the running (year-to-date) revenue, plus the share of the year-to-date total that the month represents.

**P8.** Find customers whose order totals strictly increased with every new order (each order larger than their previous one), considering only customers with at least two orders.
:::

::: answers
**P1.**

```sql run
SELECT product_name
FROM products
WHERE product_name ILIKE '%desk%' OR product_name ILIKE '%chair%';
```

**P2.** LEFT JOIN, and count a column from the right side:

```sql run
SELECT c.customer_name, COUNT(o.order_id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY orders DESC, c.customer_name;
```

**P3.**

```sql run
SELECT DISTINCT price
FROM products
ORDER BY price DESC
OFFSET 2 LIMIT 1;
```

**P4.** RANK or DENSE_RANK keeps ties at rank 1:

```sql run
SELECT dept_id, emp_name, salary
FROM (SELECT dept_id, emp_name, salary,
             RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk
      FROM employees
      WHERE dept_id IS NOT NULL) t
WHERE rnk = 1
ORDER BY dept_id;
```

**P5.**

```sql run
SELECT DISTINCT ON (customer_id) customer_id, order_id, order_date
FROM orders
ORDER BY customer_id, order_date, order_id;
```

**P6.** Conditional aggregation with a date filter inside each FILTER:

```sql run
SELECT p.category,
       COALESCE(SUM(i.quantity) FILTER (WHERE o.order_date >= '2024-01-01' AND o.order_date < '2024-02-01'), 0) AS jan_units,
       COALESCE(SUM(i.quantity) FILTER (WHERE o.order_date >= '2024-02-01' AND o.order_date < '2024-03-01'), 0) AS feb_units,
       COALESCE(SUM(i.quantity) FILTER (WHERE o.order_date >= '2024-03-01' AND o.order_date < '2024-04-01'), 0) AS mar_units
FROM order_items i
JOIN orders   o ON o.order_id   = i.order_id
JOIN products p ON p.product_id = i.product_id
WHERE o.status <> 'CANCELLED'
GROUP BY p.category
ORDER BY p.category;
```

**P7.**

```sql run
WITH monthly AS (
    SELECT DATE_TRUNC('month', order_date)::date AS month,
           SUM(total_amount) AS revenue
    FROM orders
    WHERE status <> 'CANCELLED'
    GROUP BY 1
)
SELECT month,
       revenue,
       SUM(revenue) OVER (ORDER BY month) AS ytd_revenue,
       ROUND(100.0 * revenue / SUM(revenue) OVER (ORDER BY month), 1) AS pct_of_ytd
FROM monthly
ORDER BY month;
```

**P8.** Compare each order with the previous one using LAG; a customer qualifies if none of their orders is less than or equal to the previous order:

```sql run
WITH seq AS (
    SELECT customer_id, order_id, total_amount,
           LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS prev_total
    FROM orders
)
SELECT customer_id
FROM seq
GROUP BY customer_id
HAVING COUNT(*) >= 2
   AND COUNT(*) FILTER (WHERE prev_total IS NOT NULL AND total_amount <= prev_total) = 0
ORDER BY customer_id;
```

Customer 4 qualifies (2798 → 3998). Every other customer has at least one order smaller than the one before.
:::
