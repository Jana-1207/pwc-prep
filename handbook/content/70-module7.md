# Modern Trends & Future Directions {: .part #m7 data-label="PART VII · MODULE 7" }

<p class="lead">This module covers the ideas currently reshaping data work: data mesh, serverless computing, AI-ready data management, real-time and cloud-native platforms. Interviewers rarely expect deep implementation detail here. They want to see that you understand <em>why</em> each trend exists, and that you can say when it is <em>not</em> a good idea.</p>

::: coverage
- Data mesh: data as a product, domain ownership, self-service platform, federated governance, centralized vs decentralized ownership † → Session 7.1
- Serverless: what and why, benefits, limitations, cold starts, scalability † → Session 7.2
- AI + data management: AI and data, modern data management, data quality, metadata, data pipelines for AI, why AI depends on good data † → Session 7.3
- Modern data systems: real-time analytics, event-driven systems, cloud-native systems, distributed data systems, data platforms † → Session 7.4
- *Interview extension:* thinking critically about trends → Session 7.5
- Module summary and checklist → Session 7.6
:::

| Topic | Priority | Typical question |
|---|---|---|
| Serverless: benefits, limits, cold starts | [MEDIUM PRIORITY] | "What is serverless? What are cold starts?" |
| Data mesh principles | [MEDIUM PRIORITY] (higher for data/consulting roles) | "What is data mesh and when would you not use it?" |
| Why AI depends on data quality; metadata; RAG | [MEDIUM PRIORITY] | "How does data quality affect AI?" |
| Cloud-native, real-time analytics, data platforms | [LOWER PRIORITY] | "What does cloud-native mean?" |

::: pwc PwC angle
Consulting firms advise clients on data strategy, cloud and AI adoption, so expect opinion questions: "What do you think about data mesh?", "Should a client go serverless?", "What must be true before a company uses AI on its data?". A strong answer gives a short definition, the problem it solves, a realistic limitation, and the conditions under which you would recommend it. That balanced reasoning matters more than buzzwords.
:::

## Session 7.1 — Data Mesh {: #s7-1 }

::: concept Trend card: Data mesh
| | |
|---|---|
| **What it is** | An organisational and architectural approach where **business domains own and publish their analytical data as products**, supported by a shared self-service platform and common governance rules. Introduced by Zhamak Dehghani (2019). |
| **Why it exists** | In large companies, one central data team becomes a **bottleneck**: every domain waits in its queue, and the central team lacks domain knowledge, so data is late or misunderstood. |
| **Problem it solves** | Scaling data work across many domains by moving ownership to the people who understand the data best. |
| **When it is useful** | Large organisations with many domains and data sources, domain teams with engineering skills, and a strong platform team. |
| **When it is not** | Small or medium companies, few data sources, teams without data skills, or no executive commitment: there it adds overhead and duplication without benefit. |
| **Interview question** | "What is data mesh, and would you recommend it for a 200-person startup?" |
:::

### Centralized vs decentralized ownership

[[fig:centralized_vs_mesh | Central data teams become bottlenecks; in a data mesh, domains publish data products on a shared platform.]]

| | Centralized (classic warehouse/lake team) | Data mesh (decentralized) |
|---|---|---|
| Who builds analytical datasets | one central data team | each business domain (orders, payments, marketing) |
| Domain knowledge | far from the data producers | inside the owning team |
| Scaling | the central team becomes a bottleneck | scales with the number of domains |
| Consistency | easier: one team, one standard | needs federated governance to stay interoperable |
| Infrastructure | one central platform, run by the data team | a shared self-serve platform, used by all domains |
| Risk | slow delivery, overloaded team | duplication, inconsistent quality if governance is weak |

### The four principles

[[fig:data_mesh | Domains own data products on a self-serve platform, under federated computational governance.]]

1. **Domain-oriented ownership:** the team that runs a business domain (e.g. Orders) owns that domain's analytical data end to end, including pipelines, quality and documentation.
2. **Data as a product:** datasets are treated like products with **consumers**. A data product must be **discoverable** (listed in a catalogue), **addressable** (a stable location), **trustworthy** (quality checks, SLAs), **self-describing** (schema and documentation), **interoperable** (shared standards) and **secure** (access policies). Each has a **data product owner**.
3. **Self-serve data platform:** a platform team provides easy, shared tooling (storage, pipelines, catalogue, access control, monitoring) so domain teams don't each build infrastructure.
4. **Federated computational governance:** global rules (security, privacy, naming, interoperability) are agreed jointly by domain and central representatives, and **enforced automatically by the platform** ("computational"), not by manual review.

::: example What a data product looks like
| Attribute | Example: `orders_daily` (owned by the Orders domain) |
|---|---|
| Owner | Order Engineering team, product owner: Priya |
| Description | one row per order per day, with status, amounts and channel |
| Location | `lakehouse.orders.orders_daily` (Delta table) + catalogue entry |
| Schema | documented columns; versioned; breaking changes announced 30 days ahead |
| Quality | tests: unique order_id per day, no null amounts, row count within ±20% of the 7-day average |
| SLA | refreshed by 06:00 IST, 99.5% of days |
| Access | analysts: read; PII columns masked except for the finance role |
:::

::: extension Data mesh vs data fabric
A **data fabric** is a **technology-led** approach: an intelligent integration layer (metadata, catalogues, virtualization, automation) that connects data wherever it lives. A **data mesh** is mainly **organisational**: ownership and products. They can coexist: a fabric-like platform can power a mesh.
:::

::: explain
"Data mesh is a way to scale analytics in large organisations by decentralising data ownership. Instead of one central team building every dataset, each business domain, like orders or payments, owns its analytical data and publishes it as a data product that is discoverable, documented, trustworthy and secure, with an owner and SLAs. A central platform team provides self-service tooling, and governance rules like security and naming are agreed federally and enforced automatically. It solves the central-team bottleneck, but it needs mature domain teams and real investment, so for a small company a well-run central warehouse is usually the better choice."
:::

::: trap
- "Data mesh is a tool or product you can buy." It's an operating model, supported by tools.
- "Data mesh means no central team." There is still a platform team and federated governance.
- Recommending it everywhere. It is overkill for small organisations.
- Calling every dataset a "data product" without owners, SLAs or documentation.
:::

::: questions
#### Basic
Q: [DEFINITION] What is data mesh?
A: A decentralised approach where business domains own their analytical data and serve it as products, on a self-serve platform under federated governance.

Q: [DEFINITION] What are the four principles of data mesh?
A: Domain ownership, data as a product, a self-serve data platform, and federated computational governance.

#### Intermediate
Q: [DEFINITION] What makes a dataset a "data product"?
A: It is built for consumers, with an owner, documentation and schema, discoverability in a catalogue, quality guarantees and SLAs, secure access, and interoperability with standards.

Q: [COMPARISON] Centralized data team vs data mesh?
A: A centralized team gives consistency but becomes a bottleneck and lacks domain context; a mesh scales through domain ownership but needs strong governance and platform support to avoid duplication and inconsistency.

Q: [COMPARISON] Data mesh vs data fabric?
A: Mesh is an organisational model (ownership, products); fabric is a technology layer (metadata-driven integration and virtualization). They can complement each other.

#### Scenario-based
Q: [SCENARIO] A 200-person startup with one data engineer asks about data mesh. Your advice?
A: Not yet. The overhead outweighs the benefit. Build a solid central warehouse or lakehouse with good modelling, a catalogue and ownership tags; revisit mesh when there are many domains and the central team becomes a bottleneck.

Q: [SCENARIO] A bank's central data team has a 9-month backlog. How could data mesh principles help?
A: Assign ownership of key datasets to domains (cards, loans, payments) with data product owners; invest in a self-serve platform; define global standards (PII, naming, quality) enforced by the platform; start with a pilot domain and measure delivery times.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does data mesh remove the need for governance?
A: No. It changes governance from central approval to federated standards enforced automatically by the platform.
:::

## Session 7.2 — Serverless Computing and Serverless Data {: #s7-2 }

::: concept Trend card: Serverless
| | |
|---|---|
| **What it is** | Running code and using managed services **without provisioning or managing servers**. You deploy functions or use services; the cloud runs, scales and bills them per use. |
| **Why it exists** | Managing servers (capacity, patching, scaling, idle cost) is undifferentiated work, and many workloads are spiky or event-driven. |
| **Problem it solves** | Paying for idle servers and doing operational work; makes automatic scaling (including to zero) the default. |
| **When it is useful** | Event-driven tasks, spiky or unpredictable traffic, APIs with variable load, glue code, scheduled jobs, prototypes. |
| **When it is not** | Constant high-throughput workloads (servers or containers become cheaper), long-running jobs beyond time limits, ultra-low-latency paths sensitive to cold starts, heavy lock-in concerns. |
| **Interview question** | "What is serverless? What is a cold start, and how do you reduce it?" |
:::

### Two halves of serverless

- **FaaS (Functions as a Service):** you write a function, the platform runs it when an event triggers it. AWS Lambda, Azure Functions, Google Cloud Functions / Cloud Run functions.
- **Serverless backends and data services:** managed services that scale automatically and bill by use: object storage (S3), serverless databases (DynamoDB, Aurora Serverless, Firestore, Cosmos DB serverless, Neon), serverless warehouses (BigQuery), queues (SQS), API gateways.

### How it works

[[fig:serverless_flow | Events trigger functions; the platform runs as many copies as needed and connects them to managed services.]]

1. An **event** occurs: an HTTP request through an API gateway, a file uploaded to storage, a message in a queue, a database change, or a schedule.
2. The platform **starts an instance** of your function (or reuses a warm one) and passes it the event.
3. The function runs your code, typically for milliseconds to minutes, calls other managed services, and returns.
4. Under load, the platform runs **many instances in parallel**; with no traffic, it runs **zero**.
5. You pay per invocation and execution time (and memory), not for idle servers.

**Example:** a user uploads a profile photo to object storage → the upload event triggers a function → the function creates a thumbnail, stores it, and updates the user record in a serverless database. No server sat idle waiting for uploads.

### Benefits and limitations

| Benefits | Limitations |
|---|---|
| No servers to patch or size | **Cold starts** add latency to some requests |
| Automatic scaling, including to zero | **Execution time limits** (e.g. AWS Lambda: 15 minutes max) |
| Pay per use: cheap for low or spiky traffic | **Stateless**: state must live in external stores |
| Fast to build event-driven glue and APIs | **Vendor lock-in**: triggers, IAM and services are provider-specific |
| Built-in high availability across zones | Harder **local testing, debugging and observability** across many small functions |
| | Can be **more expensive** than servers at constant high load |
| | Many concurrent functions can **exhaust relational database connections** (use connection proxies or pooling, e.g. RDS Proxy) |

### Cold starts explained

When a function hasn't run recently (or must scale out), the platform has to **create a new execution environment**: allocate a container or micro-VM, start the runtime, load your code and dependencies, and run initialisation. That extra delay, from roughly 100 milliseconds to a few seconds depending on runtime and package size, is a **cold start**. Later requests reuse the **warm** environment and are fast.

**Ways to reduce it:** keep deployment packages small; prefer runtimes that start fast; do heavy initialisation once, outside the handler; use **provisioned concurrency** (keep instances pre-warmed, at a cost); or keep latency-critical paths on always-on containers.

### Scalability, in practice

Serverless scales out by running more instances, up to **concurrency limits** set by the provider and your account. Downstream systems must also scale: a function that scales to 1,000 instances can overwhelm a small database. Common protections are queues to smooth bursts, reserved concurrency limits, and connection pooling.

::: explain
"Serverless means we deploy code or use managed services without managing servers. With functions as a service like AWS Lambda or Azure Functions, an event such as an HTTP request, a file upload or a queue message triggers our function; the platform runs as many instances as needed, even scaling to zero, and we pay per execution. It's great for event-driven and spiky workloads and removes ops work. The limitations are cold starts, the extra latency when a new instance initialises, plus execution time limits, statelessness, vendor lock-in and higher cost under constant heavy load. I'd use it for event-driven glue, APIs with variable traffic and scheduled jobs, and containers for steady, long-running services."
:::

::: trap
- "Serverless means no servers." Servers exist; you just don't manage them.
- "Serverless is always cheaper." Not at sustained high load.
- Ignoring cold starts for latency-sensitive APIs.
- Opening a new database connection per invocation at scale, exhausting connections.
- Putting long-running batch jobs in functions with time limits.
:::

::: questions
#### Basic
Q: [DEFINITION] What is serverless computing?
A: A cloud model where the provider manages servers, scaling and availability; you deploy functions or use managed services and pay only for actual usage.

Q: [DEFINITION] What is FaaS?
A: Functions as a Service: event-triggered functions (AWS Lambda, Azure Functions, Google Cloud Functions) that run on demand and scale automatically.

Q: [DEFINITION] What is a cold start?
A: The extra latency when a function runs in a new execution environment that must first be initialised (runtime start-up, code loading) before handling the request.

#### Intermediate
Q: [HOW] How can you reduce cold starts?
A: Smaller packages, faster-starting runtimes, initialisation outside the handler, provisioned concurrency (pre-warmed instances), or containers for latency-critical paths.

Q: [WHY] When is serverless not a good choice?
A: Constant high-throughput workloads (cheaper on servers or containers), long-running processes beyond time limits, strict low-latency requirements sensitive to cold starts, or when portability matters more than convenience.

Q: [WHY] Why can serverless functions overload a relational database?
A: Each concurrent instance may open its own connection; a burst of hundreds of instances can exceed the database's connection limit. Use connection proxies or pooling, or a serverless-friendly database.

#### Scenario-based
Q: [DESIGN QUESTION] Design a serverless pipeline that processes invoice PDFs uploaded by vendors.
A: Upload to object storage → an event triggers a function that extracts data (OCR/AI service) → the result goes to a queue → another function validates and writes it to a database → failures go to a DLQ with alerts → a scheduled function produces a daily summary.

Q: [SCENARIO] A Lambda-based API has 2-second delays for the first request in the morning. Why and what do you do?
A: Cold starts after idle time. Reduce package size and initialisation work, use provisioned concurrency for the critical endpoints, or keep a minimal warm capacity.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is a serverless database the same as SQLite running inside a function?
A: No. A serverless database is a managed service whose capacity scales automatically and which bills by use (DynamoDB, Aurora Serverless). An embedded database inside a stateless function would lose its data between invocations.
:::

## Session 7.3 — AI and Modern Data Management {: #s7-3 }

::: concept Trend card: AI-ready data management
| | |
|---|---|
| **What it is** | Managing data (quality, metadata, governance, pipelines) so it can be trusted to train, ground and monitor AI systems, and using AI to help manage data. |
| **Why it exists** | AI systems are only as good as the data behind them; with generative AI, companies want models to answer from their own documents and data. |
| **Problem it solves** | Unreliable, biased, undocumented or non-compliant data producing wrong, unfair or risky AI outputs. |
| **When it is useful** | Any organisation building ML models or GenAI assistants on its own data. |
| **When it is not** | It is always relevant, but "AI first" projects without basic data quality and governance usually fail; fix the foundation first. |
| **Interview question** | "Why does AI depend on good data? What would you check before training a model?" |
:::

### Why AI depends on good data

A machine-learning model **learns patterns from examples**. If the examples are wrong, incomplete or biased, the model faithfully learns the wrong lessons: **garbage in, garbage out**.

| Data problem | What happens to the AI |
|---|---|
| Inaccurate labels (fraud marked as normal) | the model learns to miss fraud |
| Missing or unrepresentative data (only metro-city customers) | poor predictions for everyone else |
| Historical bias (past loan approvals favoured one group) | the model reproduces discrimination |
| Duplicates and leakage (test data seen in training) | great test scores, poor real performance |
| Stale data (2019 shopping patterns) | wrong recommendations today: **data drift** |
| Outdated documents (old HR policy) in a GenAI assistant | confident but wrong answers |

### The building blocks of modern data management

**Data quality** (Session 5.6): accuracy, completeness, consistency, validity, uniqueness, timeliness, plus, for AI, **representativeness** and **label quality**. Quality is checked continuously in pipelines, not once.

**Metadata** is data about data, and it is what makes data findable and trustworthy:

| Type | Examples |
|---|---|
| Technical | table and column names, types, sizes, partitions |
| Business | definitions ("active customer = ordered in the last 90 days"), owner, sensitivity (PII) |
| Operational | last refresh time, row counts, quality-test results, lineage |

A **data catalogue** (Microsoft Purview, Databricks Unity Catalog, Collibra, Alation, DataHub) stores this metadata so people can search for data, understand it and request access. **Lineage** shows where data came from and what depends on it: essential to explain an AI output, to assess the impact of changes, and for audits.

**Data governance** defines who owns data, who may use it and how: access control, privacy (personal data, consent, retention), and compliance with laws such as India's **Digital Personal Data Protection (DPDP) Act, 2023** and the EU's GDPR. For AI, governance also covers **responsible AI**: fairness, transparency and human oversight.

### Data pipelines for AI

[[fig:ai_data_pipeline | The data lifecycle behind an AI application, with a monitoring loop that feeds back into data fixes and retraining.]]

1. **Collect** data from applications, documents, logs and sensors.
2. **Clean and validate**: de-duplicate, fix types, handle missing values, mask PII.
3. **Label and enrich**: human or programmatic labels; add metadata and lineage.
4. **Prepare features or embeddings**: features for classic ML (often in a **feature store**, so training and live predictions use identical definitions); **embeddings** (number vectors that capture meaning) for GenAI search.
5. **Train or retrieve**: train or fine-tune models, or retrieve relevant content for a large language model (RAG).
6. **Serve** predictions or answers in applications.
7. **Monitor**: data drift, model accuracy, bias and feedback; fix the data and retrain.

### Generative AI and enterprise data: RAG in one paragraph

**Retrieval-Augmented Generation (RAG)** lets a large language model answer questions from *your* documents without retraining it:

1. Split documents (policies, manuals, contracts) into chunks.
2. Convert each chunk into an **embedding** and store it in a **vector database** (pgvector in PostgreSQL, Pinecone, Weaviate, or vector search in other databases).
3. When a user asks a question, embed the question and **retrieve** the most similar chunks (a similarity search).
4. Send the question **plus** the retrieved chunks to the LLM, which answers **grounded** in them, ideally citing sources.

RAG makes data management *more* important, not less: outdated, duplicated or unauthorised documents lead to wrong or leaked answers, so freshness, access control on retrieval and metadata all matter.

### AI helping data management

AI is also used **by** data teams: automatically classifying sensitive columns (PII detection), flagging anomalies in pipelines (sudden drops in row counts), suggesting matches for de-duplication, generating documentation, and translating natural-language questions into SQL. The rule: **AI suggestions need validation**. Generated SQL must be reviewed and tested like any other code.

::: explain
"AI depends on good data because models learn patterns from the data they're given. If the data is inaccurate, incomplete, biased or outdated, the model learns those problems. Garbage in, garbage out. So before AI, I'd check data quality, representativeness and label accuracy, make sure there's metadata and lineage, so we know what the data means and where it came from, and make sure governance covers privacy, consent and access, for example under India's DPDP Act. For generative AI, techniques like RAG ground a model in company documents through a vector database, which makes freshness and access control of those documents critical. Then we monitor for drift and feed issues back into the data pipeline."
:::

::: trap
- "More data always beats better data." Biased or noisy data at scale makes things worse.
- Treating data quality as a one-time cleanup.
- Forgetting privacy and consent when reusing personal data for AI.
- Trusting AI-generated SQL or classifications without review.
- Thinking RAG removes the need for document governance.
:::

::: questions
#### Basic
Q: [WHY] Why does AI depend on good data?
A: Models learn from data; errors, gaps and bias in the data become errors, gaps and bias in predictions (garbage in, garbage out).

Q: [DEFINITION] What is metadata, and why does it matter?
A: Data about data (definitions, types, owners, freshness, lineage); it makes data discoverable, understandable, trustworthy and governable.

Q: [DEFINITION] What is data drift?
A: A change over time in the statistical properties of incoming data compared with the training data, which degrades model performance.

#### Intermediate
Q: [DEFINITION] What is data lineage?
A: The record of where data comes from and how it is transformed and used, from source to report or model, used for trust, impact analysis, debugging and compliance.

Q: [DEFINITION] What is RAG?
A: Retrieval-Augmented Generation: retrieving relevant chunks of your own content (via embeddings and a vector database) and giving them to an LLM so its answer is grounded in them.

Q: [DEFINITION] What is a feature store?
A: A system that manages ML features with consistent definitions for training and real-time serving, plus versioning and reuse across models.

#### Scenario-based
Q: [SCENARIO] A loan-approval model rejects many applicants from one region. What would you investigate?
A: Training data representativeness and historical bias, proxy features (pin code standing in for protected attributes), label quality, data drift, and fairness metrics, then fix the data or features, add fairness constraints and human review.

Q: [SCENARIO] An HR chatbot built with RAG gives answers based on last year's leave policy. Why, and how do you fix it?
A: The vector index contains outdated documents. Govern the document source (one authoritative version), re-index on change, attach effective-date metadata, filter retrieval by status, and show citations so users can verify.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can AI fix bad data automatically?
A: It can help (anomaly detection, matching, classification), but the suggestions need validation and root causes must be fixed in source systems and pipelines. AI doesn't replace data ownership and governance.
:::

## Session 7.4 — Modern Data Systems: Real-Time, Event-Driven, Cloud-Native and Distributed {: #s7-4 }

### Real-time analytics

::: concept Trend card: Real-time analytics
| | |
|---|---|
| **What it is** | Analysing data within seconds of it being created, so dashboards and decisions reflect what is happening *now*. |
| **Why it exists** | Some decisions lose value quickly: fraud, surge pricing, live operations, sales events. |
| **Problem it solves** | Decisions based on yesterday's data in situations that change by the minute. |
| **When it is useful** | Fraud and risk, logistics and delivery tracking, live sales monitoring, IoT, personalization. |
| **When it is not** | Monthly or weekly reporting, strategic planning: the extra cost and complexity bring no benefit. |
| **Interview question** | "When would you build real-time analytics, and what would you use?" |
:::

Typical stack: events flow through a **stream** (Kafka, Kinesis, Event Hubs), are processed by a **stream processor** (Flink, Spark Structured Streaming), and land in a **real-time analytical store** built for fast aggregations on fresh data (ClickHouse, Apache Druid, Apache Pinot, or streaming tables in a lakehouse or warehouse), with dashboards on top.

### Event-driven systems, at business level

Session 6.4 covered the mechanics. The trend is that companies increasingly treat **business events** (OrderPlaced, PaymentFailed, ShipmentDelayed) as first-class data, streamed to everyone who needs them, instead of nightly extracts. That enables real-time customer experiences and operations. Its cost is the need for event governance: schemas, ownership and retention.

### Cloud-native systems

::: concept Trend card: Cloud-native
| | |
|---|---|
| **What it is** | Building systems designed for the cloud from the start: **containers**, **orchestration (Kubernetes)**, **microservices**, **managed services**, **autoscaling**, **infrastructure as code** and **CI/CD**, with strong **observability**. |
| **Why it exists** | Simply moving old servers to the cloud ("lift and shift") keeps old limitations; cloud-native designs exploit elasticity and managed services. |
| **Problem it solves** | Slow releases, manual scaling, fragile deployments and poor resilience. |
| **When it is useful** | Products that change frequently, scale variably and need high availability. |
| **When it is not** | Small or stable apps where Kubernetes and microservices add more complexity than value; a managed monolith may be better. |
| **Interview question** | "What does cloud-native mean? Is Kubernetes always needed?" |
:::

| Cloud-native building block | What it gives you |
|---|---|
| Containers (Docker) | the same packaged app runs identically everywhere |
| Kubernetes | runs and heals containers, scales them, rolls out updates |
| Managed services (DBaaS, queues, serverless) | less operational work; built-in HA |
| Infrastructure as code (Terraform, Bicep, CloudFormation) | environments created repeatably from version-controlled code |
| CI/CD pipelines | automated testing and frequent, safe releases |
| Observability (logs, metrics, traces) | see and debug what distributed systems are doing |

### Distributed data systems

A **distributed** data system spreads data and work across many machines, for **scale** (more data and traffic than one machine can handle), **availability** (survive machine or zone failures) and **geography** (data close to users, or within a country for regulation).

The price is new problems that single machines don't have:

| Challenge | What it means | Usual answer |
|---|---|---|
| Network failures and partitions | machines can't reach each other | replication + the CAP trade-off (Session 4.3) |
| Consistency | replicas may disagree for a while | strong vs eventual consistency, quorums |
| Partitioning / sharding | deciding which node holds which data | partition keys, consistent hashing |
| Coordination | agreeing on a leader or an order of events | consensus algorithms (Raft, Paxos) in etcd, ZooKeeper, distributed SQL |
| Clocks | machines' clocks drift | logical clocks, careful use of timestamps |
| Partial failure | some nodes fail while others work | retries, idempotency, timeouts, health checks |

Examples: Cassandra, MongoDB sharded clusters, Kafka, distributed SQL (Spanner, CockroachDB, YugabyteDB), and cloud warehouses (Snowflake, BigQuery), which are distributed under the hood.

### Data platforms and the modern data stack

[[fig:modern_data_stack | The modern data stack: managed, cloud-native components for ingestion, storage, transformation, BI and orchestration.]]

A **data platform** is the shared set of tools and services an organisation uses to ingest, store, process, govern and serve data. The **modern data stack** describes a popular cloud version of it: managed ingestion connectors (Fivetran, Airbyte), a cloud warehouse or lakehouse (Snowflake, BigQuery, Databricks), SQL transformation with tests (dbt), BI (Power BI, Tableau, Looker), orchestration (Airflow, Dagster), plus catalogue, lineage and observability tools.

Two related practices:

- **DataOps:** applying DevOps habits to data: version control, automated testing, CI/CD for pipelines, monitoring, and quick, safe changes.
- **Data observability:** monitoring data health along five common dimensions: **freshness** (is it up to date?), **volume** (are row counts normal?), **schema** (did columns change?), **distribution** (are values in normal ranges?) and **lineage** (what is affected?).

::: extension Data contracts
A **data contract** is an agreement between the producer of data (say, the orders service) and its consumers, specifying schema, meaning, quality expectations and change rules, ideally checked automatically in CI. It prevents "an engineer renamed a column and the CFO's dashboard broke".
:::

::: explain
"Modern data systems are increasingly real-time, event-driven, cloud-native and distributed. Real-time analytics streams events through Kafka and a processor like Flink into fast analytical stores, for use cases like fraud or live operations. Cloud-native means designing for the cloud with containers, Kubernetes, managed services, infrastructure as code and CI/CD. Distributed systems give scale and availability but bring partitioning, consistency and coordination challenges. All of this sits on a data platform, often the modern data stack of managed connectors, a cloud warehouse or lakehouse, dbt, BI and orchestration, run with DataOps practices and data observability."
:::

::: trap
- Equating cloud-native with "running on a cloud VM".
- Adopting Kubernetes and microservices for a small, stable app.
- Building real-time analytics where daily reports are enough.
- Forgetting that distributed systems trade simplicity for scale: consistency and failures must be designed for.
:::

::: questions
#### Basic
Q: [DEFINITION] What is real-time analytics?
A: Analysing data within seconds of its creation, typically through streaming pipelines and fast analytical stores, to support immediate decisions.

Q: [DEFINITION] What does cloud-native mean?
A: Building applications to fully use cloud capabilities: containers, orchestration, microservices, managed services, autoscaling, infrastructure as code, CI/CD and observability.

Q: [DEFINITION] What is a distributed data system?
A: A data system whose storage and processing are spread across multiple machines for scale, availability and geographic reach.

#### Intermediate
Q: [DEFINITION] What is the modern data stack?
A: A set of cloud-based, mostly managed tools: ingestion connectors, a cloud warehouse or lakehouse, SQL transformation (dbt), BI, orchestration, plus catalogue and observability.

Q: [DEFINITION] What is data observability?
A: Monitoring the health of data, meaning freshness, volume, schema, distribution and lineage, to detect and resolve data issues quickly.

Q: [WHY] Why are distributed systems harder than single-node systems?
A: Network failures and partitions, consistency between replicas, data partitioning, coordination and consensus, clock differences and partial failures all have to be handled.

#### Scenario-based
Q: [SCENARIO] A retailer wants live sales during a festival sale. Propose an architecture.
A: POS and online orders publish events to a stream (Kafka/Event Hubs); a stream processor aggregates sales per store and minute (tumbling windows); results land in a real-time OLAP store or a streaming table; a dashboard refreshes every few seconds; raw events also go to the lakehouse for later analysis.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is moving an on-prem app to cloud VMs "cloud-native"?
A: No, that's lift-and-shift. Cloud-native means redesigning around managed services, elasticity, automation and resilience.
:::

## Session 7.5 — Thinking Critically About Trends {: #s7-5 }

[INTERVIEW EXTENSION] Interviewers, especially in consulting, like candidates who neither dismiss new ideas nor repeat hype. Use this reality check.

| Trend | Problem it really solves | Hype claim | Reality |
|---|---|---|---|
| Data mesh | central data team bottleneck at large scale | "Every company should adopt data mesh" | needs many domains, data-skilled teams and a platform; overkill for small organisations |
| Serverless | idle cost, ops work, spiky load | "Always cheaper, infinitely scalable" | cold starts, limits, lock-in; expensive at steady high load |
| Lakehouse | duplicate lake + warehouse, unreliable lakes | "Warehouses are dead" | warehouses remain excellent for structured BI; choose by workload |
| Real-time analytics | stale data for time-critical decisions | "All analytics should be real-time" | most reporting is fine with batch; streaming costs more |
| Microservices | team autonomy and independent scaling | "Monoliths are bad" | a modular monolith is often better for small teams |
| NoSQL | scale, flexible schemas | "SQL can't scale" | distributed SQL exists; relational fits most business data |
| GenAI on company data | unlocking knowledge in documents | "Just plug in an LLM" | needs data quality, access control, evaluation and governance |

### How to answer "What do you think about X?"

1. **Define** it in one sentence.
2. **Name the problem** it solves (why it exists).
3. **Say when it fits**, with one concrete example.
4. **Say when it doesn't**, with one limitation.
5. **Give your recommendation** for the situation asked about.

::: explain Example answer: "Is serverless the future?"
"Serverless is great for event-driven and spiky workloads because it removes server management and scales to zero, for example processing uploaded files or running an API with uneven traffic. But it has cold starts, execution limits and can cost more at constant high load, so long-running or steady services are often cheaper on containers. I see the future as a mix: serverless for glue and bursty work, containers and managed databases for the core. The right choice depends on the workload."
:::

::: trap
- Repeating hype ("X is the future") without naming the problem X solves.
- Dismissing a trend outright. Interviewers want balanced judgement, not cynicism.
- Listing tools instead of trade-offs: cost, skills, complexity, lock-in.
- Ignoring organisational readiness. People, process and governance matter as much as technology.
- Claiming hands-on experience with a trend you have only read about.
:::

::: questions
#### Basic
Q: [WHY] Why do interviewers ask for your opinion on technology trends?
A: To test judgement: whether you understand the problem a technology solves, its trade-offs and when it is the wrong choice, rather than whether you can repeat buzzwords.

Q: [DEFINITION] What is hype, and how do you spot it?
A: A claim that a technology fits every situation. You can spot it when the claim names no problem, no trade-off and no condition: "always cheaper", "SQL can't scale", "warehouses are dead".

#### Intermediate
Q: [HOW] How do you structure an answer to "What do you think about X?"
A: Define it in one sentence, name the problem it solves, say when it fits (with an example), say when it doesn't (one limitation), then recommend what to do in the situation asked about.

Q: [COMPARISON] Is the lakehouse replacing the data warehouse?
A: Not entirely. A lakehouse removes the duplicate lake-plus-warehouse copy and suits mixed BI, data science and ML on open table formats; a cloud warehouse remains excellent for structured BI with less engineering effort. Many companies use both, chosen by workload.

#### Scenario-based
Q: [SCENARIO] A client's CEO read that "data mesh is the future" and wants to start next month. How do you respond?
A: Acknowledge the goal (faster, domain-owned data), then assess readiness: number of domains, data skills in teams, platform maturity, governance. Propose a pilot with one or two domains on a self-serve platform, with success metrics, rather than a big-bang reorganisation.

Q: [SCENARIO] Should a company with 5 GB of sales data build a streaming lakehouse?
A: Probably not. A managed cloud warehouse (or even PostgreSQL) with daily ELT meets the need at a fraction of the cost and complexity. Scale up when real requirements appear.

#### Follow-up / Trap
Q: [TRAP QUESTION] Name one trend you think is overhyped and defend your view.
A: Any reasoned answer works, for example: "Real-time everything. Most decisions don't need second-level freshness, and streaming adds cost and operational complexity; I'd start with batch and add streaming only for decisions that lose value within minutes."
:::

::: practice
#### Level 1 — Basic understanding
**P1.** List the four principles of data mesh.

**P2.** What causes a cold start?

**P3.** Name three types of metadata with an example each.

#### Level 2 — Interview application
**P4.** Explain "garbage in, garbage out" with an AI example from banking or retail.

**P5.** Give two workloads that suit serverless and two that don't, with reasons.

#### Level 3 — Scenario / problem solving
**P6.** A company wants an internal chatbot that answers questions from 10,000 policy PDFs. List the data management steps needed before and after launch.

**P7.** Critically evaluate the claim "Our company should move everything to microservices and Kubernetes this year" for a 15-developer team.
:::

::: answers
**P1.** Domain-oriented ownership; data as a product; a self-serve data platform; federated computational governance.

**P2.** A request arriving when no warm execution environment exists, so the platform must create one: allocate resources, start the runtime, load code and dependencies, and run initialisation before handling the request.

**P3.** Technical: column `order_date` is a DATE. Business: "active customer = ordered in the last 90 days", owned by the Sales Ops team. Operational: the table was refreshed at 05:42 today with 1.2M rows, and all quality tests passed.

**P4.** A retail recommendation model trained on data where returned orders were recorded as successful sales learns to recommend products that customers actually send back. Bad labels lead to bad recommendations, no matter how advanced the model.

**P5.** Suit: (1) image or file processing on upload, which is event-driven and bursty; (2) a webhook receiver or low-traffic API, with uneven load and scale-to-zero savings. Don't suit: (1) a high-traffic API running 24×7 at steady load, where containers or VMs are cheaper; (2) a 3-hour batch transformation, which exceeds function time limits and needs Spark or containers.

**P6.** Before: identify authoritative documents and owners; remove duplicates and outdated versions; extract text (OCR where needed); add metadata (department, effective date, confidentiality); define access rules so users retrieve only what they're allowed to see; chunk, embed and index in a vector store; build an evaluation set of real questions with correct answers. After: re-index on document changes; monitor answer quality and user feedback; log sources cited; review failures; check for leakage of restricted content; keep a governance owner accountable.

**P7.** "Microservices and Kubernetes solve real problems, independent deployment and scaling for many teams, but they add significant operational complexity: networking, observability, distributed failures and platform skills. With 15 developers, a well-structured modular monolith on a managed platform (app service or containers) with CI/CD probably delivers faster and more reliably. I'd extract services only where there is a clear scaling or team-autonomy need, and adopt Kubernetes when the number of services and teams justifies a platform."
:::

## Session 7.6 — Module 7 Summary & Rapid Revision {: #s7-6 }

::: summary Module 7 Summary
#### Most important concepts
- **Data mesh:** domain ownership, data as a product, self-serve platform, federated computational governance; solves central-team bottlenecks; overkill for small organisations.
- **Serverless:** FaaS + serverless data services; event-triggered, auto-scaling to zero, pay per use; limits: cold starts, time limits, statelessness, lock-in, cost at steady load.
- **AI + data management:** garbage in, garbage out; quality, metadata, catalogues, lineage, governance (DPDP Act, GDPR); AI pipelines with drift monitoring; RAG and vector databases; AI assisting data teams (with validation).
- **Modern data systems:** real-time analytics; event-driven business; cloud-native (containers, Kubernetes, IaC, CI/CD, observability); distributed systems' challenges; data platforms, the modern data stack, DataOps, data observability, data contracts.
- **Critical thinking:** define → problem → when it fits → when it doesn't → recommendation.

#### What to memorize
- The four data mesh principles; what a cold start is and how to reduce it; the five data observability dimensions.

#### What to understand
- Why each trend exists and its main limitation.
- Why AI makes data governance more important.

#### Most common interview questions
- What is data mesh? · What is serverless / a cold start? · Why does AI depend on good data? · What is RAG? · What is cloud-native? · What is the modern data stack? · Is trend X right for this company?

#### Common mistakes
- Treating trends as universally good · "serverless = no servers" · "mesh = no central team" · ignoring governance for AI.
:::

::: checklist
- [ ] I can explain data mesh and its four principles
- [ ] I can compare centralized and decentralized data ownership
- [ ] I can describe a good data product
- [ ] I can explain serverless, FaaS and serverless databases
- [ ] I can explain cold starts and how to reduce them
- [ ] I can list when serverless is and isn't a good fit
- [ ] I can explain why AI depends on data quality
- [ ] I can explain metadata, catalogues and lineage
- [ ] I can describe a data pipeline for AI, including drift monitoring
- [ ] I can explain RAG in a few sentences
- [ ] I can explain real-time analytics and when to use it
- [ ] I can define cloud-native and its building blocks
- [ ] I can list the challenges of distributed data systems
- [ ] I can describe the modern data stack, DataOps and data observability
- [ ] I can evaluate any trend with a balanced answer
:::
