---
name: linkedin-profile
description: Find the LinkedIn profile URL of people the user names, in one step: free routes first (Loopster Data from an email, the people search from name and company), paid lookups only for the misses. Use when someone asks for LinkedIn URLs or profiles of these people, or to fill a LinkedIn column. For full profiles, current titles and company data on a list, use enrich-list.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# LinkedIn profile

One step: the profile URL. For current title, company and other fields on a whole list, use `enrich-list`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Split the people** by what they have: an email, or name + company (domain best), or neither (say how many).
2. **With an email:** `loopster-data-email-to-linkedin` on all of them in one call (free, `maxCostUsd: 0`).
3. **With name + company:** `search_people` with `personName` and `specificCompanies`, about 25 people per call (free). Accept a match only when the company matches too. Two profiles at the same company, or only an initial for a surname: mark it **ambiguous**, don't pick one.
4. **Misses only, priced first:** `surfe-find-profile` (name + company) or `icypeas-email-to-linkedin` (email) from `references/routes.md`. Show the price and ask.
5. Never use an AI web research column (`find-linkedin-url`, `ai-web`) before these routes. It is for the few rows they can't answer, after measuring 3 rows and asking.
6. **Report** found, not found and ambiguous, and the cost (zero when only free routes ran).

## Does not claim

- That the profile is current: the person may have moved since.
- A match on the name alone.
