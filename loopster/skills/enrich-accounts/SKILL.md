---
name: enrich-accounts
description: Fill in company fields (industry, employee count and range, revenue range, location, founded year, LinkedIn page) for a list of companies in one step, from the free Loopster Data company lookup. Use when someone asks to add industry, size or location to these domains or companies, quickly and for free. For paid fields (tech stack, open roles, funding, news), people, or a mix, use enrich-list.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Enrich accounts

One step: the free company lookup over a list of companies. For paid fields, people or a mix, use the `enrich-list` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Keys.** Domains match best (not `linkedin.com`, a parent group or a link shortener). Names without domains: find the domain with `search_companies` (`name`, free) and confirm on location or size.
2. **One call:** `loopster-data-enrich-company` with all domains (`run_capability`, up to 1,000 inputs, `maxCostUsd: 0`), or one column on the user's table run with `trigger_rows`. Never one call per domain.
3. **Keep the fields asked for:** name, industry, employee count and range, revenue range, HQ, founded year, LinkedIn URL (`references/data-routes.md`).
4. **Report** the fill rate per field and the domains not found. Save a CSV next to the original, or the columns in the table.
5. Fields this lookup doesn't have (tech stack, jobs, news, funding): say so and offer `enrich-list`, which prices them.

## Does not claim

- That a field is current: say the source.
- A value for a company not found: leave it empty, never guess.
