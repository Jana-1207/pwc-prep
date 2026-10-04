## Session 3.7 — Subqueries and CTEs {: #s3-7 }

[HIGH PRIORITY] Most "medium" SQL interview questions are solved with a subquery, a CTE or a window function. Often all three work, and interviewers like to hear you compare them.

### What is a subquery?

**A subquery is a query inside another query.** The inner query produces a value, a list or a table, and the outer query uses it. "Who earns more than the average?" needs the average first, and that is a subquery.

| Kind | Returns | Where it is used | Example |
|---|---|---|---|
| **Scalar** | one value (1 row, 1 column) | WHERE, SELECT, HAVING | `(SELECT AVG(salary) FROM employees)` |
| **Multi-row** | a list of values | `IN`, `ANY`, `ALL`, `EXISTS` | `dept_id IN (SELECT dept_id FROM departments WHERE …)` |
| **Table (derived table)** | rows and columns | FROM | `FROM (SELECT …) AS t` |
| **Correlated** | depends on the current outer row | WHERE, SELECT | `salary > (SELECT AVG(salary) FROM employees x WHERE x.dept_id = e.dept_id)` |

### Scalar subquery in WHERE

```sql run
SELECT emp_name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;
```

::: linebyline
| Part | What it does |
|---|---|
| `(SELECT AVG(salary) FROM employees)` | runs first and returns one number: the company average (84571.43) |
| `WHERE salary > (…)` | compares every employee with that single number |
:::

You cannot write `WHERE salary > AVG(salary)`: aggregates are not allowed in WHERE (Session 3.5). The subquery computes the aggregate separately.

A scalar subquery must return **at most one row**. If it returns several, PostgreSQL stops with an error:

```sql run error
SELECT emp_name
FROM employees
WHERE salary = (SELECT salary FROM employees WHERE dept_id = 2);
```

Use `IN` for lists, or make the inner query return one value (MAX, LIMIT 1 or a precise filter).

### Multi-row subquery with IN, ANY and ALL

Employees who work in departments located in Bengaluru or Mumbai:

```sql run
SELECT emp_name, dept_id
FROM employees
WHERE dept_id IN (SELECT dept_id
                  FROM departments
                  WHERE location IN ('Bengaluru', 'Mumbai'))
ORDER BY dept_id, emp_name;
```

- `x > ANY (subquery)`: greater than **at least one** value (that is, greater than the minimum).
- `x > ALL (subquery)`: greater than **every** value (that is, greater than the maximum).

```sql run
SELECT emp_name, salary
FROM employees
WHERE salary > ALL (SELECT salary FROM employees WHERE dept_id = 2);
```

Everyone listed earns more than every Finance employee, and Finance's top salary is 110000.

### Subquery in FROM (derived table)

A subquery in FROM acts like a temporary table. Give it an alias (`AS dept_avg`): most databases, and PostgreSQL before version 16, require one.

```sql run
SELECT dept_id, avg_salary
FROM (SELECT dept_id, ROUND(AVG(salary), 2) AS avg_salary
      FROM employees
      WHERE dept_id IS NOT NULL
      GROUP BY dept_id) AS dept_avg
WHERE avg_salary > 70000
ORDER BY avg_salary DESC;
```

The outer query can filter on `avg_salary` by name, because the inner query has already turned it into a column. This is the subquery alternative to HAVING, and a way around the "can't use an alias in WHERE" rule.

### Subquery in SELECT

```sql run
SELECT emp_name,
       salary,
       (SELECT ROUND(AVG(salary), 2) FROM employees) AS company_avg,
       salary - (SELECT ROUND(AVG(salary), 2) FROM employees) AS diff_from_avg
FROM employees
WHERE dept_id = 4;
```

### Correlated subqueries

A **correlated** subquery refers to a column of the outer query, so conceptually it **re-runs for each outer row**. Classic question: "employees who earn more than the average of *their own* department".

```sql run
SELECT e.emp_name, e.dept_id, e.salary
FROM employees e
WHERE e.salary > (SELECT AVG(x.salary)
                  FROM employees x
                  WHERE x.dept_id = e.dept_id)
ORDER BY e.dept_id;
```

::: linebyline
| Part | What it does |
|---|---|
| `FROM employees e` | the outer query looks at one employee at a time |
| `(SELECT AVG(x.salary) FROM employees x WHERE x.dept_id = e.dept_id)` | for *that* employee, compute the average of their department; `e.dept_id` links inner to outer |
| `WHERE e.salary > (…)` | keep the employee if they beat their department's average |
:::

Farhan never appears: his `dept_id` is NULL, `x.dept_id = NULL` matches nothing, the average is NULL, and the comparison is UNKNOWN.

**Performance:** a correlated subquery can be slow on big tables if it really runs once per row, although modern optimizers often rewrite it as a join. The same question can be answered with a join to a grouped derived table, or with a window function (Session 3.8), which reads the table once:

```sql
SELECT emp_name, dept_id, salary
FROM (SELECT emp_name, dept_id, salary,
             AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg
      FROM employees) t
WHERE salary > dept_avg;
```

### EXISTS and NOT EXISTS

`EXISTS (subquery)` is true if the subquery returns **at least one row**. It does not matter what the subquery selects; `SELECT 1` is the convention.

Customers who have placed at least one order (a **semi-join**):

```sql run
SELECT c.customer_name
FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)
ORDER BY c.customer_name;
```

Customers who have never ordered (an **anti-join**):

```sql run
SELECT c.customer_name
FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
```

### The NOT IN + NULL trap

[TRAP QUESTION] "Find employees who are not managers of anyone." The natural attempt:

```sql run
SELECT emp_name
FROM employees
WHERE emp_id NOT IN (SELECT manager_id FROM employees);
```

**Zero rows**, even though most employees manage nobody. Why? The subquery's list contains a **NULL** (Arjun has no manager). `x NOT IN (1, 2, NULL)` means `x <> 1 AND x <> 2 AND x <> NULL`, and `x <> NULL` is UNKNOWN, so the whole condition can never be TRUE. Two correct versions:

```sql run
SELECT e.emp_name
FROM employees e
WHERE NOT EXISTS (SELECT 1 FROM employees x WHERE x.manager_id = e.emp_id)
ORDER BY e.emp_name;
```

```sql
-- or remove NULLs from the list explicitly
WHERE emp_id NOT IN (SELECT manager_id FROM employees WHERE manager_id IS NOT NULL)
```

**Habit:** prefer `NOT EXISTS` over `NOT IN` with subqueries.

| | IN | EXISTS |
|---|---|---|
| Checks | is the value in the list? | does at least one matching row exist? |
| NULLs in the subquery | `NOT IN` breaks (returns nothing) | `NOT EXISTS` is safe |
| Typical use | small, fixed or NULL-free lists | correlated "has / has no related rows" checks |
| Performance | modern optimizers often plan both the same way; `EXISTS` can stop at the first match | |

### Subquery or join?

| Prefer a JOIN when… | Prefer a subquery when… |
|---|---|
| you need columns from both tables in the output | you only need to *filter* by the other table (EXISTS / IN) |
| the relationship is a straightforward key match | you need an aggregate first (compare with an average) |
| | it reads more naturally: "customers with no orders" → NOT EXISTS |

### CTEs: Common Table Expressions (WITH)

A **CTE** gives a name to a subquery and puts it **at the top** of the statement. The query then reads top to bottom like steps in a recipe.

```sql run
WITH dept_stats AS (
    SELECT dept_id,
           COUNT(*)              AS headcount,
           ROUND(AVG(salary), 2) AS avg_salary
    FROM employees
    WHERE dept_id IS NOT NULL
    GROUP BY dept_id
),
big_depts AS (
    SELECT * FROM dept_stats WHERE headcount >= 2
)
SELECT d.dept_name, b.headcount, b.avg_salary
FROM big_depts b
JOIN departments d ON d.dept_id = b.dept_id
ORDER BY b.avg_salary DESC;
```

::: linebyline
| Part | What it does |
|---|---|
| `WITH dept_stats AS (…)` | step 1: a named result with headcount and average salary per department |
| `big_depts AS (SELECT * FROM dept_stats …)` | step 2: a second CTE can use the first one |
| final `SELECT … FROM big_depts JOIN departments` | step 3: the main query uses the CTEs like tables |
:::

**Why CTEs are useful:**

- **Readability:** complex logic becomes named steps instead of nested brackets.
- **Reuse:** a CTE can be referenced several times in the same query.
- **Debugging:** run each step on its own.
- **Recursion:** only CTEs can be recursive (below).

A CTE exists only for the duration of that one statement.

::: extension CTEs and performance in PostgreSQL
Since PostgreSQL 12, simple CTEs are inlined into the main query and optimized like subqueries. Writing `WITH x AS MATERIALIZED (…)` forces PostgreSQL to compute the CTE once and store it, which helps when an expensive CTE is referenced many times. Before version 12, every CTE was materialized, which sometimes made CTE queries slower than the subquery version.
:::

### Recursive CTEs

A **recursive CTE** refers to itself. It is the standard SQL tool for **hierarchies** (org charts, category trees, folder structures) and for generating sequences. It has two parts joined by `UNION ALL`:

1. the **anchor** member: the starting rows;
2. the **recursive** member: joins back to the CTE to find the next level, and repeats until it returns no new rows.

[[fig:org_chart | The reporting hierarchy stored in the employees table through manager_id.]]

```sql run
WITH RECURSIVE org AS (
    -- anchor: the top of the hierarchy
    SELECT emp_id, emp_name, manager_id,
           1 AS level,
           emp_name::text AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- recursive step: people who report to someone already found
    SELECT e.emp_id, e.emp_name, e.manager_id,
           o.level + 1,
           o.path || ' > ' || e.emp_name
    FROM employees e
    JOIN org o ON e.manager_id = o.emp_id
)
SELECT level, emp_name, path
FROM org
ORDER BY path;
```

::: linebyline
| Part | What it does |
|---|---|
| `WITH RECURSIVE org AS (` | declares a CTE that may refer to itself |
| anchor `WHERE manager_id IS NULL` | starts from Arjun, the person with no manager (level 1) |
| `UNION ALL` | adds each new level's rows to the result |
| `JOIN org o ON e.manager_id = o.emp_id` | finds employees whose manager is already in `org`, one level deeper |
| `o.level + 1`, <code>o.path &#124;&#124; ' &gt; ' &#124;&#124; e.emp_name</code> | carries the depth and the chain of names downward |
| stops when | a step finds no new employees (Pooja has no reports) |
:::

Recursion also generates sequences. Here are the first seven days of March 2024 (in PostgreSQL, `generate_series` does the same more simply):

```sql run
WITH RECURSIVE days AS (
    SELECT DATE '2024-03-01' AS day
    UNION ALL
    SELECT (day + 1)::date FROM days WHERE day < DATE '2024-03-07'
)
SELECT day FROM days;
```

Always make sure the recursive part eventually returns no rows (a stopping condition). A cycle in the data, such as A manages B and B manages A, would otherwise loop. PostgreSQL 14+ even has a `CYCLE` clause to detect this.

### CTE vs subquery vs view vs temporary table

| | Subquery | CTE | View | Temporary table |
|---|---|---|---|---|
| Lives for | one query (inline) | one statement | permanently (until dropped) | the session |
| Named and reusable | no | within the statement | across queries and users | within the session |
| Stores data | no | no (unless materialized) | no (a materialized view does) | yes |
| Best for | small, one-off logic | readable multi-step queries, recursion | shared logic, security (expose only some columns) | big intermediate results reused by many queries |

::: explain
"A subquery is a query nested inside another. It can return a single value for a comparison, a list for IN or EXISTS, or a whole derived table in the FROM clause. A correlated subquery refers to the outer row, like comparing each employee with their own department's average. A CTE, written with WITH, is a named subquery placed at the top, which makes multi-step logic much more readable and can be referenced more than once. Recursive CTEs handle hierarchies like an org chart. One trap I always avoid is NOT IN with a subquery that may contain NULLs; it returns no rows, so I use NOT EXISTS instead."
:::

::: trap
- `NOT IN (subquery)` returns nothing if the subquery yields any NULL. Use `NOT EXISTS`.
- A scalar subquery that returns more than one row raises an error.
- Forgetting the alias on a derived table (`FROM (SELECT …) AS t`): required by most databases and by PostgreSQL before version 16.
- Thinking a CTE is stored like a table; it lives only for one statement.
- A recursive CTE without a stopping condition loops until it errors.
:::

::: questions
#### Basic
Q: [DEFINITION] What is a subquery?
A: A query nested inside another query (in WHERE, FROM, SELECT or HAVING) whose result is used by the outer query.

Q: [DEFINITION] What is a correlated subquery?
A: A subquery that references a column of the outer query, so it is conceptually evaluated once per outer row, e.g. comparing each employee's salary with their own department's average.

Q: [DEFINITION] What is a CTE?
A: A Common Table Expression: a named temporary result defined with WITH at the start of a statement and used by the main query.

#### Intermediate
Q: [COMPARISON] IN vs EXISTS?
A: IN checks membership in a list of values; EXISTS checks whether a correlated subquery returns any row. NOT EXISTS is safe with NULLs, while NOT IN returns nothing if the list contains NULL.

Q: [COMPARISON] Subquery vs CTE?
A: Logically similar. A CTE is named, defined up front, readable, reusable within the statement and can be recursive; a subquery is inline and anonymous.

Q: [WHY] Why might `WHERE id NOT IN (SELECT parent_id FROM t)` return no rows?
A: If parent_id contains a NULL, every NOT IN comparison becomes UNKNOWN. Filter the NULLs out or use NOT EXISTS.

Q: [HOW] How does a recursive CTE work?
A: An anchor query produces the starting rows; a recursive query joins back to the CTE to find the next level; results are combined with UNION ALL, repeating until no new rows appear.

Q: [COMPARISON] Correlated subquery vs window function for "above department average"?
A: Both are correct. The window function (`AVG() OVER (PARTITION BY dept_id)`) reads the data once and is usually faster and clearer; the correlated subquery can be costly on large tables unless the optimizer rewrites it.

#### Scenario-based
Q: [SQL PROBLEM] Find products priced above the average price of their own category.
A: `SELECT product_name, category, price FROM products p WHERE price > (SELECT AVG(price) FROM products x WHERE x.category = p.category);`

Q: [SQL PROBLEM] List departments that have no employees.
A: `SELECT dept_name FROM departments d WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.dept_id = d.dept_id);`

Q: [DESIGN QUESTION] How would you store and query a product category tree (Electronics > Computers > Laptops)?
A: Store `categories(category_id, name, parent_id REFERENCES categories)`, an adjacency list, and query descendants or full paths with a recursive CTE.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does `EXISTS (SELECT NULL FROM …)` work?
A: Yes. EXISTS only checks whether rows exist; what is selected is irrelevant.

Q: [TRAP QUESTION] Can a CTE be used in UPDATE or DELETE?
A: Yes, in PostgreSQL a WITH clause can precede INSERT, UPDATE and DELETE, and CTEs can even contain data-modifying statements.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Find the product(s) with the highest price using a subquery.

**P2.** List customers who have placed at least one order using IN.

**P3.** What is wrong with `SELECT * FROM (SELECT emp_name FROM employees);` in PostgreSQL versions before 16?

#### Level 2 — Interview application
**P4.** Using a CTE, find the total revenue per customer and then show only customers whose revenue is above the average customer revenue.

**P5.** Find the employees who are managers (they appear as someone's manager_id) using EXISTS.

#### Level 3 — Scenario / problem solving
**P6.** Write a recursive CTE that lists everyone who reports, directly or indirectly, to Priya Sharma (emp 2), with their level below her.

**P7.** For each order, show the order id, its total and the customer's average order total, using a correlated subquery. Then rewrite it with a window function.
:::

::: answers
**P1.**

```sql run
SELECT product_name, price
FROM products
WHERE price = (SELECT MAX(price) FROM products);
```

**P2.**

```sql run
SELECT customer_name
FROM customers
WHERE customer_id IN (SELECT customer_id FROM orders)
ORDER BY customer_name;
```

**P3.** The derived table has no alias. Before PostgreSQL 16 (and in most other databases), a subquery in FROM must be named: `FROM (SELECT …) AS t`. Version 16 relaxed this rule, but writing the alias is still the portable habit.

**P4.**

```sql run
WITH customer_revenue AS (
    SELECT customer_id, SUM(total_amount) AS revenue
    FROM orders
    WHERE status <> 'CANCELLED'
    GROUP BY customer_id
)
SELECT c.customer_name, r.revenue
FROM customer_revenue r
JOIN customers c ON c.customer_id = r.customer_id
WHERE r.revenue > (SELECT AVG(revenue) FROM customer_revenue)
ORDER BY r.revenue DESC;
```

The CTE is used twice: once in the main query and once inside the scalar subquery.

**P5.**

```sql run
SELECT m.emp_id, m.emp_name
FROM employees m
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.manager_id = m.emp_id)
ORDER BY m.emp_id;
```

**P6.**

```sql run
WITH RECURSIVE team AS (
    SELECT emp_id, emp_name, 1 AS level
    FROM employees
    WHERE manager_id = 2                -- Priya's direct reports
    UNION ALL
    SELECT e.emp_id, e.emp_name, t.level + 1
    FROM employees e
    JOIN team t ON e.manager_id = t.emp_id
)
SELECT level, emp_name
FROM team
ORDER BY level, emp_name;
```

**P7.** Correlated subquery version:

```sql run
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       (SELECT ROUND(AVG(x.total_amount), 2)
        FROM orders x
        WHERE x.customer_id = o.customer_id) AS customer_avg
FROM orders o
ORDER BY o.customer_id, o.order_id
LIMIT 6;
```

Window function version, which reads the table once:

```sql
SELECT order_id, customer_id, total_amount,
       ROUND(AVG(total_amount) OVER (PARTITION BY customer_id), 2) AS customer_avg
FROM orders
ORDER BY customer_id, order_id;
```
:::
