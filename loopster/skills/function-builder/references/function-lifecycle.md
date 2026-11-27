# Function lifecycle: calls and answers

Read these answers after each call.

| Call | Key fields | Answer to read |
|---|---|---|
| `create_function` | `title`, `description` (or `fromTable`) | `function.id`; `published: false`, `agentAccess: false` |
| `open_function_sandbox` | `functionId` | `sandbox.opened: true`, `seededRows` |
| `add_function_input` | `header`, `required` (always send it), `description` | `input.id` (a UUID); stored `header` |
| `add_function_step` | `templateId`, `header`, and `taskConfig` or `aiConfig` | `column.id`, `dependencies`, `costEstimate.maxUsdPerRun`, `warnings`, `appliedFixes`, `childColumnsBuilt` (waterfalls) |
| `get_function` | `functionId` | `draft.inputs`, `draft.steps`, `draft.outputs[].columnId` (what can be returned) |
| `set_function_outputs` | `columnIds` (the whole list) | `draft.outputs[].selected` |
| `publish_function` | `dryRun: true` first | `wouldPublish`, `contract.outputs` (keys), `refusal` |
| `publish_function` | live | `published: true`; the sandbox closes |
| `set_function_agent_access` | `agentAccess: true` | `agentAccess: true` (can be set before publishing, but it can't run until published) |
| `run_function` | `inputs`: one object, or a list of up to 1,000, keyed by **input id**; `idempotencyKey` | one input: `runId`; a list: `runId` for the batch and `items[]` with `index` and `rowId`, plus `rejected[]` |
| `get_function_run` | `functionId` and `runId` (a single run's `runId`, or a batch item's `rowId`) | `status`, `outputs` (text, or a JSON number for a number-shaped step), `skipped`, `hasUnpublishedChanges` |
| `get_run` / `list_run_items` | the batch `runId` | counts and per-item state (no outputs) |
| `delete_function` | `functionId` | `inTrash: true`, `usedBy.tables`; later runs answer 404 |

## Refusals to expect

- `run_function` on a Function not open to agents: 403 "This function is not enabled for agent access."
- `run_function` open to agents but never published: 409 "This function has never been published…"
- A value keyed by the input's name instead of its id: 400 "Missing required inputs: <id>".
- `publish_function` with no outputs: 409 `no_outputs`.
- Changing inputs, steps or outputs with no sandbox open: 409 `sandbox_required` (publishing closes the sandbox).

## Notes

- The output key is made from the step's name: "Why now" → `why_now`, "Work Email" → `work_email`.
- Output values come back as text, except an output whose step is shaped as a number, which is a JSON number when it holds one. Parse JSON outputs yourself.
- A `fromTable` Function keeps working after its source table goes to Trash.
- Waterfall steps get a result column plus one column per step (`childColumnsBuilt`). Return the result column.
