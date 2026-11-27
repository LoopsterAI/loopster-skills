---
name: lead-score
description: Score and grade leads already in a Loopster table (A to D) in one step, from the fields they have, with the weights shown and the grade written into one column. Use when someone asks to score, grade or rank these leads or the rows in a table. For inbound routing (enrich, score and alert as leads arrive), use inbound-router.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Lead score

One step: a grade per row from what the table already holds. For live inbound routing, use the `inbound-router` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Read the columns once** (`get_table`), and one page of rows to see the values.
2. **Rules from the fields present:** seniority, title words, company size, industry, location. Show the weights (for example seniority 35, title match 30, size 20, industry 15) and the grade bands (A 80+, B 60–79, C 40–59, D below 40) before writing.
3. **Write one column:** a Formula column over existing columns (free), or the grades with one `update_cells`.
4. **Missing fields** lower the score and are named. Offer free enrichment (`loopster-data-enrich-person`, `loopster-data-enrich-company`) to fill them; paid enrichment only if asked, priced first.
5. **Report** counts per grade and the top rows.

## Does not claim

- That a grade predicts a reply: it ranks the data you have.
