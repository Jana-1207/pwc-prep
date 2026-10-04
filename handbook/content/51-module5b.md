## Session 5.4 — API Security: Authentication and Authorization {: #s5-4 }

[HIGH PRIORITY] "Authentication vs authorization" and "how does JWT work?" are asked very often.

### Two different questions

- **Authentication (AuthN): "Who are you?"** Proving identity: password, OTP, fingerprint, "Login with Google", an API key, a token.
- **Authorization (AuthZ): "What are you allowed to do?"** Checking permissions *after* identity is known: a customer may view **their own** orders; an admin may delete products.

[[fig:authn_authz | Authentication establishes identity and issues a token; authorization checks what that identity may do.]]

| | Authentication | Authorization |
|---|---|---|
| Question | who are you? | what can you do? |
| Happens | first | after authentication |
| Based on | credentials: password, OTP, keys, certificates, tokens | roles, permissions, policies, ownership |
| Failure status | **401 Unauthorized** (really "unauthenticated") | **403 Forbidden** |
| Example | logging in with email + OTP | only admins can access `/admin/reports` |
| Typical tech | passwords + MFA, OAuth 2.0 / OpenID Connect, JWT | RBAC (roles), ABAC (attributes), OAuth scopes |

::: analogy The office building
Showing your ID card at the reception is **authentication**: they now know who you are. Whether your card opens the server room is **authorization**: it depends on your role.
:::

### Common authentication methods for APIs

| Method | How it works | Good for | Watch out |
|---|---|---|---|
| **API key** | a secret string sent in a header (`X-API-Key: …`) | server-to-server, simple partner APIs, usage tracking | identifies an application, not a user; keep it secret; rotate it |
| **Basic auth** | `Authorization: Basic base64(user:password)` | internal tools, quick tests | base64 is *not* encryption: HTTPS only, avoid in production |
| **Session cookie** | server stores a session; browser sends the session ID cookie | traditional web apps | server-side state; CSRF protection needed |
| **Bearer token (JWT)** | after login the server issues a signed token; the client sends `Authorization: Bearer <token>` | SPAs, mobile apps, microservices | must expire; can't easily revoke before expiry; never put secrets in it |
| **OAuth 2.0 / OpenID Connect** | a trusted authorization server (Google, Azure AD/Entra ID, Okta) issues tokens | "Login with Google", delegated access, enterprise single sign-on | more moving parts; use well-tested libraries |
| **mTLS** [INTERVIEW EXTENSION] | both client and server present certificates | high-security service-to-service traffic (banking) | certificate management |

### How JWT-based authentication works

1. The user logs in (`POST /auth/login` with email + password, or OTP).
2. The server verifies the credentials (passwords are stored as **hashes**, e.g. bcrypt, never as plain text).
3. The server creates a **JWT (JSON Web Token)**, **signs** it with a secret or private key, and returns it.
4. The client stores it and sends it on every request: `Authorization: Bearer <JWT>`.
5. Each API verifies the **signature** and the **expiry**, and reads the user's ID and role from the token, with no database lookup and no server-side session (it is stateless).
6. When the short-lived access token expires (e.g. after 15–60 minutes), the client uses a longer-lived **refresh token** to get a new one.

A JWT has three base64url-encoded parts, `header.payload.signature`. Decoded:

```json
{ "alg": "HS256", "typ": "JWT" }
```

```json
{ "sub": "42", "name": "Isha Kulkarni", "role": "customer", "iat": 1713550000, "exp": 1713553600 }
```

- **Header:** the signing algorithm.
- **Payload (claims):** who the user is (`sub`), their role, issue time (`iat`) and expiry (`exp`).
- **Signature:** proves the token was issued by the server and not modified. Change one character of the payload and verification fails.

::: trap A JWT is signed, not encrypted
Anyone can base64-decode a JWT and read its payload. Never put passwords, card numbers or other secrets in it. The signature only guarantees **integrity** (no tampering), not **confidentiality**.
:::

### OAuth 2.0 in plain words

**OAuth 2.0 is a delegation framework:** it lets an application access resources **on a user's behalf** without ever seeing the user's password. "Allow this app to read your Google Calendar."

| Role | In "Login with Google" |
|---|---|
| Resource owner | you, the user |
| Client | the app you are logging into |
| Authorization server | Google's login/consent service, which issues tokens |
| Resource server | the API holding your data (e.g. Google Calendar API) |

The common **authorization code flow**: the app redirects you to Google → you log in and consent → Google redirects back with a short-lived **code** → the app's backend exchanges the code for an **access token** (and maybe a refresh token) → the app calls APIs with that token. **OpenID Connect (OIDC)** adds an **ID token** on top of OAuth 2.0 so the app also learns *who* you are, which is what "Login with Google" actually uses.

### Authorization models

- **RBAC (Role-Based Access Control):** permissions are attached to roles (customer, support agent, admin), and users get roles. Simple and common.
- **ABAC (Attribute-Based Access Control):** decisions use attributes: "a manager may approve expenses **in their own department** under ₹50,000".
- **Ownership checks:** a customer may `GET /orders/9001` **only if order 9001 belongs to them**. Forgetting this is one of the most common API vulnerabilities (broken object-level authorization).
- **OAuth scopes:** what a token may do (`orders:read`, `orders:write`).
- Always follow **least privilege**.

### Essential API security practices

| Practice | Why |
|---|---|
| HTTPS everywhere | tokens and data are encrypted in transit |
| Hash passwords with a slow algorithm (bcrypt, Argon2) | a stolen database doesn't reveal passwords |
| Short-lived access tokens + refresh tokens | limits the damage of a stolen token |
| Validate every input; use **parameterized queries** | prevents SQL injection and bad data |
| Check authorization on every request, including object ownership | prevents users reading other users' data |
| Rate limiting and lockouts on login | slows brute-force attacks |
| Don't leak details in errors; log centrally | attackers learn less; you can investigate |
| Configure CORS carefully | only trusted browser origins can call the API from JavaScript |

### SQL injection: why parameterized queries matter

If an API builds SQL by pasting user input into a string, a malicious input becomes part of the SQL itself. Suppose the code is:

```python
# DANGEROUS: user input pasted into SQL
query = f"SELECT * FROM customers WHERE email = '{email_from_user}'"
```

If an attacker sends the email `' OR '1'='1`, the database receives this query and returns **every customer**:

```sql run
SELECT customer_id, customer_name, email
FROM customers
WHERE email = '' OR '1'='1';
```

The fix is a **parameterized query**, where the driver sends the value separately from the SQL text, so it can never change the query's structure:

```python
# SAFE: the value is passed as a parameter, not as SQL text
cur.execute("SELECT * FROM customers WHERE email = %s", (email_from_user,))
```

ORMs (JPA/Hibernate, Django ORM) parameterize automatically, unless you concatenate strings into native queries yourself.

::: explain
"Authentication is proving who you are, for example logging in with a password and OTP; authorization is deciding what you're allowed to do once we know who you are, like only admins deleting products. If authentication fails the API returns 401; if the user is known but not allowed, it returns 403. A common setup is token-based: after login the server issues a signed JWT with the user ID, role and an expiry, and the client sends it as a Bearer token on every request. The API verifies the signature and expiry and then checks roles and ownership. For third-party login we use OAuth 2.0 with OpenID Connect, so the app never sees the user's Google password."
:::

::: trap
- Mixing up authentication and authorization, or 401 and 403.
- "JWTs are encrypted." They are signed; the payload is readable.
- Long-lived tokens with no expiry or rotation.
- Checking the role but not **ownership** (any customer can read `/orders/{anyId}`).
- Basic auth or tokens over plain HTTP.
- Building SQL with string concatenation.
:::

::: questions
#### Basic
Q: [COMPARISON] Authentication vs authorization?
A: Authentication verifies identity (who you are); authorization determines permissions (what you can do). Authentication comes first.

Q: [DEFINITION] What is an API key?
A: A secret identifier sent with requests (usually in a header) that identifies the calling application, used for simple access control, quotas and tracking.

Q: [DEFINITION] What is a JWT?
A: A JSON Web Token: a compact, signed token (`header.payload.signature`) carrying claims such as user ID, role and expiry, used for stateless authentication.

#### Intermediate
Q: [HOW] How does token-based authentication work?
A: The user logs in; the server verifies the credentials and issues a signed, expiring token; the client sends it in the Authorization header; each API verifies the signature and expiry and reads the identity and roles from it.

Q: [DEFINITION] What is OAuth 2.0?
A: An authorization framework that lets a client app obtain limited access tokens to a user's resources from an authorization server, without handling the user's password. OpenID Connect adds identity (ID tokens) on top.

Q: [COMPARISON] Session-based vs token-based authentication?
A: Sessions store state on the server and send a session ID cookie (easy to revoke, needs shared storage to scale); tokens are self-contained and stateless (scale easily, but harder to revoke, so they must be short-lived).

Q: [COMPARISON] RBAC vs ABAC?
A: RBAC grants permissions through roles; ABAC evaluates policies on attributes of the user, the resource and the context (department, amount, time), which is more fine-grained.

Q: [DEFINITION] What is SQL injection and how do you prevent it?
A: An attack where input is interpreted as SQL because it was concatenated into a query. Prevent it with parameterized queries or prepared statements (or an ORM), input validation and least-privilege database accounts.

#### Scenario-based
Q: [SCENARIO] A customer can view another customer's order by changing the ID in the URL. What's wrong and how do you fix it?
A: Broken object-level authorization: the API authenticates the user but doesn't check ownership. On every request, verify the order's `customer_id` matches the token's user (or that the user has an admin role) and return 403/404 otherwise.

Q: [DESIGN QUESTION] How would you secure an internal reporting API used by a BI tool?
A: HTTPS; a service account with an API key or OAuth client-credentials token; least-privilege read-only scope; network restrictions (private network, IP allow-list); rate limiting; audit logging; read from a replica or the warehouse rather than OLTP.

#### Follow-up / Trap
Q: [TRAP QUESTION] Why is 401 named "Unauthorized" if it's about authentication?
A: A historical naming quirk in the HTTP specification. In practice 401 means "not authenticated", and 403 means "authenticated but not authorized".

Q: [TRAP QUESTION] How do you log out a user with a stateless JWT?
A: You can't truly invalidate it before expiry without state. Use short expiry plus refresh-token revocation, or keep a deny-list of token IDs (jti) until they expire.
:::

## Session 5.5 — API Integration and Reliability {: #s5-5 }

### Integrating with external APIs

Real applications constantly call **third-party APIs**: payment gateways, SMS/email providers, maps, KYC/identity verification, GST validation, shipping partners, CRM systems. An integration usually involves:

1. **Reading the documentation and contract** (endpoints, auth, limits, error codes, sandbox).
2. **Authenticating** (API key or OAuth client credentials), keeping secrets in a vault or environment config, never in code.
3. **Mapping data** between your model and theirs (field names, formats, currencies, time zones).
4. **Handling failure**: the network *will* fail, the provider *will* be slow sometimes.
5. **Monitoring**: logs, metrics, alerts on error rates and latency.

### Synchronous vs asynchronous communication

[[fig:sync_vs_async | Synchronous calls block the caller until the reply arrives; asynchronous messages let the caller continue immediately.]]

| | Synchronous | Asynchronous |
|---|---|---|
| How | the caller sends a request and **waits** for the response | the caller sends a message or event and **continues**; the result arrives later (callback, webhook, polling, event) |
| Example | checkout calls the payment API and waits for approve/decline | after the order, send the confirmation email through a queue |
| Pros | simple, immediate result, easy to reason about | resilient (survives the other side being down), absorbs spikes, scales |
| Cons | caller is slowed or broken by a slow or failing dependency; tight coupling | eventual results, harder debugging, needs queues and duplicate handling |
| Use when | the user needs the answer **now** to continue | the work can happen later, or takes long (reports, emails, video processing) |

A common hybrid: the API accepts a long job and returns **202 Accepted** with a job URL (`/jobs/77`); the client polls it or receives a webhook when the job is done.

### Webhooks vs polling

[[fig:webhook_vs_polling | Polling repeatedly asks "is it done?"; a webhook lets the provider call you when it is.]]

- **Polling:** the client asks repeatedly ("is payment done?"). Simple, but wasteful and delayed.
- **Webhook:** you register a URL once; the provider sends an HTTP POST to it when an event happens ("payment.captured").

**Webhook receivers must:** verify the provider's **signature** (so attackers can't fake events); respond **2xx quickly** and do heavy work asynchronously; be **idempotent**, because providers retry and duplicates happen; and handle events arriving **out of order**.

### When APIs fail

| Failure | Example | Response |
|---|---|---|
| Timeout | the provider takes 40 seconds | always set connect and read timeouts; fail fast |
| Network error | connection reset, DNS failure | retry (if safe) with backoff |
| 5xx | 500, 502, 503, 504 | retry with backoff; it may be temporary |
| 429 | rate limited | wait for `Retry-After`, then retry; reduce the request rate |
| 4xx (other) | 400, 401, 403, 404, 422 | **do not retry blindly**: fix the request, credentials or data |
| Partial failure | payment succeeded but our DB write failed | idempotency, reconciliation jobs, status tracking |

### Retries with exponential backoff and jitter

[[fig:retry_backoff | Retry after 1 s, 2 s, 4 s… with a little randomness (jitter), and give up after a few attempts.]]

- **Exponential backoff:** wait 1 s, 2 s, 4 s, 8 s between attempts, so a struggling service gets room to recover.
- **Jitter:** add randomness so thousands of clients don't all retry at the same instant (the "thundering herd").
- **Limit** the attempts, then fail gracefully (show a message, queue for later, alert).
- **Only retry operations that are safe to repeat**: idempotent requests, or POSTs protected by an idempotency key.

```python
import random
import time

import requests


def call_with_retry(url, payload, idempotency_key, max_attempts=4):
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.post(url, json=payload, timeout=5,
                                 headers={"Idempotency-Key": idempotency_key})
            if resp.status_code < 500 and resp.status_code != 429:
                return resp                          # success or a client error: don't retry
        except requests.exceptions.RequestException:
            pass                                     # network problem or timeout: retry
        if attempt == max_attempts:
            raise RuntimeError("payment service unavailable, try later")
        time.sleep(2 ** (attempt - 1) + random.uniform(0, 0.5))   # 1s, 2s, 4s + jitter
```

::: linebyline
| Line | What it does |
|---|---|
| `for attempt in range(1, max_attempts + 1)` | try at most 4 times |
| `headers={"Idempotency-Key": …}` | the same key on every attempt, so the server can detect repeats |
| `timeout=5` | never wait more than 5 seconds for one attempt |
| `if resp.status_code < 500 and resp.status_code != 429: return resp` | success (2xx) or a client error (4xx): retrying won't help, so return |
| `except requests.exceptions.RequestException` | timeouts and connection errors are worth retrying |
| `time.sleep(2 ** (attempt - 1) + random.uniform(0, 0.5))` | exponential backoff plus jitter |
:::

### Idempotency and idempotency keys

**Idempotency:** performing an operation several times has the same effect as performing it once (Session 5.2). It is the safety net that makes retries harmless.

The danger case: you send `POST /payments` to charge ₹500, the payment succeeds, but the **response is lost** (timeout). Did it work? Retrying blindly could charge the customer twice.

The solution is an **idempotency key**: a unique ID (e.g. a UUID) the client generates per logical operation and sends with every retry. The server stores the key with the result; when the same key arrives again, it **returns the stored result instead of charging again**. Stripe, Razorpay and many payment APIs use exactly this design.

[[fig:idempotency_flow | The response is lost, the client retries with the same key, and the server returns the saved result: the customer is charged once.]]

On the database side, the same idea is enforced with a unique constraint, e.g. `UNIQUE (idempotency_key)` on a payments table, plus `INSERT … ON CONFLICT DO NOTHING` (Session 3.4).

### Circuit breakers and fallbacks [INTERVIEW EXTENSION]

A **circuit breaker** stops calling a dependency that keeps failing: after N failures it "opens" and fails fast for a cool-down period, then lets a few test requests through. This protects your threads and the struggling service. Combine it with **fallbacks** (cached data, a default response, or "we'll notify you") and **bulkheads** (separate thread pools per dependency).

::: project In a real project
"In our order service, the call to the payment gateway has a 5-second timeout and up to three retries with exponential backoff, always sending the same idempotency key, which we also store with a unique constraint. Confirmation emails go through a queue, so a slow email provider never blocks checkout. Webhooks from the gateway are signature-verified and processed idempotently, and a nightly reconciliation job compares our payments table with the gateway's settlement report."
:::

::: explain
"When integrating with an external API I assume it will sometimes be slow or fail. I set timeouts, retry only on transient errors like timeouts, 5xx or 429, using exponential backoff with jitter and a retry limit, and I never retry blindly on other 4xx errors. Retries are only safe if the operation is idempotent, so for POST requests like payments we send an idempotency key; if the response is lost and we retry, the server returns the original result instead of charging twice. For work that doesn't need an immediate answer, like emails, I prefer asynchronous messaging or webhooks over synchronous calls."
:::

::: trap
- No timeout: one slow provider hangs every request thread.
- Retrying non-idempotent POSTs without an idempotency key leads to duplicate payments and orders.
- Retrying 400/401/403/422 errors, which will never succeed.
- Immediate, synchronized retries that create a thundering herd.
- Webhook handlers that aren't idempotent or don't verify signatures.
- Calling an external API while holding a database transaction open.
:::

::: questions
#### Basic
Q: [COMPARISON] Synchronous vs asynchronous communication?
A: Synchronous: the caller waits for the response before continuing (simple, immediate, but coupled). Asynchronous: the caller sends a message and continues; the result comes later (resilient and scalable, but eventual).

Q: [DEFINITION] What is a webhook?
A: An HTTP callback: you register a URL, and the provider sends a POST request to it when an event happens.

Q: [DEFINITION] What is exponential backoff?
A: A retry strategy where the wait doubles after each failure (1 s, 2 s, 4 s…), usually with random jitter and a maximum number of attempts.

#### Intermediate
Q: [DEFINITION] What is an idempotency key?
A: A unique client-generated ID sent with a non-idempotent request (like a payment POST); the server stores the result per key and returns the same result for repeats, so retries don't duplicate the operation.

Q: [HOW] Which failures should you retry?
A: Timeouts, network errors, 5xx (especially 502, 503, 504) and 429 (after `Retry-After`). Not 400, 401, 403, 404 or 422; those need a fix, not a retry.

Q: [COMPARISON] Webhooks vs polling?
A: Polling repeatedly asks for status (simple but wasteful and delayed); webhooks push events when they happen (efficient, near real-time, but you must secure and idempotently process them).

Q: [DEFINITION] What is a circuit breaker?
A: A pattern that stops calls to a failing dependency after repeated errors and fails fast for a while, periodically testing whether it has recovered.

#### Scenario-based
Q: [SCENARIO] The payment API times out. The customer clicks "Pay" again. How do you avoid charging twice?
A: Use one idempotency key per checkout attempt, reused on retries, and a unique constraint on it in the payments table. Check the payment's status with the provider (or wait for its webhook) before creating a new charge, and show "payment pending" instead of encouraging a retry.

Q: [DESIGN QUESTION] An order confirmation must send an email and an SMS. Should checkout call these APIs synchronously?
A: No. Publish an `OrderPlaced` event or enqueue jobs; notification workers send email and SMS with retries. Checkout stays fast and works even if the SMS provider is down.

Q: [SCENARIO] Your webhook endpoint receives the same "payment.captured" event three times. Is something broken?
A: Not necessarily; providers retry until they get a 2xx and may send duplicates. Store processed event IDs and ignore repeats (idempotent processing), and return 2xx quickly.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is it safe to retry a PUT request?
A: Yes in principle, since PUT is idempotent (the same full update applied twice gives the same state). PATCH and POST need more care.

Q: [TRAP QUESTION] Why add jitter to backoff?
A: Without randomness, many clients that failed together retry at the same moments and overload the recovering service again.
:::

## Session 5.6 — Data Integration {: #s5-6 }

### Simple meaning, revisited

**Data integration is combining data from different sources into a unified, consistent and usable form**, either to keep operational systems in sync (CRM ↔ order system) or to feed analytics (everything → warehouse). Session 1.2 introduced *why*; this session covers *how*.

[[fig:data_integration_overview | Many sources, one integration layer (APIs, ETL/ELT, CDC, messaging) and many targets.]]

### Integration approaches

| Approach | How it works | Latency | Typical use |
|---|---|---|---|
| **API-based** | systems call each other's REST/SOAP APIs | real time | create a customer in the CRM when they sign up |
| **File-based** | exports such as CSV, Excel or XML, exchanged via SFTP or cloud storage | hours (batch) | bank statements, partner catalogues, legacy systems |
| **ETL / ELT** | scheduled jobs extract, transform and load data into a target | minutes to hours | loading the warehouse every night (Module 6) |
| **CDC (Change Data Capture)** | read the source database's change log and stream every insert, update and delete | seconds | keeping a warehouse, search index or cache in sync |
| **Messaging / events** | systems publish events to a broker; others subscribe | near real time | `OrderPlaced` → inventory, email, analytics |
| **Data virtualization** [INTERVIEW EXTENSION] | query sources in place through a virtual layer, without copying | query time | quick unified views; limited by source performance |

[[fig:cdc_flow | Change Data Capture reads the database's transaction log and streams each change to other systems.]]

**Why CDC is popular:** it captures *every* change, including deletes, in near real time, without adding load from frequent polling queries or requiring an `updated_at` column. Tools: Debezium, AWS DMS, Fivetran, Oracle GoldenGate, SQL Server CDC.

### Full vs incremental loads

- **Full load:** copy everything every time. Simple, but slow and expensive as data grows.
- **Incremental load:** copy only what changed since the last run, using a **watermark** (the highest `updated_at` or ID already loaded) or CDC.

```sql run
-- incremental extract: the previous load finished with orders up to 31 March
SELECT order_id, order_date, status, total_amount
FROM orders
WHERE order_date > DATE '2024-03-31'
ORDER BY order_date, order_id;
```

In real systems the watermark is usually an `updated_at` timestamp rather than the order date, so that *changes* to old orders (a status moving to DELIVERED) are picked up too. Loading uses **upserts** (`INSERT … ON CONFLICT DO UPDATE` or `MERGE`) so re-running a load never creates duplicates: the load is **idempotent**.

### Data formats you will meet

| Format | Shape | Strengths | Weaknesses |
|---|---|---|---|
| CSV | rows of text values | universal, human-readable | no types, quoting and encoding issues, no nesting |
| JSON | nested key-value | APIs, flexible, readable | verbose; types limited; no schema by default |
| XML | nested tags | strict schemas (XSD), common in enterprise and banking | verbose, heavier to parse |
| Parquet | columnar, binary | compressed, fast analytics, schema included | not human-readable; for batch analytics |
| Avro | row-based, binary, schema | streaming (Kafka), schema evolution | not human-readable |

### Data mapping and transformation

Integration projects are built on a **source-to-target mapping** document. For example, CRM contacts to the warehouse customer dimension:

| Source (CRM) | Target (dim_customer) | Rule |
|---|---|---|
| `Contact.Id` | `crm_id` | copy as is |
| `FirstName` + `LastName` | `customer_name` | concatenate with a space, trim, Title Case |
| `Email` | `email` | lower-case, trim; reject if invalid format |
| `MailingCity` | `city` | map variants (`Bombay` → `Mumbai`); unknown → 'Unknown' |
| `CreatedDate` (UTC) | `signup_date` | convert to IST date |
| `IsDeleted` | (filter) | exclude deleted contacts |

### Matching records across systems

The same customer appears in the shop database and in the CRM with slightly different data. Matching on a normalized key (here, lower-cased email) shows what matches and what exists on only one side, using the FULL OUTER JOIN from Session 3.6:

```sql run
WITH crm_contacts (crm_id, contact_name, email) AS (
    VALUES ('C-01', 'Aarav Patel', 'AARAV@MAIL.COM'),
           ('C-02', 'Isha K.',     'isha@mail.com'),
           ('C-03', 'Rohit Sinha', 'rohit@mail.com')
)
SELECT c.customer_id, c.customer_name, k.crm_id, k.contact_name,
       CASE WHEN c.customer_id IS NULL THEN 'only in CRM'
            WHEN k.crm_id IS NULL      THEN 'only in shop'
            ELSE 'matched' END AS match_status
FROM customers c
FULL OUTER JOIN crm_contacts k ON LOWER(c.email) = LOWER(k.email)
ORDER BY match_status, c.customer_id;
```

::: linebyline
| Part | What it does |
|---|---|
| `WITH crm_contacts (…) AS (VALUES …)` | a small inline table standing in for the CRM extract |
| `FULL OUTER JOIN … ON LOWER(c.email) = LOWER(k.email)` | match on normalized email; keep unmatched rows from both sides |
| `CASE …` | label each row: matched, only in the shop, or only in the CRM |
:::

Aarav matched despite the upper-case email, thanks to normalization. Rohit exists only in the CRM, and five shop customers have no CRM record. The output of such a query drives decisions: create the missing records, review near-matches, or build a **golden record**.

::: extension Master Data Management (MDM)
**MDM** creates a single trusted "golden record" for key entities (customer, product, supplier) across systems, using matching rules (exact and fuzzy), survivorship rules (which source wins for each field), and stewardship (people who resolve conflicts).
:::

### Data quality: trust is the product

| Dimension | Question | Example check |
|---|---|---|
| Completeness | is required data present? | customers with no email |
| Uniqueness | are there duplicates? | the same email several times |
| Validity | does data follow the rules and formats? | status in the allowed list; email pattern |
| Consistency | do related values agree? | order total = sum of its lines |
| Accuracy | does it reflect reality? | the address actually exists |
| Timeliness | is it fresh enough? | latest order date vs today |

Checks like these can run as SQL after every load. One query can produce a small quality report:

```sql run
SELECT 'customers: missing email'           AS check_name, COUNT(*) AS failures
FROM customers WHERE email IS NULL
UNION ALL
SELECT 'leads: duplicate emails', COUNT(*) - COUNT(DISTINCT LOWER(email))
FROM leads
UNION ALL
SELECT 'orders: total does not match lines', COUNT(*)
FROM orders o
WHERE o.total_amount <> (SELECT SUM(i.quantity * i.unit_price)
                         FROM order_items i WHERE i.order_id = o.order_id)
UNION ALL
SELECT 'employees: no department', COUNT(*)
FROM employees WHERE dept_id IS NULL
UNION ALL
SELECT 'orders: dated after 2024-12-31', COUNT(*)
FROM orders WHERE order_date > DATE '2024-12-31';
```

Non-zero failures become alerts or tickets. Tools such as dbt tests and Great Expectations automate exactly this.

::: explain
"Data integration is bringing data from different systems together consistently. Depending on how fresh it needs to be, I'd use APIs for real-time system-to-system calls, file transfers for simple batch exchanges, ETL or ELT jobs for loading a warehouse, change data capture to stream database changes with low latency, or events through a message broker. The real work is in mapping and transforming fields, matching records across systems, for example on a normalized email, loading incrementally with upserts so re-runs are safe, and checking data quality: completeness, uniqueness, validity and consistency."
:::

::: trap
- Full reloads forever: they get slower and costlier as data grows.
- Incremental loads based on creation date only, missing updates (use `updated_at` or CDC).
- Non-idempotent loads that duplicate data when a job is re-run.
- Matching records on raw values without normalizing case, spaces and formats.
- Treating data quality as a one-time cleanup instead of continuous checks.
:::

::: questions
#### Basic
Q: [DEFINITION] What is Change Data Capture (CDC)?
A: A technique that captures inserts, updates and deletes from a source database, usually by reading its transaction log, and streams them to other systems in near real time.

Q: [COMPARISON] Full load vs incremental load?
A: A full load copies all data every run; an incremental load copies only new or changed data since the last run, using a watermark or CDC.

Q: [DEFINITION] Name four data quality dimensions.
A: Completeness, uniqueness, validity, consistency (also accuracy and timeliness).

#### Intermediate
Q: [WHY] Why prefer CDC over querying `updated_at` regularly?
A: CDC captures deletes and every intermediate change, adds little load to the source, has low latency and doesn't depend on applications maintaining `updated_at` correctly.

Q: [DEFINITION] What is a source-to-target mapping?
A: A document listing each target field, its source field(s) and the transformation rule (format, lookup, default, filter), which guides building and testing integrations.

Q: [HOW] How do you make a data load idempotent?
A: Use upserts or MERGE keyed on a business key, or delete-and-reload a partition (e.g. one day) inside a transaction, so re-running produces the same result without duplicates.

#### Scenario-based
Q: [SCENARIO] How would you integrate CRM customer data with the e-commerce order system?
A: Agree on the master system and a matching key (normalized email or a shared customer ID); sync new and updated customers by API or CDC; map fields (names, cities, time zones); match and de-duplicate; load with upserts; add quality checks and a reconciliation report; and for analytics, land both in the warehouse and build a unified customer dimension.

Q: [SCENARIO] A nightly load failed halfway. How do you recover without duplicates?
A: Design loads to be idempotent (upserts, or replace by date partition in one transaction), keep the watermark updated only after success, then simply re-run the job for the failed window.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is real-time integration always the goal?
A: No. Pick the latency the business needs; batch is simpler and cheaper and is perfectly fine for many reports.

Q: [TRAP QUESTION] Two systems both have `customer_id = 105`. Is it the same customer?
A: Not necessarily: IDs are local to each system. Use a shared key or a cross-reference (mapping) table.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Name five ways to move data between systems.

**P2.** Which HTTP status should an API return when a user is logged in but lacks permission?

**P3.** What are the three parts of a JWT?

#### Level 2 — Interview application
**P4.** Explain idempotency keys to a non-technical manager using the "double payment" example.

**P5.** Write a SQL check that returns how many leads have an email that is not lower-case.

#### Level 3 — Scenario / problem solving
**P6.** Design the integration between a hospital's lab system and its doctor app so results appear within a minute, survive outages and never duplicate.

**P7.** A partner sends a daily CSV of 2 million product prices. Describe a robust load process, from file arrival to the updated product table.
:::

::: answers
**P1.** API calls, file transfer, ETL/ELT pipelines, CDC/replication, and messaging/events (data virtualization is a sixth).

**P2.** 403 Forbidden.

**P3.** Header (algorithm), payload (claims such as user ID, role, expiry) and signature, separated by dots and base64url-encoded.

**P4.** "If our payment request times out, we don't know whether the customer was charged. So every payment attempt carries a unique reference number. If we have to resend the request, we send the same number, and the payment provider recognises it and replies 'already done', instead of charging again."

**P5.**

```sql run
SELECT COUNT(*) AS not_lowercase
FROM leads
WHERE email <> LOWER(email);
```

All sample emails are already lower-case, so the check passes with 0.

**P6.** The lab system publishes a `ResultReady` event (or CDC captures new result rows) to a durable message broker. A consumer service transforms the result to the app's format and upserts it into the app database keyed by `result_id` (idempotent, so duplicates are harmless), then notifies the doctor. If the app database is down, messages wait in the queue and are retried; repeated failures go to a dead-letter queue with alerts. Latency is seconds, which meets the one-minute target.

**P7.** (1) The file lands in a raw storage area; record its arrival. (2) Validate: header, row count, required fields, number formats; quarantine bad rows. (3) Bulk-load it into a staging table (PostgreSQL `COPY`). (4) Transform: trim, cast, map product codes. (5) `INSERT … ON CONFLICT (product_code) DO UPDATE` into the product table, ideally only for changed prices. (6) Run quality checks (e.g. price > 0, no unexpected 50% swings) and a reconciliation of counts. (7) Commit, archive the file and log the run. Re-running the same file gives the same result, so the process is idempotent.
:::

## Session 5.7 — Module 5 Summary & Rapid Revision {: #s5-7 }

::: summary Module 5 Summary
#### Most important concepts
- **API** = a contract between systems; **client–server**: clients request, servers process and respond; REST servers are stateless.
- **HTTP**: method + URL + headers + body → status + headers + body; HTTPS = HTTP over TLS.
- **Methods**: GET (read), POST (create, not idempotent), PUT (replace, idempotent), PATCH (partial), DELETE (idempotent).
- **Status codes**: 200, 201, 204 · 400, 401, 403, 404, 409, 422, 429 · 500, 502, 503, 504.
- **REST**: resources as nouns, uniform interface, statelessness, JSON, proper status codes; plus pagination, filtering, versioning, rate limiting and consistent errors.
- **AuthN vs AuthZ**: who you are vs what you may do; API keys, sessions, JWT, OAuth 2.0 / OIDC; RBAC/ABAC; ownership checks; parameterized queries against SQL injection.
- **Reliability**: timeouts, retries with exponential backoff + jitter, idempotency keys, webhooks, circuit breakers; sync vs async.
- **Data integration**: API, file, ETL/ELT, CDC, events; incremental loads with watermarks; mapping; record matching; data quality.

#### What to memorize
- PUT vs PATCH; 401 vs 403; which methods are idempotent.
- The key status codes and when to use each.
- JWT = header.payload.signature (signed, not encrypted).

#### What to understand
- The end-to-end flow of `GET /users`.
- Why retries require idempotency.
- When to choose synchronous vs asynchronous integration.

#### Most common interview questions
- What is REST? · PUT vs PATCH? · 401 vs 403? · Path vs query parameters? · Is POST idempotent? · How does JWT authentication work? · What is OAuth? · How do you handle API failures? · What is CDC?

#### Common mistakes
- 200 for errors · verbs in URLs · no timeouts · retrying 4xx · retrying POST without a key · JWT treated as encrypted · missing ownership checks · string-built SQL.
:::

::: checklist
- [ ] I can define an API and explain client–server
- [ ] I can describe the parts of an HTTP request and response
- [ ] I can explain path vs query parameters
- [ ] I know each HTTP method, and whether it is safe and idempotent
- [ ] I can explain PUT vs PATCH with an example
- [ ] I know the important status codes (including 401 vs 403)
- [ ] I can explain REST principles and good resource naming
- [ ] I can walk through GET /users end to end
- [ ] I can explain pagination, versioning and rate limiting
- [ ] I can explain authentication vs authorization
- [ ] I can explain how JWT and OAuth 2.0 work
- [ ] I can explain and prevent SQL injection
- [ ] I can compare synchronous and asynchronous communication
- [ ] I can explain retries, backoff, jitter and idempotency keys
- [ ] I can compare webhooks and polling
- [ ] I can list data integration approaches and explain CDC
- [ ] I can design an incremental, idempotent load
- [ ] I can name the data quality dimensions
:::
