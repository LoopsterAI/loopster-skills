---
name: record-audit
description: Audit company records (from a CRM export or a Loopster table) against fresh data in one step: the free Loopster Data company lookup, a flag per mismatch with the fresh value, and no change without a yes. Use when someone asks to check, audit or validate company names, industries, sizes or locations on a list. For people records, use refresh-contacts; for a whole CRM audit with write-back, use crm-manager.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Record audit

One step: compare company records with fresh data, once. For people, use `refresh-contacts`; for a CRM audit with write-back, use the `crm-manager` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Fields to check:** the ones the team relies on (name, industry, employee range, country). Agree on them.
2. **Free lookup:** `loopster-data-enrich-company` on every domain in one call (free, `maxCostUsd: 0`; see `references/data-routes.md`).
3. **Compare** per field: **match**, **differs** (with the fresh value), **no data**. Normalise first (case, suffixes like Inc or Ltd), so "Stripe, Inc." and "Stripe" match.
4. **Show** mismatches as record · field · on record · fresh value, and counts per field.
5. **Apply only on a yes**: write fresh values with one `update_cells` after the user agrees. Never overwrite on your own.

## Does not claim

- That the fresh value is right and the record wrong: it shows they differ, and the source.
