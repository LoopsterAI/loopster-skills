---
name: hiring-signals
description: See which companies are hiring for a given team right now, in one step: job postings filtered by title keywords and a recent window, priced per company and agreed first, ranked by open roles. Use when someone asks which of these accounts are hiring engineers, SDRs or another team, or for open roles at a list of companies. To turn hiring into outreach with openers, use signal-outbound.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Hiring signals

One step: open roles per company for one team. For outreach with openers, use the `signal-outbound` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **The team** as title keywords (for engineers: "software engineer", "backend", "frontend", "data engineer"…) and a window (default: posted in the last 90 days, active only). Show them.
2. **Job postings:** `predict-leads-find-jobs` with `title_keywords`, `posted_within_days` and `active_only` (see `references/signal-recipes.md`, "Hiring for roles you serve"), as a table column or capability with `execution_mode: "managed"`.
3. **Price per company** (live `cost`), ask with the pricing sentence. Run 1, then 10, then the rest, `maxCostUsd` and `idempotencyKey`.
4. **Rank** by matching open roles (`count`). Companies with none: say so.
5. **Report** the ranked counts, companies not matched, and the cost. Openers or messages only if asked (`signal-outbound`).

## Does not claim

- That a posted role is really open: postings stay up after a hire.
- A trend from one run.
