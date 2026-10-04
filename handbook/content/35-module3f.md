## Session 3.10 — Transactions and ACID {: #s3-10 }

[HIGH PRIORITY] "What is ACID?" is one of the most common DBMS questions, and PwC write-ups mention it by name.

### Simple meaning

**A transaction is a group of database operations that must succeed or fail together, as one unit.** Either *all* of its changes are saved, or *none* are.

The classic example is a bank transfer of ₹5000 from Aarav to Isha. It is two updates: debit Aarav, credit Isha. If the system crashes between them, money must not vanish (debited but never credited) or appear from nowhere.

[[fig:transaction_transfer | A transfer as one transaction: COMMIT saves both updates together; any failure rolls both back.]]

### COMMIT and ROLLBACK in action

```sql run
BEGIN;
UPDATE accounts SET balance = balance - 5000 WHERE account_id = 1;   -- debit Aarav
UPDATE accounts SET balance = balance + 5000 WHERE account_id = 2;   -- credit Isha
COMMIT;

SELECT account_id, holder_name, balance FROM accounts ORDER BY account_id;
```

::: linebyline
| Line | What happens |
|---|---|
| `BEGIN;` | start a transaction: changes are now provisional |
| first `UPDATE` | Aarav's balance drops by 5000, visible only inside this transaction |
| second `UPDATE` | Isha's balance rises by 5000 |
| `COMMIT;` | both changes become permanent and visible to everyone, at the same instant |
:::

Now a transfer that must fail: Kabir has only ₹5000 and tries to send ₹6000. The `CHECK (balance >= 0)` constraint rejects the debit, and the transaction is aborted:

```sql run error
BEGIN;
UPDATE accounts SET balance = balance + 6000 WHERE account_id = 2;   -- credit Isha first
UPDATE accounts SET balance = balance - 6000 WHERE account_id = 3;   -- debit Kabir: violates CHECK
COMMIT;
```

The credit to Isha had already succeeded, but because the transaction failed, it is undone as well. Nobody else ever saw it:

```sql run
SELECT account_id, holder_name, balance FROM accounts ORDER BY account_id;
```

After an error inside a transaction, PostgreSQL rejects every further command with *"current transaction is aborted, commands ignored until end of transaction block"* until you issue `ROLLBACK` (or `ROLLBACK TO SAVEPOINT`, Session 3.4).

**Autocommit:** outside an explicit `BEGIN`, PostgreSQL treats each single statement as its own transaction and commits it immediately. Applications and frameworks (for example Spring's `@Transactional`) open explicit transactions when several statements must succeed together.

### ACID: the four guarantees

| Property | Simple meaning | Bank-transfer example | How databases provide it |
|---|---|---|---|
| **Atomicity** | all or nothing | both the debit and the credit happen, or neither does | undo information and the write-ahead log (WAL) let the DB roll back incomplete work |
| **Consistency** | every transaction moves the database from one valid state to another | the balance never goes negative; total money is unchanged | constraints (CHECK, FK, UNIQUE), triggers, and correct application logic |
| **Isolation** | concurrent transactions don't see each other's half-finished work | a report running during the transfer never sees "money in neither account" | locks and MVCC snapshots; isolation levels control how strict this is |
| **Durability** | once committed, it survives crashes and power cuts | after "Transfer successful", a server crash does not undo it | the WAL is flushed to disk before COMMIT returns; replicas and backups add more safety |

::: tip A memory hook
**A**ll or nothing · **C**orrect state · **I**ndependent of others · **D**on't lose it.
:::

::: trap Two different "consistency"s
**ACID consistency** means "the data obeys its rules (constraints)". **CAP consistency** (Session 4.3) means "every node in a distributed system returns the latest write". Interviewers sometimes check whether you mix them up.
:::

### What goes wrong without isolation: the read anomalies

When many transactions run at the same time, three classic problems can occur. Read each table top to bottom as time passes.

**1. Dirty read**: reading data another transaction has **not committed yet**.

| Time | Transaction A | Transaction B |
|---|---|---|
| 1 | `UPDATE accounts SET balance = 0 WHERE account_id = 1;` (not committed) | |
| 2 | | `SELECT balance … WHERE account_id = 1;` → **0** (dirty) |
| 3 | `ROLLBACK;` (balance is 50000 again) | |
| 4 | | B made a decision based on a value that never really existed |

**2. Non-repeatable read**: reading the **same row twice** in one transaction and getting **different values**, because another transaction committed a change in between.

| Time | Transaction A | Transaction B |
|---|---|---|
| 1 | `SELECT balance … id 1;` → 50000 | |
| 2 | | `UPDATE … SET balance = 45000 WHERE id = 1; COMMIT;` |
| 3 | `SELECT balance … id 1;` → **45000**: the same query gives a different answer | |

**3. Phantom read**: running the **same range query twice** and getting **new or missing rows**, because another transaction inserted or deleted rows that match.

| Time | Transaction A | Transaction B |
|---|---|---|
| 1 | `SELECT COUNT(*) FROM orders WHERE status = 'PENDING';` → 2 | |
| 2 | | `INSERT INTO orders (…, 'PENDING'); COMMIT;` |
| 3 | `SELECT COUNT(*) … 'PENDING';` → **3**: a "phantom" row appeared | |

**Lost update** [INTERVIEW EXTENSION]: two transactions read the same value, both compute a new value from it, and the second write overwrites the first. Two cashiers both read stock = 10 and both write 9 after selling one item each, so the stock should be 8 but shows 9.

### Isolation levels

The SQL standard defines four isolation levels. Stricter levels prevent more anomalies but allow less concurrency.

| Isolation level | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| Read Uncommitted | possible | possible | possible |
| **Read Committed** (PostgreSQL default) | prevented | possible | possible |
| Repeatable Read | prevented | prevented | possible (by the standard) |
| Serializable | prevented | prevented | prevented |

**PostgreSQL specifics** (good to mention):

- **Read Committed is the default.** Each *statement* sees data committed before that statement began.
- **Read Uncommitted behaves like Read Committed**: PostgreSQL never allows dirty reads.
- **Repeatable Read** gives the whole transaction one snapshot, and in PostgreSQL it **also prevents phantoms**, which is stronger than the standard requires.
- **Serializable** behaves as if transactions ran one after another. If that is impossible, one transaction fails with a *serialization failure*, and the application must **retry** it.
- MySQL InnoDB's default is Repeatable Read; SQL Server's and Oracle's default is Read Committed.

```sql run
SHOW transaction_isolation;
```

Choosing a level for a transaction:

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- ... statements that must see one consistent snapshot, e.g. a multi-step report
COMMIT;
```

### MVCC: how PostgreSQL isolates without blocking readers [INTERVIEW EXTENSION]

PostgreSQL uses **MVCC (Multi-Version Concurrency Control)**: an UPDATE does not overwrite a row in place; it writes a **new version** of the row. Each transaction reads the versions that were committed as of its snapshot. As a result:

- **readers never block writers, and writers never block readers**;
- old row versions are later cleaned up by **VACUUM** (autovacuum runs this automatically).

Writers that change the **same row** still have to wait for each other (row locks).

### Locks, SELECT … FOR UPDATE and deadlocks [INTERVIEW EXTENSION]

To prevent lost updates in read-then-write logic, lock the row while you work with it:

```sql run
BEGIN;
SELECT account_id, balance
FROM accounts
WHERE account_id = 1
FOR UPDATE;              -- other transactions that try to lock or update this row now wait
UPDATE accounts SET balance = balance - 1000 WHERE account_id = 1;
COMMIT;
```

Simpler still: make the update **atomic** in one statement (`SET balance = balance - 1000 WHERE balance >= 1000`), so there is no gap between reading and writing.

**Optimistic locking** (common in web apps): keep a `version` column and update only if nobody changed the row since you read it: `UPDATE … SET …, version = version + 1 WHERE id = 7 AND version = 3;`. If it updates 0 rows, someone else got there first, so reload and retry.

A **deadlock** happens when two transactions each hold a lock the other needs:

| Time | Transaction A | Transaction B |
|---|---|---|
| 1 | locks account 1 | locks account 2 |
| 2 | waits for account 2… | waits for account 1… |
| 3 | PostgreSQL detects the cycle and aborts one transaction with a deadlock error | |

**Prevention:** always lock rows in the same order (e.g. lower account_id first), keep transactions short, and retry when a deadlock error occurs.

::: project Transactions in a real application
In a Spring Boot service, a method annotated with `@Transactional` runs inside one database transaction: if it throws an exception, everything is rolled back. Two habits interviewers like: keep transactions **short**, and never wait on a slow external call (such as a payment gateway) while holding database locks inside a transaction. Call the external service first, or use a pattern like a status column plus a retry job.
:::

::: explain
"A transaction groups operations into one unit that either fully succeeds or fully fails, like a bank transfer that debits one account and credits another. ACID describes its guarantees: Atomicity means all or nothing; Consistency means the database moves from one valid state to another, with constraints enforced; Isolation means concurrent transactions don't see each other's uncommitted work; and Durability means once committed, the change survives a crash, because it's written to the log on disk first. Isolation levels trade strictness for concurrency: Read Committed, PostgreSQL's default, prevents dirty reads; Repeatable Read also prevents non-repeatable reads; and Serializable prevents phantoms too."
:::

::: trap
- Saying "Consistency means all replicas agree". That is CAP consistency, not ACID.
- Claiming PostgreSQL supports dirty reads at Read Uncommitted. It does not.
- Thinking a single UPDATE needs BEGIN/COMMIT to be atomic. Every single statement is already atomic (autocommit).
- Forgetting to ROLLBACK after an error inside a transaction (PostgreSQL ignores further commands).
- Long transactions holding locks while waiting for user input or external APIs.
- Mixing up non-repeatable reads (a changed *row*) and phantom reads (new or missing *rows* in a range).
:::

::: questions
#### Basic
Q: [DEFINITION] What is a transaction?
A: A sequence of database operations executed as a single unit of work: either all changes are committed or all are rolled back.

Q: [DEFINITION] What is ACID?
A: Atomicity (all or nothing), Consistency (valid state to valid state, constraints respected), Isolation (concurrent transactions don't interfere) and Durability (committed data survives failures).

Q: [COMPARISON] COMMIT vs ROLLBACK?
A: COMMIT makes the transaction's changes permanent and visible; ROLLBACK discards all changes made since the transaction began.

#### Intermediate
Q: [DEFINITION] What is a dirty read?
A: Reading data written by another transaction that has not committed yet, which might later be rolled back.

Q: [COMPARISON] Non-repeatable read vs phantom read?
A: A non-repeatable read is the same row returning a different value on a second read (an update by someone else); a phantom read is the same range query returning extra or missing rows (an insert or delete by someone else).

Q: [DEFINITION] What are the isolation levels and PostgreSQL's default?
A: Read Uncommitted, Read Committed, Repeatable Read and Serializable; PostgreSQL defaults to Read Committed (and treats Read Uncommitted as Read Committed).

Q: [HOW] How does a database guarantee durability?
A: It writes changes to a write-ahead log and flushes it to stable storage before confirming COMMIT, so after a crash it can replay the log; replication and backups add protection against disk loss.

Q: [DEFINITION] What is a deadlock and how is it resolved?
A: Two transactions each wait for a lock held by the other. The database detects the cycle and aborts one of them; applications should retry and acquire locks in a consistent order.

#### Scenario-based
Q: [SCENARIO] Two users book the last seat on a flight at the same moment and both succeed. What went wrong and how do you fix it?
A: A race condition, i.e. a lost update or check-then-act problem. Fix it with an atomic conditional update (`UPDATE seats SET booked_by = ? WHERE seat_id = ? AND booked_by IS NULL`, then check the row count), with `SELECT … FOR UPDATE` inside a transaction, or with a unique constraint on (flight_id, seat_no).

Q: [SCENARIO] A month-end report runs several queries and the totals don't add up because orders keep arriving. What do you do?
A: Run the report in one transaction at REPEATABLE READ (or SERIALIZABLE) so every query sees the same snapshot, or run it on a replica or warehouse snapshot.

Q: [DESIGN QUESTION] In an e-commerce checkout, which steps belong in one transaction?
A: Creating the order and its items, decrementing stock, and recording the payment reference, all in one transaction. The external payment call and email sending should stay outside the database transaction, with status columns and retries to coordinate them.

#### Follow-up / Trap
Q: [TRAP QUESTION] Is a single UPDATE statement atomic without BEGIN?
A: Yes. In autocommit mode each statement is its own transaction, so either all rows it targets are updated or none are.

Q: [TRAP QUESTION] Does Serializable isolation mean transactions literally run one at a time?
A: No. They run concurrently, but the database guarantees the result equals *some* serial order, aborting transactions (serialization failures) when that can't be guaranteed.

Q: [TRAP QUESTION] Can NoSQL databases be ACID?
A: Some can. MongoDB supports multi-document ACID transactions, and many others offer per-record atomicity. "NoSQL means no transactions" is outdated.
:::

::: practice
#### Level 1 — Basic understanding
**P1.** Expand ACID and give a one-line meaning for each letter.

**P2.** Which isolation level is PostgreSQL's default?

**P3.** What happens to uncommitted changes if the database server crashes?

#### Level 2 — Interview application
**P4.** Write a transaction that moves ₹2000 from Isha (account 2) to Kabir (account 3) and then shows all balances.

**P5.** Explain, with a timeline, how a lost update can happen when two sessions run `SELECT stock` and then `UPDATE stock = old_value - 1`.

#### Level 3 — Scenario / problem solving
**P6.** A wallet app must never let a balance go negative, even with simultaneous withdrawals. Give two database-level protections.

**P7.** A nightly job updates 2 million rows inside one huge transaction and blocks other users for an hour. How would you redesign it?
:::

::: answers
**P1.** Atomicity: all changes or none. Consistency: data stays valid according to its rules. Isolation: concurrent transactions don't see each other's unfinished work. Durability: committed changes survive crashes.

**P2.** Read Committed.

**P3.** They are lost (rolled back) during crash recovery; only committed transactions are restored from the write-ahead log.

**P4.**

```sql run
BEGIN;
UPDATE accounts SET balance = balance - 2000 WHERE account_id = 2;
UPDATE accounts SET balance = balance + 2000 WHERE account_id = 3;
COMMIT;

SELECT account_id, holder_name, balance FROM accounts ORDER BY account_id;
```

**P5.** Stock = 10. Session A reads 10; session B reads 10; A writes 9 and commits; B writes 9 and commits. Two items were sold, but the stock shows 9 instead of 8: A's update was lost. Fix it with an atomic `UPDATE … SET stock = stock - 1 WHERE stock > 0`, with `SELECT … FOR UPDATE`, or with optimistic locking on a version column.

**P6.** (1) A `CHECK (balance >= 0)` constraint, so any update that would go negative fails and its transaction rolls back. (2) An atomic conditional update, `UPDATE wallets SET balance = balance - :amt WHERE id = :id AND balance >= :amt`, then check that exactly 1 row was updated. Row locks (`SELECT … FOR UPDATE`) or SERIALIZABLE isolation with retries are further options.

**P7.** Process in batches (for example 10,000 rows per transaction, keyed by id ranges) so locks are short and progress is saved; run during low traffic; make the job idempotent so a failed batch can be re-run; consider writing to a new table and swapping it in for very large changes.
:::
