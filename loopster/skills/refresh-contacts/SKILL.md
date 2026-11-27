---
name: refresh-contacts
description: Check whether the people on an old contact list still work where the list says, in one step: the free Loopster Data person lookup first, a verdict per person (same, title changed, moved, unknown), and no change written without a yes. Use when someone asks to refresh, re-check or update an old contact list or CRM export, or whether these people are still at their companies. To watch past champions over time, use champion-tracker.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Refresh contacts

One step: compare the list with fresh data, once. To keep watching people over time, use `champion-tracker`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Load once.** A file goes into a new table with Auto-run off (`insert_rows`), or read the user's table once.
2. **LinkedIn URLs first** for people who lack one: `loopster-data-email-to-linkedin` or `search_people` (`personName` + `specificCompanies`), both free.
3. **Free lookup:** `loopster-data-enrich-person` on every URL (free, `maxCostUsd: 0`). Its profiles refresh about every 55 days.
4. **Verdict per person**: **same**, **title changed**, **moved** (new company), **unknown** (no lookup). Write it into one manual column with one `update_cells`.
5. **Paid live profile** (`enrich-professional-profile`, see `references/routes.md`) only for the unknowns, or if the user asks for today's data. Price it and ask first.
6. **Apply only on a yes.** Show the changes as a list; write new titles or companies with one `update_cells` after the user agrees. Never overwrite the user's columns on your own.
7. **Report** counts per verdict and the cost. Offer `work-email` for the movers.

## Does not claim

- A move the profile doesn't show yet: profiles lag.
- That "same" is confirmed by the person: it means the lookup agrees.
