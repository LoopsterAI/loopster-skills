# Signal recipes

`<domain>` is the account's domain: an input id in a Function, or a column id in a table, as `@{…}`. Every PredictLeads step takes `"execution_mode": "managed"` unless the user has their own PredictLeads key.

The `taskConfig` is the same on both surfaces:
- **In a table column:** `domain` is `@{<column id>}`. Use this route for a first build; running it with `trigger_rows` takes `maxCostUsd`.
- **In a Function step** (`add_function_step`): `domain` is `@{<input id>}`. The jobs and news steps are the first two steps of "Why now · Loopster skill" (`why-now.function.md`).
- For tech stack and financing, build the column first. Once it works and the user will run it again, turn it into a Function with `create_function` and `fromTable`, record its id in the "Functions" section of `loopster-context.md`, and run it from then on with `run_function` or one `run-function` column.

## Hiring for roles you serve

Template `predict-leads-find-jobs`. The full `taskConfig`:

```json
{"predictLeadsFindJobs": {"execution_mode": "managed", "domain": "@{<domain>}",
 "title_keywords": ["sales development", "SDR", "BDR", "account executive", "revenue operations"],
 "posted_within_days": 90, "active_only": true, "max_results": 10}}
```

- Build `title_keywords` from the personas the user sells to. Hiring for the team your buyer runs is the signal.
- Read the output as JSON: `count`, plus `items[]` (title, location, posted date, URL). `count: 0` means no matching openings.
- Add `description_keywords` for a tool or skill named in postings (for example a competitor's product name).

## Funding and company news

Template `predict-leads-find-news`. The full `taskConfig`:

```json
{"predictLeadsFindNews": {"execution_mode": "managed", "domain": "@{<domain>}", "max_results": 25}}
```

- Each item has `category`, `summary`, `found_at`, `effective_date`, `amount` and `article.url`.
- Categories include: `receives_financing`, `invests_into`, `launches`, `hires`, `expands_offices_in`, `integrates_with`, `signs_new_client`, `attends_event`, `recognized_as`, `has_revenue`, `identified_as_competitor_of`.
- Keep items whose `effective_date` (or `found_at`) is within the window.

For round details (amount, investors), use template `predict-leads-find-financing`. It costs more than the news step (see the cost guide), so run it only on accounts whose signal is funding.

- Every step in a Function runs for every input, so keep financing out of the Why now Function: it would run on every account.
- First build: add the financing column to the Signals table (or a small table of the flagged domains) and run it on the flagged rows only (`trigger_rows` with those `rowIds`).
- To reuse it, turn that column into a `Funding round · Loopster skill` Function with `create_function` and `fromTable`, and record its id in the "Functions" section as soon as it returns. After a Why now run, pass only the flagged domains to `run_function`. If more than about 25 domains are flagged, call that Function from one `run-function` column in a table instead of `run_function`. Price it as the number of flagged domains × the financing price, and ask with the pricing sentence (over the big-spend limit in house rules 4c needs its own yes). Then run 1, then 10, then 100 at a time. Read `get_wallet` `consumedUsd` after each batch, and stop and ask if a batch costs more than 1.5 times its share of the quote.

## Tech stack (switch or integrate)

Template `predict-leads-find-tech-stack`, key `predictLeadsFindTechStack`. The output lists technologies with detection strength, plus the competing tools found.

- **Switch play:** a competitor's tool is detected. The angle is the one-line difference in `loopster-context.md`.
- **Integrate play:** a tool you integrate with is detected. The angle is "works with the <tool> you already use".

## New leaders (free)

```json
{"filters": {
  "monthsInRole": {"kind": "numberRange", "min": 0, "max": 4},
  "seniority": {"kind": "multiSelect", "include": ["C Suite", "VP", "Head"]},
  "jobTitle": {"kind": "textList", "include": ["VP Sales", "Head of Sales", "Chief Revenue Officer", "VP Revenue Operations"],
               "exclude": ["AVP", "EVP", "Area", "Associate", "Fractional", "Regional", "Development", "Engineering", "Enablement"], "mode": "contains"},
  "companySizeBand": {"kind": "multiSelect", "include": ["51-200", "201-500"]},
  "country": {"kind": "textList", "include": ["United States"]},
  "companyCountry": {"kind": "textList", "include": ["US"]}
}}
```

Signal date: `roleStartedAt`. Re-check the current `title`. `country` is where the person is, `companyCountry` where the company is; send both, or a US company's team abroad slips in.

## Customer alumni (free; see also `champion-tracker`)

`pastCompany` set to your customers' names, plus the persona and ICP filters. These are people who used your product at their last company.

## Cost guide (list prices, managed accounts, 2026-10-25)

| Engine | Per account |
|---|---|
| Jobs only | $0.0127 |
| News only | $0.0127 |
| Tech stack only | $0.0233 |
| Financing | $0.0871 |
| Why-now Function (jobs + news + AI summary) | about $0.03 to $0.05 (AI priced by use) |

`trigger_rows` and `run_capability` take `maxCostUsd`; `run_function` takes none. Price a `run-function` column from its Function (`get_function` `costEstimate.maxUsdPerRun` × the accounts, plus any usage-priced step measured on 10 rows). Read the real cost on 10 domains (`get_wallet` `consumedUsd` before and after) before you quote a big run.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.
