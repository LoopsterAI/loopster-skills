# Pre-flight and push columns

Every sequencer column runs on the user's own connected account (`connection: own_key`), so nothing is charged to the Loopster wallet. Set `integrationConnectionId` to the right account from `list_connections`, because a workspace can have several. Read each template's live settings with `get_column_template` before creating the column.

Sequencer actions are table columns, never Function steps. Keep the pre-flight lookups and the push here, and let a `run-function` column (First line, Find work email) feed them.

## Pre-flight lookups (read-only on the user's account)

| Check | Template | Reads |
|---|---|---|
| Already in a HeyReach campaign | `heyreach-get-campaigns-for-lead` | LinkedIn URL (or email or HeyReach id) |
| Already a LinkedIn connection | `heyreach-is-connection` | LinkedIn URL |
| Lead status in a Smartlead campaign | `smartlead-lookup-lead-status-in-campaign` | email |
| Lead exists in Instantly | `instantly-find-lead` | email |

## Name clean-up (free Formula)

```js
(() => { let n = String(@{<First name id>} || '').trim();
  n = n.replace(/\p{Extended_Pictographic}/gu, '').replace(/\b(dr|mr|mrs|ms|prof)\.?\s+/i, '').split(/[|,(]/)[0].trim();
  if (n === n.toUpperCase()) n = n.charAt(0) + n.slice(1).toLowerCase();
  return n; })()
```

## HeyReach: add to campaign

Template `heyreach-add-leads-to-campaign`, task `heyreachSendLeadToCampaign`:

```json
{"heyreachSendLeadToCampaign": {
  "campaign_id": "<campaign id>",
  "first_name": "@{<Clean first name id>}",
  "last_name": "@{<Last name id>}",
  "profile_url": "@{<LinkedIn URL id>}",
  "custom_fields": [
    {"key": "FIRST_LINE", "value": "@{<First line id>}"},
    {"key": "COMPANY", "value": "@{<Company id>}"}
  ]
}}
```

- `linkedin_account_id` is optional; it pins a sender.
- Custom field keys must match the campaign's variables. In HeyReach messages, the variable `{FIRST_LINE}` is fed by key `FIRST_LINE`.
- Related templates:
  - `heyreach-add-leads-to-list` adds to a list instead of a campaign;
  - `heyreach-stop-lead-in-campaign` removes a lead;
  - `heyreach-add-tags` tags leads.

## Instantly, Smartlead, Mixmax

| Destination | Template |
|---|---|
| Instantly | `instantly-add-lead` (add to a campaign with custom variables), or `instantly-update-lead-email` (create or update by email) |
| Smartlead | `smartlead-add-lead-to-campaign` (with custom fields) |
| Mixmax | `mixmax-add-recipient` (add to a sequence with variables) |

Read their settings schema with `get_column_template` and map variables the same way.

## Pushing safely

1. Create the push column with `autoplay` off on the table.
2. `trigger_rows` with **one** `rowId` and the push column in `columnIds`. Read the cell: success, or an error message. Have the user confirm in the sequencer.
3. Then 10 `rowIds`, then the rest, each after a yes. Nothing is charged to the wallet, so `maxCostUsd: 0` is a safe cap.
4. Run the First line column (an AI column or a `run-function` column) first, and on its own. Put only the push column in a trigger that uses `maxCostUsd: 0`.
5. Never trigger the push column without naming `rowIds`.
