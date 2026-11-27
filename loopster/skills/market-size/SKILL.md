---
name: market-size
description: Size a market in one free step: how many companies or people match a profile, broken down by slices such as country, size or industry, with count-only searches. Use when someone asks how many companies match, how big the market is, or for counts by country, size or industry. To build the list itself, use prospect-list.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Market size

One step: counts, no list. To build the list, use the `prospect-list` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Filters** from the description (`list_search_filters` once, `references/icp-to-filters.md`).
2. **Count only:** one `search_companies` (or `search_people`) per slice with a small `limit`, reading the total. Searches are free. At most one call per slice; for many slices, say how many calls it takes first.
3. **Table:** slice · count, plus the total. Check the slices add up to the total; say why if not (overlap, unknown values).
4. **Say what the count is:** companies in Loopster's data that match, not the whole market.

No import and no table unless the user asks.

## Does not claim

- Revenue or spend per company: these are counts.
