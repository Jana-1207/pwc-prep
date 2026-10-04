# Integration Patterns in the Enterprise {: .part #m6 data-label="PART VI · MODULE 6" }

<p class="lead">A large company runs dozens or hundreds of applications: ERP, CRM, HR, billing, e-commerce, warehouses, partner systems. This module covers the patterns that connect them: integration styles, APIs vs messaging, queues and publish/subscribe, event-driven architecture, data pipelines, ETL vs ELT, streaming, and a concrete Salesforce-to-warehouse integration.</p>

::: coverage
- Enterprise integration, system-to-system communication, integration patterns † → Session 6.1
- Synchronous vs asynchronous communication; API vs message queue † → Session 6.2
- Messaging: message queues, publish/subscribe, producers, consumers; point-to-point vs pub/sub † → Session 6.3
- Event-driven architecture † → Session 6.4
- Batch processing, real-time processing, data pipelines; batch vs streaming † → Session 6.5
- ETL, ELT; ETL vs ELT † → Session 6.6
- Streaming † → Session 6.7
- Salesforce / cloud data warehouse integration: the underlying architecture † → Session 6.8
- *Interview extension:* choosing the right integration pattern → Session 6.9
- Module quiz concepts → interview questions in each session and Session 6.10
:::

| Topic | Priority | Typical question |
|---|---|---|
| ETL vs ELT, batch vs streaming | [HIGH PRIORITY] for data roles | "Explain ETL vs ELT and when you'd use each." |
| API vs message queue, sync vs async | [MEDIUM PRIORITY] | "When would you use a queue instead of a REST call?" |
| Point-to-point vs pub/sub | [MEDIUM PRIORITY] | "Queue vs topic?" |
| Event-driven architecture | [MEDIUM PRIORITY] | "What are the benefits and challenges of EDA?" |
| Streaming (Kafka concepts), windows | [MEDIUM PRIORITY] | "What is a Kafka partition / consumer group?" |
| Salesforce-to-warehouse integration | [LOWER PRIORITY] (high for consulting/data roles) | "How would you load CRM data into Snowflake?" |

::: pwc PwC angle
Integration is everyday consulting work: connecting a client's SAP, Salesforce, e-commerce platform and data warehouse; choosing between real-time and batch; or replacing fragile point-to-point links with a platform. Interviewers often present a scenario ("Finance wants yesterday's Salesforce deals in the warehouse every morning") and listen for trade-offs: latency, cost, reliability, volume and ownership.
:::

## Session 6.1 — Enterprise Integration Fundamentals {: #s6-1 }

### What is enterprise integration?

**Enterprise integration is connecting a company's separate applications so that data and business processes flow between them automatically**, without people re-typing data from one screen into another.

Typical systems in one company:

| System type | Examples | Owns data about |
|---|---|---|
| ERP | SAP S/4HANA, Oracle ERP, Microsoft Dynamics | finance, inventory, procurement, manufacturing |
| CRM | Salesforce, Microsoft Dynamics CRM, HubSpot | leads, customers, sales opportunities, support cases |
| HRMS | Workday, SAP SuccessFactors | employees, payroll, leave |
| E-commerce / apps | custom apps, Shopify | orders, carts, users |
| Billing / payments | Zuora, payment gateways | invoices, payments |
| Analytics | data warehouse, lakehouse, BI | history, KPIs |

### Why integration matters: processes cross systems

Consider **order-to-cash**: a sales rep closes a deal in the **CRM** → an order is created in the **ERP** → the warehouse ships it → **billing** sends an invoice → the payment is recorded in **finance** → everything lands in the **data warehouse** for reporting. If any link is manual, you get delays, typing errors and arguments about which number is right. Similar cross-system processes include **procure-to-pay** (purchasing to supplier payment) and **hire-to-retire** (HR).

### The four classic integration styles

The book *Enterprise Integration Patterns* (Hohpe & Woolf) describes four basic ways for applications to integrate:

[[fig:integration_styles | The four classic integration styles: file transfer, shared database, remote call (API) and messaging.]]

| Style | How it works | Strengths | Weaknesses | Still used for |
|---|---|---|---|---|
| **File transfer** | app A exports a file (CSV, XML), app B imports it | simple, universal, works with legacy systems | batch delay, file handling and format errors | bank files, partner catalogues, payroll |
| **Shared database** | both apps read and write the same database | very simple, always consistent | tight coupling; one schema change breaks everyone; ownership unclear | small, closely related apps (an anti-pattern across teams) |
| **Remote procedure invocation (API)** | app A calls app B's API and waits | real time, clear contracts | both must be up (temporal coupling); chains of calls are fragile | queries, commands needing an immediate answer |
| **Messaging** | app A sends a message to a broker; app B processes it when ready | decoupled, reliable, absorbs spikes | eventual consistency; brokers to run; harder debugging | events, background processing, high volume |

### Integration topologies: from spaghetti to platforms

[[fig:p2p_vs_hub | Point-to-point integration grows quadratically; a hub or platform keeps connections manageable.]]

- **Point-to-point:** every system connects directly to each system it needs. Fine for 2–3 systems, but *n* systems can need up to *n(n−1)/2* links: 10 systems → 45 integrations, each with its own format, error handling and owner. This is the "spaghetti architecture".
- **Hub-and-spoke / ESB (Enterprise Service Bus):** a central middleware (MuleSoft, IBM Integration Bus, TIBCO, Oracle Service Bus) routes, transforms and delivers messages, so each system connects once, to the hub. The risk is a central bottleneck and a single team owning all integration logic.
- **iPaaS (Integration Platform as a Service):** cloud-hosted integration platforms (MuleSoft Anypoint, Dell Boomi, Informatica Cloud, Azure Logic Apps, Workato) with ready-made connectors for Salesforce, SAP and others.
- **API-led connectivity:** organise APIs into reusable layers. *System APIs* unlock core systems, *process APIs* combine them into business processes, and *experience APIs* tailor data for each channel.

[[fig:api_led | API-led connectivity: experience, process and system API layers.]]

- **Event-driven integration:** systems publish events to a broker (Session 6.4); anyone interested subscribes. This is the most decoupled topology.

### The vocabulary of integration patterns

These are the building blocks named in *Enterprise Integration Patterns*; integration tools implement them all:

| Pattern | Plain-English meaning | Example |
|---|---|---|
| Message channel | a named pipe that carries messages | queue `orders-to-erp` |
| Message translator | convert one format to another | CRM JSON → ERP IDoc/XML |
| Content-based router | send a message to different places based on its content | orders over ₹1 lakh go to a manual-approval queue |
| Splitter | break one message into many | one order message → one message per line item |
| Aggregator | combine related messages into one | wait for all items' stock confirmations, then confirm the order |
| Publish-subscribe channel | deliver a copy to every subscriber | `OrderPlaced` to inventory, email and analytics |
| Dead letter channel | where messages that can't be processed go | failed messages after 3 retries |
| Idempotent receiver | safely ignore duplicate messages | track processed message IDs |
| Canonical data model | one shared "standard" format between systems | a company-wide Customer schema that every system maps to |

::: explain
"Enterprise integration is connecting applications like SAP, Salesforce, HR and e-commerce so data and processes flow automatically, for example order-to-cash from CRM to ERP to billing. The classic styles are file transfer, a shared database, remote calls through APIs, and messaging. Point-to-point connections become unmanageable as systems grow, so companies use an integration platform or ESB, API-led layers, or event-driven integration through a broker. The patterns underneath, like routers, translators, publish-subscribe channels and dead-letter queues, are the same whatever tool is used."
:::

::: trap
- Treating the shared database as a good long-term integration style between teams. It couples everyone to one schema.
- Assuming point-to-point is "simpler", without counting how the links grow.
- Thinking an ESB is mandatory. Modern designs often combine API gateways, iPaaS and event streaming.
- Forgetting ownership: every integration needs an owner, monitoring and error handling.
:::

::: questions
#### Basic
Q: [DEFINITION] What is enterprise integration?
A: Connecting an organisation's separate applications and data sources so data and business processes flow automatically between them.

Q: [DEFINITION] Name the four classic integration styles.
A: File transfer, shared database, remote procedure invocation (APIs) and messaging.

Q: [DEFINITION] What is an ESB?
A: An Enterprise Service Bus: central middleware that routes, transforms and delivers messages between applications, replacing many point-to-point connections.

#### Intermediate
Q: [WHY] What's wrong with point-to-point integration at scale?
A: The number of connections grows roughly with n², each with its own format and error handling, so changes ripple everywhere and nobody has an overall view: "spaghetti architecture".

Q: [DEFINITION] What is API-led connectivity?
A: Organising APIs into layers: system APIs expose core systems, process APIs implement business processes, and experience APIs serve specific channels, to maximise reuse and isolate change.

Q: [DEFINITION] What is a canonical data model?
A: A shared, standard representation of key entities (Customer, Order) that all integrations translate to and from, reducing pairwise mappings.

#### Scenario-based
Q: [SCENARIO] A company connects 12 systems with 40 custom scripts and outages are frequent. What would you recommend?
A: Inventory the integrations; move to a platform (iPaaS/ESB or event broker) with standard connectors, a canonical model, central monitoring, retries and dead-letter handling; prioritise the most critical flows; and retire scripts gradually.

Q: [DESIGN QUESTION] How would you integrate a new e-commerce site with SAP for orders and stock?
A: Expose SAP through a system API (or iPaaS connector). The site calls a synchronous stock-check API, and orders go asynchronously through a queue to SAP, with a translator to SAP's format, retries, a dead-letter queue and status updates back to the site.

#### Follow-up / Trap
Q: [TRAP QUESTION] Isn't a shared database the most consistent integration?
A: It's consistent, but it tightly couples systems: any schema change can break other apps, ownership is unclear, and performance problems spread. APIs or events with clear contracts are safer across teams.
:::

## Session 6.2 — Synchronous vs Asynchronous Communication; API vs Message Queue {: #s6-2 }

### Coupling: the real topic

Integration choices are about **coupling**: how much one system depends on another.

| Kind of coupling | Meaning | Reduced by |
|---|---|---|
| **Temporal** | both systems must be running at the same time | asynchronous messaging (the queue holds messages) |
| **Location** | the caller must know where the other system is | brokers, service discovery, gateways |
| **Format / contract** | both must agree on data structures | versioned contracts, schemas, canonical models |

Synchronous APIs have high temporal coupling: if the inventory service is down, a synchronous checkout that calls it fails too. Messaging removes that, at the cost of eventual results. (See the sync vs async diagram in Session 5.5.)

### API (request/response) vs message queue

| | REST API call (synchronous) | Message queue (asynchronous) |
|---|---|---|
| Interaction | request → wait → response | send → continue; processed later |
| Receiver availability | must be up right now | can be down; messages wait |
| Result | immediate (success, data or error) | later, via a reply message, webhook, status poll or event |
| Load spikes | caller feels them; the receiver can be overwhelmed | the queue buffers; consumers work at their own pace |
| Scaling consumers | load balancer in front of servers | add more competing consumers |
| Failure handling | caller retries with timeouts and backoff | broker redelivers; dead-letter queue |
| Ordering | per call | FIFO queues or partitions (per key) |
| Typical tech | HTTP/REST, gRPC | RabbitMQ, Amazon SQS, Azure Service Bus, Kafka |
| Best for | queries and commands needing an immediate answer | background work, events, high volume, decoupling teams |

### Choosing between them

- **Use a synchronous API** when the user is waiting for the answer to continue: "Is this coupon valid?", "Was the payment approved?", "Show my order history."
- **Use a queue or events** when the work can happen later or takes time: sending emails, generating invoices, updating search indexes, syncing to the ERP or warehouse, video processing. Also when you need to **absorb spikes** (a sale) or **decouple teams**.
- **Combine them:** accept the request synchronously (validate, save, return **202 Accepted** or "order received") and process the rest asynchronously.

::: tip The "chain of synchronous calls" smell
If service A calls B, which calls C, which calls D synchronously, availability multiplies: four services at 99.9% each give roughly 99.6% for the chain, and latency adds up. Break long chains with asynchronous steps, caching, or by giving each service the data it needs (event-carried state).
:::

::: explain
"Synchronous communication, like a REST call, means the caller waits for the answer, which is simple and gives an immediate result but couples both systems in time: if the other side is slow or down, so is the caller. Asynchronous communication through a message queue means the caller drops a message and moves on; the queue stores it until a consumer processes it. That gives resilience, buffering for spikes and easy scaling with more consumers, at the cost of eventual consistency and more complex debugging. I use synchronous APIs when the user needs the answer immediately, and queues for background or high-volume work."
:::

::: trap
- "Asynchronous is always better." It adds brokers, duplicates, ordering and debugging complexity; use it where decoupling pays off.
- Using a queue for something the user must see immediately (e.g. "is my payment approved?") without a way to deliver the result.
- Long chains of synchronous calls between microservices.
- Forgetting that queues don't remove failures; they move failure handling to consumers (retries, DLQs, idempotency).
:::

::: questions
#### Basic
Q: [COMPARISON] API vs message queue?
A: An API call is request/response: the caller waits and both sides must be up. A message queue is asynchronous: the producer sends a message and continues, and a consumer processes it later, even if it was down when the message was sent.

Q: [DEFINITION] What is temporal coupling?
A: A dependency where two systems must be available at the same time for an interaction to succeed, typical of synchronous calls.

#### Intermediate
Q: [WHY] Why do queues help during traffic spikes?
A: They buffer incoming work, so consumers process at a sustainable rate instead of being overwhelmed; you can also add more consumers temporarily.

Q: [HOW] How does a client get a result from asynchronous processing?
A: By polling a status endpoint, receiving a webhook or callback, listening for a reply or completion event, or getting a push notification.

#### Scenario-based
Q: [SCENARIO] Generating a monthly statement PDF takes 2 minutes. How should the API handle "Download statement"?
A: Return 202 Accepted with a job ID, put the job on a queue, let workers generate the PDF, and notify the user (or let them poll `/jobs/{id}`) when it's ready, with a download link.

Q: [SCENARIO] During a flash sale the order service crashes because the inventory service is slow. What would you change?
A: Make non-critical calls asynchronous, add timeouts and circuit breakers, buffer orders through a queue, cache stock levels, and scale consumers, so a slow inventory service no longer takes down ordering.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can you do request/reply over a message queue?
A: Yes. The requester includes a reply-to queue and a correlation ID, and the responder sends the reply to that queue. It's asynchronous request/reply, useful between systems that can't call each other directly.
:::

## Session 6.3 — Messaging: Message Queues and Publish/Subscribe {: #s6-3 }

### The vocabulary

| Term | Meaning |
|---|---|
| **Message** | a unit of data sent between systems: a body (often JSON) + headers (ID, type, timestamp) |
| **Producer** (publisher, sender) | the application that sends messages |
| **Consumer** (subscriber, receiver) | the application that receives and processes messages |
| **Broker** | the middleware that stores and delivers messages: RabbitMQ, Kafka, Amazon SQS/SNS, Azure Service Bus, Google Pub/Sub |
| **Queue** | a channel where **each message is consumed by one consumer** |
| **Topic** | a channel where **each message goes to every subscriber** |
| **Acknowledgement (ack)** | the consumer tells the broker "done, you can delete it"; unacknowledged messages are redelivered |
| **Dead-letter queue (DLQ)** | where messages go after failing too many times, for inspection |

### Point-to-point: message queues

[[fig:message_queue | A queue: producers add messages; each message is processed by exactly one of the competing consumers; failures go to a dead-letter queue.]]

- Each message is delivered to **one** consumer.
- Several consumers reading the same queue are **competing consumers**: add more workers to process faster.
- Messages are stored until processed, so the producer doesn't care whether consumers are up.
- Typical uses: background jobs (send email, generate invoice, resize image), work distribution, smoothing load.

### Publish/subscribe: topics

[[fig:pub_sub | Publish/subscribe: one event, many independent subscribers, each receiving its own copy.]]

- The publisher sends a message to a **topic** without knowing who listens.
- **Every subscriber gets its own copy** and processes it independently.
- Adding a new subscriber (say, a fraud-check service) needs **no change** to the publisher.
- Typical uses: broadcasting events (`OrderPlaced`, `CustomerUpdated`), fan-out to many systems.

### Point-to-point vs publish/subscribe

| | Point-to-point (queue) | Publish/subscribe (topic) |
|---|---|---|
| Receivers per message | exactly one | every subscriber |
| Purpose | distribute **work** | broadcast **events** |
| Adding receivers | shares the load (competing consumers) | adds a new independent reaction |
| Analogy | a ticket queue at a bank: the next free teller serves you | a newspaper subscription: every subscriber gets the paper |
| Examples | SQS queue, RabbitMQ queue, Service Bus queue | SNS topic, Service Bus topic, Google Pub/Sub, a Kafka topic read by several consumer groups |

Many systems combine both: a topic fans out to several **subscription queues**, one per consuming service, so each service gets a copy and can also scale with competing consumers. (SNS → several SQS queues is a classic AWS setup.)

### Delivery guarantees

| Guarantee | Meaning | Risk |
|---|---|---|
| At-most-once | a message is delivered 0 or 1 times (no retries) | messages can be lost |
| **At-least-once** (most common) | a message is delivered 1 or more times (redelivered until acknowledged) | **duplicates** |
| Exactly-once | each message affects the result exactly once | hard; usually achieved as "effectively once" via idempotent consumers or transactional processing |

**Practical rule:** assume at-least-once delivery and make consumers **idempotent**. Store processed message IDs, or design operations so a repeat has no extra effect (set status = SHIPPED instead of "toggle status").

### Ordering, retries and poison messages

- **Ordering:** most queues don't guarantee global order at scale. FIFO queues (e.g. SQS FIFO) or partitions (Kafka) keep order **per key**, for example all events for order 9001 in sequence.
- **Retries:** if a consumer fails, the message is redelivered after a delay.
- **Poison message:** a message that always fails (bad data). Without a limit it blocks or loops forever, so after N attempts send it to the **DLQ**, alert someone, fix the problem, and replay it.

### RabbitMQ vs Kafka (a common follow-up) [INTERVIEW EXTENSION]

| | RabbitMQ (traditional broker) | Apache Kafka (distributed log) |
|---|---|---|
| Model | queues with flexible routing (exchanges) | append-only partitioned log (topics) |
| After consumption | message is removed once acknowledged | message **stays** for the retention period; consumers track their offset |
| Replay old messages | not by design | yes: re-read from any offset |
| Throughput | high | very high (millions of messages per second across a cluster) |
| Ordering | per queue | per partition |
| Typical use | task queues, request routing, RPC-style messaging | event streaming, CDC, log aggregation, data pipelines |

::: explain
"Messaging lets systems communicate asynchronously through a broker. With a queue, which is point-to-point, each message is processed by exactly one consumer, so adding consumers shares the work, which is ideal for background jobs like sending emails. With publish/subscribe, a producer publishes to a topic and every subscriber gets its own copy, which is ideal for events like OrderPlaced that inventory, email and analytics all care about. Most brokers deliver at least once, so consumers must be idempotent, and failing messages go to a dead-letter queue after a few retries."
:::

::: trap
- Mixing up queues (one consumer per message) and topics (every subscriber gets a copy).
- Assuming exactly-once delivery: design for duplicates.
- Expecting global ordering at scale: order is usually per queue or per partition key.
- No dead-letter queue, so poison messages block processing or retry forever.
- Treating Kafka like a traditional queue that deletes messages on read.
:::

::: questions
#### Basic
Q: [DEFINITION] What is a message queue?
A: A broker-managed buffer where producers put messages and consumers take them off, each message being processed by one consumer, enabling asynchronous, decoupled communication.

Q: [DEFINITION] What is publish/subscribe?
A: A messaging pattern where publishers send messages to a topic and all subscribers to that topic receive a copy, without the publisher knowing who they are.

Q: [COMPARISON] Point-to-point vs publish/subscribe?
A: Point-to-point delivers each message to one consumer (work distribution); publish/subscribe delivers each message to all subscribers (event broadcasting).

#### Intermediate
Q: [DEFINITION] What is a dead-letter queue?
A: A separate queue that receives messages that couldn't be processed after a set number of attempts (or that expired), so they don't block processing and can be investigated and replayed.

Q: [DEFINITION] What does at-least-once delivery imply for consumers?
A: Messages may be delivered more than once, so consumers must be idempotent: deduplicate by message ID or make operations safe to repeat.

Q: [DEFINITION] What are competing consumers?
A: Several instances of a consumer reading from the same queue, each taking different messages, to scale processing horizontally.

Q: [COMPARISON] RabbitMQ vs Kafka?
A: RabbitMQ is a traditional broker that routes messages to queues and deletes them on acknowledgement, good for task queues. Kafka is a distributed, partitioned log that retains messages and lets consumers replay from offsets, good for high-throughput event streaming.

#### Scenario-based
Q: [DESIGN QUESTION] When an order is placed, inventory, email, loyalty points and analytics must react. Design it.
A: The order service publishes `OrderPlaced` to a topic; each downstream service has its own subscription (queue) and processes events idempotently with retries and its own DLQ. New consumers can subscribe later without touching the order service.

Q: [SCENARIO] One malformed message keeps failing and the consumer is stuck retrying it. What do you do?
A: Configure a maximum retry count with a dead-letter queue, alert on DLQ arrivals, fix the data or code, and replay the message from the DLQ. Also add validation at the producer.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does adding more consumers to a queue preserve message order?
A: Not globally. Parallel consumers can finish out of order. Use FIFO queues with message groups or partition by key when per-entity order matters.
:::

## Session 6.4 — Event-Driven Architecture {: #s6-4 }

### What is an event?

**An event is a record that something has happened**, for example `OrderPlaced`, `PaymentSucceeded`, `StockReserved` or `CustomerAddressChanged`. Events are named in the **past tense** and are **immutable**: you can't un-happen a fact.

| | Event | Command | Query |
|---|---|---|---|
| Meaning | "this happened" | "please do this" | "tell me this" |
| Example | `OrderPlaced` | `ReserveStock` | `GetOrderStatus` |
| Direction | broadcast to anyone interested | sent to one specific handler | sent to one specific handler |
| Can be refused? | no, it already happened | yes | — |
| Sender knows the receivers? | no | yes | yes |

### Event-driven architecture (EDA)

In an **event-driven architecture**, services communicate mainly by **publishing events** to a broker and **reacting** to events from others, instead of calling each other directly.

[[fig:event_driven | Services publish and subscribe to events through a broker instead of calling each other directly.]]

**A worked flow:**

1. The order service saves the order and publishes `OrderPlaced`.
2. The payment service reacts, charges the customer and publishes `PaymentSucceeded` (or `PaymentFailed`).
3. Inventory reserves stock on `PaymentSucceeded` and publishes `StockReserved`.
4. Shipping creates a shipment; notifications send SMS/email at each step; analytics stores every event.
5. No service called another directly; each only knows the events.

### Benefits and challenges

| Benefits | Challenges |
|---|---|
| **Loose coupling:** producers don't know or wait for consumers | **Eventual consistency:** the overall state settles a moment later |
| **Extensibility:** add a new consumer without changing anything else | **Debugging and tracing:** a flow is spread across services (needs correlation IDs and distributed tracing) |
| **Scalability and resilience:** consumers scale independently; the broker buffers outages | **Duplicates and ordering:** idempotent consumers, partition keys |
| **Real-time reactions** to business events | **Schema evolution:** changing an event's format can break consumers (use versioning or a schema registry) |
| **Audit trail:** the event log records what happened | **Hidden complexity:** "who is responsible if step 3 fails?" must be designed explicitly |

### Patterns you may be asked about [INTERVIEW EXTENSION]

| Pattern | Idea | Why it matters |
|---|---|---|
| **Event notification** | the event says "order 9001 placed"; consumers call back for details | small events, but consumers depend on the producer's API |
| **Event-carried state transfer** | the event contains the data consumers need | consumers don't need to call back; more decoupled |
| **Event sourcing** | store the sequence of events as the source of truth; current state = replay of events | full history and audit; more complex queries (often paired with CQRS) |
| **CQRS** | separate the write model (commands) from read models (queries), often fed by events | read models optimised per screen |
| **Choreography vs orchestration** | services react to each other's events (choreography) vs a central coordinator telling each step what to do (orchestration, e.g. AWS Step Functions, Camunda, Temporal) | choreography is decoupled but harder to see; orchestration is visible and controllable |
| **Saga** | a long business transaction split into local transactions, with **compensating actions** if a step fails (refund the payment if stock is unavailable) | there is no global ACID transaction across services |
| **Transactional outbox** | write the event to an `outbox` table in the **same database transaction** as the business change; a relay publishes it to the broker | avoids "DB updated but event lost" (or the reverse) |

::: example A saga with compensation
1. Order service: create order (PENDING) → `OrderCreated`.
2. Payment service: charge → `PaymentSucceeded`.
3. Inventory service: reserve stock fails → `StockUnavailable`.
4. Compensation: the payment service **refunds** → `PaymentRefunded`; the order service marks the order **CANCELLED** and notifies the customer.

Each step is a local ACID transaction; consistency across services comes from the compensating steps.
:::

::: explain
"In an event-driven architecture, services communicate by publishing events, facts like OrderPlaced, to a broker such as Kafka, and other services subscribe and react. The publisher doesn't know who listens, so we can add a new consumer, like a loyalty-points service, without touching the order service. It gives loose coupling, independent scaling and real-time reactions. The trade-offs are eventual consistency, harder end-to-end debugging, and the need for idempotent consumers and versioned event schemas. For multi-step business transactions across services we use sagas with compensating actions, and the outbox pattern to publish events reliably."
:::

::: trap
- Naming events like commands (`SendEmail` is a command; `OrderPlaced` is an event).
- Assuming events arrive exactly once and in order.
- Forgetting failure paths: who compensates when step 3 fails?
- Publishing an event and updating the database as two separate steps, which can leave them inconsistent (use an outbox).
- Using events for everything, including simple queries that need an immediate answer.
:::

::: questions
#### Basic
Q: [DEFINITION] What is an event in EDA?
A: An immutable record of something that happened (named in the past tense, e.g. `OrderPlaced`), published for any interested service to react to.

Q: [DEFINITION] What is event-driven architecture?
A: An architecture where components communicate by producing and consuming events through a broker, instead of direct synchronous calls.

#### Intermediate
Q: [COMPARISON] Event vs command?
A: An event states that something happened and is broadcast to unknown listeners; a command asks a specific receiver to do something and can be rejected.

Q: [WHY] What are the main benefits and challenges of EDA?
A: Benefits: loose coupling, extensibility, scalability, resilience, real-time reactions, an audit trail. Challenges: eventual consistency, tracing and debugging, duplicates and ordering, schema evolution and failure handling.

Q: [DEFINITION] What is a saga?
A: A way to manage a business transaction across services as a sequence of local transactions, with compensating actions that undo earlier steps if a later step fails.

Q: [DEFINITION] What problem does the transactional outbox pattern solve?
A: The dual-write problem: it guarantees the database change and the published event both happen, by writing the event to an outbox table in the same transaction and publishing it afterwards.

#### Scenario-based
Q: [DESIGN QUESTION] Add a fraud-check step to an existing event-driven order flow. What changes?
A: The fraud service subscribes to `OrderPlaced` and publishes `OrderApproved` or `OrderFlagged`; payment listens to `OrderApproved` instead of `OrderPlaced`. Ideally the order service itself is unchanged.

Q: [SCENARIO] Customers sometimes receive two confirmation emails. Why, and how do you fix it?
A: At-least-once delivery or retries caused duplicate processing. Make the notification consumer idempotent: record processed event IDs (or an order-level "email sent" flag) and skip repeats.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can you use a database transaction across microservices in EDA?
A: Not a normal ACID transaction across independently owned databases. Use sagas with compensation, plus idempotency and outbox patterns.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Which pattern delivers each message to exactly one consumer: queue or topic?

**P2.** Classify as event or command: (a) `CancelOrder`, (b) `OrderCancelled`, (c) `GenerateInvoice`, (d) `InvoiceGenerated`.

**P3.** Name the four classic integration styles.

#### Level 2 — Interview application
**P4.** Explain why consumers must be idempotent under at-least-once delivery, with an example.

**P5.** Give two situations where you would choose a synchronous API over a queue, and two for the opposite.

#### Level 3 — Scenario / problem solving
**P6.** Design an event-driven flow for a food-delivery order from "placed" to "delivered", naming the events, the services and one failure scenario with its compensation.

**P7.** Ten internal applications currently integrate point-to-point with nightly scripts. Propose a target architecture and a migration plan in five steps.
:::

::: answers
**P1.** A queue (point-to-point).

**P2.** (a) command, (b) event, (c) command, (d) event.

**P3.** File transfer, shared database, remote procedure invocation (APIs), messaging.

**P4.** With at-least-once delivery, the same message can arrive twice (for example after a consumer crashes before acknowledging). A non-idempotent consumer would add loyalty points twice or ship twice. An idempotent one records processed message IDs (or uses unique constraints) and ignores repeats.

**P5.** Synchronous: checking whether a coupon is valid before showing the final price; authorising a payment before confirming the order. Queue: sending order confirmation emails; syncing new orders to the ERP or warehouse.

**P6.** Events: `OrderPlaced` (order service) → `PaymentAuthorized` (payment) → `RestaurantAccepted` (restaurant service) → `RiderAssigned` (dispatch) → `OrderPickedUp` → `OrderDelivered`; the notification and analytics services subscribe to all of them. Failure: the restaurant rejects or times out (`RestaurantRejected`) → compensation: payment publishes `PaymentReleased` (void or refund), the order is marked CANCELLED, and the customer is notified with an apology coupon. All consumers are idempotent; the order ID is the partition key to keep per-order ordering.

**P7.** Target: an integration platform (iPaaS or ESB) for system APIs, plus an event broker (e.g. Kafka or Service Bus) for business events, with a canonical model, central monitoring and DLQs. Steps: (1) inventory the integrations and rank them by business criticality and failure rate; (2) define canonical schemas and naming for the top entities (Customer, Order, Product); (3) stand up the platform with monitoring, alerting and security; (4) migrate the most critical or most fragile flows first, running old and new in parallel and reconciling outputs; (5) retire scripts one by one, document ownership, and add new integrations only through the platform.
:::
