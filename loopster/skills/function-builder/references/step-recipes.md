# Step recipes

`<inputId>` and `<stepId>` stand for the ids returned when you add inputs and steps. Mentions keep the braces: `@{<inputId>}`.

## Formula: clean or derive a value (free)

```json
{"templateId": "formula", "header": "Clean domain",
 "taskConfig": {"formula": {"expression": "String(@{<inputId>}).trim().toLowerCase().replace(/^https?:\\/\\//,'').replace(/^www\\./,'').split('/')[0]"}}}
```

The expression is JavaScript, and `@{id}` stands for the value. A later step can read this one with `@{<stepId>}`.

**Reading one field of a JSON result** (for example `company_website` from a person lookup): use a field reference, `@{ref:v1:<data>}`. `<data>` is the base64url encoding, with no `=` padding, of `{"columnId":"<step or column id>","source":"value","path":["company_website"]}`, with exactly those keys in that order and no spaces. Extract the field into its own Formula step or column, then compare it in the next one. Use one field reference per Formula expression. A plain column mention can be used more than once.

## AI: judge, summarize or write, using the workspace ICP

```json
{"templateId": "ai", "header": "ICP fit",
 "aiConfig": {"prompt": "Our ideal customer profile:\n@{ctx:<icpContextId>}\n\nCompany data (JSON):\n@{<stepId>}\n\nAnswer with JSON only: {\"fit\": \"high|medium|low\", \"reason\": \"one sentence\"}"}}
```

- Get context ids from `list_contexts`.
- Ask for JSON only, and give the exact shape, so callers can parse the result.
- AI steps are priced by use (`unpricedSteps: 1`), so the Function's quote is only a floor. Until you have run 10 inputs, quote 4 × the step's estimate. After a yes, run the Function on 1 input, then 10, and read `get_wallet` `consumedUsd` before and after each run, then quote from what you measured.
- Every mention is required by default. A blank value stops the step from running. PredictLeads list results come back as JSON even when empty, so they do not block.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## PredictLeads signal steps

All of these take `domain` and `execution_mode: "managed"` (Loopster's account) unless the user has their own PredictLeads key.

| templateId | taskConfig key | Useful settings | List price |
|---|---|---|---|
| `predict-leads-find-jobs` | `predictLeadsFindJobs` | `title_keywords` (list), `description_keywords`, `posted_within_days`, `active_only`, `max_results` | $0.0127 |
| `predict-leads-find-news` | `predictLeadsFindNews` | `categories`, `max_results` | $0.0127 |
| `predict-leads-find-financing` | `predictLeadsFindFinancing` | | $0.0871 |
| `predict-leads-find-tech-stack` | `predictLeadsFindTechStack` | | $0.0233 |
| `predict-leads-find-lookalikes` | `predictLeadsFindLookalikes` | | $0.0017 |
| `predict-leads-website-subpages` | `predictLeadsWebsiteSubpages` | | $0.0017 |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Example:

```json
{"templateId": "predict-leads-find-jobs", "header": "Open sales roles",
 "taskConfig": {"predictLeadsFindJobs": {"execution_mode": "managed", "domain": "@{<inputId>}",
   "title_keywords": ["sales development", "SDR", "account executive"], "posted_within_days": 90, "active_only": true, "max_results": 10}}}
```

## Work-email waterfall

Add four inputs first: `First name`, `Last name` and `Company domain` (all required), and `LinkedIn URL` (not required; with it, the free step can answer). Then add one step:

```json
{"templateId": "waterfall-email", "header": "Work email",
 "taskConfig": {"waterfallEmail": {
   "providers": [
     {"id": "loopsterDataFindWorkEmail-default", "order": 0, "enabled": true, "taskType": "loopsterDataFindWorkEmail"},
     {"id": "icypeasFindEmail-default", "order": 1, "enabled": true, "taskType": "icypeasFindEmail", "executionMode": "managed"},
     {"id": "findymailFindByName-default", "order": 2, "enabled": true, "taskType": "findymailFindByName", "executionMode": "managed"}],
   "validation": {"enabled": false},
   "inputMapping": {"first_name": "@{<first name input id>}", "last_name": "@{<last name input id>}",
     "domain": "@{<domain input id>}", "linkedin_url": "@{<LinkedIn URL input id>}"}}}}
```

- Providers run in order, free Loopster Data first, and the waterfall stops at its first hit.
- Map only the inputs the Function has. Leave `linkedin_url` out when there is no LinkedIn input.
- Leave `executionMode` off a provider if the user has their own key for it.
- The answer lists `childColumnsBuilt`. Return the result column ("Work Email", output key `work_email`), not the per-provider columns.
- `appliedFixes` may say verification was left off. That is expected, because email checks can't be Function steps.
- After a yes, test any other provider mix on 1 input, then 10, before you rely on it.

## Provider actions

Any API-addable task works as a step. Read its settings with `get_column_template` (on any table id) and pass them under `taskConfig.<taskType>`. For the step to run on Loopster's account, set `execution_mode: "managed"` where the schema offers it, or `executionMode` on waterfall steps.
