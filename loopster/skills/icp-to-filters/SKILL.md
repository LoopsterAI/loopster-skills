---
name: icp-to-filters
description: Turn an ideal customer profile written in plain words into Loopster search filters that run, and give one count, in one free step. Use when someone asks to turn this ICP into filters, what filters to use, or how to search for their target companies or people. To build the list itself (people, exclusions, export), use prospect-list; for a market count by slices, use market-size.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# ICP to filters

One step: plain words to filters, plus one count. To build the list, use the `prospect-list` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Vocabulary once:** `list_search_filters`. Values must come from its options.
2. **Map each part** of the ICP to a filter with `references/icp-to-filters.md`: industries (several neighbouring ones), size band, location of the company or the person, titles and seniority for people.
3. **Name the gaps:** parts with no filter (for example "selling to finance teams") stay out of the filters. Say so, and say how they could be checked later (an AI question on the results, `account-question`).
4. **One count:** `search_companies` or `search_people` with the filters and a small `limit`, and read the total. Search is free.
5. **Show** the filters as JSON and a plain table (ICP words · filter · values), the count, and the gaps.

No import and no table unless the user asks: that is `prospect-list`.

## Does not claim

- That the count is the whole market: it is Loopster's coverage.
