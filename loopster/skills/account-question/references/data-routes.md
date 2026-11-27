# Data routes: which source for which field

Cheapest first. These are list prices on Loopster's managed account, read 2026-10-25; read the live `cost` in `list_capabilities` or `list_column_templates` before quoting.

- **Runs as:** "capability" runs with no table (`run_capability`). "Column template" is a table column template. For a source marked "capability" that you want as a table column, read the template with the same id using `get_column_template` (any table id) to confirm it exists and to see its settings.
- **Function step?** says whether a Function can take it (`add_function_step`). Any job that will run again goes in a Function (house rules, section 7), so check this column before you choose how to run a source.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Companies (key: domain)

| Field | Source | Runs as | Function step? | List price |
|---|---|---|---|---|
| Name, industry, employees, revenue range, HQ, founded, LinkedIn URL (output keys include `found`, `industry`, `employee_count` and `employee_range`; read one row to see the rest) | `loopster-data-enrich-company` | capability | yes | free |
| Extended firmographics, NAICS, funding stage | `predict-leads-enrich-company-extended` | column template | yes | $0.0017 |
| Company profile, parent and subsidiaries | `predict-leads-enrich-company` | column template | yes | $0.0017 |
| Firmographics (second source) | `ai-ark-enrich-company` | capability | yes | $0.0003 |
| Website text (pricing, about, careers) for an AI summary | `predict-leads-website-subpages` | column template | yes | $0.0017 |
| Products and services | `predict-leads-products` | column template | yes | $0.0017 |
| Similar companies | `predict-leads-find-lookalikes` / `ai-ark-find-lookalike-companies` | column template / capability | yes / yes | $0.0017 / $0.013 |
| Open jobs (with title filters and recency) | `predict-leads-find-jobs` | column template | yes | $0.0127 |
| Recent news (funding, launches, hires, expansion) | `predict-leads-find-news` | column template | yes | $0.0127 |
| Tech stack | `predict-leads-find-tech-stack` | column template | yes | $0.0233 |
| Funding rounds and investors | `predict-leads-find-financing` | column template | yes | $0.0871 |
| Web traffic | `aviato-company-web-traffic` | capability | yes | $0.1083 |
| Total funding, financials | `aviato-company-financials` | capability | yes | $0.5121 |
| People count at a company | `ai-ark-count-people` | capability | yes | $0.0026 |
| Headcount by title or location | `professional-company-headcount` | capability* | no | $0.0015 |
| Open jobs (second source) | `professional-company-open-jobs` | capability* | no | $0.0015 |
| Domain from company name | `search_companies` with `name` | search | no | free |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## People (key: LinkedIn URL)

| Field | Source | Runs as | Function step? | List price |
|---|---|---|---|---|
| Title, seniority, company, company website, location, role start date | `loopster-data-enrich-person` | capability | yes | free |
| LinkedIn URL from an email | `loopster-data-email-to-linkedin` | capability | yes | free |
| LinkedIn URL from name + company | `search_people` with `personName` + `specificCompanies` | search | no | free |
| LinkedIn URL (paid, for misses) | `surfe-find-profile` (name + company) | capability | yes | $0.0127 |
| LinkedIn URL (paid, for misses) | `icypeas-email-to-linkedin` (email) | capability | no | $0.0325 |
| Live profile, positions, about, skills | `enrich-professional-profile` | capability* | no | $0.0015 |
| Recent posts (for personalization) | `professional-person-posts` | capability* | no | $0.006 |
| Person enrichment (second source) | `ai-ark-enrich-person` | capability | yes | $0.0013 |
| Personality profile | `ai-ark-personality-profile` | capability | yes | $0.05 |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

\* Runs on the professional-network provider ("professionalNetwork"). **Not a Function step.** For a repeat job, use a managed table column for these (`execution_mode: "managed"`, runs on Loopster's account, no default needed) and a Function for the rest. As a capability it needs the user's own key, or Loopster's account saved as that provider's default (`set_provider_default` with `account: "loopster"`; ask first). Some outputs are large, so in a table use the column template rather than the capability when there are more than about 10 rows.

## AI web research (last resort)

`ai-web` ("Loopgent"), `find-linkedin-url` ("Find LinkedIn profile URL") and the model templates whose id ends in `-web` search the web for every row. They list from about $0.01 to $1.23 a row, and the real cost can be several times that. Use them only for rows and fields no route above answers, after measuring 3 rows and asking (house rules, sections 3 and 4c).

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Contacts (emails and phones)

Use the `contact-finder` skill.

## Notes

- Capabilities that need `connection: required` (for example `theirstack-find-tech-stack` and `hunter-find-email`) run only on the user's own key.
- **These can be Function steps:** Loopster Data lookups, PredictLeads, AI Ark, Aviato, Wiza, FullEnrich, BetterContact, Reverse Contact, Surfe, Icypeas and Hunter email finders, AI steps and Formula steps. That's how to bundle "website text + AI summary" or "jobs + news + AI why-now" into one reusable call.
- **These can't:** the `professional-*` routes and `enrich-professional-profile`, `search_people` and `search_companies`. Keep them as table columns or searches.
- **A bundle Function costs the sum of all its steps on every input,** and AI steps bill by use on top. `costEstimate.maxUsdPerRun` is a floor when the Function has an AI step. Keep expensive steps (for example `aviato-company-financials`, about $0.51 a row) out of a bundle that runs on every row. Put them in a second Function that you run only on the rows that need them, or use `run_capability` for a one-off.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.
