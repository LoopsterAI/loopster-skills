# Write-back columns

All of these write to the user's CRM on their own connected account (`connection: own_key`; nothing is charged to the Loopster wallet). Every batch needs its own yes. Read the live settings with `get_column_template` before creating a column.

## HubSpot

**Step 1: build a blank-safe payload** with one Formula column, `Write payload`. It holds only the approved fields that have a value:

```js
(() => { const p = {};
  const add = (k, v) => { v = String(v ?? '').trim(); if (v) p[k] = v; };
  add('industry', @{<Proposed industry id>});
  add('jobtitle', @{<Proposed title id>});
  add('hs_linkedin_url', @{<Proposed LinkedIn id>});
  return Object.keys(p).length ? JSON.stringify(p) : ''; })()
```

- Mark every proposed column it reads as optional (`update_column` with `optionalMentions` listing their ids), so a blank proposal doesn't stop the Formula.
- The proposed columns must themselves always complete. Give them a fallback, never a skip.
- When nothing is approved for a row, the payload is blank. Do not rely on a blank value to stop the write. Add a free Formula column `Has payload` that always returns `yes` or `no`: `(() => String(@{<Write payload id>}).trim() ? 'yes' : 'no')()`. Mark `Write payload` optional in `Has payload` (`update_column` with `optionalMentions`), so a blank payload still lets it run. Then set a run condition on the write-back column with `update_column`: `{"enabled": true, "description": "Only when there is something to write", "condition": "(() => String(@{<Has payload id>}).trim() === 'yes')()"}`. Test on a row with nothing approved: the write-back cell must be skipped, and the CRM record must not change. Check the record in the CRM, not just the cell.

**Step 2: the write-back column.** Template `hubspot-update-object`, task `hubspotSendObject`:

```json
{"hubspotSendObject": {
  "mode": "update",
  "objectType": "contacts",
  "recordId": "@{<Record ID column id>}",
  "properties": "@{<Write payload id>}"
}}
```

- `properties` is a string holding a JSON object of HubSpot internal property names to values. Use internal names (HubSpot → Settings → Properties), not labels.
- Never map a proposed column directly into `properties`. A blank value would be sent as `""`, and that can clear the CRM field.
- Set `integrationConnectionId` to the right HubSpot connection; a workspace can hold several portals.
- Related templates:
  - `hubspot-create-object` (create mode, described for companies and deals; contacts are updated, not created, with these columns);
  - `hubspot-find-object` (look a record up);
  - `hubspot-associate-object`;
  - `hubspot-add-to-list`.

## Salesforce

| Template | Use it when |
|---|---|
| `salesforce-upsert-object` | An external id field exists. Updates a match or creates a new record, and is safe to re-run. |
| `salesforce-update-object` | You have the Salesforce record id. |
| `salesforce-find-object` | You need to look a record up first. |
| `salesforce-create-object` | Creating a new record. |

## Attio

| Template | Does |
|---|---|
| `attio-send-record` | Creates or updates a record, matching on a unique attribute |
| `attio-find-record` | Looks a record up |

## Before the first write

Ask the user to check their CRM automations. A property change can enrol contacts in a HubSpot workflow or a Salesforce flow that emails them. If one would fire, pause it or exclude these records first.

## Safe order

1. Proposed-value columns are filled and reviewed.
2. Create the write-back column with Auto-run off and the `Has payload` run condition.
3. `trigger_rows` with **one** `rowId`. Have the user check the record in the CRM, and confirm no other field changed.
4. Then 10, then the rest. Every trigger names `rowIds` explicitly, and `maxCostUsd: 0` is a safe cap for the write-back column.
5. Trigger the write-back column on its own. A `run-function` column is checked by reading the wallet, so run it first and separately (`get_wallet` `consumedUsd` before and after), and never include it in the write-back trigger.
6. Read the cell errors after each batch; they name the property or permission problem.
