# Data Integration & APIs {: .part #m5 data-label="PART V · MODULE 5" }

<p class="lead">Systems are useful only when they can talk to each other. This module explains APIs from first principles: client–server, HTTP, REST, JSON, status codes, authentication and authorization, then how to integrate with external APIs reliably (timeouts, retries, idempotency, webhooks) and how data integration works across a company.</p>

::: coverage
- What is an API, why APIs exist, client-server architecture, request/response † → Session 5.1
- REST, HTTP, GET, POST, PUT, PATCH, DELETE, HTTP status codes, JSON † → Session 5.2
- REST API example; pagination, rate limiting, API versioning † → Session 5.3
- Authentication and authorization † → Session 5.4
- API integration, external APIs, synchronous vs asynchronous communication, API failures, retries, idempotency † → Session 5.5
- Data integration † → Session 5.6
- Module quiz concepts → interview questions in each session and Session 5.7
:::

| Topic | Priority | Typical question |
|---|---|---|
| HTTP methods, PUT vs PATCH, idempotency | [HIGH PRIORITY] | "Difference between PUT and PATCH?" "Is POST idempotent?" |
| Status codes, 401 vs 403 | [HIGH PRIORITY] | "What does 201 / 204 / 404 / 409 / 429 mean?" |
| REST principles, request flow | [HIGH PRIORITY] | "Explain what happens when the frontend calls GET /users." |
| Authentication vs authorization, JWT, OAuth | [HIGH PRIORITY] | "How does token-based authentication work?" |
| Retries, timeouts, idempotency keys, webhooks | [MEDIUM PRIORITY] | "A payment API times out. What do you do?" |
| Data integration methods, CDC, data quality | [MEDIUM PRIORITY] | "How would you integrate CRM data with the order system?" |

::: pwc PwC angle
Reports from PwC software interviews mention HTTP status codes, HTTP methods, query vs path parameters, PUT vs PATCH, idempotency and REST (see the PwC Interview Orientation chapter). Integration is also everyday consulting work: connecting a client's ERP, CRM and web channels is a classic engagement. Be ready to explain both the protocol details and the business reason for an integration.
:::

## Session 5.1 — What Is an API? Client–Server and Request/Response {: #s5-1 }

### Simple meaning

**An API (Application Programming Interface) is a contract that lets one piece of software ask another for data or an action, without knowing how the other side works inside.** The contract says which requests you may send, in what format, and what responses you will get back.

::: analogy The waiter and the menu
In a restaurant you don't walk into the kitchen. You read the **menu** (the API documentation), tell the **waiter** (the API) what you want, and the waiter brings back your **food** (the response). The kitchen can change its staff and equipment, but as long as the menu stays the same, customers are unaffected.
:::

### Why APIs exist

| Reason | Example |
|---|---|
| **Abstraction:** hide complexity | a payment API hides card networks, banks, fraud checks |
| **Reuse:** build once, use everywhere | the same order API serves the website, the Android app and the iPhone app |
| **Security:** controlled access instead of direct database access | clients call `GET /orders/9001`; they never see database credentials |
| **Decoupling:** teams change internals independently | the order service can switch databases without breaking the app |
| **Integration:** connect with partners and third parties | a food app calls a maps API for routes and an SMS API for OTPs |
| **Business:** expose capabilities as products | public APIs for weather, payments, KYC/identity verification |

### Kinds of APIs

- **Web APIs** over HTTP, the main topic here: **REST** (most common), **SOAP** (XML, common in older enterprise and banking systems), **GraphQL** (the client asks for exactly the fields it needs) and **gRPC** (fast, binary, service-to-service).
- **Library/SDK APIs:** the functions a library exposes, like Java's `List` interface or a payment SDK.
- **By audience:** **private** (internal, between your own services), **partner** (shared with selected companies) and **public** (anyone with a key).

### Client–server architecture

[[fig:client_server | Clients send requests to a server; the server does the work, talks to the database and returns responses.]]

- The **client** (browser, mobile app or another server) **starts** the conversation and asks for something.
- The **server** **waits** for requests, applies business logic and security, talks to the database, and responds.
- Many clients share one server, and the server is the only component allowed to touch the database.
- REST servers are usually **stateless**: each request carries everything needed to process it (for example the auth token), so any server instance can handle any request, which makes scaling easy.

### The request/response cycle

1. The client builds a **request**: an HTTP **method** (GET, POST…), a **URL**, **headers** (metadata such as the auth token and content type) and optionally a **body** (data, usually JSON).
2. The request travels over the network (HTTPS) to the server.
3. The server **authenticates** the caller, **validates** the input, runs the **business logic** and reads or writes the **database**.
4. The server returns a **response**: a **status code** (200, 404…), **headers** and a **body** (usually JSON).
5. The client reads the status first, then uses the body (show the data, or show an error).

::: example Everyday example: paying with a UPI app
You tap "Pay ₹500". The app (client) sends an API request to its backend; the backend calls the payment network's APIs; the bank's systems debit your account; each hop replies with a status; finally your app shows "Payment successful". Every arrow in that chain is an API call with a request and a response.
:::

::: explain
"An API is a contract that lets one system request data or actions from another without knowing its internals, like a waiter taking your order to the kitchen. In client–server architecture, the client, say a mobile app, sends an HTTP request with a method, URL, headers and maybe a JSON body; the server authenticates and validates it, runs the business logic, talks to the database, and sends back a response with a status code and usually a JSON body. APIs give us reuse, security, decoupling and integration: one backend can serve the website, the mobile apps and partner systems."
:::

::: trap
- Saying "an API is a URL". A URL identifies a resource; the API is the whole contract (operations, formats, rules).
- Thinking clients can or should connect to the database directly.
- Thinking "REST" and "API" mean the same thing. REST is one style of web API.
:::

::: questions
#### Basic
Q: [DEFINITION] What is an API?
A: An Application Programming Interface: a defined contract for how software components request data or actions from each other, for example over HTTP with JSON.

Q: [DEFINITION] What is client–server architecture?
A: A model where clients send requests and servers process them and return responses; the server centralises business logic, security and data access.

Q: [WHY] Why do we need APIs?
A: To expose functionality safely and reusably, decouple systems so they can change independently, and integrate with other applications and partners.

#### Intermediate
Q: [DEFINITION] What does "stateless" mean for a REST server?
A: The server keeps no client session between requests; each request contains all the information needed (such as the auth token), so any server instance can handle it.

Q: [COMPARISON] REST vs SOAP vs GraphQL in one line each?
A: REST: resources plus HTTP methods, usually JSON, simple and common. SOAP: XML envelopes with strict contracts (WSDL), common in older enterprise systems. GraphQL: one endpoint where clients specify exactly which fields they want.

#### Scenario-based
Q: [SCENARIO] Your company has a web app and is launching mobile apps. Why build an API layer instead of letting each app talk to the database?
A: One API centralises business rules and security, keeps database credentials off devices, lets all clients share the same logic, and lets the backend evolve without breaking installed apps.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can one server be a client too?
A: Yes. A backend is a server to the app and a client when it calls a payment gateway or another microservice.
:::

## Session 5.2 — HTTP and REST Fundamentals {: #s5-2 }

### HTTP in one paragraph

**HTTP (HyperText Transfer Protocol)** is the request/response protocol of the web. It is **stateless** (each request is independent) and text-based in its classic form. **HTTPS** is HTTP over **TLS** encryption, so nobody on the network can read or alter requests and responses. Every API carrying tokens or personal data must use HTTPS.

### Anatomy of a request and a response

[[fig:http_anatomy | An HTTP request (method, path, headers, body) and its response (status line, headers, body).]]

```http
POST /api/v1/orders HTTP/1.1
Host: shop.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
Accept: application/json

{"productId": 2, "quantity": 1}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/v1/orders/9001

{"orderId": 9001, "status": "PENDING", "total": 3499}
```

::: linebyline
| Line | Meaning |
|---|---|
| `POST /api/v1/orders HTTP/1.1` | method (create), path of the resource collection, protocol version |
| `Host: shop.example.com` | which server the request is for |
| `Authorization: Bearer …` | the caller's token, proving who they are (Session 5.4) |
| `Content-Type: application/json` | the body is JSON |
| `Accept: application/json` | the client wants JSON back |
| blank line, then `{"productId": 2, …}` | the request body |
| `HTTP/1.1 201 Created` | status: a new resource was created |
| `Location: /api/v1/orders/9001` | where the new resource lives |
| `{"orderId": 9001, …}` | the response body describing the new order |
:::

### Anatomy of a URL, and path vs query parameters

`https://api.shop.com/v1/customers/42/orders?status=PENDING&page=2`

| Part | Value | Meaning |
|---|---|---|
| Scheme | `https` | protocol (HTTP over TLS) |
| Host | `api.shop.com` | the server |
| Path | `/v1/customers/42/orders` | the resource: orders of customer 42, API version 1 |
| Path parameter | `42` | **identifies** a specific resource |
| Query string | `?status=PENDING&page=2` | **filters, sorts, paginates** the result |

| | Path parameter | Query parameter |
|---|---|---|
| Purpose | identify **which** resource | refine **how** to return it: filter, sort, page, search |
| Example | `/customers/42` | `/customers?city=Pune&sort=name&page=2` |
| Required? | yes, part of the resource's address | usually optional |
| Rule of thumb | "the thing" | "options about the thing" |

### The HTTP methods

| Method | Purpose | Request body | Safe? | Idempotent? | Typical success code |
|---|---|---|---|---|---|
| `GET` | read a resource or a list | no | yes | yes | 200 OK |
| `POST` | create a resource / trigger an action | yes | no | **no** | 201 Created |
| `PUT` | replace a resource completely (or create it at a known URL) | yes (full representation) | no | yes | 200 OK / 204 No Content |
| `PATCH` | update part of a resource | yes (only the changes) | no | not guaranteed | 200 OK / 204 No Content |
| `DELETE` | delete a resource | usually no | no | yes | 204 No Content / 200 OK |
| `HEAD` | like GET but headers only | no | yes | yes | 200 OK |
| `OPTIONS` | which methods are allowed (used in CORS preflight) | no | yes | yes | 204 / 200 |

- **Safe** means the request does not change anything on the server (read-only).
- **Idempotent** means sending the **same request once or ten times has the same effect** on the server's state. `DELETE /orders/9001` twice still leaves order 9001 deleted (the second call may return 404, but the *state* is the same). `POST /orders` twice creates **two** orders, so POST is not idempotent.

| CRUD | HTTP | Example |
|---|---|---|
| Create | POST | `POST /customers` |
| Read | GET | `GET /customers/42` |
| Update (full) | PUT | `PUT /customers/42` |
| Update (partial) | PATCH | `PATCH /customers/42` |
| Delete | DELETE | `DELETE /customers/42` |

### PUT vs PATCH

[MUST KNOW] Suppose customer 42 is currently:

```json
{"id": 42, "name": "Isha Kulkarni", "email": "isha@mail.com", "city": "Pune"}
```

`PUT /customers/42` sends the **complete new version**. Fields you leave out may be cleared:

```json
{"name": "Isha Kulkarni", "email": "isha.k@mail.com", "city": "Pune"}
```

`PATCH /customers/42` sends **only what changes**:

```json
{"email": "isha.k@mail.com"}
```

| | PUT | PATCH |
|---|---|---|
| Sends | the whole resource | only the fields to change |
| Missing fields | treated as removed or reset (replace semantics) | left unchanged |
| Idempotent | yes: same full document each time | not necessarily (`{"op": "increment", "stock": 1}` is not), though simple field sets usually are |
| Payload size | larger | smaller |
| Typical use | "save the whole form" | "change just the email" |

### HTTP status codes

| Class | Meaning |
|---|---|
| 1xx | informational (rarely seen in APIs) |
| **2xx** | **success** |
| 3xx | redirection (the resource is elsewhere, or not modified) |
| **4xx** | **client error**: the request is wrong; fix it before retrying |
| **5xx** | **server error**: the server failed; retrying later may work |

| Code | Name | When to use it |
|---|---|---|
| 200 | OK | successful GET, PUT or PATCH with a response body |
| 201 | Created | POST created a resource (add a `Location` header) |
| 202 | Accepted | request accepted for asynchronous processing (job started) |
| 204 | No Content | success with no body (often DELETE) |
| 301 / 302 | Moved Permanently / Found | redirects |
| 304 | Not Modified | cached copy is still valid (ETag matched) |
| 400 | Bad Request | malformed request, invalid JSON, missing field |
| 401 | Unauthorized | **not authenticated**: missing or invalid credentials or token |
| 403 | Forbidden | **authenticated but not allowed** |
| 404 | Not Found | the resource does not exist |
| 405 | Method Not Allowed | e.g. DELETE on a read-only resource |
| 409 | Conflict | state conflict: duplicate email, version mismatch |
| 415 | Unsupported Media Type | sent XML where JSON was expected |
| 422 | Unprocessable Content | well-formed but semantically invalid (quantity = −5) |
| 429 | Too Many Requests | rate limit exceeded; see `Retry-After` |
| 500 | Internal Server Error | unexpected server failure (a bug) |
| 502 | Bad Gateway | a gateway or proxy got a bad response from upstream |
| 503 | Service Unavailable | overloaded or down for maintenance; retry later |
| 504 | Gateway Timeout | the upstream service did not answer in time |

::: trap 401 vs 403
**401 Unauthorized** really means **unauthenticated**: "I don't know who you are" (no token, or an expired or invalid one). **403 Forbidden** means "I know who you are, but you are not allowed to do this". A logged-in customer trying to delete a product gets 403.
:::

### JSON: the language of APIs

**JSON (JavaScript Object Notation)** is a lightweight text format for structured data.

```json
{
  "orderId": 9001,
  "customer": {"id": 42, "name": "Isha Kulkarni"},
  "items": [
    {"product": "Mechanical Keyboard", "qty": 1, "price": 3499.00}
  ],
  "paid": true,
  "couponCode": null
}
```

- Six value types: **string** (double quotes only), **number**, **boolean** (`true`/`false`), **null**, **object** `{ }` and **array** `[ ]`.
- Keys must be double-quoted strings; no trailing commas; no comments.
- JSON has no date type: dates travel as strings, ideally ISO 8601 (`"2024-04-19T19:42:00Z"`).
- Money: send exact decimal values as strings or in the smallest unit (paise), to avoid floating-point surprises.

| | JSON | XML |
|---|---|---|
| Syntax | `{"name": "Isha"}` | `<name>Isha</name>` |
| Size | smaller | larger (closing tags) |
| Readability | easy | verbose |
| Data types | string, number, boolean, null, object, array | text (types via schemas) |
| Typical use | REST APIs, web and mobile | SOAP, older enterprise and banking integrations, documents |

### REST: the architectural style

**REST (Representational State Transfer)** is a style for designing web APIs around **resources**. Its main constraints, in plain words:

| Constraint | Meaning |
|---|---|
| Client–server | UI and data/logic are separated |
| **Stateless** | every request carries all the context it needs; no server-side session required |
| **Uniform interface** | resources identified by URLs, manipulated with standard HTTP methods, represented as JSON (or XML) |
| Cacheable | responses say whether they can be cached (`Cache-Control`, `ETag`) |
| Layered system | clients don't know whether they talk to the real server or a gateway or cache |
| (optional) HATEOAS | responses include links to related actions |

**Resource naming best practices:**

| Good | Avoid | Why |
|---|---|---|
| `GET /customers` | `GET /getAllCustomers` | the method already says "get"; use nouns |
| `GET /customers/42/orders` | `GET /orders?customer=42` *as the only way* | nesting shows ownership (both are acceptable; be consistent) |
| `POST /orders` | `POST /createOrder` | no verbs in paths |
| `/order-items` (lowercase, hyphens) | `/OrderItems` | consistency, readability |
| plural collections: `/products/7` | mixing `/product/7` and `/products` | predictable URLs |

For actions that are not simple CRUD, use a sub-resource: `POST /orders/9001/cancellation` or `POST /payments/55/refunds`.

::: extension REST vs GraphQL vs gRPC
**GraphQL** exposes one endpoint where the client sends a query naming exactly the fields it wants, which avoids over-fetching and multiple round trips, at the cost of more complex caching and security. **gRPC** uses HTTP/2 and binary Protocol Buffers for fast, strongly typed service-to-service calls, popular inside microservice systems. REST remains the default for public and partner APIs because of its simplicity.
:::

::: explain
"REST is an architectural style where everything is a resource identified by a URL, like /customers/42, and we act on resources with standard HTTP methods: GET to read, POST to create, PUT to replace, PATCH to partially update and DELETE to remove. It's stateless, so every request carries its own context, such as the auth token. The server answers with a status code: 2xx for success, 4xx for client errors like 400, 401, 403 or 404, and 5xx for server errors. The body is usually JSON. GET, PUT and DELETE are idempotent, meaning repeating them has the same effect, while POST is not."
:::

::: trap
- "PUT and PATCH are the same." PUT replaces the whole resource; PATCH changes parts.
- "POST is idempotent." It isn't: two POSTs usually create two resources (see idempotency keys in Session 5.5).
- Returning 200 with `{"error": "not found"}` instead of a proper 404.
- Confusing 401 (who are you?) with 403 (you're not allowed).
- Verbs in URLs (`/getUsers`) and inconsistent naming.
- Sending sensitive data in query strings (they end up in logs and browser history).
:::

::: questions
#### Basic
Q: [DEFINITION] What are the main HTTP methods?
A: GET (read), POST (create), PUT (replace), PATCH (partial update), DELETE (remove), plus HEAD and OPTIONS.

Q: [COMPARISON] PUT vs PATCH?
A: PUT sends the complete resource and replaces it (idempotent); PATCH sends only the fields to change and leaves the rest untouched.

Q: [DEFINITION] What do 2xx, 4xx and 5xx status codes mean?
A: 2xx means success, 4xx means the client sent a bad or unauthorized request, and 5xx means the server failed to process a valid request.

Q: [COMPARISON] Path parameter vs query parameter?
A: A path parameter identifies a specific resource (`/customers/42`); query parameters filter, sort or paginate (`/customers?city=Pune&page=2`).

#### Intermediate
Q: [DEFINITION] What does idempotent mean? Which methods are idempotent?
A: Repeating the same request has the same effect on server state as sending it once. GET, PUT, DELETE, HEAD and OPTIONS are idempotent; POST is not; PATCH may or may not be.

Q: [COMPARISON] 401 vs 403?
A: 401: the request lacks valid authentication (who are you?). 403: the user is authenticated but lacks permission for this action.

Q: [DEFINITION] What makes an API RESTful?
A: Resources addressed by URLs, standard HTTP methods with correct semantics, stateless requests, representations such as JSON, meaningful status codes, and cacheability.

Q: [HOW] Which status code should a successful POST return, and what header?
A: 201 Created, with a `Location` header pointing to the new resource (and usually the created resource in the body).

Q: [COMPARISON] 400 vs 422?
A: 400 means the request is malformed (invalid JSON, wrong types). 422 means it is well-formed but fails business validation (quantity must be positive).

#### Scenario-based
Q: [DESIGN QUESTION] Design REST endpoints for a library: books, members and loans.
A: `GET/POST /books`, `GET/PUT/PATCH/DELETE /books/{id}`, `GET/POST /members`, `GET /members/{id}/loans`, `POST /loans` (borrow), `POST /loans/{id}/return` or `PATCH /loans/{id}` with return_date; filtering like `GET /books?author=…&available=true&page=2`.

Q: [SCENARIO] A client sends `DELETE /orders/9001` twice because of a network retry. What should happen?
A: The first call deletes the order (204); the second finds nothing and can return 404 (or 204). Either way the state is unchanged, because DELETE is idempotent.

Q: [SCENARIO] Users sometimes get 503 errors during sales. What does that tell you, and what should clients do?
A: The service is overloaded or temporarily unavailable, so the server side needs scaling. Clients should retry later with exponential backoff, respecting any `Retry-After` header.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can a GET request have a body?
A: The HTTP spec doesn't forbid it, but servers and proxies may ignore it, and GET semantics don't define it. Put filters in query parameters, or use POST for complex searches.

Q: [TRAP QUESTION] If PATCH can be idempotent, why is it "not guaranteed"?
A: Because it depends on the patch: "set email = x" is idempotent, but "append item" or "increment stock by 1" changes state again on every repeat.
:::

## Session 5.3 — Designing and Consuming REST APIs {: #s5-3 }

### One request, end to end

The brief's example, *Frontend → GET /users → Backend → Database → JSON response*, drawn as a sequence of steps:

[[fig:api_request_flow | What happens during GET /api/users: authentication, validation, SQL, conversion to JSON, response.]]

The request the frontend sends:

```http
GET /api/users?page=1&size=20 HTTP/1.1
Host: api.shop.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Accept: application/json
```

What a Spring Boot backend might look like (simplified):

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public Page<UserDto> listUsers(@RequestParam(defaultValue = "1") int page,
                                   @RequestParam(defaultValue = "20") int size) {
        return userService.findUsers(page, size);   // runs SQL with LIMIT/OFFSET
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable long id) {
        return userService.findById(id)
                .map(ResponseEntity::ok)                      // 200 + JSON
                .orElse(ResponseEntity.notFound().build());   // 404
    }
}
```

::: linebyline
| Line | What it does |
|---|---|
| `@RestController` | this class handles HTTP requests and returns data (JSON), not HTML pages |
| `@RequestMapping("/api/users")` | every method below lives under `/api/users` |
| `@GetMapping` | handles `GET /api/users` |
| `@RequestParam(defaultValue = "1") int page` | reads the query parameter `?page=…`, defaulting to 1 |
| `userService.findUsers(page, size)` | the service layer applies rules; the repository runs `SELECT … LIMIT 20 OFFSET 0` |
| `@GetMapping("/{id}")` + `@PathVariable long id` | handles `GET /api/users/42`; `42` comes from the path |
| `.map(ResponseEntity::ok)` | found → 200 OK with the user as JSON |
| `.orElse(ResponseEntity.notFound().build())` | not found → 404 |
:::

The response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": [
    {"id": 1, "name": "Asha Rao", "email": "asha@mail.com"},
    {"id": 2, "name": "Vikram Shah", "email": "vikram@mail.com"}
  ],
  "page": 1,
  "size": 20,
  "totalItems": 245,
  "next": "/api/users?page=2&size=20"
}
```

### Consuming an API from code

```python
import requests

resp = requests.get(
    "https://api.shop.example.com/api/users",
    params={"page": 1, "size": 20},
    headers={"Authorization": "Bearer <token>"},
    timeout=5,                       # never wait forever
)
resp.raise_for_status()              # turn 4xx/5xx into an exception
for user in resp.json()["data"]:
    print(user["id"], user["name"])
```

::: linebyline
| Line | What it does |
|---|---|
| `requests.get(url, params=…)` | builds `…/api/users?page=1&size=20` and sends a GET |
| `headers={"Authorization": …}` | sends the token |
| `timeout=5` | give up after 5 seconds instead of hanging (Session 5.5) |
| `raise_for_status()` | stops here with an error if the status is 4xx or 5xx |
| `resp.json()["data"]` | parse the JSON body and read the list |
:::

### Pagination

Never return 1 million rows in one response. Two common styles:

| | Offset / page pagination | Cursor (keyset) pagination |
|---|---|---|
| Request | `?page=3&size=20` (or `?offset=40&limit=20`) | `?after=last_seen_id&limit=20` |
| SQL | `ORDER BY id LIMIT 20 OFFSET 40` | `WHERE id > :last_id ORDER BY id LIMIT 20` |
| Jump to page N | easy | not directly |
| Performance on deep pages | slow (skipped rows are still read) | fast (uses the index) |
| Consistency when data changes | items can shift, causing duplicates or skips | stable |
| Good for | admin tables, small datasets | feeds, infinite scroll, large datasets |

Return paging metadata (`page`, `size`, `totalItems`, or a `next` link or cursor) so clients know how to continue.

### Filtering, sorting and field selection

Use query parameters consistently: `GET /orders?status=PENDING&from=2024-04-01&sort=-order_date&fields=id,total`. A leading `-` meaning "descending" is a common convention. Validate and whitelist sort fields; never paste them into SQL as raw strings (SQL injection, Session 5.4).

### API versioning

APIs change; clients (especially installed mobile apps) cannot all update at once. **Versioning** lets old clients keep working while new ones use the new contract.

| Strategy | Example | Notes |
|---|---|---|
| URI path | `/api/v1/orders`, `/api/v2/orders` | most common; very visible and simple |
| Header | `Accept: application/vnd.shop.v2+json` or `API-Version: 2` | cleaner URLs; less visible |
| Query parameter | `/orders?version=2` | easy, but mixes versioning with filters |

**Rules of thumb:** additive changes (a new optional field) usually don't need a new version; breaking changes (renaming or removing fields, changing types or meanings) do. Announce deprecations and keep old versions running for an agreed period.

### Rate limiting

**Rate limiting** caps how many requests a client may make in a time window (for example 100 per minute per API key). It protects the service from overload and abuse, and enforces fair use or paid tiers.

- When the limit is exceeded, return **429 Too Many Requests**, ideally with `Retry-After`.
- Common headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
- Common algorithms: **fixed window**, **sliding window** and **token bucket** (tokens refill at a steady rate; each request spends one, which allows short bursts).
- Clients should back off and retry later, not hammer the API.

### Consistent errors

Return the right status code **and** a helpful, consistent body. A widely used standard is "problem details" (RFC 9457):

```json
{
  "type": "https://api.shop.example.com/errors/out-of-stock",
  "title": "Product out of stock",
  "status": 409,
  "detail": "Only 0 units of product 5 are available.",
  "instance": "/api/v1/orders"
}
```

Never return stack traces or SQL errors to clients; log them on the server with a **correlation ID** and include that ID in the response for support.

### Caching [INTERVIEW EXTENSION]

- `Cache-Control: max-age=60` lets clients and CDNs reuse a response for 60 seconds.
- `ETag: "v7"` labels a version of the resource; the client sends `If-None-Match: "v7"` and gets **304 Not Modified** (no body) if nothing changed, which saves bandwidth.

### Documenting and testing APIs

- **OpenAPI (Swagger):** a machine-readable description of endpoints, parameters, schemas and responses; it generates interactive docs and client code.
- **Postman** or `curl` for manual testing; automated contract and integration tests in CI.
- An **API gateway** (Kong, Apigee, AWS API Gateway, Azure API Management) often sits in front of APIs to handle authentication, rate limiting, routing, logging and versioning in one place.

::: explain
"When the frontend calls GET /api/users?page=1, the request goes over HTTPS with a bearer token. The backend's controller receives it, the security layer validates the token, the service layer applies business rules, and the repository runs a SQL query like SELECT … ORDER BY id LIMIT 20 OFFSET 0. The rows are mapped to DTOs and serialised to JSON, and the server returns 200 with the data plus paging info. For a good API I'd add pagination, filtering through query parameters, consistent error responses with proper status codes, versioning like /v1, and rate limiting that returns 429 when a client sends too many requests."
:::

::: trap
- Returning unbounded lists with no pagination.
- Deep OFFSET pagination on huge tables (slow), and inconsistent pages while data changes.
- Breaking changes without a new version.
- Leaking stack traces, SQL or internal IDs in error messages.
- Clients that ignore 429 and immediately retry, making the overload worse.
:::

::: questions
#### Basic
Q: [DEFINITION] What is pagination and why is it needed?
A: Returning large result sets in pages (e.g. 20 items at a time), to keep responses fast and small and protect the server and the client.

Q: [DEFINITION] What is API versioning?
A: Managing changes to an API's contract so old clients keep working, typically via `/v1/` in the path, a header or a query parameter.

Q: [DEFINITION] What is rate limiting?
A: Restricting the number of requests a client can make in a time window, returning 429 Too Many Requests when the limit is exceeded.

#### Intermediate
Q: [COMPARISON] Offset vs cursor pagination?
A: Offset (`page`, `offset`) is simple and allows jumping to page N but is slow on deep pages and unstable when data changes. Cursor/keyset (`after=id`) is fast and stable but only moves forward and backward.

Q: [HOW] What changes require a new API version?
A: Breaking changes: removing or renaming fields, changing types or meanings, making optional fields required, changing URLs or behaviour. Adding optional fields or new endpoints usually doesn't.

Q: [HOW] What would you include in an API error response?
A: The correct status code, a stable machine-readable error type or code, a human-readable message, details about invalid fields, and a correlation/request ID, but no internal details.

Q: [DEFINITION] What is OpenAPI/Swagger?
A: A standard, machine-readable specification of a REST API (endpoints, parameters, schemas, responses) used to generate documentation, client SDKs and tests.

#### Scenario-based
Q: [SCENARIO] Explain what happens when the frontend calls `GET /users`.
A: The browser sends an HTTPS GET with headers (token); the server routes it to a controller; auth is verified; the service applies rules; the repository queries the database with pagination; the rows are converted to JSON; the server returns 200 with the body; the frontend renders the list (or handles 401/500 errors).

Q: [DESIGN QUESTION] Your public API is being hammered by one client's script. What do you implement?
A: Per-key rate limiting (token bucket) at the gateway returning 429 with `Retry-After`, monitoring and alerts, possibly quotas by tier, and caching for expensive GET endpoints.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is it OK to return 200 for every response and put the real status in the body?
A: No. Proper status codes let clients, proxies, monitoring and retry logic behave correctly; 200-with-error breaks all of them.

Q: [TRAP QUESTION] Does adding a new optional field to a response break clients?
A: Usually not, as long as clients ignore unknown fields, which they should. It's considered a non-breaking change.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Which HTTP method and status code would you use to (a) create an order, (b) fetch order 9001, (c) delete order 9001?

**P2.** Identify the path and query parameters in `/api/v2/stores/17/products?category=Furniture&sort=price`.

**P3.** What does a 429 status mean, and what should the client do?

#### Level 2 — Interview application
**P4.** Write the JSON body for a PATCH that changes only a customer's city to "Mysuru", and explain why PUT with the same body would be risky.

**P5.** Design the endpoints (method + path) for a job portal: list jobs with filters, view a job, apply to a job, list my applications, withdraw an application.

#### Level 3 — Scenario / problem solving
**P6.** A mobile app shows "Something went wrong" for every error. Propose an error-response design that lets the app show useful messages.

**P7.** An endpoint `GET /transactions?page=50000` takes 8 seconds. Explain why, and redesign the pagination.
:::

::: answers
**P1.** (a) `POST /orders` → 201 Created; (b) `GET /orders/9001` → 200 OK (404 if missing); (c) `DELETE /orders/9001` → 204 No Content.

**P2.** Path parameters: `v2` (the version, part of the path) and `17` (the store ID). Query parameters: `category=Furniture` and `sort=price`.

**P3.** Too Many Requests: the client exceeded the rate limit. It should wait (respecting `Retry-After` if present) and retry with exponential backoff, and reduce its request rate.

**P4.** `PATCH /customers/42` with body `{"city": "Mysuru"}`. With PUT, the body is treated as the *complete* new representation, so fields not sent (name, email) could be cleared or reset to defaults.

**P5.** `GET /jobs?skill=sql&city=Pune&page=1` · `GET /jobs/{jobId}` · `POST /jobs/{jobId}/applications` · `GET /me/applications` · `DELETE /applications/{applicationId}` (or `PATCH /applications/{id}` with `{"status": "WITHDRAWN"}` to keep history).

**P6.** Use correct status codes (400, 401, 403, 404, 409, 422, 429, 5xx) plus a consistent JSON body: a stable `code` (e.g. `OUT_OF_STOCK`) the app can map to friendly messages, a human-readable `message`, a `fields` list for validation errors (`email: invalid format`), and a `requestId` for support. Document all codes in OpenAPI.

**P7.** With OFFSET pagination the database must read and discard 50,000 × page-size rows before returning a page. Switch to cursor/keyset pagination: `GET /transactions?after=<last_id>&limit=50` → `WHERE id > :last_id ORDER BY id LIMIT 50`, using the primary key index, and return a `next` cursor in each response.
:::
