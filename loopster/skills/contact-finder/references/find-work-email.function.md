# Function design: Find work email · Loopster skill

Build it with the `function-builder` steps; the exact calls are below.

## Title and description

- Title: `Find work email · Loopster skill`
- Description: `Built by the Loopster contact-finder skill 0.1.0. Free Loopster Data first, then Icypeas and Findymail only when it misses. Safe to edit in Loopster.`

## Inputs (add in this order)

| Header | required | Notes |
|---|---|---|
| `First name` | true | |
| `Last name` | true | |
| `Company domain` | true | `example.com` form, no `www` |
| `LinkedIn URL` | false | With it, the free step can answer |

Keep each `input.id` from `add_function_input`; the step below mentions them.

## Step: work-email waterfall

`add_function_step` with `templateId: "waterfall-email"`, `header: "Work email"`, and:

```json
{"waterfallEmail": {
  "providers": [
    {"id": "loopsterDataFindWorkEmail-default", "order": 0, "enabled": true, "taskType": "loopsterDataFindWorkEmail"},
    {"id": "icypeasFindEmail-default", "order": 1, "enabled": true, "taskType": "icypeasFindEmail", "executionMode": "managed"},
    {"id": "findymailFindByName-default", "order": 2, "enabled": true, "taskType": "findymailFindByName", "executionMode": "managed"}
  ],
  "validation": {"enabled": false},
  "inputMapping": {
    "first_name": "@{<First name id>}",
    "last_name": "@{<Last name id>}",
    "domain": "@{<Company domain id>}",
    "linkedin_url": "@{<LinkedIn URL id>}"
  }
}}
```

- If the user has their own key for a provider, drop `executionMode: "managed"` from that step so it runs on their key.
- The answer lists `childColumnsBuilt`: a result column ("Work Email", key `result`) and one column per step.
- `appliedFixes` may say verification was left off because no verifier account is set. That's fine. Keep `validation` off: email checks cannot be Function steps. Check emails separately (SKILL.md, Step 3).
- The answer's `costEstimate.maxUsdPerRun` is the most one run of this Function can cost, because it has no AI step. If you add an AI step, treat the figure as a floor. It is about $0.019 at list prices; the paid steps charge only when they find an email.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Output

`get_function` → `draft.outputs` lists the result column ("Work Email", grouped under "Work email"). Set it as the only output:

`set_function_outputs` with `columnIds: ["<result column id>"]`. The output key becomes `work_email`.

## Publish and open

1. `publish_function` with `dryRun: true`. Expect `wouldPublish: true` and outputs `["work_email"]`.
2. Show the user the contract from the dry run (inputs, output key, cost per run) and ask. Only after a clear yes, publish live. Ask again before opening it to agents: it is a separate yes.
3. `publish_function` (live).
4. After that second yes, `set_function_agent_access` with `agentAccess: true`.

## Run

Run it as SKILL.md, Step 2 says: 1, then 10, then 100 at a time, with the wallet read after each batch and a stop at 1.5 times the quote. Use `run_function` up to about 25 people and one `run-function` column above that (see "When a table is needed"). Function-specific points:

- Inputs are keyed by input id (`get_function` lists them). Leave `LinkedIn URL` out when the free pass has already run on these people.
- `work_email` holds the email when one was found. An empty answer, or JSON such as `{"found":false}`, means not found. Skipped or rejected inputs are "not run".
- In a table, map the three required inputs, and `LinkedIn URL` only when the free pass has not run on those rows.
