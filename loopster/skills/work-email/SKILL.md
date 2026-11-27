---
name: work-email
description: Find the work email of a few named people, or of the people in one table column, in one step: the free Loopster Data lookup first, then one paid finder only for the people it missed, priced and agreed first. Use when someone asks for the work email of these people, an email for this LinkedIn profile, or to fill an email column once. For a repeat job (every week, new people keep coming) or emails plus phones for a whole list, use contact-finder.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Work email

One step: work emails for the people the user names, now. For a job that repeats or covers emails and phones together, use the `contact-finder` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Inputs

- Per person: a **LinkedIn URL** (best), or **name + company domain**.
- A few people in chat, a CSV, or a column in a Loopster table.

## Steps

1. **Free pass.** Run `loopster-data-find-work-email` (needs `linkedin_url`) on every person in one call: `run_capability` with all inputs and `maxCostUsd: 0`, or a column in the user's table. People with only name + domain and no URL: find the URL first with `search_people` (`personName` + `specificCompanies`, free).
2. **Count the misses.** Found, not found, and no input. Stop here if every person was found.
3. **Price the misses only.** Take the next route from `references/routes.md` ("Work email"), cheapest first, and read its live `cost`. Show: people left · route · price per person · total. Ask, with the pricing sentence.
4. **Run on a yes**, on the misses only, with `maxCostUsd` and an `idempotencyKey`. More than 10 people: 1, then 10, then the rest (house rules, section 5).
5. **Report** found free, found paid, not found, and the real cost (`get_usage`).

No Function and no new table for a one-off: those are for jobs that repeat (`contact-finder`).

## Does not claim

- That an address on a catch-all domain will deliver. Offer `verify-email` for those.
- That "not found" means the person has no work email: only that no route had it.
