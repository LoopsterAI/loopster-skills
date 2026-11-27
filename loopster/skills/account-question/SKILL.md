---
name: account-question
description: Answer one yes/no question about every company in a list (for example which sell into healthcare, which have a free plan, which are building an AI team) in one step: free data first, AI web research only for unclear rows after measuring 3 and a yes. Use when someone asks which of these companies do or have something. For a full research brief, use company-brief.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Account question

One step: one question, an answer per company. For a full brief, use `company-brief`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **The question** as one line with a yes/no/unknown answer. Agree on it before running.
2. **Free data first:** `loopster-data-enrich-company` (industry, description) answers many questions for free. Mark yes or no where the data is clear.
3. **Cheaper text next:** website text (`predict-leads-website-subpages`, see `references/data-routes.md`) plus an AI column without web search, for the unclear rows, priced and asked.
4. **AI web research last**, on the rows still unclear: run 3 rows with `maxCostUsd` (the request covers that test), read the real cost, then ask for the rest with the measured figure.
5. **Answer** yes, no or unknown per company, each with its source (the data field or a URL).
6. **Report** counts per answer and the cost.

## Does not claim

- More than the sources show: "unknown" is an answer.
