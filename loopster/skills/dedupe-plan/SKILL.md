---
name: dedupe-plan
description: Find duplicate contacts or companies in a list or Loopster table and propose a merge plan (which records are the same, which to keep and why), in one free step that deletes nothing. Use when someone asks to find duplicates, dedupe a list or CRM export, or which records are the same. Applying the plan is a separate step the user approves.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Dedupe plan

One step: a plan, not a change. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Read once:** the file, or the table with one `list_rows` over the key columns.
2. **Normalise** without changing the data: lower-case emails and domains, trim spaces, drop `www.` and trailing slashes, strip common company suffixes (Inc, Ltd, GmbH).
3. **Group** rows that match on email; then name + company; then domain for companies. Give each group a reason (same email, same name and company).
4. **Keeper per group:** the most complete or most recent record, with a one-line why. Show which values the keeper would take from the others.
5. **Show the plan** (group · rows · keeper · reason) and counts. Write it to a new column or a CSV if asked.

Never delete, merge or overwrite anything. Applying the plan is a separate yes, and deletion stays with the user.

## Does not claim

- That two people with the same name are the same person without a second match (email, company).
