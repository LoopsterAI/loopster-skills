---
name: headcount-growth
description: Measure how fast companies are growing or shrinking by headcount, in one step: one priced headcount source, growth bands, and companies without data reported as no data. Use when someone asks which accounts are growing fastest, who is hiring the most, or for headcount trends on a list. For hiring signals turned into outreach, use signal-outbound.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Headcount growth

One step: headcount and its growth per company. For outreach on top of it, use the `signal-outbound` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Free headcount now:** `loopster-data-enrich-company` gives the current employee count (free). Growth over time needs a paid source.
2. **Growth source:** the professional-network company headcount route (see `references/data-routes.md`), as a table column with `execution_mode: "managed"`. Read the live `cost`.
3. **Ask before the first paid row.** This source is not AI web research, so the request doesn't cover a test: show the price for 3 rows and for all companies, and ask with the pricing sentence.
4. **On a yes, 3 rows first** to see which periods the growth comes in. If they have no growth data, stop, say the source has none for these companies, and offer a proxy (open roles per 100 staff, `hiring-signals`). Otherwise 10, then the rest.
5. **Bands** (default: below −5% shrinking, −5% to +5% flat, +5% to +20% growing, above +20% fast-growing). Write them into one column with one `update_cells`.
6. **Report** counts per band, the fastest growers, the companies with no growth data (as "no data", never "flat"), and the cost.

## Does not claim

- Why a company grew or shrank.
- Growth the source doesn't report.
