# How to Use This Handbook {: #start data-label="START HERE" }

<p class="lead">This handbook replaces the course videos for interview preparation. It follows the seven modules of the Tekstac <em>Modern Data Systems</em> course, re-teaches every topic in plain English, and adds what interviewers usually ask on top of the course.</p>

You do not need to watch the videos first. Read a session, run through its interview questions out loud, try the practice set, and tick the checklist at the end of the module.

## What Is Inside {: .nobreak #inside }

| Part | Module | What you will be able to do after it |
|---|---|---|
| I | Introduction to Modern Data Systems | Explain how an app stores, moves and analyses data; OLTP vs OLAP; batch vs real-time |
| II | Data Modeling Fundamentals | Design tables, choose keys, normalize to 3NF, design a star schema, model documents |
| III | Basics of SQL (Foundational) | Write SELECT, joins, GROUP BY, subqueries, CTEs, window functions; explain indexes and transactions; solve 22 classic SQL interview patterns |
| IV | Cloud Databases & Storage Systems | Choose SQL vs NoSQL, explain CAP, use MongoDB CRUD, compare warehouse, lake and lakehouse |
| V | Data Integration & APIs | Explain a REST request end to end, HTTP methods and status codes, auth, retries, idempotency |
| VI | Integration Patterns in the Enterprise | Compare APIs vs queues, pub/sub, event-driven design, ETL vs ELT, batch vs streaming |
| VII | Modern Trends & Future Directions | Discuss data mesh, serverless and AI-ready data critically, with trade-offs |
| Final | Final Interview Revision | 100 key questions, a 50-question SQL bank, scenario questions, rapid fire, a one-day revision sheet and an answering strategy |
| Appendix | Glossary and Coverage Verification | Look up any term in plain English; see how the handbook was checked against its brief |

## How Every Session Is Built {: .nobreak #session-structure }

Every session follows the same rhythm, so you always know where to look:

1. **The idea in simple words**, then *why it exists*, *how it works*, an example and where it is used in real systems.
2. **Diagrams and tables** wherever a picture is faster than a paragraph.
3. **Code with real output.** Every SQL query marked with an *Output* panel was actually run on PostgreSQL while this PDF was built. Important queries are followed by a **Line by Line** explanation.
4. **How I Would Explain This in an Interview**: a natural 30–60 second spoken answer.
5. **Common Traps & Mistakes**: the confusions that cost candidates marks.
6. **Interview Questions** in four groups (Basic, Intermediate, Scenario-based, Follow-up/Trap), each with a short model answer.
7. **Practice Questions** at three levels at the end of each important topic group, with the answers kept in a separate **Answer / Explanation** box so you can test yourself first.
8. At the end of each module: a **Module Summary** and a **Rapid Revision Checklist**.

## Labels You Will See {: .nobreak #labels }

| Label | Meaning |
|---|---|
| [DEFINITION] | "What is X?" questions. Answer in one or two clean sentences. |
| [WHY] | "Why do we need X?" Talk about the problem it solves. |
| [HOW] | "How does X work?" Walk through the mechanism step by step. |
| [COMPARISON] | "X vs Y". Use a small table in your head: purpose, how, when to use. |
| [SCENARIO] | A real situation. Ask a clarifying question, then propose and justify. |
| [SQL PROBLEM] | Write a query. Think aloud, start simple, then refine. |
| [DESIGN QUESTION] | Design a small system or schema. Cover data, flow and trade-offs. |
| [TRAP QUESTION] | A question designed to catch a common misunderstanding. |
| [EASY] [MEDIUM] [HARD] | Difficulty of a SQL pattern or practice question. |
| [HIGH PRIORITY] [MEDIUM PRIORITY] [LOWER PRIORITY] | How much interview time a topic usually gets. Spend your time accordingly. |
| [INTERVIEW EXTENSION] | Useful knowledge that goes beyond the course content. |

::: extension Interview Extension boxes
Purple boxes and the [INTERVIEW EXTENSION] label mark material that is **not** part of the original course but that interviewers commonly expect (for example, isolation levels, SCD types or idempotency keys). Everything else follows the course topics.
:::

::: prereq Recommended Prerequisite boxes
Grey boxes mark background knowledge you need before a topic makes sense, such as "what is a database?" before data modeling.
:::

## Study Plans {: .nobreak #study-plans }

Pick the plan that matches the time you have. Sessions tagged [HIGH PRIORITY] come first in every plan.

| If you have… | Do this |
|---|---|
| **1 day** (about 8 hours) | One-Day Revision Sheet (1 h) → Module 3 Sessions 3.1–3.8 skim plus SQL Patterns 1–12 (3 h) → Sessions 2.3–2.5 keys and normalization (1 h) → Sessions 4.2–4.5 SQL vs NoSQL and MongoDB (1 h) → Sessions 5.2–5.5 REST and HTTP (45 min) → Sessions 6.2, 6.3 and 6.6 (30 min) → Module 7 summary (15 min) → 100 Most Important Questions, read aloud (30 min) |
| **3 days** | Day 1: Modules 1–2 plus their practice sets. Day 2: all of Module 3 with every SQL example typed out once. Day 3: Modules 4–7 summaries and questions, the SQL Question Bank, then the One-Day Sheet in the evening. |
| **7 days** | One module per day (Module 3 gets two days), finishing every practice set. Day 7: the Final Interview Revision part, a mock interview with a friend, and your project story. |

::: tip The single best habit
Say answers **out loud**. Reading an answer and being able to say it clearly are different skills. The "How I Would Explain This" boxes exist for that reason.
:::

## About the Source Material {: .nobreak #source-note }

This handbook was built from the module and topic structure of the Tekstac *Modern Data Systems* course as described in the preparation brief: seven modules and their listed sessions, quizzes, practice programs and subtopics. The course screenshots themselves were not available when this edition was produced, so:

- Session titles that were named explicitly (for example *PostgreSQL Basics – Part 1*, *DDL*, *DML* and *Window Functions & Indexing*) are used as they are.
- Where a module's sessions were described only by topic, the session titles were rebuilt from those topics and are marked **†** in the Course Coverage Map. The topics themselves are all covered; only the exact titles or the split into parts may differ from the videos.
- Nothing is presented as course content unless it was part of the course topic list. Extra material is labelled [INTERVIEW EXTENSION].

If your course shows a session that is not listed in the coverage map, look its topic up in the map on the next pages or in the Glossary at the back. Every topic from the brief is covered somewhere.

# Course Coverage Map {: #coverage-map data-label="START HERE" }

<p class="lead">Use this map to check that every course session and topic is covered, and to jump straight to it. Titles marked † were reconstructed from the module's topic list (see "About the Source Material").</p>

::: covmap
<p class="tablecap">Module 1 — Introduction to Modern Data Systems</p>

| Course session / topic | Covered in | Page |
|---|---|---|
| (Prerequisite) Data, databases and DBMS basics | Session 1.0 [INTERVIEW EXTENSION] | <a class="pageref" href="#s1-0"></a> |
| Modern Data Systems & Integration — Part 1: data systems, how applications store data † | Session 1.1 | <a class="pageref" href="#s1-1"></a> |
| Modern Data Systems & Integration — Part 2: how data moves, data integration, APIs, backend systems † | Session 1.2 | <a class="pageref" href="#s1-2"></a> |
| Modern Data Systems & Integration — Part 3: batch vs real-time, OLTP vs OLAP, operational vs analytical data, why many data technologies † | Session 1.3 | <a class="pageref" href="#s1-3"></a> |
| Module 1 quiz concepts, summary and checklist | Session 1.4 | <a class="pageref" href="#s1-4"></a> |

<p class="tablecap">Module 2 — Data Modeling Fundamentals</p>

| Course session / topic | Covered in | Page |
|---|---|---|
| Introduction to data modeling (conceptual, logical, physical) † | Session 2.1 | <a class="pageref" href="#s2-1"></a> |
| Entities, attributes and relationships; ER concepts † | Session 2.2 | <a class="pageref" href="#s2-2"></a> |
| Primary keys, foreign keys and constraints † | Session 2.3 | <a class="pageref" href="#s2-3"></a> |
| Relational model, schema, table design; one-to-one, one-to-many, many-to-many † | Session 2.4 | <a class="pageref" href="#s2-4"></a> |
| Normalization: functional dependency, anomalies, 1NF, 2NF, 3NF, BCNF † | Session 2.5 | <a class="pageref" href="#s2-5"></a> |
| Denormalization: when to normalize, when to denormalize † | Session 2.6 | <a class="pageref" href="#s2-6"></a> |
| Data warehousing: fact and dimension tables, star vs snowflake, OLTP vs OLAP † | Session 2.7 | <a class="pageref" href="#s2-7"></a> |
| NoSQL modeling: schema flexibility, embedding vs referencing, access patterns † | Session 2.8 | <a class="pageref" href="#s2-8"></a> |
| Module 2 quiz concepts, summary and checklist | Session 2.9 | <a class="pageref" href="#s2-9"></a> |

<p class="tablecap">Module 3 — Basics of SQL (Foundational)</p>

| Course session / topic | Covered in | Page |
|---|---|---|
| (Prerequisite) The sample database used in every example | Session 3.0 | <a class="pageref" href="#s3-0"></a> |
| PostgreSQL Basics — Part 1 (SELECT, FROM, WHERE, DISTINCT, ORDER BY, LIMIT, OFFSET, aliases, data types) | Session 3.1 | <a class="pageref" href="#s3-1"></a> |
| PostgreSQL Basics — Part 2 (operators, NULL, aggregate, string, date and numeric functions, CASE) | Session 3.2 | <a class="pageref" href="#s3-2"></a> |
| DDL (CREATE, ALTER, DROP, TRUNCATE, constraints) | Session 3.3 | <a class="pageref" href="#s3-3"></a> |
| DML (INSERT, UPDATE, DELETE) plus DCL and TCL | Session 3.4 | <a class="pageref" href="#s3-4"></a> |
| Grouping and aggregation: GROUP BY, HAVING, WHERE vs HAVING † | Session 3.5 | <a class="pageref" href="#s3-5"></a> |
| Joins: inner, left, right, full, cross, self; referential integrity † | Session 3.6 | <a class="pageref" href="#s3-6"></a> |
| Subqueries, CTEs (including recursive) † | Session 3.7 | <a class="pageref" href="#s3-7"></a> |
| Window Functions & Indexing — window functions | Session 3.8 | <a class="pageref" href="#s3-8"></a> |
| Window Functions & Indexing — indexing | Session 3.9 | <a class="pageref" href="#s3-9"></a> |
| Transactions, ACID, isolation and read anomalies † | Session 3.10 | <a class="pageref" href="#s3-10"></a> |
| Practice programs: SQL interview patterns (22 patterns) | Session 3.11 | <a class="pageref" href="#s3-11"></a> |
| Module 3 quiz concepts, summary and checklist | Session 3.12 | <a class="pageref" href="#s3-12"></a> |

<p class="tablecap">Module 4 — Cloud Databases & Storage Systems</p>

| Course session / topic | Covered in | Page |
|---|---|---|
| Cloud databases: managed, RDS / Cloud SQL, serverless, analytical; scaling, availability, backups, replication, failover † | Session 4.1 | <a class="pageref" href="#s4-1"></a> |
| SQL vs NoSQL: relational, document, key-value, graph, column-family, columnar † | Session 4.2 | <a class="pageref" href="#s4-2"></a> |
| NoSQL fundamentals and the CAP theorem; eventual consistency † | Session 4.3 | <a class="pageref" href="#s4-3"></a> |
| MongoDB: database, collection, document, field, BSON † | Session 4.4 | <a class="pageref" href="#s4-4"></a> |
| MongoDB CRUD: insert, find, update, delete, updateMany, deleteMany † | Session 4.5 | <a class="pageref" href="#s4-5"></a> |
| MongoDB indexing, aggregation, embedding vs referencing † | Session 4.6 | <a class="pageref" href="#s4-6"></a> |
| Data storage: database, warehouse, lake, lakehouse; structured, semi-structured, unstructured data † | Session 4.7 | <a class="pageref" href="#s4-7"></a> |
| Module 4 quiz concepts, summary and checklist | Session 4.8 | <a class="pageref" href="#s4-8"></a> |

<p class="tablecap">Module 5 — Data Integration & APIs</p>

| Course session / topic | Covered in | Page |
|---|---|---|
| What an API is; client-server; request/response † | Session 5.1 | <a class="pageref" href="#s5-1"></a> |
| HTTP and REST: methods, status codes, JSON † | Session 5.2 | <a class="pageref" href="#s5-2"></a> |
| Designing and consuming REST APIs: pagination, rate limiting, versioning † | Session 5.3 | <a class="pageref" href="#s5-3"></a> |
| Authentication and authorization † | Session 5.4 | <a class="pageref" href="#s5-4"></a> |
| API integration and external APIs: sync vs async, failures, retries, idempotency † | Session 5.5 | <a class="pageref" href="#s5-5"></a> |
| Data integration † | Session 5.6 | <a class="pageref" href="#s5-6"></a> |
| Module 5 quiz concepts, summary and checklist | Session 5.7 | <a class="pageref" href="#s5-7"></a> |

<p class="tablecap">Module 6 — Integration Patterns in the Enterprise</p>

| Course session / topic | Covered in | Page |
|---|---|---|
| Enterprise integration and system-to-system communication; integration patterns † | Session 6.1 | <a class="pageref" href="#s6-1"></a> |
| Synchronous vs asynchronous; API vs message queue † | Session 6.2 | <a class="pageref" href="#s6-2"></a> |
| Messaging: queues, publish/subscribe, producers, consumers † | Session 6.3 | <a class="pageref" href="#s6-3"></a> |
| Event-driven architecture † | Session 6.4 | <a class="pageref" href="#s6-4"></a> |
| Data pipelines; batch vs real-time processing † | Session 6.5 | <a class="pageref" href="#s6-5"></a> |
| ETL vs ELT † | Session 6.6 | <a class="pageref" href="#s6-6"></a> |
| Streaming † | Session 6.7 | <a class="pageref" href="#s6-7"></a> |
| Salesforce and cloud data warehouse integration † | Session 6.8 | <a class="pageref" href="#s6-8"></a> |
| Choosing an integration pattern [INTERVIEW EXTENSION] | Session 6.9 | <a class="pageref" href="#s6-9"></a> |
| Module 6 quiz concepts, summary and checklist | Session 6.10 | <a class="pageref" href="#s6-10"></a> |

<p class="tablecap">Module 7 — Modern Trends & Future Directions</p>

| Course session / topic | Covered in | Page |
|---|---|---|
| Data mesh † | Session 7.1 | <a class="pageref" href="#s7-1"></a> |
| Serverless † | Session 7.2 | <a class="pageref" href="#s7-2"></a> |
| AI and data management † | Session 7.3 | <a class="pageref" href="#s7-3"></a> |
| Modern data systems: real-time analytics, event-driven, cloud-native, distributed, data platforms † | Session 7.4 | <a class="pageref" href="#s7-4"></a> |
| Thinking critically about trends [INTERVIEW EXTENSION] | Session 7.5 | <a class="pageref" href="#s7-5"></a> |
| Module 7 summary and checklist | Session 7.6 | <a class="pageref" href="#s7-6"></a> |

<p class="tablecap">Final Interview Revision</p>

| Section | Page |
|---|---|
| 100 Most Important Questions | <a class="pageref" href="#f1"></a> |
| SQL Question Bank — Top 50 SQL Questions | <a class="pageref" href="#f2"></a> |
| Top Database Questions | <a class="pageref" href="#f3"></a> |
| Top Scenario Questions | <a class="pageref" href="#f4"></a> |
| Rapid-Fire Questions | <a class="pageref" href="#f5"></a> |
| Project Connection | <a class="pageref" href="#f6"></a> |
| One-Day Revision Sheet | <a class="pageref" href="#f7"></a> |
| Interview Answering Strategy | <a class="pageref" href="#f8"></a> |

<p class="tablecap">Appendix</p>

| Section | Page |
|---|---|
| Glossary (162 terms) | <a class="pageref" href="#glossary"></a> |
| Coverage Verification (self-review against the brief) | <a class="pageref" href="#coverage-check"></a> |
:::

::: note Quizzes and practice programs
The course modules include quizzes and practice programs. Their concepts are covered by the **Interview Questions** and **Practice Questions** boxes in each session, by Session 3.11 (SQL patterns, which mirror typical SQL practice programs) and by the SQL Question Bank in the final part.
:::

# PwC Interview Orientation {: #pwc data-label="START HERE" }

<p class="lead">This chapter explains what is publicly known about PwC technology interviews in India, what is only reported by candidates, and how to prepare. It does not invent "official PwC questions".</p>

## Four Kinds of Information — Keep Them Separate {: .nobreak #pwc-kinds }

| Category | What it means | How much to trust it |
|---|---|---|
| **A. Common software and database questions** | Questions asked across the industry for any software or data role (joins, normalization, ACID, REST…). | Very reliable. These are the core of every technical interview. |
| **B. Reported candidate experiences** [REPORTED] | What individual candidates wrote about their own PwC interviews on public sites. | Useful signal, but each report is one person, one year, one role, one campus. |
| **C. Likely topics for the role** [LIKELY] | Topics that fit the job description of technology, data and consulting roles. | Reasonable inference, not a promise. |
| **D. Recommended preparation** [RECOMMENDED] | This handbook's advice on what to study and how. | Our judgement, based on A–C. |

::: trap Do not over-trust "PwC question lists"
Websites that publish "PwC interview questions" are usually generic question banks. PwC has many business units (Advisory, Tax, Assurance, the Acceleration Centers) and many roles, and the process changes from year to year. Prepare the fundamentals well and you will be ready for any variation.
:::

## A. Common Software and Database Questions {: .nobreak #pwc-a }

These appear in almost every entry-level technical interview, including consulting firms. They are the backbone of this handbook:

- **SQL:** write a query with a join, GROUP BY with HAVING, the second-highest salary, duplicates, top N per group, a window function.
- **DBMS:** primary vs foreign key, normalization (1NF–3NF), ACID, transactions, indexes, DELETE vs TRUNCATE vs DROP.
- **Data modeling:** design tables for a small business problem (library, hospital, e-commerce).
- **APIs:** what is REST, HTTP methods, status codes, PUT vs PATCH, authentication vs authorization.
- **Programming and OOP:** the four pillars of OOP, one language in depth, basic data structures.
- **Your project:** architecture, your role, a problem you solved, what you would improve.

## B. Reported Candidate Experiences {: .nobreak #pwc-b }

The following themes come from public interview write-ups (sources at the end of this chapter). They were collected from search summaries in October 2026; individual details vary a lot.

| Theme | What candidates reported [REPORTED] |
|---|---|
| Process | An online assessment, then a technical interview, then a managerial or partner round, then HR. Some write-ups describe a "Launchpad" programme and a hackathon before the interviews. |
| Online assessment | Aptitude sections (quantitative, logical reasoning, verbal/English). Some reports also mention technical multiple-choice questions on OOP, DBMS, networking and data structures. |
| Technical round | Often around 30 minutes, frequently resume- and project-based. SQL joins and their types, normalization, ACID properties and basic DBMS terms appear repeatedly. |
| Practical SQL | One report describes being asked to create a table, alter it to add columns, create a table from existing tables and write a GROUP BY query. |
| Programming | Easy-to-medium problems: sort an array without a built-in sort, swap two numbers without a third variable, list vs tuple and dictionaries in Python, OOP concepts. |
| APIs and backend | Reports for software roles mention HTTP methods, status codes, query vs path parameters, PUT vs PATCH, idempotency, REST and SOLID principles. |
| Data roles | Experienced data-engineering candidates report scenario-based questions on SQL, Spark, Databricks and Power BI. |
| Final rounds | The partner or managerial round may be technical or about fit and attitude. HR questions include "Why PwC?". |

## C. Likely Topics for Technology and Data Roles {: .nobreak #pwc-c }

Based on the role descriptions and the reports above, a technology or data candidate should expect [LIKELY]:

1. **SQL writing on the spot**, from simple filters to joins, grouping, subqueries and window functions.
2. **DBMS concepts** asked as "what is" and "difference between" questions.
3. **Designing a small schema** and normalizing it.
4. **SQL vs NoSQL** and when to use MongoDB.
5. **How a web request flows** through frontend, API and database.
6. **Cloud and data basics**: managed databases, warehouse vs lake, ETL vs ELT.
7. **Your project**, explained with clear architecture and your contribution.
8. **Consulting behaviours**: communication, teamwork, client focus and learning attitude.

::: pwc PwC's own framework for behavioural questions
PwC publicly describes the **PwC Professional** framework with five dimensions: **Whole leadership**, **Business acumen**, **Technical and digital**, **Global and inclusive**, and **Relationships**. Prepare one short story for each (use STAR: Situation, Task, Action, Result). For example: a project where you learned a new tool quickly (*Technical and digital*), or a team conflict you resolved (*Relationships*).
:::

## D. Recommended Preparation {: .nobreak #pwc-d }

| Priority | Study | Where in this handbook |
|---|---|---|
| 1 | SQL fundamentals and the 22 interview patterns | Module 3, Session 3.11, SQL Question Bank |
| 2 | Keys, normalization, ACID, indexes, transactions | Sessions 2.3–2.5, 3.9, 3.10 |
| 3 | REST, HTTP, authentication, request flow | Module 5 |
| 4 | SQL vs NoSQL, MongoDB basics, CAP | Sessions 4.2–4.6 |
| 5 | ETL/ELT, warehouses, lakes, queues, event-driven basics | Sessions 2.7, 4.7, Module 6 |
| 6 | Modern trends, at a "can discuss sensibly" level | Module 7 |
| 7 | Your project story and behavioural stories | Project Connection, Interview Answering Strategy |

::: tip How PwC interviews feel, according to most reports
Fundamentals are tested more than tricks. Interviewers often start from your resume and keep asking "why?" until they find the edge of your understanding. Being honest ("I have not used that, but I understand it as…") is better than guessing.
:::

::: source Sources consulted (via web search, October 2026)
- PwC Acceleration Centers India — *Entry Level Campus Launchpad Program* and *AC India Assurance Launchpad Program* pages (jobs-ta.pwc.com). The programme page describes hands-on training in areas such as IT, SQL, data engineering and Python.
- PwC India — *Want to be a PwCite?* campus careers page (pwc.in): register → pre-placement talk → assessment → interview → final selection.
- PwC — *The PwC Professional / The skills we look for* (pwc.com).
- GeeksforGeeks — PwC India interview experiences for Technology Consultant, Technology Consulting Intern (2023) and Associate Engineer (on-campus) roles; *PwC Recruitment Process*.
- Naukri Code360 — PwC AC India interview experience (on-campus, October 2025).
- Glassdoor — PwC Associate Software Engineer interview questions (India).
- Medium — "PwC India Interview Experience" (S. Palit), a data-engineering interview.
- InterviewBit and PrepInsta — PwC interview process summaries.

These sources describe individual experiences and change over time. Treat them as signals, not as a syllabus.
:::
