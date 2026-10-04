## Session 4.4 — MongoDB: Core Concepts {: #s4-4 }

[HIGH PRIORITY] MongoDB is the most widely used document database and the NoSQL system interviewers ask about most.

### What is MongoDB?

**MongoDB is a document database**: instead of rows in tables, it stores **documents** (records that look like JSON) inside **collections**. A document can contain nested objects and arrays, so data that belongs together (an order and its items) can live together.

### The building blocks

[[fig:mongo_structure | A MongoDB server holds databases; databases hold collections; collections hold documents made of fields.]]

| MongoDB | Relational equivalent | Notes |
|---|---|---|
| database | database | e.g. `shop` |
| collection | table | e.g. `customers`; no fixed schema by default |
| document | row | a JSON-like record, up to 16 MB |
| field | column | `name`, `city`; can hold objects and arrays |
| `_id` | primary key | every document has a unique `_id`; auto-generated as an `ObjectId` if you don't set one |
| embedded document / array | child table rows | stored *inside* the parent document |
| reference (`customer_id`) | foreign key | **not** enforced by the database |
| `$lookup` | LEFT OUTER JOIN | an aggregation stage |
| index | index | B-tree indexes, plus text, geospatial and TTL indexes |

### JSON vs BSON

- **JSON** is the text format you read and write: `{"name": "Aarav", "city": "Mumbai"}`.
- **BSON (Binary JSON)** is how MongoDB actually **stores and transmits** documents. It is a binary encoding that is faster to scan and that supports **more data types** than JSON: `ObjectId`, `Date`, 32- and 64-bit integers, `Decimal128` (exact decimals for money), binary data and more.

### The _id field and ObjectId

Every document needs a unique `_id`. If you don't provide one, MongoDB creates an **ObjectId**: a 12-byte value made of a **timestamp**, a random value and a counter. So ObjectIds are unique across machines without coordination, and they roughly sort by creation time.

```javascript
{ "_id": ObjectId("665f1c2e8a4b7d0012ab34cd"), "name": "Aarav Patel" }
```

### A tour of the shell (mongosh)

```javascript
show dbs                 // list databases
use shop                 // switch to (or create on first write) the "shop" database
show collections         // list collections in the current database
db.customers.find()      // read documents from the "customers" collection
```

A database or collection is created automatically the first time you insert into it.

### Flexible schema, and how to tame it

Two documents in the same collection may have different fields: one customer has `phone`, another has `tags`. That is useful for evolving data, but production systems usually add **schema validation** so bad data is rejected:

```javascript
db.createCollection("customers", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "city"],
      properties: {
        name:  { bsonType: "string" },
        email: { bsonType: "string", pattern: "^.+@.+$" },
        city:  { bsonType: "string" }
      }
    }
  }
})
```

### Replica sets and sharding, in two lines each

- **Replica set:** a group of MongoDB servers holding the same data: one **primary** (takes writes) and several **secondaries** (copies). If the primary fails, the members **elect** a new primary automatically, which gives high availability.
- **Sharding:** splitting a collection across several replica sets by a **shard key**, so data and load spread horizontally.

**MongoDB Atlas** is MongoDB's managed cloud service: replica sets, backups and scaling handled for you, the same idea as RDS in Session 4.1.

::: explain
"MongoDB is a document database. Data is stored as documents, JSON-like records, grouped into collections, which are roughly like tables. Documents can hold nested objects and arrays, so related data like an order and its items can be stored together and read in one go. Internally it stores documents as BSON, a binary form of JSON with extra types like ObjectId, dates and exact decimals. Every document has a unique _id. The schema is flexible, but we can add JSON-schema validation, and replica sets give high availability through automatic failover."
:::

::: trap
- "MongoDB stores JSON." It stores **BSON**; JSON is the human-readable form.
- "MongoDB enforces foreign keys." It does not; references are just values your application manages.
- "Schemaless means anything goes." Use schema validation and consistent application models.
- Forgetting the 16 MB document limit when embedding ever-growing arrays.
:::

::: questions
#### Basic
Q: [DEFINITION] What is MongoDB?
A: A document-oriented NoSQL database that stores data as BSON documents in collections, with a flexible schema, rich queries, indexes, replication and sharding.

Q: [COMPARISON] Collection vs table, document vs row?
A: A collection groups documents like a table groups rows, but without a fixed schema; a document is a JSON-like record (with nested data) like a row.

Q: [DEFINITION] What is BSON?
A: Binary JSON: MongoDB's storage and wire format, which is faster to parse and supports extra types such as ObjectId, Date, Int64 and Decimal128.

#### Intermediate
Q: [DEFINITION] What is an ObjectId?
A: The default 12-byte `_id` value, containing a timestamp, a random value and a counter, so it is unique without central coordination and roughly time-ordered.

Q: [DEFINITION] What is a replica set?
A: A group of MongoDB nodes with the same data: one primary for writes and secondaries that replicate it, with automatic election of a new primary on failure.

Q: [HOW] How can you enforce a structure in MongoDB?
A: With schema validation (`$jsonSchema` validators) on the collection, plus consistent models in the application (for example Mongoose schemas in Node.js).

#### Scenario-based
Q: [SCENARIO] A team says "MongoDB lets us skip data modeling." How do you respond?
A: The flexible schema removes migrations, not design. We still need to plan documents around access patterns, decide embedding vs referencing, add indexes and validation, or we'll end up with inconsistent, slow data.

#### Follow-up / Trap
Q: [TRAP QUESTION] Does MongoDB support ACID transactions?
A: Yes. Single-document operations are always atomic, and multi-document ACID transactions are supported (replica sets since 4.0, sharded clusters since 4.2), although good document design reduces the need for them.
:::

## Session 4.5 — MongoDB: CRUD Operations {: #s4-5 }

CRUD = **C**reate, **R**ead, **U**pdate, **D**elete. The examples use a small `shop` database. The results shown in comments were worked out by hand from this exact data.

::: note About these examples
This handbook's build environment could not run a MongoDB server, so unlike the SQL examples, the MongoDB outputs below were not executed automatically. The shell syntax was checked automatically, and each result was traced by hand against the sample data. Each example assumes the original data inserted below (as if run on a fresh copy), not the state left by the previous example.
:::

### Create: insertOne and insertMany

```javascript
use shop

db.customers.insertOne({
  _id: 1,
  name: "Aarav Patel",
  email: "aarav@mail.com",
  city: "Mumbai",
  tags: ["prime"],
  signup_date: ISODate("2023-11-05")
})
// → { acknowledged: true, insertedId: 1 }

db.customers.insertMany([
  { _id: 2, name: "Isha Kulkarni", email: "isha@mail.com",  city: "Pune",  signup_date: ISODate("2023-12-12") },
  { _id: 3, name: "Kabir Khan",    email: "kabir@mail.com", city: "Delhi", tags: ["new"], signup_date: ISODate("2024-01-03") },
  { _id: 4, name: "Diya Joshi",    city: "Bengaluru", phone: "+91-98450-00000",  signup_date: ISODate("2024-01-20") }
])
// → { acknowledged: true, insertedIds: { '0': 2, '1': 3, '2': 4 } }
```

::: linebyline
| Part | What it means |
|---|---|
| `use shop` | switch to the `shop` database (created on the first insert) |
| `db.customers.insertOne({...})` | insert one document into `customers` (the collection is created if needed) |
| `_id: 1` | we chose the ID; leave it out and MongoDB generates an ObjectId |
| `tags: ["prime"]` | an array field |
| `ISODate("2023-11-05")` | a real BSON Date, not a string |
| `insertMany([...])` | insert several documents in one call; note the different fields per document |
:::

We also need products and orders. Each order **embeds** its items:

```javascript
db.products.insertMany([
  { _id: 1, name: "Wireless Mouse",      category: "Electronics", price: 799,   stock: 120 },
  { _id: 2, name: "Mechanical Keyboard", category: "Electronics", price: 3499,  stock: 40  },
  { _id: 4, name: "Office Chair",        category: "Furniture",   price: 8999,  stock: 15  },
  { _id: 5, name: "Standing Desk",       category: "Furniture",   price: 15999, stock: 5   },
  { _id: 6, name: "Notebook Pack",       category: "Stationery",  price: 249,   stock: 500 }
])

db.orders.insertMany([
  { _id: 101, customer_id: 1, order_date: ISODate("2024-01-05"), status: "DELIVERED", total: 2843,
    items: [ { product_id: 1, name: "Wireless Mouse", qty: 2, price: 799 },
             { product_id: 6, name: "Notebook Pack",  qty: 5, price: 249 } ] },
  { _id: 102, customer_id: 2, order_date: ISODate("2024-01-12"), status: "DELIVERED", total: 3499,
    items: [ { product_id: 2, name: "Mechanical Keyboard", qty: 1, price: 3499 } ] },
  { _id: 103, customer_id: 1, order_date: ISODate("2024-01-28"), status: "DELIVERED", total: 8999,
    items: [ { product_id: 4, name: "Office Chair", qty: 1, price: 8999 } ] },
  { _id: 104, customer_id: 3, order_date: ISODate("2024-02-02"), status: "CANCELLED", total: 15999,
    items: [ { product_id: 5, name: "Standing Desk", qty: 1, price: 15999 } ] },
  { _id: 115, customer_id: 1, order_date: ISODate("2024-04-19"), status: "PENDING", total: 3499,
    items: [ { product_id: 2, name: "Mechanical Keyboard", qty: 1, price: 3499 } ] }
])
```

### Read: find() with filters, projection, sort and limit

The general form is `db.collection.find(filter, projection)`.

```javascript
db.products.find({ category: "Electronics" })
// → Wireless Mouse, Mechanical Keyboard   (equality filter)

db.products.find({ price: { $gt: 1000 } }, { name: 1, price: 1, _id: 0 })
// → { name: 'Mechanical Keyboard', price: 3499 }
//   { name: 'Office Chair', price: 8999 }
//   { name: 'Standing Desk', price: 15999 }
```

::: linebyline
| Part | What it means |
|---|---|
| `{ category: "Electronics" }` | filter: like `WHERE category = 'Electronics'` |
| `{ price: { $gt: 1000 } }` | an operator inside the filter: `price > 1000` |
| `{ name: 1, price: 1, _id: 0 }` | **projection**: return only name and price (`1` = include) and hide `_id` (`0` = exclude) |
:::

| Operator type | Operators | Example |
|---|---|---|
| Comparison | `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin` | `{ city: { $in: ["Pune", "Delhi"] } }` |
| Logical | `$and`, `$or`, `$not`, `$nor` | `{ $or: [ {a: 1}, {b: 2} ] }` |
| Element | `$exists`, `$type` | `{ phone: { $exists: true } }` |
| Array | `$all`, `$size`, `$elemMatch` | `{ tags: { $all: ["prime", "new"] } }` |
| Text pattern | `$regex` | `{ name: { $regex: "^A", $options: "i" } }` |

More reads:

```javascript
// AND: two conditions in one filter object
db.products.find({ category: "Furniture", price: { $lt: 10000 } })
// → Office Chair

// OR
db.products.find({ $or: [ { category: "Stationery" }, { price: { $gte: 10000 } } ] })
// → Standing Desk, Notebook Pack

// IN
db.customers.find({ city: { $in: ["Pune", "Delhi"] } })
// → Isha Kulkarni, Kabir Khan

// field exists (flexible schema!)
db.customers.find({ phone: { $exists: true } })
// → Diya Joshi

// array contains a value
db.customers.find({ tags: "prime" })
// → Aarav Patel

// query inside embedded documents with dot notation
db.orders.find({ "items.product_id": 2 }, { _id: 1, status: 1 })
// → { _id: 102, status: 'DELIVERED' }, { _id: 115, status: 'PENDING' }

// sort, limit, skip (pagination)
db.products.find().sort({ price: -1 }).limit(2)
// → Standing Desk (15999), Office Chair (8999)

db.orders.countDocuments({ status: "DELIVERED" })   // → 3
db.products.distinct("category")                    // → [ 'Electronics', 'Furniture', 'Stationery' ]
db.customers.findOne({ email: "isha@mail.com" })     // → the single Isha document (or null)
```

### Update: updateOne, updateMany, replaceOne

Updates take a **filter** (which documents) and an **update document** that uses **update operators**:

```javascript
db.products.updateOne({ _id: 1 }, { $set: { price: 749 } })
// → { acknowledged: true, matchedCount: 1, modifiedCount: 1, upsertedCount: 0, ... }

db.products.updateMany({ category: "Electronics" }, { $inc: { stock: -1 } })
// → { acknowledged: true, matchedCount: 2, modifiedCount: 2, ... }

db.orders.updateMany({ status: "DELIVERED" }, { $set: { reviewed: false } })
// → matchedCount: 3, modifiedCount: 3   (adds a new field to three documents)
```

::: linebyline
| Part | What it means |
|---|---|
| `updateOne({ _id: 1 }, …)` | change at most **one** document matching the filter |
| `{ $set: { price: 749 } }` | set (or add) the `price` field; other fields stay untouched |
| `updateMany({ category: "Electronics" }, …)` | change **every** matching document |
| `{ $inc: { stock: -1 } }` | add −1 to `stock` atomically (no read-then-write race) |
| `matchedCount` / `modifiedCount` | how many documents matched, and how many actually changed |
:::

| Update operator | Effect | Example |
|---|---|---|
| `$set` | set or add fields | `{ $set: { city: "Pune" } }` |
| `$unset` | remove fields | `{ $unset: { phone: "" } }` |
| `$inc` | increment a number | `{ $inc: { stock: -1 } }` |
| `$push` | append to an array (creates it if missing) | `{ $push: { tags: "prime" } }` |
| `$addToSet` | append only if not already present | `{ $addToSet: { tags: "prime" } }` |
| `$pull` | remove matching values from an array | `{ $pull: { tags: "new" } }` |
| `$rename` | rename a field | `{ $rename: { phone: "mobile" } }` |

**Upsert**: update if found, insert otherwise:

```javascript
db.products.updateOne(
  { _id: 9 },
  { $set: { name: "Laptop Stand", category: "Furniture", price: 1299 } },
  { upsert: true }
)
// → { matchedCount: 0, modifiedCount: 0, upsertedCount: 1, upsertedId: 9 }
```

**replaceOne** replaces the *entire* document (except `_id`) with a new one:

```javascript
db.customers.replaceOne({ _id: 4 }, { name: "Diya Joshi", city: "Mysuru" })
// Diya's phone and signup_date are gone: only name and city remain.
```

### Delete: deleteOne, deleteMany, drop

```javascript
db.orders.deleteOne({ _id: 115 })
// → { acknowledged: true, deletedCount: 1 }

db.orders.deleteMany({ status: "CANCELLED" })
// → { acknowledged: true, deletedCount: 1 }   (order 104)

db.orders.deleteMany({})     // ⚠ deletes EVERY document, like DELETE without WHERE
db.orders.drop()             // removes the whole collection and its indexes, like DROP TABLE
```

### SQL to MongoDB translation

| SQL | MongoDB |
|---|---|
| `INSERT INTO customers VALUES (…)` | `db.customers.insertOne({…})` |
| `SELECT * FROM products WHERE category = 'Electronics'` | `db.products.find({ category: "Electronics" })` |
| `SELECT name, price FROM products WHERE price > 1000` | `db.products.find({ price: { $gt: 1000 } }, { name: 1, price: 1, _id: 0 })` |
| `… WHERE city IN ('Pune', 'Delhi')` | `{ city: { $in: ["Pune", "Delhi"] } }` |
| `… ORDER BY price DESC LIMIT 2` | `.sort({ price: -1 }).limit(2)` |
| `SELECT COUNT(*) FROM orders WHERE status = 'DELIVERED'` | `db.orders.countDocuments({ status: "DELIVERED" })` |
| `UPDATE products SET price = 749 WHERE id = 1` | `db.products.updateOne({ _id: 1 }, { $set: { price: 749 } })` |
| `UPDATE … WHERE category = 'Electronics'` (many rows) | `db.products.updateMany({ category: "Electronics" }, { … })` |
| `DELETE FROM orders WHERE status = 'CANCELLED'` | `db.orders.deleteMany({ status: "CANCELLED" })` |
| `DROP TABLE orders` | `db.orders.drop()` |

::: explain
"In MongoDB, CRUD maps to insertOne and insertMany for create, find with a filter document and an optional projection for read, updateOne, updateMany and replaceOne for update, and deleteOne and deleteMany for delete. Filters use operators like $gt, $in and $or, and dot notation reaches into embedded documents, for example items.product_id. Updates must use operators like $set, $inc or $push, so only the named fields change; replaceOne swaps the whole document. Also, updateMany and deleteMany with an empty filter affect every document, so I double-check the filter first."
:::

::: trap
- `updateOne({_id: 1}, { price: 749 })` without `$set`: modern drivers reject it ("Update document requires atomic operators"); `replaceOne` with a partial document silently drops the other fields.
- `deleteMany({})` deletes everything.
- `updateOne` changes only the **first** match; use `updateMany` for all matches.
- Comparing dates stored as strings: use real `ISODate` values.
- Expecting `find()` results in insertion order without `sort()`.
:::

::: questions
#### Basic
Q: [HOW] How do you insert multiple documents in MongoDB?
A: `db.collection.insertMany([ {...}, {...} ])`, which returns the inserted IDs.

Q: [COMPARISON] updateOne vs updateMany?
A: updateOne modifies at most the first document matching the filter; updateMany modifies all matching documents.

Q: [COMPARISON] deleteOne vs deleteMany?
A: deleteOne removes the first matching document; deleteMany removes all matching documents (an empty filter `{}` removes all documents).

Q: [DEFINITION] What is a projection?
A: The second argument of `find()`, which chooses which fields to return: `{ name: 1, _id: 0 }`.

#### Intermediate
Q: [COMPARISON] $set vs replaceOne?
A: `$set` changes only the named fields; `replaceOne` replaces the entire document except `_id`, dropping any fields not in the new document.

Q: [COMPARISON] $push vs $addToSet?
A: `$push` always appends (duplicates possible); `$addToSet` appends only if the value isn't already in the array.

Q: [HOW] How do you query a field inside an embedded document or array?
A: With dot notation, e.g. `{ "items.product_id": 2 }`, or `$elemMatch` when several conditions must match the same array element.

Q: [DEFINITION] What does `{ upsert: true }` do?
A: If no document matches the filter, a new one is inserted, built from the filter and the update; otherwise the match is updated.

#### Scenario-based
Q: [SCENARIO] Increase the price of all Furniture products by 10%.
A: `db.products.updateMany({ category: "Furniture" }, { $mul: { price: 1.1 } })`.

Q: [SCENARIO] Two users buy the last unit of a product at the same time. How do you avoid overselling in MongoDB?
A: Use an atomic conditional update: `updateOne({ _id: 5, stock: { $gte: 1 } }, { $inc: { stock: -1 } })` and check `modifiedCount`. Only one request can succeed when stock is 1.

#### Follow-up / Trap
Q: [TRAP QUESTION] What happens if you call `db.products.updateMany({}, { $set: { active: true } })`?
A: Every document in the collection gets `active: true`. An empty filter matches all documents.

Q: [TRAP QUESTION] Does `find()` return a list?
A: It returns a **cursor** that fetches documents in batches as you iterate (mongosh prints the first 20); `toArray()` loads everything into memory.
:::

## Session 4.6 — MongoDB: Indexing, Aggregation and Data Modeling {: #s4-6 }

### Indexes in MongoDB

The same idea as in SQL (Session 3.9): without an index MongoDB performs a **collection scan (COLLSCAN)**; with one it performs an **index scan (IXSCAN)**.

```javascript
db.customers.createIndex({ email: 1 }, { unique: true })     // → 'email_1'
db.orders.createIndex({ customer_id: 1, order_date: -1 })    // → 'customer_id_1_order_date_-1' (compound)
db.products.createIndex({ name: "text" })                    // text index for keyword search
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })   // TTL: auto-delete after 1 hour
db.orders.getIndexes()                                       // list indexes

db.orders.find({ customer_id: 1 }).sort({ order_date: -1 }).explain("executionStats")
// winning plan uses stage 'IXSCAN' on customer_id_1_order_date_-1;
// totalDocsExamined: 3 (only Aarav's orders), instead of scanning every order
```

| Index type | Use |
|---|---|
| Single field | `{ email: 1 }` (1 ascending, −1 descending) |
| Compound | `{ customer_id: 1, order_date: -1 }`; follows the leftmost-prefix rule like SQL |
| Multikey | created automatically when the field is an array (`tags`); indexes each element |
| Text | keyword search over string fields |
| TTL | documents expire automatically (sessions, OTPs, logs) |
| Unique / partial / sparse | enforce uniqueness; index only documents matching a condition |

::: trap Unique indexes and missing fields
A unique index treats a **missing** field as `null`, so only **one** document may lack the field. Diya has no email: creating the unique index works, but a second customer without an email would fail with a duplicate-key error on `null`. Use a **partial** index (`partialFilterExpression: { email: { $exists: true } }`) to enforce uniqueness only where the field exists. Compare PostgreSQL, where a UNIQUE column allows many NULLs (Session 2.3).
:::

::: extension The ESR rule for compound indexes
Order the fields of a compound index as **E**quality, **S**ort, **R**ange: fields you match exactly first, then fields you sort by, then fields filtered by ranges. For `find({ customer_id: 1, total: { $gt: 1000 } }).sort({ order_date: -1 })`, the index `{ customer_id: 1, order_date: -1, total: 1 }` follows ESR.
:::

### The aggregation pipeline

The **aggregation pipeline** is MongoDB's tool for grouping, joining and transforming data, the equivalent of SQL's GROUP BY, JOIN and computed columns. Documents flow through a sequence of **stages**, like items on an assembly line; each stage transforms the stream and passes it on.

| Stage | Does | SQL equivalent |
|---|---|---|
| `$match` | filter documents | WHERE (or HAVING, after `$group`) |
| `$group` | group and aggregate (`$sum`, `$avg`, `$min`, `$max`, `$push`) | GROUP BY + aggregates |
| `$sort` | order documents | ORDER BY |
| `$project` / `$addFields` | choose, rename or compute fields | SELECT list, computed columns |
| `$limit` / `$skip` | paginate | LIMIT / OFFSET |
| `$unwind` | turn one document with an array into one document per element | like joining to a child table |
| `$lookup` | pull matching documents from another collection | LEFT OUTER JOIN |
| `$count` | count documents | COUNT(*) |

**Example 1: orders and revenue per customer (excluding cancelled orders)**

```javascript
db.orders.aggregate([
  { $match: { status: { $ne: "CANCELLED" } } },
  { $group: { _id: "$customer_id",
              orders:  { $sum: 1 },
              revenue: { $sum: "$total" } } },
  { $sort: { revenue: -1 } }
])
// → { _id: 1, orders: 3, revenue: 15341 }    (2843 + 8999 + 3499)
//   { _id: 2, orders: 1, revenue: 3499 }
```

::: linebyline
| Stage | What it does |
|---|---|
| `$match: { status: { $ne: "CANCELLED" } }` | keep orders that are not cancelled (filter early, so indexes help and less data flows on) |
| `$group: { _id: "$customer_id", … }` | one output document per customer; `_id` is the group key; `"$total"` means "the value of the total field" |
| `orders: { $sum: 1 }` | add 1 per document, i.e. count orders |
| `revenue: { $sum: "$total" }` | add up the totals |
| `$sort: { revenue: -1 }` | highest revenue first |
:::

**Example 2: best-selling products, using `$unwind` to open up the embedded items**

```javascript
db.orders.aggregate([
  { $match: { status: { $ne: "CANCELLED" } } },
  { $unwind: "$items" },
  { $group: { _id: "$items.name",
              units:   { $sum: "$items.qty" },
              revenue: { $sum: { $multiply: ["$items.qty", "$items.price"] } } } },
  { $sort: { revenue: -1 } },
  { $limit: 3 }
])
// → { _id: 'Office Chair',        units: 1, revenue: 8999 }
//   { _id: 'Mechanical Keyboard', units: 2, revenue: 6998 }
//   { _id: 'Wireless Mouse',      units: 2, revenue: 1598 }
```

`$unwind` turns order 101 (two items) into two documents, one per item, so the items can be grouped by product.

**Example 3: joining with `$lookup`**

```javascript
db.orders.aggregate([
  { $match: { _id: 101 } },
  { $lookup: { from: "customers", localField: "customer_id",
               foreignField: "_id", as: "customer" } },
  { $unwind: "$customer" },
  { $project: { total: 1, "customer.name": 1, "customer.city": 1 } }
])
// → { _id: 101, total: 2843, customer: { name: 'Aarav Patel', city: 'Mumbai' } }
```

`$lookup` adds an array field (`customer`) holding the matching customer documents; `$unwind` turns that one-element array into an object.

### Modeling in MongoDB: embedding vs referencing, revisited

Session 2.8 introduced the idea; here is the MongoDB-specific checklist:

| Question | If yes → |
|---|---|
| Is the data always read together with the parent (order + items)? | embed |
| Is it owned by the parent and bounded (a few addresses)? | embed |
| Is it shared by many parents (customer, product details)? | reference (optionally copy a snapshot) |
| Can it grow without limit (comments, logs, events)? | reference (separate collection) |
| Do you need to update it independently and often? | reference |
| Must several documents change atomically? | prefer embedding them in one document; otherwise use a multi-document transaction |

### MongoDB or PostgreSQL?

| Choose MongoDB when… | Choose PostgreSQL when… |
|---|---|
| data is naturally hierarchical or varies per record | data is highly relational with many joins |
| access patterns are known and document-shaped | queries are ad hoc and change often (reporting) |
| you want flexible schema evolution | strong constraints and multi-table transactions are central |
| horizontal scaling via sharding is a primary need | a single primary plus replicas is enough (true for most apps) |

::: explain
"Indexes in MongoDB work like in SQL: without one, a query does a collection scan; with one, an index scan, and explain() shows which. Compound indexes follow the leftmost-prefix idea; the ESR rule, equality then sort then range, is a good guide. For analytics MongoDB uses the aggregation pipeline, a series of stages: $match to filter, $group to aggregate, $sort, $project, $unwind to flatten arrays and $lookup to join another collection. It's basically GROUP BY and JOIN expressed as steps. For modeling, I embed what is owned and read together, like order items, and reference what is shared or unbounded, like customers or comments."
:::

::: trap
- `$match` placed late in the pipeline: filter as early as possible so indexes can be used.
- Forgetting `$unwind` before grouping by array elements.
- `$lookup` everywhere: a sign that the model should embed more.
- Unique indexes treating missing fields as null.
- Indexing fields that are rarely queried (each index slows writes, as in SQL).
:::

::: questions
#### Basic
Q: [DEFINITION] What is the aggregation pipeline?
A: A sequence of stages ($match, $group, $sort, $project, $lookup…) through which documents flow and are filtered, grouped and transformed, MongoDB's equivalent of SQL GROUP BY and JOIN queries.

Q: [HOW] How do you create an index in MongoDB?
A: `db.collection.createIndex({ field: 1 })` (ascending) or with options, e.g. `{ unique: true }`.

Q: [DEFINITION] What does $lookup do?
A: It performs a left-outer-join-like operation, adding matching documents from another collection as an array field.

#### Intermediate
Q: [DEFINITION] What does $unwind do?
A: It deconstructs an array field so each element produces its own document, typically before grouping by array elements.

Q: [HOW] How do you check whether a query uses an index?
A: `explain("executionStats")`: look for IXSCAN vs COLLSCAN and compare totalDocsExamined with the number of results.

Q: [DEFINITION] What is a TTL index?
A: An index on a date field with `expireAfterSeconds`, which automatically deletes documents after that time, e.g. sessions or OTPs.

Q: [DEFINITION] What is a multikey index?
A: An index on an array field; MongoDB indexes each element so queries on array values can use it.

#### Scenario-based
Q: [SQL PROBLEM] Write the MongoDB equivalent of `SELECT city, COUNT(*) FROM customers GROUP BY city ORDER BY COUNT(*) DESC`.
A: `db.customers.aggregate([ { $group: { _id: "$city", count: { $sum: 1 } } }, { $sort: { count: -1 } } ])`.

Q: [DESIGN QUESTION] Model a hospital's patients and their visits in MongoDB.
A: `patients` documents with demographics and embedded allergies (small, owned); `visits` as a separate collection referencing `patient_id` (unbounded over time), indexed on `{ patient_id: 1, visit_date: -1 }`, possibly embedding a summary of the latest visit in the patient document for fast display.

#### Follow-up / Trap
Q: [TRAP QUESTION] Can you have two documents without an `email` field when `email` has a unique index?
A: Not with a normal unique index: both count as `null`, which is a duplicate. Use a partial index on documents where email exists.

Q: [TRAP QUESTION] Is the aggregation pipeline order important?
A: Yes. Stages run in order; filtering first ($match) reduces work and allows index use, and `$group` changes the document shape for later stages.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Write a query to find all products cheaper than 1000, showing only their names.

**P2.** Increase the stock of product 4 by 10.

**P3.** Delete all orders with status "PENDING".

#### Level 2 — Interview application
**P4.** Add the tag "vip" to customer 2 without creating duplicates if it already exists.

**P5.** Write an aggregation that counts orders per status.

**P6.** Find orders that contain a Wireless Mouse with quantity at least 2.

#### Level 3 — Scenario / problem solving
**P7.** Write an aggregation that returns each customer's name with their number of non-cancelled orders, using `$lookup`.

**P8.** Searches by `{ category, price }` with a sort on price are slow. Propose an index and explain the field order.
:::

::: answers
**P1.** `db.products.find({ price: { $lt: 1000 } }, { name: 1, _id: 0 })` → Wireless Mouse, Notebook Pack.

**P2.** `db.products.updateOne({ _id: 4 }, { $inc: { stock: 10 } })`

**P3.** `db.orders.deleteMany({ status: "PENDING" })` → deletedCount: 1 (order 115).

**P4.** `db.customers.updateOne({ _id: 2 }, { $addToSet: { tags: "vip" } })`. `$addToSet` creates the array if it is missing and skips duplicates.

**P5.**

```javascript
db.orders.aggregate([
  { $group: { _id: "$status", orders: { $sum: 1 } } },
  { $sort: { orders: -1 } }
])
// → { _id: 'DELIVERED', orders: 3 }, then CANCELLED: 1 and PENDING: 1
```

**P6.** Both conditions must hold for the **same** array element, so use `$elemMatch`:

```javascript
db.orders.find({ items: { $elemMatch: { name: "Wireless Mouse", qty: { $gte: 2 } } } })
// → order 101
```

**P7.**

```javascript
db.orders.aggregate([
  { $match: { status: { $ne: "CANCELLED" } } },
  { $group: { _id: "$customer_id", orders: { $sum: 1 } } },
  { $lookup: { from: "customers", localField: "_id", foreignField: "_id", as: "c" } },
  { $unwind: "$c" },
  { $project: { _id: 0, name: "$c.name", orders: 1 } },
  { $sort: { orders: -1 } }
])
// → { orders: 3, name: 'Aarav Patel' }, { orders: 1, name: 'Isha Kulkarni' }
```

**P8.** `db.products.createIndex({ category: 1, price: 1 })`. Equality field first (category), then the sort/range field (price), so MongoDB can jump to the category and read prices already in order, with no in-memory sort.
:::
