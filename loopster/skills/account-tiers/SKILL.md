---
name: account-tiers
description: Sort a list of accounts into tiers 1 to 4 against the user's ideal customer profile in one step, from free data first, with visible weights and a reason per tier. Use when someone asks to tier, rank or prioritise these accounts against their ICP. For scoring inbound leads, use lead-score; to find new accounts, use prospect-list.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Account tiers

One step: tiers for accounts the user already has. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **The ICP** from the user or `loopster-context.md`: the 3 to 5 things that matter (industry, size, location, a tool or signal).
2. **Free data first:** `loopster-data-enrich-company` on every domain (free) for industry, size and location. Paid fields (tech stack, hiring) only if the ICP needs them: price per account and ask (`references/data-routes.md`).
3. **Weights.** Show a small table (criterion · weight · how it's met) before tiering, for example industry match 40, size in range 30, location 20, extra signal 10.
4. **Tier** with a Formula column or one `update_cells`: 1 = 80+, 2 = 60–79, 3 = 40–59, 4 = below 40, plus a one-line reason per account.
5. **Report** counts per tier and the top accounts. Unknown fields lower the score and are named, never guessed.

No AI web research per row without a price and a yes.

## Does not claim

- That a tier predicts a deal: it is the ICP fit on the data found.
