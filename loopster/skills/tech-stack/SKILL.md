---
name: tech-stack
description: Find which tools these companies use (CRM, marketing, data, cloud) in one step: tech-stack data first, AI web research only for what it can't answer, priced and agreed first. Use when someone asks whether these companies use HubSpot, Salesforce or another tool, or what their tech stack is. To turn a tool signal into outreach (switch or integrate plays with openers), use signal-outbound.
license: MIT
metadata:
  author: Loopster
  version: "0.3.0"
---

# Tech stack

One step: tools per company. For outreach built on it (switch or integrate plays), use the `signal-outbound` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Which tools?** "Everything" or named tools. Named tools are cheaper to check and clearer to report.
2. **Data route first:** `predict-leads-find-tech-stack` (see `references/signal-recipes.md`, "Tech stack", and `references/data-routes.md`). The user's own TheirStack key, if connected (`list_connections`), runs on their account.
3. **Price per company** from the live `cost`: companies · price · total. Ask with the pricing sentence. Then 1, then 10, then the rest, with `maxCostUsd` and an `idempotencyKey`.
4. **AI web research** only for companies the data route didn't cover, after measuring 3 rows and asking.
5. **Answer per company and tool:** yes, no or unknown, with the detection strength or source.
6. **Report** how many use each tool, the unknowns, and the cost.

## Does not claim

- That a tool is still in use: detections and job posts can be old.
- Tools with no public trace (internal systems).
