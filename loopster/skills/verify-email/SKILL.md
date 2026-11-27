---
name: verify-email
description: Run one email verifier over addresses the user already has and sort them into send, risky and do not send, in one step, priced and agreed first. Use when someone asks to verify these addresses, check whether these emails are valid, or add a verification column to a table. To clean a whole list before a campaign (duplicates, role and disposable addresses, then verification), use email-check.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Verify email

One step: one verifier over addresses that are already clean. To clean a list first (duplicates, malformed, role and disposable addresses), use `email-check`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Drop what needs no check:** exact duplicates and text that is not an email address. Say how many.
2. **Choose the verifier** from `references/routes.md` ("Email checks"): the user's own connected account if they have one (`list_connections`), otherwise one that runs on Loopster's account. As a capability it may need a provider default; ask before `set_provider_default`.
3. **Price one call for all addresses** (a capability takes up to 1,000 inputs; a table column runs on the rows you name). Show addresses · verifier · price · total, and ask with the pricing sentence.
4. **Run once on a yes**, `maxCostUsd` and an `idempotencyKey`. Never one call per address.
5. **Sort** into **send** (valid), **risky** (catch-all, unknown, role address) and **do not send** (invalid, disposable), with counts.

## Does not claim

- That a valid result on a catch-all domain proves anything: such a server accepts every address.
- That the mailbox belongs to the intended person, or that the verdict stays true later.
