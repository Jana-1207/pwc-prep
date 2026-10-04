## SQL Question Bank: Top 50 SQL Questions {: #f2 }

<p class="lead">Fifty problems on the sample database (Session 3.0), from warm-ups to the hard questions that separate candidates. Try each one before reading the solution. Every solution below was executed on PostgreSQL while this PDF was built.</p>

::: tip How to practise with this bank
Write your answer on paper or in psql first. Then compare: is your result identical? Did you handle ties, NULLs and cancelled orders the way the question asks? If your query differs but gives the same result, it may still be correct. Interviewers accept any correct, readable solution.
:::

### The questions

| # | Question | Level | Pattern |
|---|---|---|---|
| 1 | List Engineering employees (dept 1), highest salary first | [EASY] | filter, sort |
| 2 | Employees hired on or after 1 Jan 2020 | [EASY] | date filter |
| 3 | Employees whose name starts with "R" | [EASY] | LIKE |
| 4 | Number of employees per city | [EASY] | GROUP BY |
| 5 | Average salary per department, rounded to 2 decimals | [EASY] | GROUP BY |
| 6 | The 3 most expensive products | [EASY] | ORDER BY + LIMIT |
| 7 | Customer names in upper case with their email domain | [EASY] | string functions |
| 8 | Customers who signed up in 2024 | [EASY] | date filter |
| 9 | Total revenue from DELIVERED orders | [EASY] | aggregation |
| 10 | Employees without an email address | [EASY] | IS NULL |
| 11 | Number of orders per customer | [EASY] | GROUP BY |
| 12 | Furniture products priced above 5000 | [EASY] | filter |
| 13 | Each employee with their department name | [EASY] | INNER JOIN |
| 14 | Highest and lowest salary in the company | [EASY] | MIN / MAX |
| 15 | Orders placed in March 2024 | [EASY] | half-open date range |
| 16 | Second-highest salary | [MEDIUM] | subquery |
| 17 | Third-highest distinct salary and who earns it | [MEDIUM] | DENSE_RANK |
| 18 | Departments with more than 2 employees | [MEDIUM] | HAVING |
| 19 | Customers who have never ordered | [MEDIUM] | anti-join |
| 20 | Products that have never been ordered | [MEDIUM] | anti-join |
| 21 | Employees earning more than the company average | [MEDIUM] | scalar subquery |
| 22 | Employees earning more than their department's average | [MEDIUM] | correlated subquery / window |
| 23 | Emails that appear more than once in `leads` | [MEDIUM] | duplicates |
| 24 | Every employee with their manager's name (including the top boss) | [MEDIUM] | self LEFT JOIN |
| 25 | All departments with employee counts, including empty ones | [MEDIUM] | LEFT JOIN + COUNT(col) |
| 26 | Top 2 earners in each department | [MEDIUM] | top N per group |
| 27 | Latest order of each customer | [MEDIUM] | ROW_NUMBER / DISTINCT ON |
| 28 | Revenue by product category, excluding cancelled orders | [MEDIUM] | multi-table join |
| 29 | Order count and revenue per month | [MEDIUM] | DATE_TRUNC |
| 30 | Percentage of orders in each status | [MEDIUM] | window over aggregate |
| 31 | Customers whose total spend (excluding cancelled) exceeds 20000 | [MEDIUM] | HAVING |
| 32 | For each order: number of distinct products and total quantity | [MEDIUM] | GROUP BY |
| 33 | Managers and how many direct reports each has | [MEDIUM] | self join |
| 34 | Rank products by revenue (ties share a rank, no gaps) | [MEDIUM] | DENSE_RANK |
| 35 | Running total of daily revenue | [MEDIUM] | SUM() OVER |
| 36 | Days between each customer's consecutive orders | [MEDIUM] | LAG |
| 37 | Orders per status per customer, as columns (pivot) | [MEDIUM] | conditional aggregation |
| 38 | Cities with more than one employee, listing their names | [MEDIUM] | STRING_AGG |
| 39 | Department(s) with the highest average salary | [HARD] | aggregate + rank |
| 40 | Employees who earn the top salary in their department (all ties) | [HARD] | RANK per group |
| 41 | Each employee's salary as a percentage of their department's total | [HARD] | window share |
| 42 | Missing order IDs | [HARD] | generate_series |
| 43 | Users who logged in on 3 or more consecutive days | [HARD] | gaps and islands |
| 44 | Month-over-month revenue growth (%) | [HARD] | CTE + LAG |
| 45 | Customers with at least one delivered order and none cancelled or returned | [HARD] | conditional HAVING |
| 46 | Best-selling product (by units) in each category | [HARD] | aggregate + ROW_NUMBER |
| 47 | Each employee's level and reporting chain | [HARD] | recursive CTE |
| 48 | Customers who bought both Electronics and Furniture | [HARD] | relational division |
| 49 | Customers who reordered within 30 days of a previous order | [HARD] | LAG + filter |
| 50 | 3-day moving average per region, flagging days 20% above it | [HARD] | window frame |

### Solutions: easy (1–15)

**Q1.** Engineering employees, highest salary first.

```sql run
SELECT emp_name, salary
FROM employees
WHERE dept_id = 1
ORDER BY salary DESC;
```

**Q2.** Hired on or after 1 Jan 2020.

```sql run
SELECT emp_name, hire_date
FROM employees
WHERE hire_date >= DATE '2020-01-01'
ORDER BY hire_date;
```

**Q3.** Names starting with R.

```sql run
SELECT emp_name FROM employees WHERE emp_name LIKE 'R%' ORDER BY emp_name;
```

**Q4.** Employees per city.

```sql run
SELECT city, COUNT(*) AS employees
FROM employees
GROUP BY city
ORDER BY employees DESC, city;
```

**Q5.** Average salary per department.

```sql run
SELECT d.dept_name, ROUND(AVG(e.salary), 2) AS avg_salary
FROM employees e
JOIN departments d ON d.dept_id = e.dept_id
GROUP BY d.dept_name
ORDER BY avg_salary DESC;
```

**Q6.** Three most expensive products.

```sql run
SELECT product_name, price FROM products ORDER BY price DESC LIMIT 3;
```

**Q7.** Upper-case names with email domain.

```sql run
SELECT UPPER(customer_name) AS name, SPLIT_PART(email, '@', 2) AS domain
FROM customers
ORDER BY customer_id;
```

**Q8.** Signed up in 2024.

```sql run
SELECT customer_name, signup_date
FROM customers
WHERE signup_date >= DATE '2024-01-01' AND signup_date < DATE '2025-01-01'
ORDER BY signup_date;
```

**Q9.** Revenue from delivered orders.

```sql run
SELECT SUM(total_amount) AS delivered_revenue FROM orders WHERE status = 'DELIVERED';
```

**Q10.** Employees with no email.

```sql run
SELECT emp_id, emp_name FROM employees WHERE email IS NULL;
```

**Q11.** Orders per customer.

```sql run
SELECT customer_id, COUNT(*) AS orders
FROM orders
GROUP BY customer_id
ORDER BY orders DESC, customer_id;
```

**Q12.** Furniture above 5000.

```sql run
SELECT product_name, price
FROM products
WHERE category = 'Furniture' AND price > 5000;
```

**Q13.** Employee with department name.

```sql run
SELECT e.emp_name, d.dept_name
FROM employees e
JOIN departments d ON d.dept_id = e.dept_id
ORDER BY d.dept_name, e.emp_name
LIMIT 8;
```

**Q14.** Highest and lowest salary.

```sql run
SELECT MAX(salary) AS highest, MIN(salary) AS lowest FROM employees;
```

**Q15.** Orders in March 2024 (half-open range, safe for timestamps too).

```sql run
SELECT order_id, order_date, status
FROM orders
WHERE order_date >= DATE '2024-03-01' AND order_date < DATE '2024-04-01'
ORDER BY order_date;
```

### Solutions: medium (16–38)

**Q16.** Second-highest salary.

```sql run
SELECT MAX(salary) AS second_highest
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
```

**Q17.** Third-highest distinct salary and who earns it.

```sql run
SELECT emp_name, salary
FROM (SELECT emp_name, salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
      FROM employees) t
WHERE rnk = 3;
```

**Q18.** Departments with more than 2 employees.

```sql run
SELECT d.dept_name, COUNT(*) AS employees
FROM employees e
JOIN departments d ON d.dept_id = e.dept_id
GROUP BY d.dept_name
HAVING COUNT(*) > 2;
```

**Q19.** Customers who never ordered.

```sql run
SELECT c.customer_name
FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);
```

**Q20.** Products never ordered.

```sql run
SELECT p.product_name
FROM products p
WHERE NOT EXISTS (SELECT 1 FROM order_items i WHERE i.product_id = p.product_id);
```

**Q21.** Above the company average.

```sql run
SELECT emp_name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;
```

**Q22.** Above their department's average (window version).

```sql run
SELECT emp_name, dept_id, salary, dept_avg
FROM (SELECT emp_name, dept_id, salary,
             ROUND(AVG(salary) OVER (PARTITION BY dept_id), 2) AS dept_avg
      FROM employees
      WHERE dept_id IS NOT NULL) t
WHERE salary > dept_avg
ORDER BY dept_id;
```

**Q23.** Duplicate emails in leads.

```sql run
SELECT email, COUNT(*) AS copies
FROM leads
GROUP BY email
HAVING COUNT(*) > 1;
```

**Q24.** Employee with manager name (top boss included).

```sql run
SELECT e.emp_name, COALESCE(m.emp_name, '— (no manager)') AS manager
FROM employees e
LEFT JOIN employees m ON m.emp_id = e.manager_id
ORDER BY e.emp_id;
```

**Q25.** All departments with employee counts.

```sql run
SELECT d.dept_name, COUNT(e.emp_id) AS employees
FROM departments d
LEFT JOIN employees e ON e.dept_id = d.dept_id
GROUP BY d.dept_name
ORDER BY employees DESC, d.dept_name;
```

**Q26.** Top 2 earners per department (ties included).

```sql run
WITH r AS (
    SELECT dept_id, emp_name, salary,
           DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk
    FROM employees
    WHERE dept_id IS NOT NULL
)
SELECT dept_id, emp_name, salary, rnk
FROM r
WHERE rnk <= 2
ORDER BY dept_id, rnk, emp_name;
```

**Q27.** Latest order of each customer.

```sql run
SELECT DISTINCT ON (customer_id) customer_id, order_id, order_date, status
FROM orders
ORDER BY customer_id, order_date DESC, order_id DESC;
```

**Q28.** Revenue by category.

```sql run
SELECT p.category, SUM(i.quantity * i.unit_price) AS revenue
FROM order_items i
JOIN products p ON p.product_id = i.product_id
JOIN orders   o ON o.order_id   = i.order_id
WHERE o.status <> 'CANCELLED'
GROUP BY p.category
ORDER BY revenue DESC;
```

**Q29.** Orders and revenue per month.

```sql run
SELECT DATE_TRUNC('month', order_date)::date AS month,
       COUNT(*) AS orders,
       SUM(total_amount) AS revenue
FROM orders
GROUP BY 1
ORDER BY 1;
```

**Q30.** Percentage of orders per status. The window runs over the grouped result:

```sql run
SELECT status,
       COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM orders
GROUP BY status
ORDER BY orders DESC;
```

**Q31.** Spend above 20000.

```sql run
SELECT c.customer_name, SUM(o.total_amount) AS spent
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status <> 'CANCELLED'
GROUP BY c.customer_name
HAVING SUM(o.total_amount) > 20000
ORDER BY spent DESC;
```

**Q32.** Distinct products and total quantity per order.

```sql run
SELECT order_id,
       COUNT(DISTINCT product_id) AS distinct_products,
       SUM(quantity)              AS total_qty
FROM order_items
GROUP BY order_id
ORDER BY order_id
LIMIT 6;
```

**Q33.** Managers and their direct-report counts.

```sql run
SELECT m.emp_name AS manager, COUNT(*) AS direct_reports
FROM employees e
JOIN employees m ON m.emp_id = e.manager_id
GROUP BY m.emp_name
ORDER BY direct_reports DESC, manager;
```

**Q34.** Rank products by revenue (DENSE_RANK).

```sql run
SELECT p.product_name,
       SUM(i.quantity * i.unit_price) AS revenue,
       DENSE_RANK() OVER (ORDER BY SUM(i.quantity * i.unit_price) DESC) AS rnk
FROM order_items i
JOIN products p ON p.product_id = i.product_id
GROUP BY p.product_name
ORDER BY rnk;
```

**Q35.** Running total of daily revenue.

```sql run
WITH daily AS (
    SELECT order_date, SUM(total_amount) AS revenue
    FROM orders
    WHERE status <> 'CANCELLED'
    GROUP BY order_date
)
SELECT order_date, revenue,
       SUM(revenue) OVER (ORDER BY order_date) AS running_total
FROM daily
ORDER BY order_date;
```

**Q36.** Days between consecutive orders per customer.

```sql run
SELECT customer_id, order_id, order_date,
       order_date - LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS gap_days
FROM orders
ORDER BY customer_id, order_date;
```

**Q37.** Pivot of statuses per customer.

```sql run
SELECT customer_id,
       COUNT(*) FILTER (WHERE status = 'DELIVERED') AS delivered,
       COUNT(*) FILTER (WHERE status = 'SHIPPED')   AS shipped,
       COUNT(*) FILTER (WHERE status = 'PENDING')   AS pending,
       COUNT(*) FILTER (WHERE status IN ('CANCELLED', 'RETURNED')) AS lost
FROM orders
GROUP BY customer_id
ORDER BY customer_id;
```

**Q38.** Cities with more than one employee.

```sql run
SELECT city, COUNT(*) AS employees,
       STRING_AGG(emp_name, ', ' ORDER BY emp_name) AS names
FROM employees
GROUP BY city
HAVING COUNT(*) > 1
ORDER BY employees DESC, city;
```

### Solutions: hard (39–50)

**Q39.** Department(s) with the highest average salary (ties allowed).

```sql run
WITH dept_avg AS (
    SELECT d.dept_name, AVG(e.salary) AS avg_salary
    FROM employees e
    JOIN departments d ON d.dept_id = e.dept_id
    GROUP BY d.dept_name
)
SELECT dept_name, ROUND(avg_salary, 2) AS avg_salary
FROM dept_avg
WHERE avg_salary = (SELECT MAX(avg_salary) FROM dept_avg);
```

**Q40.** Top earner(s) in each department.

```sql run
SELECT dept_id, emp_name, salary
FROM (SELECT dept_id, emp_name, salary,
             RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk
      FROM employees
      WHERE dept_id IS NOT NULL) t
WHERE rnk = 1
ORDER BY dept_id;
```

**Q41.** Salary as a percentage of the department total.

```sql run
SELECT emp_name, dept_id, salary,
       ROUND(100.0 * salary / SUM(salary) OVER (PARTITION BY dept_id), 1) AS pct_of_dept
FROM employees
WHERE dept_id IN (2, 4)
ORDER BY dept_id, pct_of_dept DESC;
```

**Q42.** Missing order IDs.

```sql run
SELECT g AS missing_id
FROM generate_series((SELECT MIN(order_id) FROM orders),
                     (SELECT MAX(order_id) FROM orders)) AS g
WHERE g NOT IN (SELECT order_id FROM orders);
```

`NOT IN` is safe here because `order_id` is a primary key and can never be NULL.

**Q43.** Three or more consecutive login days.

```sql run
WITH days AS (
    SELECT DISTINCT user_id, login_time::date AS day FROM user_logins
),
grp AS (
    SELECT user_id, day,
           day - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day))::int AS island
    FROM days
)
SELECT user_id, MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS days
FROM grp
GROUP BY user_id, island
HAVING COUNT(*) >= 3;
```

**Q44.** Month-over-month growth.

```sql run
WITH m AS (
    SELECT DATE_TRUNC('month', order_date)::date AS month, SUM(total_amount) AS revenue
    FROM orders
    WHERE status <> 'CANCELLED'
    GROUP BY 1
)
SELECT month, revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 1) AS growth_pct
FROM m
ORDER BY month;
```

**Q45.** At least one delivered order and none cancelled or returned.

```sql run
SELECT c.customer_name
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.customer_name
HAVING COUNT(*) FILTER (WHERE o.status = 'DELIVERED') >= 1
   AND COUNT(*) FILTER (WHERE o.status IN ('CANCELLED', 'RETURNED')) = 0
ORDER BY c.customer_name;
```

**Q46.** Best-selling product by units in each category.

```sql run
WITH units AS (
    SELECT p.category, p.product_name, SUM(i.quantity) AS units
    FROM order_items i
    JOIN products p ON p.product_id = i.product_id
    JOIN orders   o ON o.order_id   = i.order_id
    WHERE o.status <> 'CANCELLED'
    GROUP BY p.category, p.product_name
)
SELECT category, product_name, units
FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY units DESC, product_name) AS rn
      FROM units) t
WHERE rn = 1
ORDER BY category;
```

**Q47.** Level and reporting chain.

```sql run
WITH RECURSIVE chain AS (
    SELECT emp_id, emp_name, 1 AS level, emp_name::text AS path
    FROM employees
    WHERE manager_id IS NULL
    UNION ALL
    SELECT e.emp_id, e.emp_name, c.level + 1, c.path || ' > ' || e.emp_name
    FROM employees e
    JOIN chain c ON e.manager_id = c.emp_id
)
SELECT level, emp_name, path
FROM chain
WHERE level >= 3
ORDER BY path;
```

**Q48.** Bought both Electronics and Furniture.

```sql run
SELECT c.customer_name
FROM orders o
JOIN order_items i ON i.order_id   = o.order_id
JOIN products p    ON p.product_id = i.product_id
JOIN customers c   ON c.customer_id = o.customer_id
WHERE o.status <> 'CANCELLED'
  AND p.category IN ('Electronics', 'Furniture')
GROUP BY c.customer_name
HAVING COUNT(DISTINCT p.category) = 2
ORDER BY c.customer_name;
```

**Q49.** Reordered within 30 days of a previous order.

```sql run
WITH seq AS (
    SELECT customer_id, order_date,
           order_date - LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS gap
    FROM orders
)
SELECT DISTINCT customer_id
FROM seq
WHERE gap <= 30;
```

**Q50.** 3-day moving average with a spike flag.

```sql run
WITH ma AS (
    SELECT region, sale_date, amount,
           ROUND(AVG(amount) OVER (PARTITION BY region ORDER BY sale_date
                                   ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS moving_avg
    FROM daily_sales
)
SELECT region, sale_date, amount, moving_avg,
       CASE WHEN amount > 1.2 * moving_avg THEN 'SPIKE' ELSE '' END AS flag
FROM ma
ORDER BY region, sale_date;
```

The moving average includes the current day, so a spike must be well above its two neighbours' level to pass 120%.
