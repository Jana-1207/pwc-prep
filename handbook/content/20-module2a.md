# Data Modeling Fundamentals {: .part #m2 data-label="PART II · MODULE 2" }

<p class="lead">Data modeling is deciding <em>what</em> data you store, <em>how</em> it is split into tables (or documents) and <em>how</em> the pieces connect. A good model makes queries simple and data trustworthy; a bad one causes duplicated, contradictory data for years. Interviewers love this module because it shows whether you can think, not just memorize.</p>

::: coverage
- Introduction to data modeling (conceptual, logical, physical) † → Session 2.1
- Entities, attributes, relationships, ER concepts † → Session 2.2
- Primary keys, foreign keys, constraints † → Session 2.3
- Relational model, schema, table design; one-to-one, one-to-many, many-to-many † → Session 2.4
- Normalization: functional dependency, update/insert/delete anomalies, 1NF, 2NF, 3NF, BCNF † → Session 2.5
- Denormalization; when to normalize and when to denormalize † → Session 2.6
- Data warehousing: data warehouse, fact and dimension tables, star and snowflake schemas, star vs snowflake, OLTP vs OLAP † → Session 2.7
- NoSQL modeling: why NoSQL, schema flexibility, document modeling, embedding vs referencing, access-pattern-driven design † → Session 2.8
- Module quiz concepts → interview questions in each session and Session 2.9
:::

| Topic | Priority | Typical question |
|---|---|---|
| Keys and constraints | [HIGH PRIORITY] | "Primary key vs foreign key vs unique key?" |
| Normalization (1NF–3NF, anomalies) | [HIGH PRIORITY] | "Normalize this table." "2NF vs 3NF?" |
| Relationships, many-to-many | [HIGH PRIORITY] | "How do you model students and courses?" |
| Star vs snowflake, facts vs dimensions | [MEDIUM PRIORITY] | "Design a star schema for sales." |
| Denormalization | [MEDIUM PRIORITY] | "When would you denormalize?" |
| NoSQL modeling, embedding vs referencing | [MEDIUM PRIORITY] | "Embed or reference order items in MongoDB?" |

::: pwc PwC angle
Consulting work often starts with messy client data: spreadsheets, legacy tables and multiple systems describing the same customer differently. Being able to spot duplication, propose clean keys and explain normalization in business terms ("we store the customer's address once, so a change is made in one place") is directly useful, and it is the kind of reasoning a "design a schema for…" question is testing.
:::

## Session 2.1 — What Is Data Modeling? {: #s2-1 }

### Simple meaning

**Data modeling is planning how data will be organised before you build the database**, in the same way an architect draws a blueprint before anyone pours concrete. It answers three questions:

1. *What* things do we need to store data about? (customers, orders, products)
2. *What* do we need to know about each one? (a customer's name, email, city)
3. *How* are they connected? (a customer places many orders)

### Why it matters

- **Fewer bugs in the data.** A good model makes it hard to store contradictions, like two different prices for the same product.
- **Simpler, faster queries.** When data is organised the way it will be used, queries are short and quick.
- **Cheaper changes.** Fixing a model after millions of rows exist is painful and risky.
- **A shared language.** Business people and engineers can agree on a picture before anyone writes code.

### The three levels of a data model

| Level | Question it answers | Who reads it | E-commerce example |
|---|---|---|---|
| **Conceptual** | What are the main things and how do they relate? | business stakeholders | "A Customer places Orders. An Order contains Products." |
| **Logical** | What exactly do we store about each thing? Which keys? | analysts, architects | Customer(customer_id, name, email, city); Order(order_id, customer_id, order_date, status) |
| **Physical** | How is it built in *this* database? | developers, DBAs | `customers` table in PostgreSQL, `email VARCHAR(80) UNIQUE`, index on `orders(customer_id)` |

A logical model is independent of any product. The physical model adds the product-specific details: exact data types, indexes, partitions and storage settings.

### The modeling process, step by step

1. **Understand the requirements.** What questions must the system answer? ("Which customers ordered in the last 30 days?")
2. **Find the entities**, the nouns that matter (Customer, Order, Product).
3. **List their attributes** (name, email, price).
4. **Define relationships and cardinality** (one customer, many orders).
5. **Choose keys** (primary and foreign keys).
6. **Normalize** to remove redundancy (Session 2.5).
7. **Design the physical tables:** types, constraints, indexes.
8. **Validate against access patterns:** can every important query be written simply and run fast?

### Different kinds of data model

| Model | Shape | Best for | Session |
|---|---|---|---|
| Relational | tables linked by keys | transactional systems (OLTP) | 2.2–2.6 |
| Dimensional | facts surrounded by dimensions (star schema) | analytics (OLAP), data warehouses | 2.7 |
| Document | JSON-like documents | flexible, nested data; read patterns known up front | 2.8 |
| Key-value / wide-column / graph | key → value; rows of sparse columns; nodes and edges | caching, huge write volumes, relationships | 2.8, 4.2 |

::: example Worked example: a small library system
**Requirement:** "Members borrow books. A book can have several authors. We must know who has which book and when it is due."

- *Entities:* Member, Book, Author, Loan.
- *Relationships:* a Member has many Loans; a Book has many Loans over time; Book ↔ Author is many-to-many.
- *Keys:* member_id, book_id, author_id; Loan(loan_id, member_id, book_id, loan_date, due_date, return_date).
- *Physical decisions:* index `loans(member_id)` for "my books" pages; `return_date` NULL means "not yet returned".
:::

::: explain
"Data modeling is designing how data will be structured before building the database: which entities we store, what attributes they have and how they relate. We usually go from a conceptual model for the business, to a logical model with entities, attributes and keys, to a physical model for a specific database with data types and indexes. A good model avoids duplicate and inconsistent data and makes the important queries simple. For example, for e-commerce I'd model customers, orders, products and an order_items table between orders and products."
:::

::: trap
- Jumping straight to `CREATE TABLE` without asking what questions the data must answer.
- Mixing up logical (product-independent) and physical (product-specific) models.
- Thinking modeling is only for relational databases. NoSQL needs modeling too, just driven by access patterns.
:::

::: questions
#### Basic
Q: [DEFINITION] What is data modeling?
A: Planning the structure of data, meaning entities, attributes, relationships and keys, before implementing it in a database.

Q: [COMPARISON] What are conceptual, logical and physical data models?
A: Conceptual: high-level entities and relationships for the business. Logical: detailed attributes, keys and relationships, independent of any product. Physical: the actual tables, types, constraints and indexes in a specific DBMS.

#### Intermediate
Q: [WHY] Why is data modeling important?
A: It prevents redundancy and inconsistency, makes queries simpler and faster, reduces the cost of later changes, and gives business and technical teams a shared picture.

Q: [HOW] What steps do you follow to model a new system?
A: Gather requirements and key questions, identify entities, attributes and relationships, choose keys, normalize, design the physical schema, then validate it against the main queries.

#### Scenario-based
Q: [DESIGN QUESTION] You are asked to model a hospital appointment system. What entities would you start with?
A: Patient, Doctor, Department, Appointment, and possibly Prescription and Bill. Doctor belongs to one Department; Patient has many Appointments; each Appointment links one Patient and one Doctor at a time slot.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does a NoSQL database mean you don't need a data model?
A: No. The model moves into the application and is driven by access patterns. Without design you get inconsistent documents and slow queries.
:::

## Session 2.2 — Entities, Attributes and Relationships (ER Modeling) {: #s2-2 }

### Entities

An **entity** is a real-world "thing" we store data about: *Customer, Product, Order, Employee, Department*. Each specific customer, such as Aarav Patel, is an **entity instance**, which becomes one **row** in the table.

- A **strong entity** can be identified on its own (a Customer has a customer_id).
- A **weak entity** cannot exist or be identified without its owner. An *order item* only makes sense inside an order: it is identified by (order_id, line number or product_id).

### Attributes

An **attribute** is a property of an entity: a customer's name, email and city.

| Attribute type | Meaning | Example | How it becomes tables |
|---|---|---|---|
| Simple | cannot be split usefully | `email` | one column |
| Composite | made of parts | `address` = street + city + pin code | several columns (`street`, `city`, `pin_code`) |
| Single-valued | one value per entity | `date_of_birth` | one column |
| Multi-valued | many values per entity | a customer's several phone numbers | a separate table `customer_phones` |
| Derived | can be calculated from others | `age` from `date_of_birth`; order total from items | usually *not* stored (or stored on purpose for speed, see Session 2.6) |
| Key | identifies the entity | `customer_id` | primary key |

### Relationships and cardinality

A **relationship** is how entities are connected: *Customer places Order*, *Employee works in Department*. **Cardinality** says *how many* on each side:

| Cardinality | Meaning | Example |
|---|---|---|
| One-to-one (1:1) | one A ↔ one B | each user has one profile |
| One-to-many (1:N) | one A ↔ many B | one customer places many orders |
| Many-to-many (M:N) | many A ↔ many B | students take many courses; each course has many students |

**Participation (optionality)** says whether the relationship is required:

- Every order *must* belong to a customer → **mandatory** (total participation). In SQL: `customer_id NOT NULL`.
- A customer *may* have zero orders → **optional** (partial participation).

### Reading an ER diagram

An **ER (Entity-Relationship) diagram** draws entities as boxes and relationships as lines. Two notations are common:

- **Chen notation** (textbooks): entities as rectangles, attributes as ovals, relationships as diamonds.
- **Crow's foot notation** (industry tools): entities as boxes listing their columns; the line ends show cardinality.

| Line-end symbol (crow's foot) | Meaning |
|---|---|
| <code>&#124;&#124;</code> (two bars) | exactly one |
| <code>o&#124;</code> (circle + bar) | zero or one |
| <code>&#124;&lt;</code> (bar + crow's foot) | one or many |
| <code>o&lt;</code> (circle + crow's foot) | zero or many |

In this handbook the diagrams simply write **1** and **N** at the line ends:

[[fig:er_ecommerce | The e-commerce part of this handbook's sample database as an ER diagram.]]

### Finding entities in a requirement

A practical trick: **nouns** are candidate entities or attributes; **verbs** are candidate relationships.

> "*Patients* **book** *appointments* with *doctors*. Each doctor **belongs to** one *department*. A patient **can have** many appointments, and each appointment **may produce** a *prescription*."

- Entities: Patient, Appointment, Doctor, Department, Prescription.
- Relationships: Patient 1:N Appointment; Doctor 1:N Appointment; Department 1:N Doctor; Appointment 1:0..1 Prescription.

::: tip Entity or attribute?
Make something its own entity when it has its own attributes or is shared. "City" can be a plain attribute of a customer, but if you need each city's state, region and delivery charges, make `cities` a table and reference it.
:::

::: explain
"An entity is a thing we store data about, like a customer or an order; each row is one instance. Attributes are its properties, like name and email. Relationships connect entities, and cardinality tells us how many: a customer places many orders, so that's one-to-many, while students and courses are many-to-many. In an ER diagram I'd draw the entities as boxes, list their keys and mark the cardinality on the lines, for example with crow's foot notation."
:::

::: trap
- Storing a multi-valued attribute (several phone numbers) as a comma-separated string. It belongs in its own table.
- Forgetting optionality: "every order has a customer" should become `NOT NULL` on the foreign key.
- Confusing an *entity* (Customer) with an *entity instance* (Aarav).
:::

::: questions
#### Basic
Q: [DEFINITION] What is an entity? Give an example.
A: A real-world object or concept we store data about, such as Customer or Product. Each instance (one customer) becomes a row.

Q: [DEFINITION] What is an attribute?
A: A property of an entity, such as a customer's name or email. It becomes a column.

Q: [DEFINITION] What is cardinality?
A: The number of instances of one entity that can relate to another: one-to-one, one-to-many or many-to-many.

#### Intermediate
Q: [COMPARISON] What is the difference between a strong and a weak entity?
A: A strong entity has its own identifier; a weak entity depends on an owner entity for its identity, for example an order line identified by order_id plus line number.

Q: [COMPARISON] What are composite, multi-valued and derived attributes?
A: Composite has parts (address = street, city, pin); multi-valued has several values (phone numbers); derived can be calculated (age from date of birth).

Q: [HOW] How do you represent a multi-valued attribute in tables?
A: Put it in a separate child table with a foreign key to the parent, for example `customer_phones(customer_id, phone)`.

#### Scenario-based
Q: [SCENARIO] From "Employees work in departments; each department has one manager who is also an employee", identify entities and relationships.
A: Entities: Employee, Department. Relationships: Department 1:N Employee (works in); Department 1:1 Employee (managed by), which is stored as `manager_emp_id` in departments, referencing employees.

#### Follow-up / Trap
Q: [TRAP QUESTION] Should you store a customer's age?
A: Usually no. Store the date of birth and calculate the age, because a stored age becomes wrong every year.
:::

## Session 2.3 — Keys and Constraints {: #s2-3 }

[HIGH PRIORITY] This is one of the most asked topics in any DBMS interview.

### Why keys exist

Keys do two jobs: they **identify each row uniquely**, and they **link tables together**. Without them, you could not reliably say "update *this* customer" or "find *this* customer's orders".

### Every kind of key, on one table

Take an `employees` table where each employee has `emp_id`, `email`, `pan_number` (a tax ID that is unique per person), `name` and `dept_id`.

| Key | Definition | Example |
|---|---|---|
| **Super key** | any set of columns that uniquely identifies a row | {emp_id}, {emp_id, name}, {email}, {email, dept_id} … |
| **Candidate key** | a *minimal* super key: remove any column and it stops being unique | {emp_id}, {email}, {pan_number} |
| **Primary key (PK)** | the candidate key we *choose* as the main identifier; unique and NOT NULL | emp_id |
| **Alternate key** | candidate keys that were not chosen as the PK | email, pan_number |
| **Unique key** | a column (or set) declared `UNIQUE`; no duplicates, but may allow NULL | email |
| **Composite key** | a key made of two or more columns | (order_id, product_id) in `order_items` |
| **Foreign key (FK)** | a column that refers to the primary (or unique) key of another table | `employees.dept_id` → `departments.dept_id` |
| **Surrogate key** | an artificial ID with no business meaning | auto-generated `emp_id` 1, 2, 3 |
| **Natural key** | a key with real-world meaning | PAN number, email |

### Primary key rules

- Must be **unique** and **NOT NULL**.
- **One primary key per table**, though it may be composite.
- Should be **stable** (never changes) and **minimal** (no unnecessary columns).

### Foreign keys and referential integrity

A **foreign key** says "this value must exist in that other table". The guarantee it provides is called **referential integrity**: there are no orphan rows, such as an order for a customer who does not exist.

<p class="tablecap">customers (parent)</p>

| customer_id | customer_name | email |
|---|---|---|
| 1 | Aarav Patel | aarav@mail.com |
| 2 | Isha Kulkarni | isha@mail.com |

<p class="tablecap">orders (child)</p>

| order_id | customer_id | order_date | total_amount |
|---|---|---|---|
| 101 | 1 | 2024-01-05 | 2843.00 |
| 102 | 2 | 2024-01-12 | 3499.00 |
| 103 | 1 | 2024-01-28 | 8999.00 |

`orders.customer_id` is a foreign key to `customers.customer_id`. Customer 1 has two orders, which is the one-to-many relationship in action. Watch PostgreSQL protect the data in the sample database. First, try to create an order for a customer who does not exist:

```sql run error
INSERT INTO orders (order_id, customer_id, order_date, status)
VALUES (200, 999, '2024-05-01', 'PENDING');
```

Now try to delete a customer who still has orders:

```sql run error
DELETE FROM customers WHERE customer_id = 1;
```

What happens to the children when a parent is deleted is controlled by the **referential action** on the foreign key:

| Action | When the parent row is deleted… | Typical use |
|---|---|---|
| `NO ACTION` / `RESTRICT` (default) | the delete is refused while children exist | orders, payments: never lose history silently |
| `CASCADE` | the children are deleted too | a post's comments; a cart's items |
| `SET NULL` | the child's FK becomes NULL | employee's manager leaves → `manager_id` NULL |
| `SET DEFAULT` | the child's FK gets its default value | rare |

### The other constraints

Constraints are rules the database enforces on every insert and update, no matter which application writes the data.

| Constraint | Rule | Example |
|---|---|---|
| `NOT NULL` | a value is required | `customer_name VARCHAR(60) NOT NULL` |
| `UNIQUE` | no duplicate values | `email VARCHAR(80) UNIQUE` |
| `PRIMARY KEY` | UNIQUE + NOT NULL, the row's identity | `customer_id INT PRIMARY KEY` |
| `FOREIGN KEY` | value must exist in the parent table | `customer_id INT REFERENCES customers(customer_id)` |
| `CHECK` | value must satisfy a condition | `price NUMERIC(10,2) CHECK (price >= 0)` |
| `DEFAULT` | value used when none is given | `status VARCHAR(12) DEFAULT 'PENDING'` |

Each violation produces a clear error. A duplicate email:

```sql run error
INSERT INTO customers (customer_id, customer_name, email, city, signup_date)
VALUES (8, 'Aarav P', 'aarav@mail.com', 'Mumbai', '2024-05-01');
```

A negative price, blocked by a `CHECK` constraint:

```sql run error
UPDATE products SET price = -10 WHERE product_id = 1;
```

A missing required value:

```sql run error
INSERT INTO products (product_id, product_name, category, price)
VALUES (9, NULL, 'Electronics', 499);
```

### Primary key vs unique key: the NULL difference

A `UNIQUE` column in PostgreSQL allows **many NULLs**, because NULL means "unknown" and two unknowns are not considered equal. A primary key allows **no** NULLs. Customer 7 already has a NULL email; adding another customer with a NULL email works:

```sql run
INSERT INTO customers (customer_id, customer_name, email, city, signup_date)
VALUES (8, 'Test User', NULL, 'Pune', '2024-05-01');

SELECT customer_id, customer_name, email
FROM customers
WHERE email IS NULL;
```

::: linebyline
| Line | What it does |
|---|---|
| `INSERT INTO customers (...) VALUES (8, 'Test User', NULL, ...)` | adds a customer whose email is unknown (NULL) |
| `SELECT customer_id, customer_name, email` | shows these three columns |
| `FROM customers` | from the customers table |
| `WHERE email IS NULL` | only rows with no email; note `IS NULL`, never `= NULL` |
:::

The example was rolled back after it ran, so the sample data is unchanged for the next query.

::: note Database differences
SQL Server allows only **one** NULL in a UNIQUE column. PostgreSQL 15+ can behave the same way with `UNIQUE NULLS NOT DISTINCT`. Mentioning this shows real depth.
:::

### Comparison tables interviewers expect

| | Primary key | Unique key |
|---|---|---|
| Purpose | the row's main identity | prevent duplicates in another column |
| NULLs | not allowed | allowed (PostgreSQL: many) |
| How many per table | one | many |
| Index | created automatically | created automatically |
| Referenced by FKs | yes (usual) | yes (allowed) |

| | Primary key | Foreign key |
|---|---|---|
| Purpose | identifies rows in *its own* table | links to rows in *another* table |
| Uniqueness | must be unique | can repeat (many orders per customer) |
| NULLs | not allowed | allowed unless declared NOT NULL |
| Count per table | one | any number |

### Surrogate vs natural keys

| | Surrogate key (`id` 1, 2, 3 or UUID) | Natural key (email, PAN) |
|---|---|---|
| Meaning | none, purely technical | has business meaning |
| Stability | never changes | can change (people change emails) |
| Size and speed | small integer, fast joins | often long strings |
| Risk | duplicates possible unless you also add UNIQUE on the natural key | business changes break keys |

**Common practice:** use a surrogate primary key (`INT GENERATED ALWAYS AS IDENTITY`, `BIGSERIAL`, or a UUID) **and** a `UNIQUE` constraint on the natural key.

::: explain
"A primary key uniquely identifies each row in a table. It must be unique and not null, and there is only one per table, although it can be made of several columns. A foreign key is a column in one table that points to the primary key of another, which enforces referential integrity: you cannot create an order for a customer who doesn't exist, and you can't delete a customer who still has orders unless you choose CASCADE or SET NULL. A unique key also prevents duplicates, but it can allow NULLs and a table can have many of them."
:::

::: trap
- "A primary key can be NULL if it's composite." No: no part of a primary key may be NULL.
- "A foreign key must be unique." No: many child rows can share the same FK value.
- "A table can have two primary keys." It has one PK; the other candidates become alternate or unique keys.
- "UNIQUE allows exactly one NULL." That depends on the database: PostgreSQL and MySQL allow many; SQL Server allows one.
- Forgetting that a FK must reference a PRIMARY KEY or UNIQUE column.
:::

::: questions
#### Basic
Q: [DEFINITION] What is a primary key?
A: A column or set of columns that uniquely identifies each row. It must be unique and not null, and each table has only one.

Q: [DEFINITION] What is a foreign key?
A: A column whose values must match the primary or unique key of another table. It links tables and enforces referential integrity.

Q: [COMPARISON] Primary key vs unique key?
A: Both prevent duplicates. A primary key cannot be NULL and there is only one per table; a unique key may allow NULLs and a table can have several.

Q: [DEFINITION] What is a composite key?
A: A key made of two or more columns, such as (order_id, product_id) in an order_items table.

#### Intermediate
Q: [COMPARISON] Super key vs candidate key vs primary key?
A: A super key is any set of columns that is unique; a candidate key is a minimal super key; the primary key is the candidate key chosen as the main identifier.

Q: [DEFINITION] What is referential integrity?
A: The guarantee that every foreign key value points to an existing parent row, so there are no orphan records.

Q: [HOW] What happens when you delete a parent row that has child rows?
A: By default the delete is rejected. With `ON DELETE CASCADE` the children are deleted too; with `SET NULL` their foreign key becomes NULL.

Q: [COMPARISON] Surrogate key vs natural key?
A: A surrogate key is an artificial, meaningless ID (auto-increment or UUID); a natural key has business meaning (email, PAN). Surrogates are stable and compact, so they are commonly used as the PK, with a UNIQUE constraint on the natural key.

Q: [DEFINITION] What is a CHECK constraint?
A: A rule that every row must satisfy, such as `CHECK (price >= 0)` or `CHECK (status IN ('PENDING','SHIPPED'))`.

#### Scenario-based
Q: [SCENARIO] An employee table uses email as its primary key. What problems could this cause?
A: Emails change, so the PK and every foreign key pointing to it would have to change. Emails are also long strings, which makes joins and indexes larger. Better: a surrogate `emp_id` PK plus `UNIQUE (email)`.

Q: [SCENARIO] Users are getting orders linked to deleted customers. What is missing?
A: A foreign key from `orders.customer_id` to `customers.customer_id` (and probably `NOT NULL`). Then the database itself blocks orphan rows.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can a foreign key be NULL?
A: Yes, unless it is declared NOT NULL. A NULL foreign key means "no related row", for example an employee with no manager.

Q: [TRAP QUESTION] Can a foreign key reference a column that is not the primary key?
A: Yes, as long as that column has a UNIQUE (or PRIMARY KEY) constraint.

Q: [TRAP QUESTION] Can a table have no primary key?
A: Technically yes, but it is bad practice: you cannot reliably identify, update or de-duplicate rows, and many tools require a PK.
:::

## Session 2.4 — The Relational Model, Schema and Table Design {: #s2-4 }

### The relational model in one picture

The relational model, proposed by E. F. Codd in 1970, stores data in **relations**, which we call tables. Its vocabulary still appears in interviews:

| Formal term | Everyday term | Meaning |
|---|---|---|
| Relation | table | a set of rows with the same columns |
| Tuple | row | one record |
| Attribute | column | one property |
| Domain | data type + allowed values | e.g. `status` must be one of five words |
| Degree | number of columns | `customers` has degree 5 |
| Cardinality (of a table) | number of rows | `customers` has 7 rows |

Rows in a relation have **no guaranteed order**, which is why SQL needs `ORDER BY` when order matters.

### Two meanings of "schema"

1. **The design** of the database: which tables, columns, types and constraints exist ("the schema of the orders table").
2. **In PostgreSQL**, a *schema* is also a **namespace (a folder) inside a database** that holds tables. The default one is `public`, so `public.orders` is the full name of `orders`. Teams use schemas such as `sales`, `hr` and `staging` to organise objects and permissions.

### Turning relationships into tables

[[fig:relationships | How each kind of relationship becomes tables and keys.]]

| Relationship | Rule | Example |
|---|---|---|
| **1 : N** | put the foreign key on the **"many"** side | `orders.customer_id` → `customers` |
| **1 : 1** | foreign key on either side **with a UNIQUE constraint**, or share the same primary key | `user_profiles.user_id` is both PK and FK |
| **M : N** | create a **junction (bridge) table** holding both foreign keys, usually as a composite PK | `enrollments(student_id, course_id)` |
| Multi-valued attribute | child table | `customer_phones(customer_id, phone)` |
| Weak entity | child table whose key includes the owner's key | `order_items(order_id, product_id, …)` |

### Building a many-to-many design for real

Students and courses are the classic many-to-many example. The block below creates the three tables with every kind of constraint, then loads a little data. It is kept for the rest of this chapter (`keep`):

```sql run keep quiet
CREATE TABLE students (
    student_id  INT PRIMARY KEY,
    full_name   VARCHAR(60) NOT NULL,
    email       VARCHAR(80) UNIQUE,
    city        VARCHAR(40) NOT NULL DEFAULT 'Unknown'
);

CREATE TABLE courses (
    course_id   VARCHAR(10) PRIMARY KEY,
    title       VARCHAR(80) NOT NULL,
    credits     INT NOT NULL CHECK (credits BETWEEN 1 AND 6)
);

CREATE TABLE enrollments (
    student_id  INT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id   VARCHAR(10) NOT NULL REFERENCES courses(course_id),
    enrolled_on DATE NOT NULL,
    grade       CHAR(1) CHECK (grade IN ('A','B','C','D','F')),
    PRIMARY KEY (student_id, course_id)
);

INSERT INTO students VALUES
    (1, 'Asha Rao',    'asha@uni.edu',   'Pune'),
    (2, 'Vikram Shah', 'vikram@uni.edu', 'Delhi'),
    (3, 'Neha Iyer',   NULL,             'Chennai');

INSERT INTO courses VALUES
    ('DB101', 'Database Systems',   4),
    ('PY101', 'Python Programming', 3),
    ('DS201', 'Data Structures',    4);

INSERT INTO enrollments VALUES
    (1, 'DB101', '2024-07-01', 'A'),
    (1, 'PY101', '2024-07-01', 'B'),
    (2, 'DB101', '2024-07-02', NULL),
    (3, 'DS201', '2024-07-03', 'A'),
    (3, 'DB101', '2024-07-03', 'B');
```

::: linebyline
| Part of the code | What it means |
|---|---|
| `student_id INT PRIMARY KEY` | every student has a unique, non-null ID |
| `email VARCHAR(80) UNIQUE` | no two students share an email (NULL allowed) |
| `DEFAULT 'Unknown'` | used if no city is supplied |
| `CHECK (credits BETWEEN 1 AND 6)` | rejects impossible credit values |
| `REFERENCES students(student_id) ON DELETE CASCADE` | each enrollment must point to a real student; deleting a student removes their enrollments |
| `PRIMARY KEY (student_id, course_id)` | a composite key: the same student cannot enroll in the same course twice |
:::

Now the junction table lets us answer "who takes what" with two joins:

```sql run
SELECT s.full_name, c.title, e.grade
FROM enrollments e
JOIN students s ON s.student_id = e.student_id
JOIN courses  c ON c.course_id  = e.course_id
ORDER BY s.full_name, c.title;
```

And `ON DELETE CASCADE` in action: deleting Asha removes her two enrollments automatically.

```sql run
DELETE FROM students WHERE student_id = 1;

SELECT student_id, course_id, grade
FROM enrollments
ORDER BY student_id, course_id;
```

### Table design best practices

| Practice | Why |
|---|---|
| Every table has a primary key | rows can be identified, updated and joined reliably |
| Use the right data types: `NUMERIC(10,2)` for money, `DATE`/`TIMESTAMP` for time, `BOOLEAN` for flags | `FLOAT` rounds money (0.1 + 0.2 ≠ 0.3); dates stored as text cannot be compared or validated |
| One fact per column, one value per cell | no `"Mouse, Keyboard"` lists; they break searching and violate 1NF |
| Declare foreign keys and `NOT NULL` where required | the database enforces correctness for every application |
| Consistent naming (`snake_case`, clear names like `customer_id`) | readable queries, fewer mistakes |
| Don't store what you can calculate cheaply (age, totals) unless you have a reason | avoids stale values (see Session 2.6 for when to break this rule) |
| Add audit columns such as `created_at`, `updated_at` | debugging, incremental loads, history |

::: explain
"To model a many-to-many relationship, like students and courses, I create a junction table, say `enrollments`, with two foreign keys: one to students and one to courses. The pair is the composite primary key, so a student can't enroll twice in the same course, and the table can also hold attributes of the relationship itself, like the enrollment date and grade. One-to-many is simpler: the foreign key goes on the many side, so `orders` gets a `customer_id`."
:::

::: trap
- Putting the foreign key on the wrong side of a 1:N relationship (for example, an `order_id` column in `customers`).
- Modeling M:N with comma-separated IDs in one column instead of a junction table.
- Using `FLOAT` for currency.
- Storing dates as text (`'05/03/2024'`): is that 5 March or 3 May?
:::

::: questions
#### Basic
Q: [DEFINITION] What is a relation in the relational model?
A: A table: a set of tuples (rows) that share the same attributes (columns).

Q: [HOW] How do you implement a one-to-many relationship?
A: Put a foreign key on the "many" side that references the primary key of the "one" side, e.g. `orders.customer_id` → `customers.customer_id`.

Q: [HOW] How do you implement a many-to-many relationship?
A: With a junction table holding foreign keys to both tables, usually forming a composite primary key, e.g. `enrollments(student_id, course_id)`.

#### Intermediate
Q: [HOW] How do you implement a one-to-one relationship?
A: Put a foreign key with a UNIQUE constraint in one table, or make the child's primary key also a foreign key to the parent (`user_profiles.user_id`).

Q: [DEFINITION] What is a schema in PostgreSQL?
A: A namespace inside a database that groups tables, views and functions; the default is `public`. "Schema" also means the overall design of the tables.

Q: [WHY] Why should money not be stored as FLOAT?
A: Floating-point numbers are binary approximations and produce rounding errors; `NUMERIC`/`DECIMAL` stores exact values.

#### Scenario-based
Q: [DESIGN QUESTION] Design tables for a library where books can have multiple authors and members borrow books.
A: `books(book_id PK, title, isbn UNIQUE)`, `authors(author_id PK, name)`, `book_authors(book_id FK, author_id FK, PK both)`, `members(member_id PK, name, email UNIQUE)`, `loans(loan_id PK, member_id FK, book_id FK, loan_date, due_date, return_date NULL)`.

Q: [SCENARIO] A colleague stores `course_ids` as "DB101,PY101" in the students table. What's wrong and how do you fix it?
A: It breaks 1NF, cannot be indexed or joined properly, and allows invalid IDs. Replace it with an `enrollments` junction table with foreign keys to both sides.

#### Follow-up / Trap
Q: [TRAP QUESTION] Are rows in a table stored in insertion order?
A: You must not rely on it. A relation is an unordered set; use `ORDER BY` whenever order matters.

Q: [TRAP QUESTION] Can a junction table have extra columns?
A: Yes. Attributes of the relationship itself, such as enrollment date and grade, belong there.
:::

## Session 2.5 — Normalization {: #s2-5 }

[HIGH PRIORITY] Expect at least one normalization question in almost every DBMS interview.

### Simple meaning

**Normalization means splitting data into sensible tables so the same fact is not stored over and over.** Each fact lives in exactly one place, and tables are linked with keys.

### Why: the three anomalies

Look at this "everything in one sheet" table. It works, until you try to change it:

<p class="tablecap">order_details_flat (unnormalized)</p>

| order_id | order_date | customer_name | customer_phone | customer_city | product_name | unit_price | qty |
|---|---|---|---|---|---|---|---|
| 101 | 2024-01-05 | Aarav Patel | 98200 11111 | Mumbai | Wireless Mouse | 799 | 2 |
| 101 | 2024-01-05 | Aarav Patel | 98200 11111 | Mumbai | Notebook Pack | 249 | 5 |
| 103 | 2024-01-28 | Aarav Patel | 98200 11111 | Mumbai | Office Chair | 8999 | 1 |
| 102 | 2024-01-12 | Isha Kulkarni | 98900 22222 | Pune | Mechanical Keyboard | 3499 | 1 |

| Anomaly | What goes wrong here |
|---|---|
| **Update anomaly** | Aarav changes his phone number. It is stored in three rows; miss one and the data contradicts itself. |
| **Insert anomaly** | We cannot record a new product, "Monitor Arm", until somebody orders it, because there is no order_id to put in the row. |
| **Delete anomaly** | If order 102 is deleted, we also lose the only record that Isha exists *and* that a keyboard costs 3499. |

All three come from the same root cause: **one table is storing facts about several different things** (orders, customers, products).

### Functional dependency: the idea behind normalization

`X → Y` (read "X determines Y") means: **if you know X, you know exactly one Y.**

- `customer_id → customer_name, customer_phone, customer_city`
- `product_id → product_name, unit_price`
- `order_id → order_date, customer_id`
- `(order_id, product_id) → qty`

Three kinds of dependency matter:

| Kind | Meaning | Example |
|---|---|---|
| **Full** | a column depends on the *whole* key | `qty` depends on (order_id, product_id) together |
| **Partial** | a column depends on only *part* of a composite key | `product_name` depends only on `product_id`, not on `order_id` |
| **Transitive** | a non-key column depends on another non-key column | `order_id → customer_id → customer_city` |

Normalization removes partial and transitive dependencies step by step.

[[fig:normalization_stairs | The normal forms build on each other; each removes one kind of redundancy.]]

### First Normal Form (1NF)

**Rule:** every cell holds **one atomic value**, there are **no repeating groups**, and each row can be identified by a key.

Before (not 1NF), one cell holds a list:

| order_id | customer_name | products |
|---|---|---|
| 101 | Aarav Patel | Wireless Mouse, Notebook Pack |

After (1NF), one product per row. The key becomes (order_id, product_name), or better (order_id, product_id):

| order_id | customer_name | product_name |
|---|---|---|
| 101 | Aarav Patel | Wireless Mouse |
| 101 | Aarav Patel | Notebook Pack |

### Second Normal Form (2NF)

**Rule:** 1NF **and** no partial dependency. Every non-key column must depend on the **whole** primary key. (This only matters when the key is composite.)

In `order_lines(order_id, product_id, qty, product_name, unit_price)`, the key is (order_id, product_id), but `product_name` and `unit_price` depend only on `product_id`. Move them out:

| order_lines (order_id, product_id, qty) | products (product_id, product_name, unit_price) |
|---|---|
| (101, 1, 2), (101, 6, 5), (103, 4, 1) | (1, Wireless Mouse, 799), (6, Notebook Pack, 249), (4, Office Chair, 8999) |

### Third Normal Form (3NF)

**Rule:** 2NF **and** no transitive dependency. Non-key columns depend **only on the key**, not on other non-key columns.

In `orders(order_id, order_date, customer_id, customer_city)`, `customer_city` depends on `customer_id`, which is not the key. Move customer details to `customers`:

| orders (order_id, order_date, customer_id) | customers (customer_id, customer_name, phone, city) |
|---|---|
| (101, 2024-01-05, 1), (103, 2024-01-28, 1) | (1, Aarav Patel, 98200 11111, Mumbai) |

A memory line many interviewers like: *every non-key attribute must depend on "the key, the whole key, and nothing but the key".*

### Boyce–Codd Normal Form (BCNF)

**Rule:** for every functional dependency `X → Y`, **X must be a super key**. BCNF is a stricter 3NF; the difference shows up only when a table has overlapping candidate keys.

**Example:** `tutoring(student, subject, teacher)`. Each teacher teaches exactly one subject (`teacher → subject`), and each student has one teacher per subject. The candidate keys are (student, subject) and (student, teacher). The table is in 3NF, but `teacher → subject` has a determinant (`teacher`) that is not a super key, so it is **not** in BCNF. The fix is to split it into `teacher_subject(teacher, subject)` and `student_teacher(student, teacher)`.

::: extension 4NF and 5NF
**4NF** removes multi-valued dependencies (independent lists stored in one table, like an employee's skills and languages in the same table). **5NF** deals with join dependencies. They are rarely asked at entry level; knowing their names and the one-line idea is enough.
:::

### The summary table to memorize

| Normal form | Rule | Removes | Quick test |
|---|---|---|---|
| 1NF | atomic values, no repeating groups, has a key | multi-valued cells | "Any cell with a list?" |
| 2NF | 1NF + no partial dependency | facts about *part* of a composite key | "Does a column depend on only part of the key?" |
| 3NF | 2NF + no transitive dependency | facts about non-key columns | "Does a column depend on another non-key column?" |
| BCNF | every determinant is a super key | remaining anomalies with overlapping keys | "Is there an X → Y where X isn't a key?" |

### The result: the handbook's sample database is the normalized version

Normalizing `order_details_flat` gives exactly the four tables this handbook uses everywhere: `customers`, `orders`, `products` and `order_items`. Nothing is lost: a join rebuilds the flat view whenever we need it. This is called a **lossless decomposition**.

```sql run
SELECT o.order_id, o.order_date, c.customer_name, c.city,
       p.product_name, i.unit_price, i.quantity
FROM orders o
JOIN customers   c ON c.customer_id = o.customer_id
JOIN order_items i ON i.order_id    = o.order_id
JOIN products    p ON p.product_id  = i.product_id
WHERE o.order_id IN (101, 102, 103)
ORDER BY o.order_id, p.product_name;
```

::: linebyline
| Line | What it does |
|---|---|
| `FROM orders o` | start from orders; `o` is a short alias |
| `JOIN customers c ON c.customer_id = o.customer_id` | attach each order's customer |
| `JOIN order_items i ON i.order_id = o.order_id` | attach the order's lines (one row per product) |
| `JOIN products p ON p.product_id = i.product_id` | attach product names |
| `WHERE o.order_id IN (101, 102, 103)` | only three orders, to keep the output short |
| `ORDER BY ...` | predictable order for reading |
:::

Aarav's phone or city now lives in **one** row of `customers`; changing it fixes every order at once.

### Advantages and disadvantages

| Advantages | Disadvantages |
|---|---|
| No update, insert or delete anomalies | More tables, so queries need joins |
| Less storage wasted on duplicates | Very heavy reporting queries can get slower |
| Data stays consistent | Over-normalizing can make the design hard to use |
| Easier to change one fact | Requires understanding of the data's dependencies |

::: explain
"Normalization is a design technique that reduces duplicate data and prevents update, insert and delete anomalies. We split a table so that each fact is stored once and connect the pieces with keys. In 1NF every cell has one value; in 2NF every non-key column depends on the whole key; in 3NF non-key columns depend only on the key, not on each other. For example, instead of repeating a customer's phone and city on every order, I keep a customers table and store just the customer_id in orders. For OLTP systems I normally aim for 3NF."
:::

::: trap
- Saying 2NF applies to every table. Partial dependency is only possible with a **composite** key; a table with a single-column key in 1NF is automatically in 2NF.
- Confusing 2NF (partial dependency on part of the key) with 3NF (dependency between non-key columns).
- Claiming normalization always makes queries faster. Writes and consistency improve; complex reads may need more joins.
- Thinking "more normalization is always better". Warehouses deliberately denormalize.
:::

::: questions
#### Basic
Q: [DEFINITION] What is normalization?
A: Organising data into related tables to remove redundancy and avoid insert, update and delete anomalies, linking the tables with keys.

Q: [DEFINITION] What is 1NF?
A: Every column holds atomic (single) values, there are no repeating groups, and each row is uniquely identifiable.

Q: [DEFINITION] What is a functional dependency?
A: X → Y means a value of X determines exactly one value of Y, e.g. customer_id → customer_name.

Q: [DEFINITION] What are update, insert and delete anomalies?
A: Update: the same fact stored in many rows becomes inconsistent when only some are changed. Insert: you cannot add a fact without unrelated data. Delete: removing a row unintentionally removes another fact.

#### Intermediate
Q: [COMPARISON] What is the difference between 2NF and 3NF?
A: 2NF removes partial dependencies (a column depending on part of a composite key). 3NF removes transitive dependencies (a non-key column depending on another non-key column).

Q: [COMPARISON] What is the difference between 3NF and BCNF?
A: BCNF requires every determinant to be a super key. 3NF allows an exception when the dependent column is part of a candidate key, so a table can be in 3NF but not in BCNF when it has overlapping candidate keys.

Q: [DEFINITION] What is a transitive dependency? Give an example.
A: A → B and B → C, so A → C indirectly through a non-key column. Example: emp_id → dept_id → dept_name in an employees table.

Q: [DEFINITION] What is a lossless decomposition?
A: Splitting a table into smaller tables such that joining them back gives exactly the original data, with no lost or extra rows.

#### Scenario-based
Q: [SCENARIO] You have a table `orders(order_id, customer_name, customer_email, product, price, qty)`. How would you redesign it?
A: Split it into `customers(customer_id, name, email UNIQUE)`, `products(product_id, name, price)`, `orders(order_id, customer_id FK, order_date)` and `order_items(order_id FK, product_id FK, qty, unit_price, PK(order_id, product_id))`.

Q: [SCENARIO] `employees(emp_id, emp_name, dept_id, dept_name, dept_location)`: which normal form is violated?
A: 3NF, because dept_name and dept_location depend on dept_id (a non-key column). Move them into `departments(dept_id, dept_name, dept_location)`.

Q: [SCENARIO] In `enrollments(student_id, course_id, course_title, grade)`, what's wrong?
A: `course_title` depends only on course_id, which is part of the composite key, so it is a partial dependency and violates 2NF. Move it to `courses`.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can normalization ever hurt performance?
A: Yes. Read-heavy reports may need many joins. That is why analytical systems denormalize, and OLTP systems sometimes keep a few derived columns or materialized views.

Q: [TRAP QUESTION] Is a table with a single-column primary key always in 2NF?
A: If it is already in 1NF, yes. Partial dependency needs a composite key.

Q: [TRAP QUESTION] Up to which normal form do you normalize in practice?
A: Usually 3NF (sometimes BCNF) for transactional systems; beyond that the benefit is rarely worth the complexity.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** In one sentence each, define 1NF, 2NF and 3NF.

**P2.** Name the anomaly: "We cannot add a new course to the database until a student enrolls in it."

**P3.** Write two functional dependencies that hold in the sample `employees` table.

#### Level 2 — Interview application
**P4.** Is this table in 1NF? `students(student_id, name, phone_numbers)` where `phone_numbers` = "98200 11111, 98900 22222". Fix it.

**P5.** Explain to an interviewer why `order_items(order_id, product_id, qty, product_name)` is not in 2NF.

**P6.** Give an example of a transitive dependency from a hospital database.

#### Level 3 — Scenario / problem solving
**P7.** Normalize this table to 3NF and list the final tables with their keys: `invoice(invoice_no, invoice_date, customer_id, customer_name, customer_gstin, item_code, item_desc, item_rate, qty)`.

**P8.** A table `exam_results(student_id, subject, marks, teacher_name, teacher_phone)` is causing problems when teachers change phone numbers. Explain the anomaly and redesign it.
:::

::: answers
**P1.** 1NF: every cell holds a single atomic value and rows are uniquely identifiable. 2NF: in 1NF, and every non-key column depends on the whole primary key (no partial dependency). 3NF: in 2NF, and no non-key column depends on another non-key column (no transitive dependency).

**P2.** Insert anomaly.

**P3.** `emp_id → emp_name, email, dept_id, salary, hire_date, city` (emp_id is the primary key, so it determines every column), and `email → emp_id` (email is unique, so knowing it identifies the employee).

**P4.** No, the phone column holds a list. Create `student_phones(student_id FK, phone, PRIMARY KEY (student_id, phone))` and remove the list column from `students`.

**P5.** "The key is the pair (order_id, product_id), but product_name depends only on product_id, which is part of the key. That's a partial dependency, so it violates 2NF. If a product is renamed we'd have to update every order line. Product name belongs in the products table."

**P6.** `appointments(appointment_id, doctor_id, doctor_department)`: appointment_id → doctor_id → doctor_department. The department depends on the doctor, not on the appointment.

**P7.** Dependencies: invoice_no → invoice_date, customer_id; customer_id → customer_name, customer_gstin; item_code → item_desc, item_rate; (invoice_no, item_code) → qty. Final tables: `customers(customer_id PK, customer_name, customer_gstin UNIQUE)`; `items(item_code PK, item_desc, item_rate)`; `invoices(invoice_no PK, invoice_date, customer_id FK)`; `invoice_lines(invoice_no FK, item_code FK, qty, rate_charged, PK(invoice_no, item_code))`. Storing `rate_charged` on the line is deliberate: the price on an old invoice must not change when today's rate changes.

**P8.** Teacher details are repeated on every result row, so a phone change must be applied to many rows: an update anomaly. If a teacher's only result row is deleted, their phone is lost: a delete anomaly. Redesign: `teachers(teacher_id PK, teacher_name, teacher_phone)`, `subjects(subject_id PK, subject_name, teacher_id FK)` (if each subject has one teacher), `exam_results(student_id FK, subject_id FK, marks, PK(student_id, subject_id))`.
:::
