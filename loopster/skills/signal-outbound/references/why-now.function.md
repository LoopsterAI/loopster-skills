# Function design: Why now · Loopster skill

Example results for two accounts:
- **An account with a recent launch:** the signal is `launch`, with its date and an opener.
- **An account with only old news:** the signal is `none`. The Function declines to invent a reason.

Typical cost is about $0.03 to $0.05 per domain at list prices, with the AI step priced by use. Measure 10 domains before you quote a big run.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Reuse or build

Look for this Function first: the "Functions" section of `loopster-context.md`, then `list_functions`. The persona keywords, the 90-day window and the ICP context are fixed inside its steps and prompt, so read it with `get_function` and compare them with the current user's. If they match, reuse it. If they differ, build a variant named `Why now · <persona> · Loopster skill` from this design.

## Title and description

- Title: `Why now · Loopster skill`
- Description: `Built by the Loopster signal-outbound skill v0.1. Open roles + recent news from PredictLeads, read by AI against your ICP. Returns the strongest buying signal and a one-line opener. Safe to edit in Loopster.`
- End the description with the settings this build uses, so a later reader can compare them: `Hiring keywords: <title_keywords>. Window: 90 days. ICP context: <icpContextId or "pasted ICP">.`

## Input

| Header | required |
|---|---|
| `Company domain` | true |

## Steps (in order)

1. **Open roles:** `predict-leads-find-jobs`, header `Open roles`. Use the hiring recipe in `signal-recipes.md`, with `title_keywords` built from the user's personas and `domain: "@{<inputId>}"`.
2. **Recent news:** `predict-leads-find-news`, header `Recent news`, with `{"execution_mode": "managed", "domain": "@{<inputId>}"}`.
3. **Why now:** template `ai`, header `Why now`, with the prompt below. Replace the ids. `<icpContextId>` comes from `list_contexts`. If there is no ICP context, paste the ICP from `loopster-context.md` into the prompt instead.

```
You help a sales team decide why to contact a company now.

Our ideal customer profile:
@{ctx:<icpContextId>}

Company domain: @{<inputId>}

Open roles posted in the last 90 days (JSON, may be empty):
@{<openRolesStepId>}

Recent company news (JSON, may be empty):
@{<newsStepId>}

Pick the single strongest, most recent buying signal that relates to our ICP. Signals that count: hiring for roles we help, funding, expansion, leadership change, product launch, acquisition, partnership. Ignore anything older than 90 days.

Answer with JSON only, no prose, in exactly this shape:
{"signal": "hiring|funding|expansion|leadership|launch|acquisition|partnership|none", "date": "YYYY-MM-DD or empty", "evidence": "one short factual phrase with the source detail", "opener": "one plain sentence a rep could open an email with, referencing the evidence, no hype, under 25 words; empty if signal is none", "fit": "high|medium|low"}
```

## Output

Return **only** the `Why now` step (`set_function_outputs` with that step id). The raw news JSON is often 20 KB or more per company. Output key: `why_now`; parse it as JSON.

## Record, publish and run

1. **Record it first.** As soon as `create_function` returns, write the Function's id in the "Functions" section of `loopster-context.md`, so the next run (or a restarted build) finds it.
2. **Ask before publishing.** Publishing, and opening the Function to agents, change what other tables and agents can run. Get a separate yes for each (house rules, sections 4b and 6).
3. After a yes: dry-run the publish, publish, then `set_function_agent_access` with `true`. Then update the "Functions" line with its version and its published and open-to-agents status.
4. **Run it.** Price it, ask, then run 1 domain, then 10, then the rest 100 at a time, as in `SKILL.md` Route 2, step 4. `run_function` takes no `maxCostUsd`, so read `get_wallet` `consumedUsd` before and after each batch, and stop and ask if a batch costs more than 1.5 times its share. For up to about 25 domains, use `run_function`. Poll `get_run` with the batch `runId`, then read each `why_now` with `get_function_run`, using `functionId` and each item's `rowId` as `runId`. For more than about 25 domains, or when the user wants the rows in Loopster, call it from one `run-function` column in a table and read the `why_now` field with a field reference whose `path` is `["why_now", "<field>"]`.
