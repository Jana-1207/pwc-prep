## Session 3.5 — Grouping and Aggregation: GROUP BY and HAVING {: #s3-5 }

[HIGH PRIORITY] [MUST KNOW]

### Simple meaning

**GROUP BY puts rows that share a value into the same group, then an aggregate function produces one result per group.** "How many employees per department?" "Revenue per month?" "Average salary per city?" are all GROUP BY questions.

::: analogy Sorting exam papers
A teacher has a pile of answer sheets from three classes. She sorts them into one pile per class (**GROUP BY class**), then counts each pile and finds its highest mark (**COUNT, MAX**). She ends with one line per class, not one line per student.
:::

### Your first GROUP BY

```sql run
SELECT dept_id,
       COUNT(*)              AS employees,
       ROUND(AVG(salary), 2) AS avg_salary,
       MAX(salary)           AS max_salary
FROM employees
GROUP BY dept_id
ORDER BY dept_id;
```

::: linebyline
| Line | What it does |
|---|---|
| `SELECT dept_id,` | one output row per department, so show which department it is |
| `COUNT(*) AS employees` | how many rows (employees) fell into each group |
| `ROUND(AVG(salary), 2) AS avg_salary` | average salary of the group, two decimals |
| `MAX(salary) AS max_salary` | highest salary in the group |
| `GROUP BY dept_id` | make one group per distinct dept_id value |
| `ORDER BY dept_id` | sort the final result |
:::

Notice the last row: Farhan's `dept_id` is NULL, and **all NULLs form one group of their own**.

### The golden rule of GROUP BY

Every column in the SELECT list must either be **in the GROUP BY** or **inside an aggregate function**. Otherwise the database cannot know which of the group's many values to show:

```sql run error
SELECT dept_id, emp_name, COUNT(*)
FROM employees
GROUP BY dept_id;
```

Engineering has six employees; which one name should appear on its single row? The database refuses to guess. (MySQL in its old, non-strict mode *did* guess, which hid bugs. Do not rely on that.)

::: extension A PostgreSQL convenience
If you group by a table's **primary key**, PostgreSQL lets you select that table's other columns without listing them, because the key functionally determines them: `SELECT d.dept_id, d.dept_name, COUNT(e.emp_id) FROM departments d LEFT JOIN employees e … GROUP BY d.dept_id;` is valid.
:::

### Grouping by several columns, and grouping joined data

```sql run
SELECT d.dept_name,
       e.city,
       COUNT(*) AS headcount
FROM employees e
JOIN departments d ON d.dept_id = e.dept_id
GROUP BY d.dept_name, e.city
ORDER BY d.dept_name, headcount DESC;
```

One row per **combination** of department and city. Joins are covered properly in Session 3.6.

### HAVING: filtering groups

`WHERE` filters **rows before** grouping. `HAVING` filters **groups after** aggregation, so it can use aggregates. "Departments with more than two employees":

```sql run
SELECT dept_id, COUNT(*) AS employees
FROM employees
GROUP BY dept_id
HAVING COUNT(*) > 2
ORDER BY employees DESC;
```

Using both: "Among employees hired before 2022, which cities have an average salary above 80000?"

```sql run
SELECT city,
       COUNT(*)              AS employees,
       ROUND(AVG(salary), 2) AS avg_salary
FROM employees
WHERE hire_date < '2022-01-01'        -- row filter: runs first
GROUP BY city
HAVING AVG(salary) > 80000            -- group filter: runs after grouping
ORDER BY avg_salary DESC;
```

| | WHERE | HAVING |
|---|---|---|
| Filters | individual rows | groups |
| Runs | before GROUP BY | after GROUP BY |
| Can use aggregates (`COUNT`, `SUM` …) | no | yes |
| Works without GROUP BY | yes | yes (the whole result is one group), but rarely useful |
| Performance tip | filter as early as possible here | only for conditions that need aggregates |

### The logical order of execution

SQL is *written* in one order but *processed* in another. Knowing the processing order explains most beginner errors:

[[fig:sql_order | Written order vs logical processing order. SELECT is evaluated late.]]

This order explains:

- **Why WHERE cannot use SELECT aliases** (WHERE runs before SELECT).
- **Why WHERE cannot use aggregates** (groups do not exist yet).
- **Why ORDER BY *can* use aliases** (it runs after SELECT).
- **Why HAVING cannot use a SELECT alias in PostgreSQL** (HAVING runs before SELECT):

```sql run error
SELECT dept_id, COUNT(*) AS n
FROM employees
GROUP BY dept_id
HAVING n > 2;
```

Write `HAVING COUNT(*) > 2` instead. (MySQL accepts aliases in HAVING; PostgreSQL and SQL Server do not.) PostgreSQL *does* accept output-column aliases in `GROUP BY` as a convenience, but the portable habit is to repeat the expression.

::: note The physical plan can differ
This is the *logical* order: it defines what the result must be. The optimizer may physically do things differently (for example, push a filter into an index scan), as long as the result is the same.
:::

### Listing the members of each group

`STRING_AGG` joins the group's values into one string; `ARRAY_AGG` builds an array.

```sql run
SELECT d.dept_name,
       COUNT(e.emp_id)                                     AS employees,
       STRING_AGG(e.emp_name, ', ' ORDER BY e.emp_name)    AS members
FROM departments d
JOIN employees e ON e.dept_id = d.dept_id
GROUP BY d.dept_name
ORDER BY employees DESC;
```

### Subtotals with ROLLUP [INTERVIEW EXTENSION]

`GROUP BY ROLLUP (a, b)` adds subtotal rows per `a` and a grand total. `CUBE` adds totals for every combination; `GROUPING SETS` lets you list exactly which groupings you want.

```sql run
SELECT COALESCE(p.category, 'ALL CATEGORIES') AS category,
       SUM(i.quantity * i.unit_price)          AS revenue
FROM order_items i
JOIN products p ON p.product_id = i.product_id
GROUP BY ROLLUP (p.category)
ORDER BY revenue;
```

::: explain
"GROUP BY splits rows into groups that share a value and lets aggregate functions like COUNT, SUM and AVG return one row per group, for example the number of employees per department. Every selected column must be grouped or aggregated. WHERE filters rows before grouping, so it can't use aggregates; HAVING filters groups after aggregation, for example departments with more than two employees. Logically the database runs FROM, WHERE, GROUP BY, HAVING, then SELECT and ORDER BY, which is also why aliases work in ORDER BY but not in WHERE."
:::

::: trap
- Putting an aggregate in WHERE (`WHERE COUNT(*) > 2`): it must go in HAVING.
- Selecting a column that is neither grouped nor aggregated.
- Using HAVING for row-level filters that belong in WHERE (works, but it is slower and less clear).
- Forgetting that NULLs form their own group.
- Using a SELECT alias in HAVING in PostgreSQL.
:::

::: questions
#### Basic
Q: [DEFINITION] What does GROUP BY do?
A: It groups rows with the same values in the given columns so aggregate functions return one result per group.

Q: [COMPARISON] WHERE vs HAVING?
A: WHERE filters rows before grouping and cannot use aggregates; HAVING filters groups after grouping and can use aggregates.

Q: [SQL PROBLEM] Count employees in each city.
A: `SELECT city, COUNT(*) FROM employees GROUP BY city;`

#### Intermediate
Q: [WHY] Why does `SELECT dept_id, emp_name, COUNT(*) FROM employees GROUP BY dept_id` fail?
A: emp_name is neither grouped nor aggregated, so there is no single value to show per department.

Q: [HOW] What is the logical order of SQL clauses?
A: FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT/OFFSET.

Q: [HOW] Can you use HAVING without GROUP BY?
A: Yes, then the whole table is one group: `SELECT COUNT(*) FROM employees HAVING COUNT(*) > 10` returns the count only if it exceeds 10. It's rarely needed.

Q: [HOW] How are NULLs treated in GROUP BY?
A: All NULLs are placed together into one group.

Q: [DEFINITION] What does ROLLUP do?
A: It adds subtotal and grand-total rows to a GROUP BY result, e.g. revenue per category plus an overall total.

#### Scenario-based
Q: [SQL PROBLEM] Find cities with at least two employees and an average salary above 70000.
A: `SELECT city, COUNT(*), AVG(salary) FROM employees GROUP BY city HAVING COUNT(*) >= 2 AND AVG(salary) > 70000;`

Q: [SQL PROBLEM] Total order value per customer for delivered orders only, top spender first.
A: `SELECT customer_id, SUM(total_amount) AS spent FROM orders WHERE status = 'DELIVERED' GROUP BY customer_id ORDER BY spent DESC;`

#### Follow-up / Trap
Q: [TRAP QUESTION] Is `WHERE salary > 50000` the same as `HAVING salary > 50000` in a grouped query?
A: No. HAVING can only refer to grouped columns or aggregates, so the HAVING version errors unless salary is grouped. Row conditions belong in WHERE.

Q: [TRAP QUESTION] Does `COUNT(*)` in a grouped query ever return 0?
A: Not for a group produced by GROUP BY, since every group has at least one row. Zero counts appear only with outer joins and `COUNT(column)` (see the next session).
:::

## Session 3.6 — Joins {: #s3-6 }

[HIGH PRIORITY] [MUST KNOW] Joins and their types are among the questions most often mentioned in PwC interview write-ups.

### Why joins exist

Normalization (Session 2.5) splits data into tables: employee names in one, department names in another. A **join** combines rows from two tables **based on a related column**, usually a foreign key matching a primary key, so you can see the pieces together again.

### The join types at a glance

[[fig:joins_venn | What each join returns. A is the left table (written first), B is the right table.]]

| Join | Returns | Typical question |
|---|---|---|
| `INNER JOIN` | only rows with a match in both tables | "employees with their department names" |
| `LEFT [OUTER] JOIN` | all rows from the left table + matches from the right (NULLs when none) | "all customers, with orders if any" |
| `RIGHT [OUTER] JOIN` | all rows from the right table + matches from the left | same as LEFT with the tables swapped |
| `FULL [OUTER] JOIN` | all rows from both; NULLs where there is no match | "reconcile two lists: what's missing on either side?" |
| `CROSS JOIN` | every combination of rows (Cartesian product) | "every store × every day" |
| Self join | a table joined to itself | "employee and their manager" |

### INNER JOIN

```sql run
SELECT e.emp_name, d.dept_name, d.location
FROM employees e
INNER JOIN departments d ON d.dept_id = e.dept_id
ORDER BY d.dept_name, e.emp_name;
```

::: linebyline
| Line | What it does |
|---|---|
| `FROM employees e` | the left table, aliased `e` |
| `INNER JOIN departments d` | the right table, aliased `d` (`INNER` is optional: plain `JOIN` means inner join) |
| `ON d.dept_id = e.dept_id` | the join condition: pair rows whose department IDs are equal |
| `SELECT e.emp_name, d.dept_name, d.location` | columns from both tables, prefixed by alias to avoid ambiguity |
:::

Two rows are missing on purpose: **Farhan** (no department, NULL never equals anything) and the **Legal** department (no employees). An inner join keeps only matches.

### LEFT JOIN

```sql run
SELECT e.emp_name, d.dept_name
FROM employees e
LEFT JOIN departments d ON d.dept_id = e.dept_id
ORDER BY d.dept_name NULLS FIRST, e.emp_name
LIMIT 5;
```

Every employee appears; Farhan's department columns are NULL. A LEFT JOIN answers "all of A, plus B where it exists".

**Counting with a LEFT JOIN, the classic trap:** employees per department, *including* departments with nobody.

```sql run
SELECT d.dept_name,
       COUNT(*)        AS count_star_wrong,
       COUNT(e.emp_id) AS employees
FROM departments d
LEFT JOIN employees e ON e.dept_id = d.dept_id
GROUP BY d.dept_name
ORDER BY employees DESC;
```

Legal shows **1** with `COUNT(*)`, because the left join produced one row for Legal (with NULL employee columns), and `COUNT(*)` counts rows. `COUNT(e.emp_id)` counts only real employees: **0**. Always count a column from the right-hand table.

### RIGHT JOIN

A RIGHT JOIN keeps every row of the *right* table. It is exactly a LEFT JOIN with the tables written in the opposite order, so many teams use only LEFT JOIN for readability.

```sql run
SELECT d.dept_name, e.emp_name
FROM employees e
RIGHT JOIN departments d ON d.dept_id = e.dept_id
WHERE e.emp_id IS NULL;
```

This finds departments with no employees: Legal.

### FULL OUTER JOIN

```sql run
SELECT e.emp_name, d.dept_name
FROM employees e
FULL OUTER JOIN departments d ON d.dept_id = e.dept_id
WHERE e.emp_id IS NULL OR d.dept_id IS NULL;
```

Both kinds of unmatched rows in one query: an employee without a department *and* a department without employees. FULL OUTER JOIN is great for **reconciliation**, such as comparing yesterday's file with today's. (MySQL has no FULL JOIN; emulate it with a LEFT JOIN `UNION` a RIGHT JOIN.)

### CROSS JOIN

```sql run
SELECT r.region, s.size
FROM (VALUES ('North'), ('South')) AS r(region)
CROSS JOIN (VALUES ('S'), ('M'), ('L')) AS s(size)
ORDER BY r.region, s.size;
```

2 rows × 3 rows = 6 rows. Use it deliberately for **all combinations** (every product × every month for a sales grid). Accidentally forgetting a join condition with the old comma syntax (`FROM a, b`) creates a cross join, which can explode into millions of rows.

### SELF JOIN

A self join treats one table as two, using two aliases. Employees and their managers live in the same table:

```sql run
SELECT e.emp_name AS employee,
       m.emp_name AS manager
FROM employees e
LEFT JOIN employees m ON m.emp_id = e.manager_id
ORDER BY m.emp_name NULLS FIRST, e.emp_name;
```

::: linebyline
| Line | What it does |
|---|---|
| `FROM employees e` | the table in its "employee" role |
| `LEFT JOIN employees m` | the same table again in its "manager" role |
| `ON m.emp_id = e.manager_id` | an employee's manager_id points at the manager's emp_id |
| `LEFT` | keeps Arjun, who has no manager (an INNER join would drop him) |
:::

Self joins also find pairs, such as employees who work in the same city. The condition `e1.emp_id < e2.emp_id` avoids pairing someone with themselves and listing each pair twice:

```sql run
SELECT e1.emp_name, e2.emp_name, e1.city
FROM employees e1
JOIN employees e2
  ON e1.city = e2.city
 AND e1.emp_id < e2.emp_id
WHERE e1.city IN ('Pune', 'Mumbai')
ORDER BY e1.city;
```

### Anti-join: rows with no match

"Customers who have never ordered" is one of the most common interview questions. A LEFT JOIN plus `IS NULL` on the right table's key:

```sql run
SELECT c.customer_id, c.customer_name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;
```

The equivalent `NOT EXISTS` form (often the clearest) appears in Session 3.7.

### Joining many tables

Revenue per customer per product category needs four tables. Join them one step at a time, following the foreign keys:

```sql run
SELECT c.customer_name,
       p.category,
       SUM(i.quantity * i.unit_price) AS revenue
FROM customers c
JOIN orders o      ON o.customer_id = c.customer_id
JOIN order_items i ON i.order_id    = o.order_id
JOIN products p    ON p.product_id  = i.product_id
WHERE o.status <> 'CANCELLED'
GROUP BY c.customer_name, p.category
ORDER BY c.customer_name, revenue DESC;
```

### Join pitfalls that break real reports

**1. Fan-out (row multiplication).** Joining a one-to-many relationship repeats the "one" side once per match. Summing a column from the "one" side then double counts:

```sql run
SELECT c.customer_name,
       SUM(o.total_amount) AS inflated_total     -- WRONG
FROM customers c
JOIN orders o      ON o.customer_id = c.customer_id
JOIN order_items i ON i.order_id    = o.order_id
GROUP BY c.customer_name
ORDER BY c.customer_name;
```

Aarav's real total is 42338, but each order total was repeated once per order line. Fix it by not joining tables you do not need, or by aggregating each side *before* joining:

```sql run
SELECT c.customer_name,
       SUM(o.total_amount) AS correct_total
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY c.customer_name;
```

**2. A WHERE clause that silently turns a LEFT JOIN into an INNER JOIN.** "All departments with their employees earning more than 60000":

```sql run
SELECT d.dept_name, e.emp_name
FROM departments d
LEFT JOIN employees e ON e.dept_id = d.dept_id
WHERE e.salary > 60000
ORDER BY d.dept_name
LIMIT 4;
```

Legal disappeared: for Legal, `e.salary` is NULL, `NULL > 60000` is UNKNOWN, and WHERE drops the row. Put conditions on the right table **inside the ON clause** to keep all left rows:

```sql run
SELECT d.dept_name, COUNT(e.emp_id) AS well_paid
FROM departments d
LEFT JOIN employees e
       ON e.dept_id = d.dept_id
      AND e.salary > 60000
GROUP BY d.dept_name
ORDER BY d.dept_name;
```

**3. NULLs never match.** `NULL = NULL` is not true, so rows with NULL join keys never pair up (Farhan above).

**4. Ambiguous columns.** If both tables have `dept_id`, writing just `dept_id` fails ("column reference is ambiguous"). Always prefix with aliases.

### Referential integrity and joins

Because `orders.customer_id` is a NOT NULL foreign key, every order is guaranteed to have a matching customer, so `orders JOIN customers` never loses an order. Without the foreign key, orphan orders would silently vanish from inner-join reports. Constraints protect your query results, not just your inserts.

### INNER JOIN vs LEFT JOIN

| | INNER JOIN | LEFT JOIN |
|---|---|---|
| Rows kept | only matching pairs | all left rows, matched or not |
| Unmatched left rows | dropped | kept, with NULLs for right-side columns |
| Typical use | "orders with their customer" | "all customers, with orders if any"; finding missing matches |
| Row count | ≤ the matching combinations | ≥ the number of left rows |
| Counting | `COUNT(*)` is fine | count a right-table column, e.g. `COUNT(o.order_id)` |

### Two more syntax notes

- `JOIN … USING (dept_id)` is shorthand when both columns have the same name; the column appears once in the output.
- Old comma syntax: `FROM employees e, departments d WHERE e.dept_id = d.dept_id` is an inner join written the 1980s way. Explicit `JOIN … ON` is clearer and avoids accidental cross joins.

::: explain
"A join combines rows from two tables based on a related column, usually a foreign key and a primary key. An inner join returns only rows that match in both tables. A left join returns every row from the left table plus matching rows from the right, with NULLs where there's no match; that's how I find, for example, customers with no orders, by checking that the order key is NULL. Right join is the mirror image, full outer join keeps unmatched rows from both sides, cross join gives every combination, and a self join joins a table to itself, like employees to their managers. Two things I watch for are duplicate rows when joining one-to-many before summing, and WHERE conditions on the right table that turn a left join into an inner join."
:::

::: trap
- `COUNT(*)` with a LEFT JOIN counts unmatched rows as 1; count a right-table column instead.
- Filtering the right table in WHERE after a LEFT JOIN removes the unmatched rows; move the condition into ON.
- Summing a "one-side" column after joining a "many" table (fan-out) inflates totals.
- Saying "RIGHT JOIN is different from LEFT JOIN". It is the same operation with the tables swapped.
- Forgetting that NULL keys never match.
- Saying "a self join needs a special keyword". It is a normal join with two aliases.
:::

::: questions
#### Basic
Q: [DEFINITION] What is a join?
A: An operation that combines rows from two or more tables based on a related column, usually a foreign key matching a primary key.

Q: [COMPARISON] INNER JOIN vs LEFT JOIN?
A: INNER returns only rows with matches in both tables. LEFT returns all rows from the left table, with NULLs for right-side columns where there is no match.

Q: [DEFINITION] What is a self join? Give an example.
A: Joining a table to itself using two aliases, e.g. employees joined to employees to show each employee's manager.

Q: [DEFINITION] What is a CROSS JOIN?
A: The Cartesian product: every row of one table combined with every row of the other (m × n rows).

#### Intermediate
Q: [SQL PROBLEM] Find customers who have never placed an order.
A: `SELECT c.* FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id WHERE o.order_id IS NULL;` or with `NOT EXISTS`.

Q: [COMPARISON] What is the difference between putting a condition in ON vs WHERE for a LEFT JOIN?
A: In ON, it controls which right rows match while all left rows are kept. In WHERE, it filters after the join and removes left rows whose right side is NULL, turning it into an inner join.

Q: [WHY] Why might a SUM be too high after joining several tables?
A: One-to-many joins duplicate the "one" side's rows (fan-out), so its values are summed several times. Aggregate before joining or remove unneeded joins.

Q: [DEFINITION] What does a FULL OUTER JOIN return, and when is it useful?
A: All rows from both tables, matched where possible and with NULLs otherwise; useful for reconciliation, such as finding records missing on either side.

Q: [HOW] If table A has 4 rows and B has 3, how many rows can each join return?
A: CROSS: exactly 12. INNER: 0 to 12, depending on matches. LEFT: at least 4 (up to 12). FULL: at least max(4, 3), at most 12 (or 7 if nothing matches).

#### Scenario-based
Q: [SQL PROBLEM] List each department with its number of employees, including departments with none.
A: `SELECT d.dept_name, COUNT(e.emp_id) FROM departments d LEFT JOIN employees e ON e.dept_id = d.dept_id GROUP BY d.dept_name;`

Q: [SQL PROBLEM] Show each employee with their manager's name; employees without a manager should still appear.
A: `SELECT e.emp_name, m.emp_name AS manager FROM employees e LEFT JOIN employees m ON m.emp_id = e.manager_id;`

Q: [SCENARIO] Yesterday's and today's product files are loaded into two tables. How do you find added, removed and changed products?
A: FULL OUTER JOIN on product_id. Rows with only the new side are added, only the old side are removed, and both sides with different values (e.g. price) are changed.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is there any difference between `JOIN` and `INNER JOIN`?
A: No. `JOIN` defaults to an inner join.

Q: [TRAP QUESTION] Can a join condition use something other than equality?
A: Yes, any condition: ranges (`o.order_date BETWEEN p.start AND p.end`), inequalities (`e1.emp_id < e2.emp_id`) and so on. These are called non-equi joins.

Q: [TRAP QUESTION] Two employees have NULL `dept_id`. Will an inner join on dept_id pair them with each other?
A: No. NULL never equals NULL, so NULL keys never match in a join.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Show each order's id, date and customer name.

**P2.** Count orders per status.

**P3.** Which join keeps all rows from both tables?

#### Level 2 — Interview application
**P4.** List products that have never been ordered.

**P5.** Show each department's name, number of employees and total salary, only for departments with total salary above 150000.

**P6.** For every employee, show their name, department name (or 'Unassigned') and manager's name (or 'None').

#### Level 3 — Scenario / problem solving
**P7.** Find the product categories each customer has bought from, as one comma-separated list per customer (exclude cancelled orders).

**P8.** Find pairs of employees in the same department where the first earns more than the second, showing both names and the salary difference. Limit the output to Finance.
:::

::: answers
**P1.**

```sql run
SELECT o.order_id, o.order_date, c.customer_name
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
ORDER BY o.order_id
LIMIT 6;
```

**P2.**

```sql run
SELECT status, COUNT(*) AS orders
FROM orders
GROUP BY status
ORDER BY orders DESC;
```

**P3.** FULL OUTER JOIN.

**P4.** Anti-join from products to order_items:

```sql run
SELECT p.product_id, p.product_name
FROM products p
LEFT JOIN order_items i ON i.product_id = p.product_id
WHERE i.product_id IS NULL;
```

**P5.**

```sql run
SELECT d.dept_name,
       COUNT(e.emp_id) AS employees,
       SUM(e.salary)   AS total_salary
FROM departments d
JOIN employees e ON e.dept_id = d.dept_id
GROUP BY d.dept_name
HAVING SUM(e.salary) > 150000
ORDER BY total_salary DESC;
```

**P6.** Two LEFT JOINs: one to departments, one self join to managers:

```sql run
SELECT e.emp_name,
       COALESCE(d.dept_name, 'Unassigned') AS department,
       COALESCE(m.emp_name, 'None')        AS manager
FROM employees e
LEFT JOIN departments d ON d.dept_id = e.dept_id
LEFT JOIN employees   m ON m.emp_id  = e.manager_id
ORDER BY e.emp_id;
```

**P7.**

```sql run
SELECT c.customer_name,
       STRING_AGG(DISTINCT p.category, ', ' ORDER BY p.category) AS categories
FROM customers c
JOIN orders o      ON o.customer_id = c.customer_id
JOIN order_items i ON i.order_id    = o.order_id
JOIN products p    ON p.product_id  = i.product_id
WHERE o.status <> 'CANCELLED'
GROUP BY c.customer_name
ORDER BY c.customer_name;
```

`DISTINCT` inside STRING_AGG removes repeated categories.

**P8.**

```sql run
SELECT a.emp_name AS higher_paid,
       b.emp_name AS lower_paid,
       a.salary - b.salary AS difference
FROM employees a
JOIN employees b
  ON a.dept_id = b.dept_id
 AND a.salary  > b.salary
WHERE a.dept_id = 2
ORDER BY difference DESC;
```

Karan and Meera both earn 70000, so neither appears as "higher paid" than the other: the strict `>` excludes equal salaries.
:::
