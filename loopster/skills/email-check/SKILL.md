---
name: email-check
description: Check a list of email addresses before a send and sort every address into keep, risky or remove, with a reason. Free checks run first (duplicates, malformed addresses, role addresses like info@, disposable domains), then one paid verifier runs only on what is left, priced and agreed first. Nothing is deleted. Use when the user asks to verify emails, check if addresses will bounce, clean or scrub an email list, remove bad or duplicate emails from a CSV, or prepare a list for a campaign. To find emails people don't have yet, use contact-finder.
license: MIT
metadata:
  author: Loopster
  version: "0.2.0"
---

# Email check

The free checks go first, so the paid verifier sees as few addresses as possible. Every address ends in one group with a reason; nothing is deleted. Read `references/house-rules.md` once per session, and keep the calls few (the `fewer-requests` skill).

## Ask first

1. **Where are the addresses?** A few in chat, a CSV, or an email column in a Loopster table.
2. **Their own verifier account?** If the user has one connected, it runs on their key. Otherwise use one that runs on Loopster's account (step 3).
3. **What happens to the result?** A CSV back, a column in the table, or saved views per group. Default: a column, plus a CSV.

## 1. Load once

- **A few addresses in chat (up to about 25):** no table. Go to step 2.
- **A CSV:** load it into a new table with Auto-run off. Above about 10,000 rows, load the file (house rules, section 10b); below that, one `insert_rows` call.
- **A table:** read the email column once with `list_rows` (`columns` set to it).

## 2. Free checks

On that one read, mark each address:

| Check | Group | Reason |
|---|---|---|
| Not an email address (no single `@`, no dot in the domain, spaces) | remove | malformed |
| Same address as an earlier row, ignoring case and spaces | remove | duplicate (the first one stays) |
| A disposable-mail domain | remove | disposable |
| A role address: info@, sales@, support@, hello@, admin@ and the like | risky | role address |
| A personal domain (gmail.com, outlook.com and the like) when the list is meant to be work emails | risky | personal address |

Say the counts before anything is paid for.

## 3. One verifier on what is left

- **Pick it** from `list_column_templates` with `tab: "enrich"` (the `contact-finder` skill lists the usual email checks). Compare the prices, and whether it needs the user's own key.
- **As a table column** (the usual case): the verifier runs on Loopster's account when its settings carry `execution_mode: "managed"`. As a capability, it needs the user's key or a saved provider default. Never save a default without asking: it applies to every column made afterwards for that provider.
- **Price, ask, run** (house rules, section 4): `estimate_trigger_cost` for the rows that passed step 2 only. After a yes, run 1 row, then 10, then the rest (house rules, section 5), with `trigger_rows` and those `rowIds`. Poll `get_run`.
- **A few addresses in chat:** one `run_capability` with all of them, if the verifier runs that way for this workspace. Otherwise make a small table.

## 4. Sort and write back

| Verifier says | Group |
|---|---|
| Valid, deliverable | keep |
| Catch-all, accept-all, unknown | risky: the server accepts every address, so "valid" proves nothing there |
| Invalid, undeliverable, disposable | remove |
| No answer | risky: say why |

- Write each row's group and reason in one `update_cells` call, into a plain column you create first.
- Offer `export_table` for a CSV, or a saved view per group.
- **Never delete rows or addresses.** Removing them from a list, a CRM or a campaign is the user's step, after a yes.

## Report

Counts per group and reason, how many addresses the verifier checked and what it cost, and where the results are.

## What it does not claim

- That a "keep" address belongs to the person on the row: a verifier checks the mailbox, not its owner.
- Anything certain about catch-all domains.
- That a verdict stays true: mailboxes close, so check again before a later send.
- Consent: whether the list may be emailed is the sender's question.
