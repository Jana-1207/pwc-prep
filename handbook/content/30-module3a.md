# Basics of SQL (Foundational) {: .part #m3 data-label="PART III · MODULE 3" }

<p class="lead">SQL is the single most tested skill in data and software interviews, and it is where preparation pays off fastest. This module teaches SQL from the first SELECT to window functions, indexing and transactions, then drills the 22 query patterns that interviewers reuse again and again.</p>

Every query in this module was **executed on PostgreSQL while this PDF was built**, and the output you see is the real output. Type the queries yourself: reading SQL and writing SQL are different skills.

::: coverage
- **PostgreSQL Basics — Part 1**: PostgreSQL and psql, data types, SELECT, FROM, WHERE, DISTINCT, ORDER BY, LIMIT, OFFSET, aliases → Session 3.1
- **PostgreSQL Basics — Part 2**: comparison and logical operators, IN, BETWEEN, LIKE, NULL, aggregate, string, date and numeric functions, CASE → Session 3.2
- **DDL**: CREATE, ALTER, DROP, TRUNCATE, constraints → Session 3.3
- **DML**: INSERT, UPDATE, DELETE; also DCL (GRANT, REVOKE) and TCL (COMMIT, ROLLBACK) → Session 3.4
- Grouping and aggregation: GROUP BY, HAVING, WHERE vs HAVING † → Session 3.5
- Joins: inner, left, right, full outer, cross, self; referential integrity † → Session 3.6
- Subqueries and CTEs: scalar, correlated, in WHERE / FROM / SELECT; WITH; recursive CTE † → Session 3.7
- **Window Functions & Indexing**: OVER, PARTITION BY, ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, running and moving totals → Session 3.8; indexes, composite, clustered vs non-clustered → Session 3.9
- Transactions: COMMIT, ROLLBACK, ACID, isolation, dirty / non-repeatable / phantom reads † → Session 3.10
- Practice programs → the 22 SQL interview patterns, Session 3.11
- Module quiz concepts → interview questions in each session and Session 3.12
:::

| Topic | Priority |
|---|---|
| SELECT basics, filtering, NULL handling | [HIGH PRIORITY] |
| GROUP BY / HAVING, joins | [HIGH PRIORITY] [MUST KNOW] |
| Subqueries, CTEs | [HIGH PRIORITY] |
| Window functions (ROW_NUMBER, RANK, DENSE_RANK, LAG/LEAD) | [HIGH PRIORITY] |
| Indexing, transactions, ACID | [HIGH PRIORITY] |
| DDL, DML, DELETE vs TRUNCATE vs DROP | [HIGH PRIORITY] |
| Recursive CTEs, isolation levels | [MEDIUM PRIORITY] |

::: pwc PwC angle
Public PwC interview write-ups repeatedly mention SQL joins and their types, GROUP BY queries, creating and altering tables, and DBMS basics such as ACID and normalization (see the PwC Interview Orientation chapter). Data-engineering candidates also report window functions and CTEs. If you master this module and the patterns in Session 3.11, you are covered for that range.
:::

## Session 3.0 — Meet the Sample Database {: #s3-0 }

All examples in Modules 2 and 3 use one small, realistic database with an HR part, an e-commerce part and a few extra tables. Knowing its data makes every output easy to check. Bookmark this session.

[[fig:sample_db_map | The sample database. Arrows point from a foreign key to the key it references.]]

| Table | Rows | What it holds | Used for |
|---|---|---|---|
| `departments` | 5 | department name and city | joins, departments with no employees |
| `employees` | 14 | name, email, department, manager, salary, hire date, city | almost everything: filters, grouping, ranking, self joins |
| `customers` | 7 | e-commerce customers | joins, customers with no orders |
| `products` | 8 | catalogue with category and price | joins, products never sold |
| `orders` | 14 | order header: customer, date, status, total | dates, running totals, latest per customer |
| `order_items` | 20 | order lines: product, quantity, price | multi-table joins, many-to-many |
| `accounts` | 3 | bank balances | transactions and ACID |
| `leads` | 7 | marketing leads, **with duplicates** | finding and removing duplicates |
| `daily_sales` | 14 | sales per region per day | window functions |
| `user_logins` | 10 | app logins per customer | latest record, date analysis |

**Deliberate quirks** (they make interview patterns possible):

- The **Legal** department has no employees.
- **Farhan Ali** (emp 13) has no department and no email (NULLs).
- Salaries contain **ties**: Rahul and Sneha both earn 95000; Karan and Meera both earn 70000.
- Customers **Saanvi** (6) and **Reyansh** (7) have never ordered; product **Monitor Arm** (8) was never sold.
- Order IDs **107** and **112** are missing (deleted orders).
- The `leads` table contains the same email several times.

### The data you will see in outputs

```sql run
SELECT * FROM employees ORDER BY emp_id;
```

```sql run
SELECT * FROM departments ORDER BY dept_id;
```

```sql run
SELECT * FROM customers ORDER BY customer_id;
```

```sql run
SELECT * FROM products ORDER BY product_id;
```

```sql run
SELECT * FROM orders ORDER BY order_id;
```

::: tip Running the examples yourself
Install PostgreSQL (or use any hosted PostgreSQL), create a database and load the script that ships with this handbook: `psql -d handbook -f handbook/sql/sample_db.sql`. The script drops and recreates all tables, so you can reload it whenever you want fresh data.
:::

## Session 3.1 — PostgreSQL Basics (Part 1) {: #s3-1 }

### What is PostgreSQL?

**PostgreSQL** ("Postgres") is a free, open-source relational database known for correctness and features: full ACID transactions, rich SQL support (CTEs, window functions), JSON support (`JSONB`), extensions and strong standards compliance. Companies use it for everything from startup apps to large enterprise systems, and every major cloud offers a managed version (Amazon RDS / Aurora, Google Cloud SQL, Azure Database for PostgreSQL).

### How PostgreSQL organises things

`cluster (server) → databases → schemas → tables, views, functions`

- One PostgreSQL **server** can host many **databases** (`handbook`, `payroll`).
- Each database contains **schemas** (namespaces), `public` by default.
- Schemas contain **tables**, **views**, **sequences** and **functions**.

### psql: the command-line client

`psql` is PostgreSQL's terminal client. Commands starting with a backslash are **psql meta-commands**: they are handled by the client, are not SQL, and do not end with a semicolon.

| Command | What it does |
|---|---|
| `psql -h localhost -U postgres -d handbook` | connect to a database |
| `\l` | list databases |
| `\c handbook` | connect to another database |
| `\dt` | list tables in the current schema |
| `\d employees` | describe a table: columns, types, indexes, constraints |
| `\dn` / `\du` | list schemas / list users (roles) |
| `\i file.sql` | run a SQL script |
| `\x` | toggle expanded display (one column per line) |
| `\timing` | show how long each query takes |
| `\?` / `\h SELECT` | help on meta-commands / help on a SQL command |
| `\q` | quit |

### Common PostgreSQL data types

| Category | Types | Notes |
|---|---|---|
| Whole numbers | `SMALLINT`, `INTEGER` (`INT`), `BIGINT` | pick by range; IDs for big tables → `BIGINT` |
| Auto-numbering | `SERIAL`/`BIGSERIAL`, or `INT GENERATED ALWAYS AS IDENTITY` | IDENTITY is the SQL-standard, recommended form |
| Exact decimals | `NUMERIC(p, s)` / `DECIMAL(p, s)` | money: `NUMERIC(10,2)` |
| Approximate | `REAL`, `DOUBLE PRECISION` | scientific values, never money |
| Text | `VARCHAR(n)`, `TEXT`, `CHAR(n)` | `CHAR(n)` pads with spaces; `TEXT` has no length limit |
| True/false | `BOOLEAN` | `true`, `false`, or `NULL` |
| Date and time | `DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMPTZ`, `INTERVAL` | `TIMESTAMPTZ` stores a moment in time with time-zone handling |
| Others | `UUID`, `JSON`/`JSONB`, arrays (`INT[]`) | `JSONB` is binary JSON that can be indexed |

### SQL is made of sub-languages

| Sub-language | Purpose | Commands | Session |
|---|---|---|---|
| **DQL** (Data Query Language) | read data | `SELECT` | 3.1–3.8 |
| **DDL** (Data Definition Language) | define structure | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` | 3.3 |
| **DML** (Data Manipulation Language) | change data | `INSERT`, `UPDATE`, `DELETE` | 3.4 |
| **DCL** (Data Control Language) | permissions | `GRANT`, `REVOKE` | 3.4 |
| **TCL** (Transaction Control Language) | transactions | `BEGIN`, `COMMIT`, `ROLLBACK`, `SAVEPOINT` | 3.4, 3.10 |

Some textbooks count `SELECT` as part of DML; either answer is accepted if you explain it.

### SELECT and FROM: reading columns

```sql run
SELECT emp_name, city, salary
FROM employees
ORDER BY emp_id
LIMIT 5;
```

- `SELECT` lists the columns you want; `FROM` names the table.
- `SELECT *` returns every column. It is fine for exploring, but avoid it in application code: it fetches more data than needed and breaks when columns change.

### Expressions and aliases

A SELECT can compute new values. **Aliases** (`AS`) give columns and tables readable names.

```sql run
SELECT e.emp_name,
       e.salary,
       e.salary * 12        AS annual_salary,
       e.salary * 12 * 0.10 AS annual_bonus
FROM employees AS e
ORDER BY annual_salary DESC
LIMIT 4;
```

::: linebyline
| Line | What it does |
|---|---|
| `SELECT e.emp_name, e.salary,` | two existing columns; `e.` says they come from the table aliased `e` |
| `e.salary * 12 AS annual_salary` | a calculated column, renamed with an alias |
| `e.salary * 12 * 0.10 AS annual_bonus` | another calculation: 10% of annual salary |
| `FROM employees AS e` | table alias: `e` now stands for `employees` (the `AS` is optional) |
| `ORDER BY annual_salary DESC` | ORDER BY *can* use a column alias, because it runs after SELECT |
| `LIMIT 4` | keep only the first four rows of the sorted result |
:::

An alias containing spaces or capitals needs double quotes: `AS "Annual Salary"`. Single quotes are for **string values**, double quotes are for **names**.

### WHERE: filtering rows

`WHERE` keeps only the rows for which the condition is true.

| Operator | Meaning | Example |
|---|---|---|
| `=` | equal | `city = 'Pune'` |
| `<>` or `!=` | not equal | `status <> 'CANCELLED'` |
| `<`, `>`, `<=`, `>=` | comparisons | `salary >= 90000` |

```sql run
SELECT emp_name, city, salary
FROM employees
WHERE salary >= 90000
ORDER BY salary DESC;
```

Text comparisons are **case-sensitive** in PostgreSQL: `city = 'pune'` finds nothing. Text and date literals go in **single quotes**.

### Why you cannot use a SELECT alias in WHERE

```sql run error
SELECT emp_name, salary * 12 AS annual_salary
FROM employees
WHERE annual_salary > 1000000;
```

PostgreSQL evaluates `WHERE` **before** `SELECT`, so the alias does not exist yet. Repeat the expression (`WHERE salary * 12 > 1000000`) or use a subquery/CTE. The full logical order is explained in Session 3.5.

### DISTINCT: removing duplicate rows

```sql run
SELECT DISTINCT city
FROM employees
ORDER BY city;
```

`DISTINCT` applies to the **whole row of selected columns**. `SELECT DISTINCT dept_id, city` returns each unique *combination* of department and city.

::: extension DISTINCT ON (PostgreSQL only)
`SELECT DISTINCT ON (dept_id) dept_id, emp_name, salary FROM employees ORDER BY dept_id, salary DESC;` keeps the **first row per department** according to the ORDER BY, i.e. the top earner in each department. It is a handy shortcut for "top 1 per group" (Pattern 12 in Session 3.11).
:::

### ORDER BY: sorting

```sql run
SELECT emp_name, dept_id, salary
FROM employees
ORDER BY dept_id ASC NULLS FIRST, salary DESC
LIMIT 8;
```

- `ASC` (default) or `DESC`, per column; later columns break ties.
- `NULLS FIRST` / `NULLS LAST` controls where NULLs go. In PostgreSQL, NULLs sort as if **larger** than every value: last in ascending order, first in descending order.
- Without `ORDER BY`, **the row order is not guaranteed**, even if it looks stable.

### LIMIT and OFFSET: top-N and pagination

```sql run
SELECT emp_id, emp_name
FROM employees
ORDER BY emp_id
LIMIT 5 OFFSET 5;      -- page 2 when each page has 5 rows
```

- `LIMIT n` returns at most n rows; `OFFSET k` skips the first k rows. Page *p* of size *n* uses `OFFSET (p - 1) * n`.
- Always pair them with `ORDER BY`, otherwise "page 2" is undefined.
- The SQL-standard spelling is `OFFSET 5 ROWS FETCH FIRST 5 ROWS ONLY`. SQL Server uses `TOP`, Oracle uses `FETCH FIRST` (or `ROWNUM` in old versions).
- A large `OFFSET` (page 10,000) is slow, because the database still reads and throws away all skipped rows. Big apps use **keyset pagination**: `WHERE emp_id > :last_seen_id ORDER BY emp_id LIMIT 5`.

### Comments and style

```sql
-- single-line comment
/* multi-line
   comment */
SELECT emp_name          -- one column per line is easy to read
FROM employees
WHERE dept_id = 1;       -- keywords in capitals is a common convention
```

::: explain
"A basic SQL query has SELECT for the columns I want, FROM for the table, WHERE to filter rows, ORDER BY to sort, and LIMIT to restrict the number of rows. I can compute expressions and name them with aliases. One subtle point is that the database logically runs FROM and WHERE before SELECT, so a column alias defined in SELECT can't be used in WHERE, but it can be used in ORDER BY. And without ORDER BY, the order of rows is never guaranteed."
:::

::: trap
- Using a SELECT alias in WHERE: error, because WHERE runs first.
- Expecting a fixed row order without ORDER BY.
- `LIMIT` without `ORDER BY` for "top N": you get *some* N rows, not the top ones.
- Thinking `DISTINCT` works on one column when several are selected; it de-duplicates whole rows.
- Double quotes for strings: `WHERE city = "Pune"` looks for a *column* named Pune.
:::

::: questions
#### Basic
Q: [DEFINITION] What does DISTINCT do?
A: It removes duplicate rows from the result, considering all selected columns together.

Q: [HOW] How do you get the 5 highest-paid employees?
A: `SELECT emp_name, salary FROM employees ORDER BY salary DESC LIMIT 5;`

Q: [DEFINITION] What is an alias?
A: A temporary name for a column or table in a query, created with `AS`, e.g. `salary * 12 AS annual_salary` or `FROM employees e`.

Q: [COMPARISON] CHAR vs VARCHAR vs TEXT in PostgreSQL?
A: CHAR(n) is fixed length and pads with spaces; VARCHAR(n) is variable length with a maximum; TEXT is variable length without a limit. In PostgreSQL VARCHAR and TEXT perform the same.

#### Intermediate
Q: [WHY] Why can't you use a column alias in the WHERE clause?
A: WHERE is evaluated before SELECT in the logical processing order, so the alias doesn't exist yet. Repeat the expression or wrap the query in a subquery or CTE.

Q: [HOW] How do you implement pagination in SQL?
A: `ORDER BY` a unique column with `LIMIT page_size OFFSET (page - 1) * page_size`. For large tables, keyset pagination (`WHERE id > last_id ORDER BY id LIMIT n`) is faster.

Q: [COMPARISON] TIMESTAMP vs TIMESTAMPTZ?
A: TIMESTAMP stores a date and time without a time zone. TIMESTAMPTZ stores an absolute moment (internally in UTC) and converts it to the session's time zone on display, which is safer for global apps.

Q: [HOW] Where do NULLs appear when you sort in PostgreSQL?
A: Last in ascending order and first in descending order by default; you can override this with `NULLS FIRST` or `NULLS LAST`.

#### Scenario-based
Q: [SQL PROBLEM] List all distinct cities where employees earning more than 70000 work, alphabetically.
A: `SELECT DISTINCT city FROM employees WHERE salary > 70000 ORDER BY city;`

Q: [SCENARIO] Page 50,000 of a product listing is extremely slow. Why, and what would you do?
A: `OFFSET` makes the database read and discard all earlier rows. Switch to keyset (cursor) pagination using the last seen sort key, with an index on that key.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does `SELECT DISTINCT dept_id, city FROM employees` return unique departments?
A: No, it returns unique (dept_id, city) combinations, so a department appears once per distinct city.

Q: [TRAP QUESTION] Is `\dt` a SQL command?
A: No, it is a psql meta-command handled by the client. It works only in psql, not from an application.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Write a query that shows each product's name and price, most expensive first.

**P2.** Write a query that lists the distinct product categories.

**P3.** What does `LIMIT 3 OFFSET 6` return?

#### Level 2 — Interview application
**P4.** Show the name and monthly salary of employees in Bengaluru, plus a column `monthly_tax` equal to 20% of salary, highest salary first.

**P5.** Return page 3 of customers ordered by `customer_id`, with 2 customers per page.

#### Level 3 — Scenario / problem solving
**P6.** A query `SELECT emp_name, salary*12 AS yearly FROM employees WHERE yearly > 1200000;` fails. Fix it in two different ways.

**P7.** Return the three most recently hired employees, showing name, city and hire date.
:::

::: answers
**P1.**

```sql run
SELECT product_name, price
FROM products
ORDER BY price DESC;
```

**P2.**

```sql run
SELECT DISTINCT category
FROM products
ORDER BY category;
```

**P3.** It skips the first 6 rows of the (ordered) result and returns the next 3, i.e. rows 7, 8 and 9. Without ORDER BY, which rows those are is not defined.

**P4.**

```sql run
SELECT emp_name,
       salary,
       salary * 0.20 AS monthly_tax
FROM employees
WHERE city = 'Bengaluru'
ORDER BY salary DESC;
```

**P5.** Page 3 with 2 per page skips (3 − 1) × 2 = 4 rows:

```sql run
SELECT customer_id, customer_name
FROM customers
ORDER BY customer_id
LIMIT 2 OFFSET 4;
```

**P6.** (a) Repeat the expression: `WHERE salary * 12 > 1200000`. (b) Compute it in a subquery first:

```sql run
SELECT emp_name, yearly
FROM (SELECT emp_name, salary * 12 AS yearly FROM employees) AS t
WHERE yearly > 1200000;
```

**P7.**

```sql run
SELECT emp_name, city, hire_date
FROM employees
ORDER BY hire_date DESC
LIMIT 3;
```
:::

## Session 3.2 — PostgreSQL Basics (Part 2) {: #s3-2 }

### Combining conditions: AND, OR, NOT

- `AND`: both conditions must be true.
- `OR`: at least one must be true.
- `NOT`: reverses a condition.

**Precedence trap:** `AND` is evaluated before `OR`, just as multiplication comes before addition. "Employees in Pune or Mumbai earning more than 60000", written without parentheses:

```sql run
SELECT emp_name, city, salary
FROM employees
WHERE city = 'Pune' OR city = 'Mumbai' AND salary > 60000
ORDER BY emp_name;
```

Farhan (Pune, 55000) sneaked in, because the database read it as `city = 'Pune' OR (city = 'Mumbai' AND salary > 60000)`. With parentheses:

```sql run
SELECT emp_name, city, salary
FROM employees
WHERE (city = 'Pune' OR city = 'Mumbai') AND salary > 60000
ORDER BY emp_name;
```

**Rule:** whenever you mix AND and OR, add parentheses.

### IN, BETWEEN and LIKE

```sql run
SELECT emp_name, city
FROM employees
WHERE city IN ('Pune', 'Kochi', 'Delhi')
ORDER BY city, emp_name;
```

`IN (list)` is shorthand for several ORs. `NOT IN` excludes a list (careful with NULLs, see Session 3.7).

```sql run
SELECT emp_name, hire_date
FROM employees
WHERE hire_date BETWEEN '2019-01-01' AND '2020-12-31'
ORDER BY hire_date;
```

`BETWEEN a AND b` is **inclusive** at both ends (`>= a AND <= b`).

::: trap BETWEEN with timestamps
For a `TIMESTAMP` column, `BETWEEN '2024-04-01' AND '2024-04-30'` stops at **midnight at the start of 30 April**, so almost the whole last day is missed. The safe pattern is a half-open range: `login_time >= '2024-04-01' AND login_time < '2024-05-01'`.
:::

`LIKE` matches text patterns: `%` means "any number of characters" (including none), `_` means "exactly one character".

| Pattern | Matches |
|---|---|
| `'A%'` | starts with A |
| `'%a'` | ends with a |
| `'%Rao%'` | contains "Rao" |
| `'_r%'` | second letter is r |
| `ILIKE 'a%'` | starts with a or A (PostgreSQL's case-insensitive LIKE) |

```sql run
SELECT emp_name, email
FROM employees
WHERE emp_name LIKE '_r%'
   OR email ILIKE 'NEHA%';
```

### NULL: the value that means "unknown"

`NULL` means **missing or unknown**. It is not zero, not an empty string, and not false. This leads to **three-valued logic**: a condition can be TRUE, FALSE or **UNKNOWN**, and `WHERE` keeps only TRUE rows.

- `NULL = NULL` is not true; it is UNKNOWN. So `WHERE email = NULL` returns **nothing**:

```sql run
SELECT emp_name FROM employees WHERE email = NULL;
```

- Use `IS NULL` / `IS NOT NULL`:

```sql run
SELECT emp_name, email, dept_id
FROM employees
WHERE email IS NULL OR dept_id IS NULL;
```

| Expression | Result |
|---|---|
| `NULL + 100` | `NULL` (arithmetic with NULL gives NULL) |
| <code>'Hi ' &#124;&#124; NULL</code> | `NULL` (concatenation with <code>&#124;&#124;</code> gives NULL) |
| `CONCAT('Hi ', NULL)` | `'Hi '` (`CONCAT` ignores NULLs) |
| `NULL = NULL` | `NULL` (unknown), never TRUE |
| `TRUE OR NULL` | `TRUE` |
| `FALSE AND NULL` | `FALSE` |

**COALESCE** returns its first non-NULL argument, which is perfect for defaults. **NULLIF(a, b)** returns NULL when a equals b, which is handy to avoid division by zero: `x / NULLIF(y, 0)`.

```sql run
SELECT emp_name,
       COALESCE(email, 'not assigned')         AS email,
       COALESCE(dept_id::text, 'no department') AS department
FROM employees
WHERE emp_id IN (12, 13);
```

### Aggregate functions over the whole table

Aggregates turn many rows into one value: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. They **ignore NULLs**, except `COUNT(*)`, which counts rows.

```sql run
SELECT COUNT(*)             AS all_rows,
       COUNT(email)         AS with_email,
       COUNT(DISTINCT city) AS cities,
       SUM(salary)          AS payroll,
       ROUND(AVG(salary), 2) AS avg_salary,
       MIN(hire_date)       AS first_hire,
       MAX(salary)          AS top_salary
FROM employees;
```

::: linebyline
| Expression | Meaning here |
|---|---|
| `COUNT(*)` | number of rows: 14 employees |
| `COUNT(email)` | rows where email is **not NULL**: 13, because Farhan has no email |
| `COUNT(DISTINCT city)` | number of different cities |
| `SUM(salary)` | total monthly payroll |
| `ROUND(AVG(salary), 2)` | average, rounded to 2 decimals |
| `MIN(hire_date)` | MIN and MAX also work on dates and text |
:::

`AVG(column)` ignores NULLs too: the average of (100, NULL, 200) is 150, not 100. If NULL should count as zero, write `AVG(COALESCE(column, 0))`. Grouping (one result per department, etc.) comes in Session 3.5.

### String functions

| Function | Example | Result |
|---|---|---|
| `UPPER`, `LOWER`, `INITCAP` | `INITCAP('rAHUL verma')` | `Rahul Verma` |
| `LENGTH` | `LENGTH('Pune')` | 4 |
| `TRIM`, `LTRIM`, `RTRIM` | `TRIM('  Pune ')` | `Pune` |
| `SUBSTRING(s FROM start FOR n)` | `SUBSTRING('PostgreSQL' FROM 1 FOR 4)` | `Post` |
| `LEFT`, `RIGHT` | `RIGHT('ORD-9001', 4)` | `9001` |
| `POSITION(sub IN s)` / `STRPOS` | `POSITION('@' IN 'a@b.com')` | 2 |
| `REPLACE` | `REPLACE('2024/01/05', '/', '-')` | `2024-01-05` |
| `CONCAT`, <code>&#124;&#124;</code> | <code>'Mr. ' &#124;&#124; 'Rao'</code> | `Mr. Rao` |
| `SPLIT_PART(s, sep, n)` | `SPLIT_PART('a@mail.com', '@', 2)` | `mail.com` |
| `LPAD`, `RPAD` | `LPAD('42', 5, '0')` | `00042` |
| `STRING_AGG(col, sep)` (aggregate) | names joined with commas | `Asha, Ravi` |

```sql run
SELECT emp_name,
       UPPER(emp_name)                AS shouting,
       SPLIT_PART(emp_name, ' ', 1)   AS first_name,
       SPLIT_PART(email, '@', 2)      AS email_domain,
       LENGTH(emp_name)               AS name_length
FROM employees
WHERE dept_id = 2;
```

### Date and time functions

Real queries use `CURRENT_DATE` or `NOW()`. To keep this book's outputs stable, the examples treat **31 December 2024** as "today".

| Function | Example | Result |
|---|---|---|
| `CURRENT_DATE`, `NOW()` | today's date, current timestamp | depends on when you run it |
| `EXTRACT(part FROM d)` | `EXTRACT(YEAR FROM DATE '2024-03-05')` | 2024 |
| `DATE_TRUNC('month', d)` | `DATE_TRUNC('month', TIMESTAMP '2024-03-05 10:00')` | 2024-03-01 00:00:00 |
| date − date | `DATE '2024-03-05' - DATE '2024-03-01'` | 4 (days, as an integer) |
| date + interval | `DATE '2024-01-31' + INTERVAL '1 month'` | 2024-02-29 00:00:00 |
| `AGE(a, b)` | `AGE(DATE '2024-12-31', DATE '2015-04-01')` | 9 years 8 mons 30 days |
| `TO_CHAR(d, fmt)` | `TO_CHAR(DATE '2024-03-05', 'DD Mon YYYY')` | 05 Mar 2024 |
| `TO_DATE(s, fmt)` / cast | `TO_DATE('05/03/2024', 'DD/MM/YYYY')` | 2024-03-05 |

```sql run
SELECT emp_name,
       hire_date,
       EXTRACT(YEAR FROM hire_date)       AS hire_year,
       TO_CHAR(hire_date, 'Mon YYYY')     AS hired_in,
       DATE '2024-12-31' - hire_date      AS days_employed,
       AGE(DATE '2024-12-31', hire_date)  AS tenure
FROM employees
WHERE emp_id IN (1, 10, 14);
```

### Numeric functions and the integer-division trap

| Function | Example | Result |
|---|---|---|
| `ROUND(x, d)` | `ROUND(84571.4286, 2)` | 84571.43 |
| `CEIL`, `FLOOR` | `CEIL(4.1)`, `FLOOR(4.9)` | 5, 4 |
| `TRUNC(x, d)` | `TRUNC(4.567, 1)` | 4.5 |
| `ABS`, `POWER`, `SQRT` | `ABS(-7)`, `POWER(2, 10)` | 7, 1024 |
| `MOD(a, b)` or `a % b` | `7 % 3` | 1 |

```sql run
SELECT 5 / 2          AS int_division,
       5 / 2.0        AS decimal_division,
       5::numeric / 2 AS cast_first,
       7 % 3          AS remainder;
```

When **both** operands are integers, PostgreSQL does integer division and drops the fraction: `5 / 2 = 2`. This silently breaks percentage calculations like `delivered_count / total_count * 100`. Cast one side first: `delivered_count::numeric / total_count`.

`CAST(x AS type)` and the PostgreSQL shortcut `x::type` convert between types: `'2024-03-05'::date`, `salary::int`, `dept_id::text`.

### CASE WHEN: if-then-else inside SQL

`CASE` evaluates conditions **in order** and returns the result of the first true one; `ELSE` covers everything else (without `ELSE`, the result is NULL).

```sql run
SELECT emp_name,
       salary,
       CASE
           WHEN salary >= 110000 THEN 'Band A'
           WHEN salary >= 80000  THEN 'Band B'
           WHEN salary >= 60000  THEN 'Band C'
           ELSE 'Band D'
       END AS salary_band
FROM employees
ORDER BY salary DESC;
```

::: linebyline
| Line | What it does |
|---|---|
| `CASE` | start of the conditional expression |
| `WHEN salary >= 110000 THEN 'Band A'` | checked first; 150000, 120000 and 110000 stop here |
| `WHEN salary >= 80000 THEN 'Band B'` | only reached if the first test failed, so this means 80000–109999 |
| `ELSE 'Band D'` | everything that matched no WHEN |
| `END AS salary_band` | closes the CASE and names the new column |
:::

CASE also works inside `ORDER BY` (custom sort orders) and inside aggregates, the basis of **conditional aggregation** (Pattern 18):

```sql run
SELECT COUNT(*) FILTER (WHERE status = 'DELIVERED')    AS delivered,
       SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending,
       COUNT(*)                                        AS total
FROM orders;
```

`COUNT(*) FILTER (WHERE …)` is PostgreSQL's neat syntax; `SUM(CASE WHEN … THEN 1 ELSE 0 END)` works in every database.

::: explain
"NULL in SQL means unknown, not zero or empty, so comparisons with NULL return unknown, and WHERE only keeps rows where the condition is true. That's why we must write IS NULL instead of = NULL. Aggregates like SUM and AVG ignore NULLs, and COUNT of a column counts only non-null values, while COUNT(*) counts all rows. To replace NULLs with a default, I use COALESCE, and NULLIF helps avoid division by zero."
:::

::: trap
- `WHERE col = NULL` returns nothing; use `IS NULL`.
- Mixing AND/OR without parentheses.
- `BETWEEN` on timestamps misses most of the last day; use `>= start AND < next_day`.
- `LIKE` is case-sensitive in PostgreSQL; use `ILIKE` or `LOWER(col) LIKE …`.
- Integer division: `5/2 = 2`.
- `COUNT(column)` silently skips NULLs; `AVG` ignores NULLs instead of counting them as zero.
- `CASE` without `ELSE` returns NULL for unmatched rows.
:::

::: questions
#### Basic
Q: [COMPARISON] What is the difference between `IN` and `BETWEEN`?
A: IN matches any value in a list (`city IN ('Pune','Delhi')`); BETWEEN matches a continuous, inclusive range (`salary BETWEEN 50000 AND 90000`).

Q: [DEFINITION] What do `%` and `_` mean in LIKE?
A: `%` matches any sequence of characters (including none); `_` matches exactly one character.

Q: [HOW] How do you find rows where a column has no value?
A: `WHERE column IS NULL`. Using `= NULL` never matches.

Q: [COMPARISON] COUNT(*) vs COUNT(column)?
A: COUNT(*) counts all rows; COUNT(column) counts rows where that column is not NULL.

#### Intermediate
Q: [DEFINITION] What is COALESCE?
A: A function returning its first non-NULL argument, used to substitute defaults: `COALESCE(phone, 'N/A')`.

Q: [WHY] What does `SELECT 7/2` return in PostgreSQL, and why?
A: 3, because both operands are integers, so integer division truncates the fraction. Use `7/2.0` or `7::numeric/2` for 3.5.

Q: [HOW] How would you extract the domain from an email address?
A: `SPLIT_PART(email, '@', 2)`, or `SUBSTRING(email FROM POSITION('@' IN email) + 1)`.

Q: [DEFINITION] What is three-valued logic?
A: SQL conditions evaluate to TRUE, FALSE or UNKNOWN (when NULL is involved). WHERE keeps only TRUE, so UNKNOWN rows are filtered out.

Q: [HOW] How do you count delivered and pending orders in one query?
A: Conditional aggregation: `SUM(CASE WHEN status='DELIVERED' THEN 1 ELSE 0 END)` and the same for PENDING, or PostgreSQL's `COUNT(*) FILTER (WHERE status = 'DELIVERED')`.

#### Scenario-based
Q: [SQL PROBLEM] Find employees whose name starts with "A" or "R" and who were hired after 2018.
A: `SELECT emp_name, hire_date FROM employees WHERE (emp_name LIKE 'A%' OR emp_name LIKE 'R%') AND hire_date >= '2019-01-01';` Note the parentheses.

Q: [SCENARIO] A report divides `delivered_orders / total_orders` and always shows 0. Why?
A: Both values are integers, so integer division truncates to 0. Cast one side to numeric and use `NULLIF(total_orders, 0)` to avoid division by zero.

Q: [SCENARIO] An average rating looks too high because unrated items have NULL. What's happening?
A: AVG ignores NULLs, so only rated items are averaged. That's usually correct; if unrated must count as 0, use `AVG(COALESCE(rating, 0))`, and state the business rule clearly.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is `NULL = NULL` true?
A: No, it is UNKNOWN (NULL). Use `IS NULL`, or `IS NOT DISTINCT FROM` to compare two possibly-NULL values.

Q: [TRAP QUESTION] Is an empty string the same as NULL?
A: In PostgreSQL, no: `''` is a known, empty value, while NULL is unknown. (Oracle is the exception: it treats `''` as NULL.)
:::

::: practice
#### Level 1 — Basic understanding
**P1.** List products in the Furniture or Stationery category priced under 3000.

**P2.** Show employees with no manager.

**P3.** What does `COALESCE(NULL, NULL, 'x', 'y')` return?

#### Level 2 — Interview application
**P4.** Show each order's id, status and a column `is_open` that is 'Yes' for PENDING or SHIPPED orders and 'No' otherwise.

**P5.** Count customers who have an email and customers who don't, in one row.

**P6.** List employees hired in 2021 or later whose email domain is `company.com`, showing the year they joined.

#### Level 3 — Scenario / problem solving
**P7.** Marketing wants leads whose email does not end with `mail.com`. Write it, and say what happens to rows whose email is NULL.

**P8.** Calculate the percentage of orders that are DELIVERED, rounded to one decimal place, avoiding integer division.
:::

::: answers
**P1.**

```sql run
SELECT product_name, category, price
FROM products
WHERE category IN ('Furniture', 'Stationery')
  AND price < 3000
ORDER BY price;
```

**P2.**

```sql run
SELECT emp_id, emp_name
FROM employees
WHERE manager_id IS NULL;
```

**P3.** `'x'`, the first non-NULL argument.

**P4.**

```sql run
SELECT order_id,
       status,
       CASE WHEN status IN ('PENDING', 'SHIPPED') THEN 'Yes' ELSE 'No' END AS is_open
FROM orders
ORDER BY order_id;
```

**P5.** `COUNT(email)` skips NULLs, so the difference from `COUNT(*)` is the number without an email:

```sql run
SELECT COUNT(email)            AS with_email,
       COUNT(*) - COUNT(email) AS without_email
FROM customers;
```

**P6.**

```sql run
SELECT emp_name,
       EXTRACT(YEAR FROM hire_date) AS joined_year
FROM employees
WHERE hire_date >= '2021-01-01'
  AND SPLIT_PART(email, '@', 2) = 'company.com'
ORDER BY hire_date;
```

Farhan (hired 2024) is missing: his email is NULL, so the domain test is UNKNOWN and the row is filtered out.

**P7.** `SELECT * FROM leads WHERE email NOT LIKE '%mail.com';` In this table every lead's email ends with `mail.com`, so it returns no rows. In general, rows with a NULL email would also be excluded, because `NULL NOT LIKE …` is UNKNOWN. Add `OR email IS NULL` if they should be included.

**P8.**

```sql run
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'DELIVERED') / COUNT(*), 1)
       AS delivered_pct
FROM orders;
```

Multiplying by `100.0` (a decimal) first makes the whole calculation decimal, so nothing is truncated.
:::
