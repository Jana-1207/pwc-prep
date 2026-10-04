# Introduction to Modern Data Systems {: .part #m1 data-label="PART I · MODULE 1" }

<p class="lead">This module gives you the big picture: what a "data system" is, how a modern application stores and moves data, and why companies end up using several kinds of databases at once. The rest of the handbook zooms into each piece.</p>

::: coverage
- **Modern Data Systems & Integration — Part 1** †: what a data system is, how modern applications store data, applications and databases, backend systems → Session 1.1
- **Modern Data Systems & Integration — Part 2** †: how data moves between systems, data integration, APIs, data processing → Session 1.2
- **Modern Data Systems & Integration — Part 3** †: batch vs real-time, transactional vs analytical systems (OLTP vs OLAP), operational data, why many data technologies → Session 1.3
- Module quiz concepts → interview questions in every session and Session 1.4
- *Recommended prerequisite (not course content):* data, database and DBMS basics → Session 1.0
:::

| Interview priority | Why |
|---|---|
| [MEDIUM PRIORITY] overall | Rarely asked as "theory", but the vocabulary (OLTP, OLAP, batch, streaming, integration) appears in many answers. |
| [HIGH PRIORITY] OLTP vs OLAP, batch vs streaming | Classic comparison questions. |
| [HIGH PRIORITY] "Explain how your app works end to end" | Almost every project discussion turns into this. |

::: pattern How this module is tested
- [DEFINITION] "What is a data system / data integration?"
- [COMPARISON] "OLTP vs OLAP", "batch vs real-time"
- [HOW] "Walk me through what happens when a user places an order."
- [DESIGN QUESTION] "Which databases would you use for a food-delivery app, and why?"
:::

## Session 1.0 — Recommended Prerequisite: Data and Database Basics {: #s1-0 }

::: prereq Why this session exists
The course assumes you already know what a database is. Interviewers often start right here ("What is a DBMS?"), so a ten-minute refresher pays off. This session is an [INTERVIEW EXTENSION], not a course video.
:::

### Data vs information

**Data** is raw facts: `42`, `Pune`, `2024-03-05`. **Information** is data with meaning: "Order 42 was delivered to Pune on 5 March 2024." Databases store data; reports and applications turn it into information.

**Metadata** is "data about data": the column name `order_date`, its type `DATE`, who created the table, when it was last updated. You will meet metadata again in Module 7, where it becomes very important for AI.

### Why not just use files or Excel?

Imagine a college keeps student records in Excel files, one file per department. It works for a while, then problems appear:

| Problem with files | What goes wrong | How a database solves it |
|---|---|---|
| Duplication | The same student's phone number is typed in three files | Store each fact once and link it with keys |
| Inconsistency | One file is updated, the others are not | One source of truth; constraints keep it valid |
| Concurrent access | Two people edit the same file and overwrite each other | Locking and transactions let many users work safely |
| Security | Anyone with the file sees everything | Users, roles and permissions per table or row |
| Crash recovery | The laptop dies mid-save and the file is corrupted | Logs and transactions recover to a consistent state |
| Searching | Finding "all students from Pune with CGPA > 8" is slow and manual | A query language (SQL) and indexes |

### Database, DBMS and RDBMS

- A **database** is an organised collection of related data, for example everything about a college's students, courses and marks.
- A **DBMS (Database Management System)** is the software that stores, retrieves and protects that data: it handles queries, users, security, backups and crashes. Examples: PostgreSQL, MySQL, Oracle, SQL Server, MongoDB.
- An **RDBMS (Relational DBMS)** stores data in **tables** (relations) made of **rows** and **columns**, and links tables using **keys**. PostgreSQL, MySQL, Oracle and SQL Server are relational. MongoDB is a DBMS but *not* relational: it stores documents.

### The vocabulary of a table

<p class="tablecap">students</p>

| student_id | name | city | cgpa |
|---|---|---|---|
| 1 | Asha Rao | Pune | 8.6 |
| 2 | Vikram Shah | Delhi | 7.9 |

| Term | Meaning in this table | Other names |
|---|---|---|
| Table | `students` | relation |
| Row | one student, e.g. `1, Asha Rao, Pune, 8.6` | record, tuple |
| Column | `city` | field, attribute |
| Schema | the table's design: column names, types and rules | structure |
| Primary key | `student_id`: uniquely identifies each row | — |

**SQL (Structured Query Language)** is the standard language for working with relational databases: `SELECT` to read, `INSERT`, `UPDATE` and `DELETE` to change data, `CREATE TABLE` to define structure. Module 3 covers it in depth.

::: explain
"A DBMS is the software that manages a database. Instead of keeping data in loose files, it lets many users store and query data safely: it gives us a query language, enforces rules like unique IDs, controls who can see what, and recovers after a crash. A relational DBMS such as PostgreSQL stores data in tables and connects them with keys. For example, in a college system we keep students and courses in separate tables and link them through enrollments."
:::

::: trap
- Saying "SQL is a database." SQL is a *language*; PostgreSQL and MySQL are databases (DBMS software).
- Saying "MongoDB is an RDBMS." It is a DBMS, but document-oriented, not relational.
- Mixing up a *database* (the data) with a *DBMS* (the software that manages it).
:::

::: questions
#### Basic
Q: [DEFINITION] What is a DBMS?
A: Software that stores, retrieves and manages data in a database, handling queries, security, concurrency and recovery. Examples: PostgreSQL, MySQL, Oracle.

Q: [COMPARISON] What is the difference between a DBMS and an RDBMS?
A: An RDBMS is a type of DBMS that stores data in related tables and uses keys and SQL. Every RDBMS is a DBMS, but not every DBMS is relational (MongoDB and Redis are not).

Q: [DEFINITION] What are a row, a column and a schema?
A: A row is one record (one student). A column is one attribute (city). The schema is the design of the table: its columns, data types and rules.

#### Intermediate
Q: [WHY] What are the advantages of a DBMS over a file system?
A: Less duplication, consistent data, safe concurrent access, security and permissions, backup and crash recovery, and fast searching with a query language and indexes.

Q: [COMPARISON] Data vs information vs metadata?
A: Data is raw facts, information is data with context and meaning, and metadata describes the data itself (column names, types, owner, last-updated time).

#### Scenario-based
Q: [SCENARIO] A small shop tracks orders in Excel and keeps losing changes when two staff edit at once. What would you suggest?
A: Move the data into a relational database (even a small managed PostgreSQL). It gives concurrent access with transactions, one source of truth, backups, and the ability to build a simple app or report on top of it.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is Excel a database?
A: Not really. It stores data in a grid, but it has no real concurrency control, transactions, enforced relationships or fine-grained security. It is a spreadsheet tool, fine for analysis, weak as a system of record.
:::

## Session 1.1 — Modern Data Systems & Integration (Part 1): What a Data System Is {: #s1-1 }

### What is a data system?

**Simple meaning:** a data system is *everything* an organisation uses to collect, store, process, move and serve data. It is not one database. It is the whole chain from the moment data is created (a customer taps "Pay") to the moment someone uses it (a manager reads a sales dashboard, or a model flags fraud).

**Why we need the idea:** in a real company, data is created in many places and used in many others. Thinking in terms of a *system* helps you see where data comes from, where it goes, what can break and who is responsible.

[[fig:data_system_components | The building blocks of a data system. Every real system has some version of each stage.]]

| Building block | Plain-English job | Real examples |
|---|---|---|
| Sources | Where data is born | mobile app, website, payment gateway, IoT sensor, Excel upload, Salesforce |
| Ingestion | Bringing data in | REST APIs, nightly file transfers, message queues, change data capture (CDC) |
| Storage | Keeping data safely | PostgreSQL, MongoDB, object storage (S3), data warehouse, data lake |
| Processing | Cleaning, combining, calculating | SQL jobs, Spark jobs, stream processors |
| Serving | Making data usable | APIs, dashboards, reports, ML feature stores |
| Governance | Rules around all of it | access control, data quality checks, privacy, metadata catalogue, monitoring |

::: analogy A city's water system
Water is collected from rivers (**sources**), pumped through pipes (**ingestion and integration**), stored in reservoirs (**storage**), treated and filtered (**processing**), and delivered to taps (**serving**). Inspectors test quality all along the way (**governance**). If any stage fails, people at the tap notice. A data system works the same way.
:::

### How modern applications store data

Almost every app you have used (food delivery, banking, e-commerce, job portals) has the same basic shape:

[[fig:app_architecture | The typical layers of a modern application, using a food-delivery order as the example.]]

| Layer | What it does | Example technologies |
|---|---|---|
| **User** | Interacts with the app | phone, laptop |
| **Frontend** | The screens. Collects input, shows results. Holds no permanent data of its own. | React, Angular, Android, iOS |
| **Backend / API** | The brain. Validates input, applies business rules, talks to the database and to other services. Exposes REST endpoints such as `POST /orders`. | Spring Boot, Node.js, Django, .NET |
| **Database** | The memory. Stores data permanently and safely. | PostgreSQL, MySQL, MongoDB |
| **Other services** | Specialist systems the backend calls | payment gateway, SMS/email, maps, login provider |
| **Analytics** | A copy of the data, organised for reporting and analysis | data warehouse + dashboards (Power BI, Tableau) |

**Why the frontend never talks to the database directly:** security (you would have to put database passwords in the app), control (business rules must run on the server, where users cannot tamper with them), and flexibility (the database can change without updating every phone).

### Applications and databases: how the backend talks to the database

1. The backend opens a **connection** to the database (in practice it keeps a *connection pool*, a set of ready connections, because opening one per request is slow).
2. It sends **SQL** queries, either written by hand or generated by an **ORM** (Object-Relational Mapper, such as Hibernate/JPA in Java) that turns objects into SQL.
3. For changes that must happen together (create order + reduce stock), it wraps the queries in a **transaction** so either all succeed or none do.
4. It turns the results into objects and then into **JSON** for the frontend.

### What a backend system really does

- **Validation:** is the quantity positive? Is the email well-formed?
- **Business rules:** apply a coupon, calculate delivery charges, check stock.
- **Security:** check who the user is (authentication) and what they may do (authorization).
- **Orchestration:** call the payment gateway, then save the order, then send a notification.
- **Data access:** read and write the database efficiently and safely.

### Where data lives in a modern app

One application often uses several storage technologies, each for what it does best:

| Kind of data | Typical store | Why |
|---|---|---|
| Orders, payments, accounts | Relational database (PostgreSQL) | Needs correctness, relationships, transactions |
| Sessions, cached pages, OTPs | In-memory key-value store (Redis) | Extremely fast, data can expire |
| Product images, invoices, videos | Object storage (Amazon S3, Azure Blob) | Cheap for large files |
| Full-text search ("red shoes size 9") | Search engine (Elasticsearch, OpenSearch) | Ranked, fuzzy text search |
| Business reports | Data warehouse (Snowflake, BigQuery, Redshift) | Fast analytics over years of history |
| Events between services | Message broker (Kafka, RabbitMQ) | Decouples services, buffers spikes |
| Application logs | Log platform (ELK, CloudWatch) | Debugging and monitoring |

### Worked example: one food-delivery order, end to end

1. You tap **Place order**. The app (frontend) sends `POST /api/orders` with JSON such as `{"restaurantId": 12, "items": [...]}`.
2. The backend checks your login token, validates the items and calculates the bill.
3. It calls the **payment gateway** API and waits for success.
4. It saves the order in **PostgreSQL** inside a transaction.
5. It publishes an `OrderPlaced` event to **Kafka**. The restaurant service, the rider-assignment service and the notification service react to it.
6. Your live rider location is kept in **Redis**, because it changes every few seconds.
7. Overnight (or continuously) the order is copied into the **data warehouse**, where the business sees "orders per city per hour".

::: extension Monolith vs microservices (how architecture affects data)
A **monolith** is one application with one database. **Microservices** split the app into small services (users, orders, payments), and the usual rule is *database per service*: each service owns its data and others reach it only through its API or events. That gives teams independence, but it makes cross-service queries and consistency harder, which is exactly why integration patterns (Modules 5 and 6) matter.

[[fig:monolith_vs_microservices | One shared database (monolith) vs one database per service (microservices).]]
:::

::: project Using this in your project story
If your project is a web app, describe it in these layers: "React frontend → Spring Boot REST API → PostgreSQL, with an external payment API and an export for reports." Then say which layer you built and one design decision you made in it. Interviewers love a clear map before details.
:::

::: explain
"A modern data system is the whole chain that collects, stores, processes and serves data, not just one database. A typical application has a frontend for the user, a backend API that holds the business logic, and a database that stores data safely. The backend also calls other services, like a payment gateway, and the data is copied to an analytics system for reporting. For example, in a food-delivery app the order is saved in PostgreSQL, the rider's live location sits in Redis, and the warehouse powers the city-wise sales dashboard."
:::

::: trap
- Describing the system as "frontend + database". The backend/API layer is essential; the frontend should never connect to the database directly.
- Assuming one database does everything. Real systems mix stores (relational, cache, search, object storage, warehouse).
- Forgetting governance: security, quality and monitoring are part of the system, not extras.
:::

::: questions
#### Basic
Q: [DEFINITION] What is a data system?
A: The complete set of components that collect, store, process, move and serve an organisation's data: sources, ingestion, storage, processing, serving and governance.

Q: [DEFINITION] What does the backend of an application do?
A: It validates input, applies business rules, handles authentication and authorization, talks to the database and other services, and returns responses (usually JSON) to the frontend.

Q: [WHY] Why shouldn't a mobile app connect directly to the database?
A: It would expose database credentials, let users bypass business rules, and make every schema change break installed apps. The API in the middle protects and controls access.

#### Intermediate
Q: [HOW] What happens between a backend and a database when a request comes in?
A: The backend takes a connection from its pool, runs SQL (often generated by an ORM), wraps related changes in a transaction, maps rows into objects and returns JSON.

Q: [COMPARISON] Where would you store product images vs order details?
A: Images in object storage (cheap, built for large files) with only the file URL in the database; order details in a relational database, because they need structure, relationships and transactions.

Q: [DEFINITION] What is a connection pool and why is it used?
A: A set of already-open database connections that requests borrow and return. Opening a new connection for every request is slow and can overload the database.

#### Scenario-based
Q: [DESIGN QUESTION] Sketch the architecture of a job portal.
A: Web/mobile frontend → REST API (job search, apply, recruiter dashboards) → PostgreSQL for users, jobs and applications; object storage for resumes; a search engine for keyword job search; email service for alerts; a warehouse for hiring analytics.

Q: [SCENARIO] Your dashboard queries are slowing down the checkout page. Why might that happen and what would you do?
A: Heavy analytical queries compete with checkout transactions on the same database. Move reporting to a read replica or, better, copy data to a warehouse (OLAP) and run dashboards there.

#### Follow-up / Trap
Q: [TRAP QUESTION] "Our app uses MongoDB, so we don't have a backend." Is that right?
A: No. The choice of database does not remove the need for a backend; something still has to validate requests, enforce rules and protect the data. Even "backend-as-a-service" products are a backend you rent.
:::

## Session 1.2 — Modern Data Systems & Integration (Part 2): How Data Moves Between Systems {: #s1-2 }

### What is data integration?

**Simple meaning:** data integration is combining data from different systems so it can be used together, or keeping several systems in sync with each other.

**Why it exists:** companies run many separate systems. Each team picks the best tool for its job, and soon the same customer exists in five places:

| System | What it knows about customer "Aarav Patel" |
|---|---|
| E-commerce database | his orders and addresses |
| Payment gateway | his payments and refunds |
| CRM (Salesforce) | his support calls and sales opportunities |
| Marketing tool | which emails he opened |
| Mobile analytics | what he clicked in the app |

Each system is a **data silo**: useful alone, but nobody can answer "Who are our most valuable customers, and are they happy?" without integrating them. A unified picture of the customer is often called **Customer 360**.

### The common ways data moves

| Method | How it works | Speed | Typical use |
|---|---|---|---|
| **API call** | One system asks another over HTTP and gets a reply | Real time | Checkout calls the payment gateway |
| **File transfer** | A system exports a CSV/Excel/JSON file; another imports it (often via SFTP or cloud storage) | Hours (batch) | Bank sends daily settlement files |
| **Database replication / CDC** | Changes in one database are copied to another, often by reading the database's change log | Seconds to minutes | Keep a reporting copy or search index fresh |
| **Messaging / events** | A system publishes a message; others consume it when ready | Near real time, asynchronous | `OrderPlaced` event triggers inventory and email |
| **ETL / ELT pipeline** | Extract from sources, transform, load into a warehouse | Minutes to hours | Nightly load of sales into the warehouse |

You will study each of these properly in Modules 5 and 6. For now, notice the trade-off: **faster integration is usually more complex** to build and run.

### APIs: the doors between systems

An **API (Application Programming Interface)** is a contract that says "send me a request in this format and I will reply in that format". Systems do not need to know each other's internals; they only need the contract.

::: analogy The restaurant waiter
You (the client) do not walk into the kitchen. You read the menu (API documentation), tell the waiter (API) what you want, and the waiter brings back your food (the response). The kitchen can change its ovens without changing the menu.
:::

### What "data processing" means

Between moving and storing, data is usually processed in a few standard steps:

1. **Collect** the raw data.
2. **Validate** it: are required fields present? Are dates real dates?
3. **Clean** it: remove duplicates, fix formats (`"PUNE"`, `"Pune "` → `"Pune"`).
4. **Transform** it: join with other data, calculate totals, convert currencies.
5. **Store** it where it will be used.
6. **Serve** it to an app, report or model.

### Why integration is hard

| Challenge | Example | Usual fix |
|---|---|---|
| Different formats | One system sends XML, another expects JSON | Transformation/mapping layer |
| Different meanings | `cust_no` in ERP vs `customer_id` in CRM; "active customer" defined differently | Data mapping documents, master data management |
| Duplicates | Same customer created twice with slightly different names | Matching and de-duplication rules |
| Timing | Report shows yesterday's stock while the app shows today's | Agree on freshness needs; use CDC or events if needed |
| Failures | Target system is down during the nightly load | Retries, idempotent loads, alerts |
| Security and privacy | Sensitive data copied to too many places | Masking, least-privilege access, encryption |

### Worked example: one order touches many systems

When an e-commerce order is placed, the order system integrates with:

- the **payment gateway** (synchronous API call: we must know the payment worked);
- **inventory** (reserve stock, often through an event);
- **notifications** (send email/SMS, asynchronously; the customer should not wait for it);
- **the warehouse** (copy for reporting, in batch or by streaming);
- **the CRM** (so support staff can see the order history).

Choosing *how* each link works (API, event, file, pipeline) is the heart of integration design.

::: explain
"Data integration means bringing data from different systems together so it can be used as one, or keeping those systems in sync. Companies have silos: orders in one database, customers in a CRM, payments with a gateway. We connect them using APIs for real-time requests, events or message queues for asynchronous updates, change data capture to copy database changes, and ETL or ELT pipelines to load a warehouse. The hard parts are mismatched formats and definitions, duplicates, failures and keeping the data fresh enough."
:::

::: trap
- Thinking integration is only about APIs. Files, CDC, events and pipelines are just as common.
- Ignoring meaning: two systems can both have a "customer" field that means different things.
- Assuming real-time is always better. It costs more; many reports are fine with daily data.
:::

::: questions
#### Basic
Q: [DEFINITION] What is data integration?
A: Combining data from multiple sources into a consistent, usable view, or keeping multiple systems synchronised.

Q: [DEFINITION] What is a data silo?
A: Data locked inside one system or team that others cannot easily access or combine, like customer support data that never reaches the sales reports.

Q: [DEFINITION] What is an API?
A: A defined contract that lets one system request data or actions from another without knowing its internals, typically over HTTP with JSON.

#### Intermediate
Q: [COMPARISON] Name four ways to move data between systems and when you would use each.
A: API calls for real-time request/response (payments); file transfer for simple batch exchange (daily bank files); CDC/replication to mirror database changes (search index); events/queues for asynchronous notifications (order placed); ETL/ELT for loading warehouses.

Q: [WHY] Why is data integration difficult?
A: Different formats and definitions, duplicates, timing differences, failures and retries, and security/privacy concerns when copying data.

#### Scenario-based
Q: [SCENARIO] Sales says the dashboard shows fewer orders than the app. What could be wrong?
A: The pipeline may run in batch (data is stale), a load may have failed silently, filters or definitions may differ (cancelled orders excluded), or duplicates/time-zone issues. I would compare counts per day between source and warehouse to find where they diverge.

Q: [DESIGN QUESTION] A hospital wants lab results from the lab system to appear in the doctor's app within a minute. How would you integrate them?
A: Event-based or CDC integration: the lab system publishes a "ResultReady" event (or CDC captures new rows), a consumer transforms it to the app's format and stores it in the app's database. A nightly batch file would be too slow.

#### Follow-up / Trap
Q: [TRAP QUESTION] If both systems have a `customer_id`, is integrating them easy?
A: Not necessarily. The IDs may come from different numbering schemes, so the same number can mean different people. You need a mapping or a shared master key (for example an email or a master customer ID).
:::

## Session 1.3 — Modern Data Systems & Integration (Part 3): Processing, OLTP vs OLAP, and Why One Database Is Not Enough {: #s1-3 }

### Batch processing vs real-time (stream) processing

**Batch processing** collects data over a period and processes it together at a scheduled time.

- *Examples:* monthly payroll, nightly sales report, end-of-day bank statement, daily load into a warehouse.
- *Why use it:* simple, efficient for large volumes, easy to re-run if something fails.

**Real-time (stream) processing** handles each event within seconds (or less) of it happening.

- *Examples:* card fraud detection, live delivery tracking, stock price alerts, "trending now" lists.
- *Why use it:* some decisions lose their value if they are late. A fraud alert tomorrow is useless.

[[fig:batch_vs_stream | Batch waits and processes everything together; streaming processes each event as it arrives.]]

| Aspect | Batch | Streaming (real-time) |
|---|---|---|
| When it runs | On a schedule (hourly, nightly) | Continuously |
| Latency (delay) | Minutes to hours | Milliseconds to seconds |
| Data size per run | Large chunks | One event or a small window |
| Complexity | Lower | Higher (ordering, late events, failures) |
| Cost | Usually cheaper | Usually more expensive |
| Re-processing | Easy: run the job again | Harder: needs replayable streams |
| Typical tools | SQL jobs, Spark, Airflow-scheduled jobs | Kafka, Kinesis, Flink, Spark Structured Streaming |
| Example | Daily sales report | Fraud detection on card swipes |

Between the two sits **near-real-time** or **micro-batch** processing (for example, every 1–5 minutes), which is often "real-time enough" at a fraction of the cost.

::: tip The interview-winning question
When asked "batch or real-time?", ask back: **"How fresh does the data need to be for the decision?"** If the answer is "by tomorrow morning", batch is simpler and cheaper.
:::

### Transactional systems (OLTP) vs analytical systems (OLAP)

**OLTP — Online Transaction Processing** systems run the business day to day: placing orders, transferring money, booking tickets. They handle many small, fast reads and writes, and they must be correct every time.

**OLAP — Online Analytical Processing** systems help people *understand* the business: "revenue by city by month for three years". They run fewer but much heavier queries that scan and summarise lots of history.

[[fig:oltp_to_olap | Operational (OLTP) databases feed an analytical (OLAP) warehouse through ETL/ELT pipelines.]]

| Aspect | OLTP | OLAP |
|---|---|---|
| Purpose | Run the business | Analyse the business |
| Typical query | Insert order #9001; fetch one customer's cart | Total sales by region and quarter for 3 years |
| Query shape | Short, touches few rows | Long, scans millions of rows, aggregates |
| Users | Customers, staff, applications (thousands at once) | Analysts, managers, data scientists |
| Data | Current, up to the second | Historical, often refreshed hourly/daily |
| Design | Normalized (avoid duplication, protect consistency) | Denormalized star/snowflake schemas (fewer joins, fast reads) |
| Storage | Row-oriented | Often column-oriented |
| Priority | Fast writes, correctness, concurrency (ACID) | Fast reads and aggregation over large data |
| Examples | PostgreSQL, MySQL, Oracle, SQL Server running the app | Snowflake, BigQuery, Redshift, Azure Synapse |

**Why keep them separate?** If a manager runs a three-year sales report on the same database that handles checkout, the report competes for CPU, memory and disk, and customers feel it as a slow checkout. Copying data into a warehouse lets each system be designed for its own job.

### Operational data vs analytical data

- **Operational data** is the *current state* needed to run the business: today's stock level, the customer's current address, the open orders.
- **Analytical data** is *history and summaries* used for decisions: stock levels every day for two years, how many customers moved city, monthly revenue trends.

Operational systems often overwrite old values (the new address replaces the old one). Analytical systems usually *keep* history so trends can be studied (Module 2 shows how, with slowly changing dimensions).

### Why modern systems need multiple data technologies

No single database is best at everything. Using several, each for the job it does best, is called **polyglot persistence**.

[[fig:polyglot_food_delivery | One food-delivery app, seven data technologies, each chosen for a specific job.]]

| Job | Best-fit technology | Why not the relational database? |
|---|---|---|
| Money and orders | Relational (PostgreSQL) | — it *is* the right tool: ACID and relationships |
| Microsecond lookups, sessions, counters | Redis | A relational DB is slower and wastes resources on this |
| Flexible, changing product/menu attributes | Document DB (MongoDB) | Constant schema changes in a relational DB are painful |
| Free-text search with typos and ranking | Elasticsearch | `LIKE '%biryani%'` cannot rank results or handle typos well |
| Large files (images, PDFs) | Object storage | Storing large binary files in tables bloats the database |
| Events between services | Kafka | A table used as a queue does not scale well to many consumers |
| Years of history for reports | Data warehouse | Heavy scans would slow down the transactional database |

::: note A balanced view (interviewers like this)
More technologies mean more to learn, monitor, secure and keep consistent. A good engineer starts simple (a single PostgreSQL database can go a long way, and it even supports JSON documents and full-text search) and adds a new store only when there is a clear need.
:::

::: explain
"OLTP systems run the business: lots of small, fast transactions like placing an order or transferring money, so they are normalized and ACID-compliant. OLAP systems analyse the business: fewer but heavy queries over years of history, like revenue by region per quarter, so they use denormalized star schemas, often in a columnar warehouse such as Snowflake or BigQuery. We keep them separate so reports don't slow down customers, and we move data from OLTP to OLAP with ETL or ELT pipelines."
:::

::: trap
- Saying "OLAP is a type of database product." OLAP is a *workload*; many products serve it.
- Claiming real-time is always better than batch. It is costlier and more complex; choose by the freshness the business needs.
- Thinking polyglot persistence is always good. Each extra store adds operational cost.
- Mixing up "operational data" (current state) with "analytical data" (history).
:::

::: questions
#### Basic
Q: [DEFINITION] What is batch processing?
A: Processing data collected over a period together at a scheduled time, for example a nightly sales report or monthly payroll.

Q: [DEFINITION] What is stream (real-time) processing?
A: Processing each event continuously within seconds of it happening, for example fraud checks on card transactions or live order tracking.

Q: [COMPARISON] What is the difference between OLTP and OLAP?
A: OLTP handles many small, fast transactions that run the business and needs correctness (ACID); OLAP handles fewer, heavy analytical queries over historical data and is optimised for reading and aggregating.

#### Intermediate
Q: [WHY] Why do companies keep separate OLTP and OLAP systems?
A: Analytical queries scan huge amounts of data and would slow down customer transactions; the two workloads also need different designs (normalized vs star schema, row vs column storage).

Q: [DEFINITION] What is polyglot persistence?
A: Using different data storage technologies for different needs within one application, such as PostgreSQL for orders, Redis for caching and Elasticsearch for search.

Q: [COMPARISON] Operational data vs analytical data?
A: Operational data is the current state needed for daily work; analytical data is historical and summarised for decision-making, and usually keeps history instead of overwriting it.

Q: [DEFINITION] What is micro-batch processing?
A: Running small batches very frequently (every few seconds or minutes) to get near-real-time results with batch-style simplicity.

#### Scenario-based
Q: [SCENARIO] A bank wants to block suspicious card transactions. Batch or streaming? Why?
A: Streaming. The decision must be made before or within seconds of the transaction; a nightly batch would only find the fraud after the money is gone.

Q: [SCENARIO] HR wants a monthly attrition report. Batch or streaming?
A: Batch. Monthly freshness is enough, batch is simpler and cheaper, and it is easy to re-run.

Q: [DESIGN QUESTION] Which data stores would you use for a ride-sharing app?
A: PostgreSQL for riders, drivers, trips and payments (ACID); Redis or a geospatial store for live driver locations; Kafka for trip events; object storage for documents; a warehouse for analytics such as trips per city per hour.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can PostgreSQL be used for analytics?
A: Yes, for moderate data sizes PostgreSQL handles reporting well, especially on a read replica. Dedicated warehouses become worth it when data grows very large or many analysts run heavy queries.

Q: [TRAP QUESTION] Is "real-time" always worth it?
A: No. It adds cost and complexity (ordering, late events, failure handling). If the business acts on data daily, batch is the better engineering choice.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** List the six building blocks of a data system.

**P2.** Classify each as OLTP or OLAP: (a) withdrawing cash at an ATM, (b) a yearly sales trend chart, (c) adding an item to a cart, (d) comparing branch performance across five years.

**P3.** Give one example each of batch and streaming processing from daily life.

#### Level 2 — Interview application
**P4.** Explain, in under a minute, why the frontend should not connect directly to the database.

**P5.** A colleague wants to store product images inside a PostgreSQL table. What would you suggest instead, and why?

**P6.** Explain polyglot persistence and give one disadvantage.

#### Level 3 — Scenario / problem solving
**P7.** An e-commerce company's checkout becomes slow every morning at 9 AM, when managers open their dashboards. Diagnose the likely cause and propose two fixes (one quick, one long-term).

**P8.** Design the data flow for a food-delivery "orders per city per hour" dashboard that must be at most 5 minutes old. Which integration method would you choose?
:::

::: answers
**P1.** Sources, ingestion, storage, processing, serving, and governance (security, quality, metadata, monitoring) across all of them.

**P2.** (a) OLTP, (b) OLAP, (c) OLTP, (d) OLAP.

**P3.** Batch: your monthly credit card statement. Streaming: the live location of your cab or delivery rider.

**P4.** "Putting database credentials inside an app is a security risk, and users could bypass the business rules. An API in the middle validates requests, checks permissions and hides the database design, so we can change the schema without breaking every installed app."

**P5.** Store the images in object storage such as Amazon S3 or Azure Blob and keep only the image URL (and maybe size and type) in PostgreSQL. Object storage is cheaper for large files, keeps the database small and fast, and works with a CDN for quick delivery.

**P6.** Using different storage technologies for different jobs within one system (relational for orders, Redis for cache, Elasticsearch for search). Disadvantage: more systems to run, secure and monitor, and keeping data consistent across them is harder.

**P7.** Heavy analytical queries are running on the same OLTP database as checkout and competing for resources. Quick fix: point dashboards at a read replica. Long-term fix: load the data into a data warehouse with ETL/ELT (or streaming) and run all dashboards there.

**P8.** Five minutes is near-real-time, so use change data capture or order events (Kafka) feeding a stream or micro-batch job that aggregates orders by city and hour into the warehouse or a small serving table. A nightly batch would be too stale; full streaming with per-second updates is more than needed.
:::

## Session 1.4 — Module 1 Summary & Rapid Revision {: #s1-4 }

::: summary Module 1 Summary
#### Most important concepts
- A **data system** = sources → ingestion → storage → processing → serving, with governance across all.
- A modern app = **frontend → backend/API → database**, plus other services and analytics.
- **Data integration** connects silos using APIs, files, CDC, events and ETL/ELT.
- **Batch** (scheduled, cheap, simple) vs **streaming** (continuous, low latency, complex).
- **OLTP** (run the business, many small ACID transactions) vs **OLAP** (analyse the business, heavy queries over history).
- **Polyglot persistence**: different stores for different jobs, at the cost of complexity.

#### What to memorize
- OLTP = transactions, normalized, row store, current data. OLAP = analytics, star schema, column store, historical data.
- Five ways data moves: API, file, CDC/replication, events/messaging, ETL/ELT.

#### What to understand (not memorize)
- *Why* the frontend never talks to the database directly.
- *Why* analytics is separated from transactions.
- *How* to choose batch vs streaming: by the freshness the decision needs.

#### Most common interview questions
- OLTP vs OLAP? · Batch vs streaming? · What is data integration? · Walk me through your app's architecture. · Why use several databases?

#### Common mistakes
- "SQL is a database." · "Real-time is always better." · "One database for everything." · Forgetting the backend layer.
:::

::: checklist
- [ ] I can define a data system and its building blocks
- [ ] I can draw frontend → API → database → analytics
- [ ] I can explain what a backend does
- [ ] I can define data integration and data silos
- [ ] I can list five ways data moves between systems
- [ ] I can compare batch and streaming with examples
- [ ] I can compare OLTP and OLAP in a table
- [ ] I can explain operational vs analytical data
- [ ] I can explain polyglot persistence and its cost
- [ ] I can describe my own project in layers
:::
