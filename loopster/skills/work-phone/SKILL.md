---
name: work-phone
description: Find mobile or direct phone numbers for a few named people in one step: the free Loopster Data lookup first, then one paid finder only for the misses, priced and agreed first. Use when someone asks for phone numbers, mobiles or a direct line for these people or LinkedIn profiles. For emails and phones for a whole list, or a job that repeats, use contact-finder.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Work phone

One step: phone numbers for the people the user names, now. For emails and phones together, or a repeat job, use the `contact-finder` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Inputs

- Per person: a **LinkedIn URL**. Every phone route needs it (some also take domain + full name).
- People with only an email: get the URL first with `loopster-data-email-to-linkedin` (free).

## Steps

1. **Free pass.** `loopster-data-find-phone-number` on every person in one call (`run_capability`, `maxCostUsd: 0`, or a table column).
2. **Count the misses.** Found, not found, no LinkedIn URL.
3. **Price the misses only** from `references/routes.md` ("Mobile phone"), cheapest first, live `cost`. Phone routes cost far more than email routes: show people left · route · price · total, and ask with the pricing sentence. A big spend (house rules, section 4c) needs that exact question, in any mode.
4. **Run on a yes**, on the misses only, `maxCostUsd` and `idempotencyKey`; 1, then 10, then the rest.
5. **Line type** (mobile or landline) only if asked: `clearout-phone-validate-phone`, priced separately.
6. **Report** found free, found paid, not found, real cost.

## Does not claim

- That a number is a mobile, unless a line check said so.
- That the person answers it: it is a provider's record, not a confirmed direct line.
