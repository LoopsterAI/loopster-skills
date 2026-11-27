---
name: scrape-website
description: Pull the content of web pages into a Loopster table in one step, with the Scrape Website template, priced first. Use when someone asks to scrape, pull or copy the text of these pages or URLs into a table. To research a company across the web (news, products, who they sell to), use company-brief.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Scrape website

One step: the text of given pages. For research across the web, use `company-brief`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **The URLs.** Full page URLs (a pricing page, a careers page). For a company's own subpages by domain, `predict-leads-website-subpages` is an alternative (see `references/data-routes.md`).
2. **Table:** the user's, or a blank one with Auto-run off and one `insert_rows` of the URLs.
3. **Column:** find the Scrape Website template with `list_column_templates` and read its `cost`. Not an AI web agent: a plain page fetch is enough for a known URL.
4. **Price** (pages · price · total), ask with the pricing sentence, then `trigger_rows` with the `rowIds`, `maxCostUsd` and an `idempotencyKey`. More than 10 pages: 1, then 10, then the rest.
5. **Named fields** (for example plan names and prices): an AI column without web search over the scraped text, priced the same way.
6. **Report** pages scraped, pages that failed and why, and the cost.

## Does not claim

- Content a page loads after sign-in or behind a script the fetch can't run.
