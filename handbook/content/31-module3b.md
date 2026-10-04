## Session 3.3 — DDL: Data Definition Language {: #s3-3 }

### Simple meaning

**DDL commands define and change the *structure* of the database**: creating tables, adding columns, removing tables. They work on the containers, not on the data inside (DML does that, Session 3.4).

| Command | What it does |
|---|---|
| `CREATE` | create a database object: database, schema, table, view, index, sequence |
| `ALTER` | change an existing object: add, drop or rename columns; change types; add constraints |
| `DROP` | delete an object completely, structure and data |
| `TRUNCATE` | remove **all rows** quickly but keep the table's structure |

::: note PostgreSQL detail that impresses interviewers
In PostgreSQL, DDL is **transactional**: `CREATE`, `ALTER` and even `DROP TABLE` inside a transaction can be rolled back. In MySQL and Oracle most DDL commits automatically. You will see a live demonstration below.
:::

### CREATE TABLE

```sql run keep
CREATE TABLE projects (
    project_id   INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_name VARCHAR(80)   NOT NULL,
    client       VARCHAR(60)   NOT NULL,
    dept_id      INT           REFERENCES departments(dept_id),
    budget       NUMERIC(12,2) CONSTRAINT chk_budget_positive CHECK (budget > 0),
    start_date   DATE          NOT NULL DEFAULT DATE '2024-01-01',
    status       VARCHAR(12)   NOT NULL DEFAULT 'PLANNED'
);
```

::: linebyline
| Line | What it means |
|---|---|
| `project_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY` | the database generates 1, 2, 3… automatically; it is the primary key |
| `project_name VARCHAR(80) NOT NULL` | text up to 80 characters, required |
| `dept_id INT REFERENCES departments(dept_id)` | foreign key; NULL allowed (a project may have no department yet) |
| `CONSTRAINT chk_budget_positive CHECK (budget > 0)` | a **named** constraint, so error messages and later changes are clearer |
| `DEFAULT DATE '2024-01-01'` / `DEFAULT 'PLANNED'` | values used when an INSERT does not supply them (normally you would write `DEFAULT CURRENT_DATE`) |
:::

`SERIAL` is the older PostgreSQL shortcut for auto-numbering; `GENERATED ... AS IDENTITY` is the SQL-standard way and is preferred today. MySQL uses `AUTO_INCREMENT`; SQL Server uses `IDENTITY(1,1)`.

### ALTER TABLE: changing structure

```sql run keep quiet
ALTER TABLE projects ADD COLUMN manager_id INT REFERENCES employees(emp_id);
ALTER TABLE projects RENAME COLUMN client TO client_name;
ALTER TABLE projects ALTER COLUMN project_name TYPE VARCHAR(120);
ALTER TABLE projects ADD CONSTRAINT uq_project_name UNIQUE (project_name);
ALTER TABLE projects ALTER COLUMN status SET DEFAULT 'ACTIVE';
```

| Statement | Effect |
|---|---|
| `ADD COLUMN manager_id INT REFERENCES employees(emp_id)` | new nullable column with a foreign key |
| `RENAME COLUMN client TO client_name` | renames the column; the data stays |
| `ALTER COLUMN project_name TYPE VARCHAR(120)` | widens the column (narrowing can fail if data is too long) |
| `ADD CONSTRAINT uq_project_name UNIQUE (project_name)` | adds a rule; fails if existing data already breaks it |
| `ALTER COLUMN status SET DEFAULT 'ACTIVE'` | new default for future inserts |

Other common forms: `DROP COLUMN`, `ALTER COLUMN … SET NOT NULL` / `DROP NOT NULL`, `DROP CONSTRAINT`, `RENAME TO new_table_name`.

You can inspect a table's structure through the standard `information_schema` views (psql users simply type `\d projects`):

```sql run
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'projects'
ORDER BY ordinal_position;
```

### Creating a table from an existing table (CTAS)

"Create another table with the help of existing tables" appears in reported PwC interview write-ups. **CREATE TABLE AS SELECT** copies the *result of a query* into a new table:

```sql run
CREATE TABLE high_earners AS
SELECT emp_id, emp_name, dept_id, salary
FROM employees
WHERE salary > 90000;

SELECT * FROM high_earners ORDER BY salary DESC;
```

- CTAS copies column names, types and data, but **not** primary keys, foreign keys, defaults or indexes. Add them with ALTER TABLE if needed.
- `CREATE TABLE copy_structure (LIKE employees INCLUDING ALL);` copies only the structure, including defaults, constraints and indexes, with no rows.
- `INSERT INTO existing_table SELECT …` copies rows into a table that already exists.

### DROP and TRUNCATE

```sql
DROP TABLE IF EXISTS high_earners;           -- no error if it doesn't exist
DROP TABLE departments CASCADE;              -- also drops dependent foreign keys and views (dangerous!)
TRUNCATE TABLE leads;                        -- remove all rows, keep the table
TRUNCATE TABLE projects RESTART IDENTITY;    -- also reset the auto-numbering
```

PostgreSQL refuses to truncate a table that other tables reference with foreign keys, because that would leave orphan rows:

```sql run error
TRUNCATE TABLE customers;
```

`TRUNCATE customers CASCADE` would also truncate `orders`, `order_items` and `user_logins`, which is a good reason to read every CASCADE twice.

### DDL inside a transaction (PostgreSQL)

Watch a dropped table come back:

```sql run
BEGIN;
DROP TABLE leads;
ROLLBACK;

SELECT COUNT(*) AS leads_still_here FROM leads;
```

### DELETE vs TRUNCATE vs DROP

[MUST KNOW] This comparison is asked constantly.

| | `DELETE` | `TRUNCATE` | `DROP` |
|---|---|---|---|
| Category | DML | DDL | DDL |
| Removes | chosen rows (`WHERE`) or all rows | all rows | the whole table: rows, structure, indexes, constraints |
| `WHERE` allowed | yes | no | no |
| Speed on big tables | slower: row by row, each row logged | very fast: deallocates storage pages | fast |
| Triggers | row-level `DELETE` triggers fire | `DELETE` triggers do not fire | — |
| Auto-number (identity) | not reset | can be reset (`RESTART IDENTITY`) | gone with the table |
| Table still exists | yes | yes | no |
| Rollback | yes, inside a transaction | PostgreSQL: yes, inside a transaction; MySQL/Oracle: no (auto-commits) | PostgreSQL: yes, inside a transaction; most others: no |
| Use when | removing specific rows | emptying a staging table quickly | the table is no longer needed |

::: explain
"DELETE is a DML command that removes rows one by one; it can take a WHERE clause, fires triggers and can be rolled back. TRUNCATE is DDL; it removes all rows at once by releasing the data pages, which makes it much faster on big tables, but there's no WHERE, row triggers don't fire, and it can reset identity columns. DROP removes the table itself, structure and all. In PostgreSQL both TRUNCATE and DROP can even be rolled back inside a transaction, whereas in MySQL or Oracle they auto-commit."
:::

::: trap
- Saying "TRUNCATE can never be rolled back". True for MySQL and Oracle, but not for PostgreSQL inside a transaction.
- Saying "DELETE without WHERE is the same as TRUNCATE". Same final rows, but different speed, logging, triggers and identity behaviour.
- Assuming CTAS copies constraints and indexes. It copies only columns and data.
- Using `DROP … CASCADE` casually; it silently removes dependent objects.
:::

::: questions
#### Basic
Q: [DEFINITION] What is DDL? Give examples.
A: Data Definition Language defines database structure: CREATE, ALTER, DROP and TRUNCATE (some also include RENAME and COMMENT).

Q: [COMPARISON] DELETE vs TRUNCATE vs DROP?
A: DELETE removes selected or all rows (DML, WHERE allowed, triggers fire, slower). TRUNCATE removes all rows quickly but keeps the table (DDL, no WHERE). DROP removes the entire table, structure included.

Q: [HOW] How do you add a column to an existing table?
A: `ALTER TABLE employees ADD COLUMN phone VARCHAR(15);`

#### Intermediate
Q: [HOW] How do you create a new table from an existing one?
A: `CREATE TABLE new_table AS SELECT … FROM old_table WHERE …;` It copies columns and data but not keys, defaults or indexes. Use `CREATE TABLE t (LIKE old INCLUDING ALL)` to copy only the structure.

Q: [COMPARISON] SERIAL vs IDENTITY in PostgreSQL?
A: Both auto-generate numbers through a sequence. IDENTITY is the SQL-standard syntax, with clearer ownership and permissions; SERIAL is an older PostgreSQL shortcut.

Q: [WHY] Why would TRUNCATE fail on a table?
A: If other tables reference it with foreign keys. PostgreSQL requires those tables to be truncated too, or `TRUNCATE … CASCADE`.

Q: [WHY] Why name constraints explicitly?
A: Error messages become readable (`chk_budget_positive`), and it's easier to drop or alter a constraint later.

#### Scenario-based
Q: [SCENARIO] You need to empty a 50-million-row staging table every night before reloading it. DELETE or TRUNCATE?
A: TRUNCATE. It's dramatically faster and generates far less log. DELETE would process and log every row.

Q: [SCENARIO] You must change a column from VARCHAR(20) to VARCHAR(10) on a live table. What do you check first?
A: Whether existing data fits: `SELECT MAX(LENGTH(col)) FROM t;`. Narrowing fails if values are too long. Also consider locks on a big table and whether applications expect the old length.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can you roll back a DROP TABLE?
A: In PostgreSQL, yes, if it was run inside an explicit transaction that hasn't been committed. In MySQL and Oracle, DDL auto-commits, so no (outside of features like Oracle's recycle bin).

Q: [TRAP QUESTION] Does TRUNCATE fire DELETE triggers?
A: No. Row-level DELETE triggers do not fire (PostgreSQL has separate TRUNCATE triggers).
:::

## Session 3.4 — DML: Data Manipulation Language (plus DCL and TCL) {: #s3-4 }

### Simple meaning

**DML commands change the data inside tables**: `INSERT` adds rows, `UPDATE` changes rows, `DELETE` removes rows. (`SELECT` is sometimes counted as DML too, and sometimes as DQL.)

### INSERT

```sql run
INSERT INTO departments (dept_id, dept_name, location)
VALUES (6, 'Data Science', 'Bengaluru'),
       (7, 'Operations',   'Chennai')
RETURNING *;
```

- Always list the columns: the statement keeps working if the table gets new columns, and it documents which value goes where.
- Several rows can be inserted in one statement.
- `RETURNING` (PostgreSQL) gives back the inserted rows, including generated IDs and defaults, without another query.

**INSERT … SELECT** copies rows from a query:

```sql run
INSERT INTO projects (project_name, client_name, dept_id, budget)
SELECT 'Audit automation for ' || dept_name, 'Internal', dept_id, 500000
FROM departments
WHERE location IN ('Mumbai', 'Kolkata')
RETURNING project_id, project_name, budget, status;
```

`project_id` came from the identity column and `status` from the column default ('ACTIVE', set by the ALTER in Session 3.3).

### UPSERT: insert, or update if it already exists

A very common need: "add this product; if its ID already exists, update the price instead." PostgreSQL uses `ON CONFLICT`:

```sql run
INSERT INTO products (product_id, product_name, category, price)
VALUES (1, 'Wireless Mouse', 'Electronics', 749.00),
       (9, 'Laptop Stand',   'Furniture',  1299.00)
ON CONFLICT (product_id)
DO UPDATE SET price = EXCLUDED.price
RETURNING product_id, product_name, price;
```

::: linebyline
| Line | What it means |
|---|---|
| `VALUES (1, …, 749.00), (9, …, 1299.00)` | product 1 already exists; product 9 is new |
| `ON CONFLICT (product_id)` | if inserting would violate the unique/primary key on product_id… |
| `DO UPDATE SET price = EXCLUDED.price` | …update the existing row instead; `EXCLUDED` means "the row we tried to insert" |
| `RETURNING …` | shows the final state of both rows: one updated, one inserted |
:::

`ON CONFLICT … DO NOTHING` simply skips duplicates. MySQL writes `ON DUPLICATE KEY UPDATE`; the SQL standard (and PostgreSQL 15+, SQL Server, Oracle) also offers `MERGE`.

### UPDATE

```sql run
UPDATE employees
SET salary = salary * 1.10
WHERE dept_id = 3
RETURNING emp_id, emp_name, salary;
```

- `SET` can change several columns: `SET salary = 70000, city = 'Pune'`.
- The new value can be an expression using the old one (`salary * 1.10`).
- **Without `WHERE`, every row is updated.** That is the most famous production accident in SQL.

**Updating with data from another table** (PostgreSQL's `UPDATE … FROM`): mark every pending order of customers from Ahmedabad as SHIPPED.

```sql run
UPDATE orders o
SET status = 'SHIPPED'
FROM customers c
WHERE c.customer_id = o.customer_id
  AND c.city = 'Ahmedabad'
  AND o.status = 'PENDING'
RETURNING o.order_id, c.customer_name, o.status;
```

The same can be written with a subquery: `WHERE customer_id IN (SELECT customer_id FROM customers WHERE city = 'Ahmedabad')`.

### DELETE

```sql run
DELETE FROM leads
WHERE created_at < '2024-01-05'
RETURNING lead_id, full_name, created_at;
```

- `DELETE … USING other_table` deletes based on a join, like `UPDATE … FROM`.
- Deleting a parent row that children reference fails unless the foreign key says `ON DELETE CASCADE` or `SET NULL` (Session 2.3).

::: tip Safe habits for UPDATE and DELETE
1. Write the `SELECT` with the same `WHERE` first and check the rows it returns.
2. Run the change inside `BEGIN; … ` and check the row count ("UPDATE 3") before `COMMIT`.
3. Use `RETURNING` to see exactly what changed.
4. In production, prefer a **soft delete** (an `is_deleted` flag or `deleted_at` timestamp) when you may need the data back or for audit.
:::

### DCL: Data Control Language (permissions)

DCL decides **who may do what**.

```sql
CREATE ROLE reporting_user LOGIN PASSWORD 'change-me';
GRANT SELECT ON orders, customers TO reporting_user;   -- read-only access to two tables
GRANT INSERT, UPDATE ON orders TO app_user;
REVOKE UPDATE ON orders FROM app_user;                  -- take a privilege back
```

- Follow the **principle of least privilege**: each user or application gets only the permissions it needs. A reporting tool needs `SELECT`, never `DROP`.
- Privileges are usually granted to **roles**, and users are made members of roles.
- PostgreSQL also supports **row-level security** (users see only their own rows).

### TCL: Transaction Control Language

TCL groups statements into **transactions** that succeed or fail as a unit. Full details, including ACID, come in Session 3.10.

| Command | Meaning |
|---|---|
| `BEGIN` (or `START TRANSACTION`) | start a transaction |
| `COMMIT` | make all changes permanent |
| `ROLLBACK` | undo all changes since BEGIN |
| `SAVEPOINT name` | a checkpoint inside a transaction |
| `ROLLBACK TO SAVEPOINT name` | undo back to the checkpoint only |

By default PostgreSQL runs in **autocommit** mode: each statement outside an explicit `BEGIN` is its own transaction and commits immediately.

```sql run
BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE account_id = 1;
SAVEPOINT after_debit;
UPDATE accounts SET balance = balance + 1000 WHERE account_id = 99;  -- wrong account: 0 rows
ROLLBACK TO SAVEPOINT after_debit;
UPDATE accounts SET balance = balance + 1000 WHERE account_id = 2;
COMMIT;

SELECT * FROM accounts ORDER BY account_id;
```

::: linebyline
| Line | What happens |
|---|---|
| `BEGIN;` | start a transaction; nothing is permanent yet |
| `UPDATE … - 1000 WHERE account_id = 1;` | debit Aarav |
| `SAVEPOINT after_debit;` | remember this point |
| `UPDATE … WHERE account_id = 99;` | a mistake: no such account, 0 rows changed |
| `ROLLBACK TO SAVEPOINT after_debit;` | undo only what happened after the savepoint (the debit is kept) |
| `UPDATE … + 1000 WHERE account_id = 2;` | credit the right account (Isha) |
| `COMMIT;` | both changes become permanent together |
:::

::: explain
"DML is the part of SQL that changes data: INSERT adds rows, UPDATE modifies them and DELETE removes them. In PostgreSQL I often use RETURNING to get back generated IDs or the changed rows, and INSERT … ON CONFLICT for upserts. The biggest risk is an UPDATE or DELETE without a WHERE clause, so I first run a SELECT with the same condition and wrap the change in a transaction. DCL handles permissions with GRANT and REVOKE, and TCL controls transactions with BEGIN, COMMIT, ROLLBACK and SAVEPOINT."
:::

::: trap
- `UPDATE` or `DELETE` without `WHERE` changes every row.
- Inserting without a column list: it breaks as soon as the table changes.
- Forgetting `COMMIT` after `BEGIN`: the changes are invisible to others and are lost when the session ends.
- Confusing `ROLLBACK TO SAVEPOINT` (partial undo) with `ROLLBACK` (undo everything).
- Granting broad rights (`ALL PRIVILEGES`) to application or reporting users.
:::

::: questions
#### Basic
Q: [DEFINITION] What is DML?
A: Data Manipulation Language: the commands that change data, namely INSERT, UPDATE and DELETE (SELECT is sometimes included).

Q: [COMPARISON] DDL vs DML?
A: DDL defines structure (CREATE, ALTER, DROP, TRUNCATE); DML changes the data inside the structure (INSERT, UPDATE, DELETE).

Q: [DEFINITION] What are DCL and TCL?
A: DCL controls permissions (GRANT, REVOKE). TCL controls transactions (BEGIN, COMMIT, ROLLBACK, SAVEPOINT).

#### Intermediate
Q: [DEFINITION] What is an upsert and how is it written in PostgreSQL?
A: Insert a row, or update it if a row with the same key exists: `INSERT … ON CONFLICT (key) DO UPDATE SET col = EXCLUDED.col;` (`DO NOTHING` to skip instead).

Q: [HOW] How do you update a table using values from another table?
A: PostgreSQL: `UPDATE t SET … FROM other o WHERE o.id = t.id AND …;` Portable: a subquery in SET or WHERE. SQL Server uses `UPDATE … FROM … JOIN`; MySQL uses `UPDATE t JOIN o ON … SET …`.

Q: [DEFINITION] What does RETURNING do?
A: It returns the rows affected by INSERT, UPDATE or DELETE (for example generated IDs), saving an extra SELECT.

Q: [DEFINITION] What is a savepoint?
A: A named checkpoint inside a transaction; `ROLLBACK TO SAVEPOINT` undoes changes after it while keeping earlier work.

#### Scenario-based
Q: [SCENARIO] Someone ran `UPDATE employees SET salary = 0;` in production without a WHERE clause. How could it have been prevented, and how do you recover?
A: Prevention: run the SELECT first, use explicit transactions, restrict permissions, require code review for production SQL. Recovery: if the transaction isn't committed, ROLLBACK; otherwise restore from a backup or point-in-time recovery, or use audit/history tables.

Q: [SCENARIO] A nightly job inserts customers from a file; some already exist. How do you avoid duplicates?
A: Use an upsert keyed on a unique business key (email or customer code): `ON CONFLICT (email) DO UPDATE` (or `DO NOTHING`), with a UNIQUE constraint so the database enforces it.

Q: [DESIGN QUESTION] What permissions would you give a BI dashboard's database user?
A: A read-only role with SELECT on only the reporting tables or views it needs (ideally a reporting schema or read replica); no INSERT, UPDATE, DELETE or DDL rights.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is TRUNCATE DML?
A: No, it is DDL, even though it removes data.

Q: [TRAP QUESTION] What happens if you run BEGIN, an UPDATE, and then close the session without COMMIT?
A: The transaction is rolled back; the update is lost.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Write the SQL to add a nullable `phone` column (up to 15 characters) to `customers`.

**P2.** Which command removes all rows but keeps the table: DELETE, TRUNCATE or DROP? Which one can use WHERE?

**P3.** Insert a new customer, id 8, "Kiara Menon", kiara@mail.com, Kochi, signed up 1 May 2024.

#### Level 2 — Interview application
**P4.** Give every employee in Engineering (dept 1) a 5% raise and return their new salaries.

**P5.** Create a table `dept_payroll` from existing data, holding each department's name and total salary.

**P6.** Write an upsert that sets the price of product 2 to 3299, inserting the product if it does not exist.

#### Level 3 — Scenario / problem solving
**P7.** Delete all leads whose email appears more than once, but only the copies created *after* the first one. (Hint: compare each lead with an earlier lead that has the same email.)

**P8.** A colleague wants to empty `orders` with TRUNCATE before a reload. What will happen in PostgreSQL, and what are the options?
:::

::: answers
**P1.** `ALTER TABLE customers ADD COLUMN phone VARCHAR(15);`

**P2.** TRUNCATE removes all rows and keeps the table. Only DELETE accepts a WHERE clause.

**P3.**

```sql run
INSERT INTO customers (customer_id, customer_name, email, city, signup_date)
VALUES (8, 'Kiara Menon', 'kiara@mail.com', 'Kochi', '2024-05-01')
RETURNING *;
```

**P4.**

```sql run
UPDATE employees
SET salary = ROUND(salary * 1.05, 2)
WHERE dept_id = 1
RETURNING emp_name, salary;
```

**P5.** A CTAS with a join and GROUP BY (grouping is covered in Session 3.5):

```sql run
CREATE TABLE dept_payroll AS
SELECT d.dept_name, SUM(e.salary) AS total_salary
FROM departments d
JOIN employees e ON e.dept_id = d.dept_id
GROUP BY d.dept_name;

SELECT * FROM dept_payroll ORDER BY total_salary DESC;
```

**P6.**

```sql run
INSERT INTO products (product_id, product_name, category, price)
VALUES (2, 'Mechanical Keyboard', 'Electronics', 3299.00)
ON CONFLICT (product_id) DO UPDATE SET price = EXCLUDED.price
RETURNING *;
```

**P7.** A lead is a later duplicate if another lead with the same email has a smaller `lead_id`:

```sql run
DELETE FROM leads l
USING leads earlier
WHERE earlier.email = l.email
  AND earlier.lead_id < l.lead_id
RETURNING l.lead_id, l.full_name, l.email;
```

Leads 3 and 6 (later copies of amit@mail.com) and 5 (a later copy of sara@mail.com) are removed; the first lead for each email stays. Session 3.11 (Pattern 6) shows the window-function version.

**P8.** It fails, because `order_items` and other tables reference `orders` through foreign keys. Options: `TRUNCATE orders, order_items;` (truncate the related tables together), `TRUNCATE orders CASCADE` (truncates every referencing table, so be careful), or load into a separate staging table and swap.
:::
