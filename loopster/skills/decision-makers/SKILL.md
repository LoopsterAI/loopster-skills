---
name: decision-makers
description: Find the people who decide or influence a purchase at companies the user names, in one free step: one people search inside the list of companies, with titles and seniority from what the user sells. Use when someone asks who to contact at these companies, who the buyers or decision makers are at these accounts, or for people at a list of domains. To build a prospect list from a target description (companies and people, exclusions, export), use prospect-list.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Decision makers

One step: named people at named companies. To build a whole prospect list from a description, use the `prospect-list` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Roles.** From what the user sells, write the buyer roles (who signs) and, if useful, influencers: 2 to 6 job titles plus seniority. Show them before searching. If the product is unclear, ask.
2. **Vocabulary once:** `list_search_filters` (see `references/icp-to-filters.md`).
3. **One search** for all companies: `search_people` with `specificCompanies` (domains match best, up to 1,000), the titles and seniority, `perCompanyLimit` = people per company (default 3). Never one search per company.
4. **Coverage.** Name the companies with nobody found. Try one wider search for those only (more titles, or seniority alone).
5. **Keep the results** the way the user wants: an answer in chat for a few, or a table with `create_table` (`type: "search"`, the `searchId`). Search and import are free.
6. **Report** per company who was found and their title, the companies with nobody, and the roles used. Offer `work-email` next.

## Does not claim

- Budget authority from a title, or that the person still works there (it is not a live check).
