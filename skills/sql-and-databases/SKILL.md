---
name: sql-and-databases
description: Use when designing schemas, writing queries, or managing database migrations.
---

# SQL and Databases

## Purpose
Design schemas and queries that stay correct, fast, and safe as data grows — driven by how the data is actually read and written.

## When to use
- Designing or changing a table schema, column, or relationship.
- Writing, reviewing, or tuning a query.
- Adding or running a database migration.

When NOT to use: a throwaway query against scratch data with no schema, security, or scale concern. Don't pre-optimize a table nobody queries yet.

## Method
1. Model for access patterns. Shape tables around how data is queried and written, not an abstract diagram.
2. Parameterize every query. Bind values as parameters — never build SQL by string concatenation. This closes injection and lets the planner reuse plans.
3. Index what you filter and join on. Add indexes for columns in WHERE, JOIN, and ORDER BY; drop ones nothing uses.
4. Enforce invariants in the schema. Use NOT NULL, UNIQUE, FOREIGN KEY, and CHECK so bad data can't exist, regardless of app bugs.
5. Avoid N+1 access. Fetch related rows in one query (join or batch) instead of looping a query per row.
6. Bound result sets. Paginate or LIMIT anything that can grow; never load an unbounded table into memory.
7. Write reversible migrations. Give every migration a tested down path and keep schema changes compatible with in-flight code.
8. EXPLAIN slow queries. Read the plan; fix full scans and missing indexes with evidence, not guesses.

## Red flags
- SQL assembled by string concatenation or interpolation of input.
- Queries inside a loop where one join or batch would do.
- Filtering or joining on an unindexed column at scale.
- SELECT with no LIMIT over a table that grows without bound.
- Invariants enforced only in app code, leaving the DB able to hold bad data.
- A migration with no down path, or one that rewrites a live table with no rollout plan.

## Checklist
- [ ] Schema matches real read/write access patterns.
- [ ] All queries parameterized — no string-built SQL.
- [ ] Columns used in WHERE/JOIN/ORDER BY are indexed.
- [ ] Key invariants enforced by DB constraints.
- [ ] No N+1; related data fetched in one round trip.
- [ ] Collections paginated or bounded.
- [ ] Migration has a tested, reversible down path.
- [ ] Slow queries checked with EXPLAIN.
