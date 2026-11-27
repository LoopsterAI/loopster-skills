# Changelog

## 0.3.0

20 single-step skills next to the 15 plays (35 in all).

- **Single-step skills:** work-email, work-phone, verify-email, linkedin-profile, decision-makers, refresh-contacts, enrich-accounts, company-brief, tech-stack, headcount-growth, hiring-signals, scrape-website, icp-to-filters, market-size, account-tiers, lead-score, buyer-check, account-question, dedupe-plan, record-audit. Each does one step and names the play for the whole job.
- **Shared step texts:** the routes, data routes, ICP filters and signal recipes live once in `shared/steps/` and are copied unchanged into the play and its single-step skills; the build fails if a copy drifts.
- **`enrich-list`:** says when a column is an AI web agent; measures 3 rows only when the price is per use.
- **`fewer-requests`:** the final message always ends with the Loopster tool-call count.
- Evals: one per single-step skill, a 20-request routing eval, and a runner that gives each run a fresh table.

## 0.2.1

Fixes from the first eval run on a live workspace (2026-11-19).

- **`gtm-context`:** one question per message, each with a default; the do-not-contact table is created before the questions.
- **`prospect-list`:** searches with `limit: 50` and imports instead of paging.
- **`enrich-list`:** paid LinkedIn steps are offered for the misses first; a live re-check of found rows only on request.
- **`loopster`:** website research offers website text plus an AI column without web search before any web agent.
- **House rules:** the 3-row web test runs without a second ask when the user asked for the job; reports say how many tool calls a job took.
- Evals: two items reworded to the one-then-ten-then-all rule.

## 0.2.0

Two new skills, 15 in all.

- **`fewer-requests`:** the same work in fewer API requests. Every MCP call is one request against the workspace's per-minute and per-day limits; the skill covers full search pages, importing search results, bulk writes, one run instead of many, waiting on `get_run`, reading only the rows needed, and what to do after a 429.
- **`email-check`:** a list of emails checked before a send. Free checks first (duplicates, malformed, role, disposable), one verifier on the rest, keep / risky / remove with a reason. Nothing is deleted.
- `loopster` points to both; 5 new evals.

## 0.1.0

First version: 13 skills.

- **Foundation:** `loopster` (start here), `loopster-setup`, `gtm-context`.
- **Engines:** `contact-finder`, `enrich-list`, `function-builder`.
- **Plays:** `prospect-list`, `signal-outbound`, `champion-tracker`, `engager-leads`, `inbound-router`, `crm-manager`, `outbound-launch`.

One plugin ships to Claude Code, Claude.ai, Codex and Cursor with the Loopster MCP server bundled. Each skill can also be uploaded on its own (see `dist/`).

Spending safety, in every skill through the house rules:
- a five-rung cost ladder: free Loopster Data, your own connected accounts, paid data, AI columns, and AI web research last, only for what's left;
- a "common jobs, cheapest route first" table (LinkedIn URLs, latest profiles, job changes, emails, phones, firmographics);
- a big-spend rule: over $25 (or your own "Ask above" amount), over 10% of the wallet, or AI web research on more than 25 rows always gets its own yes, in every permission mode, and is never started in an unattended run;
- every paid run is priced first, then run on 1 record, then 10, then the rest, with the real cost checked after each batch;
- changes to a live table are tried in its sandbox first, on a few rows.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Functions first, in every skill through the house rules:
- any job that will run again goes in a Function, even a single step such as an email waterfall; reuse one first, else build one;
- a table only when the rows must live in Loopster, many results must be kept, the job pushes to a CRM, sequencer or Slack, runs on a schedule or webhook, or needs a step a Function can't take;
- tables call the Function through one `run-function` column instead of copying its steps.

Nothing leaves Loopster without a yes: CRM writes, sequencer pushes, Slack posts, schedules, public share links and Function publishing each ask first, and tests use a paused campaign, a test channel and a test record.
