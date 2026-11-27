---
name: company-brief
description: Write a short, sourced research brief on a few companies in one step, with one AI web research run capped and priced first. Use when someone asks for a brief, a summary, research or background on these companies before a call or outreach. For data fields across a list, use enrich-list or enrich-accounts.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Company brief

One step: a short brief per company from web research. For data fields on a list, use `enrich-accounts` or `enrich-list`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Free facts first:** `loopster-data-enrich-company` for every domain (free). The brief builds on these and doesn't pay to research what is already known.
2. **Cheaper text before the web agent:** website text (`predict-leads-website-subpages`, see `references/data-routes.md`) plus an AI column without web search often answers "what they do, who they sell to". Offer it first.
3. **AI web research** (`ai-web` as a column or capability) when the user wants news or depth. Prompt with fixed keys: `what_they_do`, `who_they_sell_to`, `products`, `size_and_location`, `recent_news` (with dates), `sources` (URLs). Say "unknown" rather than guess.
4. **Cap and measure.** Up to 3 companies: the request covers the run, so run it with `maxCostUsd` and an `idempotencyKey`. More: run 3, read the real cost (`get_usage`), then ask for the rest with the measured figure.
5. **Show** each brief with its sources, and the real cost.

## Does not claim

- That every fact is right: the sources are listed so a person can check.
- Private data (a private company's revenue, internal plans).
