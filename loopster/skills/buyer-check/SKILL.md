---
name: buyer-check
description: Mark each person in a Loopster table as buyer, influencer or not a buyer for what the user sells, in one step: rules from title and seniority first (free), an AI column only for unclear rows after a price and a yes. Use when someone asks who in this list would buy, who the buyers or influencers are, or to filter out people who wouldn't buy. To find buyers at companies, use decision-makers.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Buyer check

One step: a label per person already in a table. To find people at companies, use `decision-makers`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **What is sold** and to whom (ask if unclear). Write the buyer titles, the influencer titles, and titles that are never buyers.
2. **Rules first (free):** label from title and seniority with a Formula column or one `update_cells`: **buyer**, **influencer**, **not a buyer**, or **unclear**. Add a persona label (for example "Sales leader") and a confidence (high on an exact title match, medium on seniority alone).
3. **Unclear rows only:** an AI column without web search on title + company. Price it on those rows (measure 10 rows, or 4 × the estimate until measured), ask with the pricing sentence, then run with `maxCostUsd`.
4. **Report** counts per label and a few examples of each.

## Does not claim

- Budget authority: a title is the best signal in the data, not an org chart.
