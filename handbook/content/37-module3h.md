## Session 3.12 — Module 3 Summary & Rapid Revision {: #s3-12 }

::: summary Module 3 Summary
#### Most important concepts
- **Query anatomy:** SELECT … FROM … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT. Logical order: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT.
- **NULL** means unknown: use `IS NULL`; aggregates ignore NULLs; `COUNT(*)` counts rows; `NOT IN` with NULLs returns nothing.
- **DDL** (CREATE, ALTER, DROP, TRUNCATE) vs **DML** (INSERT, UPDATE, DELETE) vs **DCL** (GRANT, REVOKE) vs **TCL** (COMMIT, ROLLBACK, SAVEPOINT).
- **WHERE vs HAVING:** rows before grouping vs groups after grouping.
- **Joins:** INNER (matches only), LEFT/RIGHT (keep one side), FULL (keep both), CROSS (every combination), self join (a table with itself); anti-join with LEFT JOIN … IS NULL or NOT EXISTS.
- **Subqueries and CTEs:** scalar, multi-row, derived tables, correlated; WITH for readable steps; recursive CTEs for hierarchies.
- **Window functions:** OVER (PARTITION BY … ORDER BY …); ROW_NUMBER vs RANK vs DENSE_RANK; LAG/LEAD; running totals and moving averages; filter results in an outer query.
- **Indexes:** B-tree, faster reads and slower writes; selectivity; composite index leftmost-prefix rule; clustered vs non-clustered (PostgreSQL tables are heaps).
- **Transactions:** all or nothing; ACID; isolation levels vs dirty, non-repeatable and phantom reads; PostgreSQL defaults to Read Committed.

#### What to memorize
- ROW_NUMBER 1,2,3,4 · RANK 1,2,2,4 · DENSE_RANK 1,2,2,3.
- DELETE (DML, WHERE, slower, rollback) · TRUNCATE (DDL, all rows, fast) · DROP (removes the table).
- ACID = Atomicity, Consistency, Isolation, Durability.
- Isolation levels and the anomalies each one prevents.

#### What to understand
- Why aliases fail in WHERE but work in ORDER BY.
- Why a WHERE on the right table breaks a LEFT JOIN.
- Why fan-out inflates sums after joins.
- Why the optimizer may ignore an index.

#### Most common interview questions
- Second / Nth highest salary · duplicates (find and delete) · customers without orders · top N per group · latest record per user · running totals · WHERE vs HAVING · join types · DELETE vs TRUNCATE vs DROP · what is an index · ACID · isolation levels.

#### Common mistakes
- `= NULL` · AND/OR without parentheses · integer division · `COUNT(*)` with LEFT JOIN · ROW_NUMBER for Nth highest *value* · window functions in WHERE · indexing everything · forgetting COMMIT/ROLLBACK.
:::

::: checklist
- [ ] I can write SELECT with WHERE, ORDER BY, LIMIT and aliases
- [ ] I handle NULL correctly (IS NULL, COALESCE, COUNT)
- [ ] I know the string, date and numeric functions I need
- [ ] I can write CASE WHEN and conditional aggregation
- [ ] I can explain DDL vs DML vs DCL vs TCL
- [ ] I can compare DELETE, TRUNCATE and DROP
- [ ] I can write INSERT, UPDATE, DELETE and an upsert
- [ ] I can use GROUP BY with HAVING correctly
- [ ] I can recite the logical order of execution
- [ ] I can write every join type and explain the results
- [ ] I can write an anti-join two different ways
- [ ] I can write scalar, correlated and EXISTS subqueries
- [ ] I can avoid the NOT IN + NULL trap
- [ ] I can structure a query with CTEs
- [ ] I can explain a recursive CTE
- [ ] I can explain ROW_NUMBER vs RANK vs DENSE_RANK
- [ ] I can use LAG/LEAD and running totals
- [ ] I can solve Nth highest, top N per group and latest per user
- [ ] I can explain how a B-tree index speeds up reads
- [ ] I know when indexes hurt, and the leftmost-prefix rule
- [ ] I can explain clustered vs non-clustered indexes
- [ ] I can explain ACID with a bank example
- [ ] I can explain dirty, non-repeatable and phantom reads
- [ ] I know the isolation levels and PostgreSQL's default
:::
