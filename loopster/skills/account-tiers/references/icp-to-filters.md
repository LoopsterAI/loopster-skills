# ICP to Loopster Data filters

Filter ids, kinds and values come from `list_search_filters`. Always call it first, because the vocabulary is live. Envelopes:

- textList: `{"kind": "textList", "include": ["…"], "exclude": ["…"], "mode": "contains" | "exact"}`
- multiSelect: `{"kind": "multiSelect", "include": ["…"], "exclude": ["…"]}`; values must come from the filter's options
- numberRange: `{"kind": "numberRange", "min": n, "max": n}`
- boolean: `{"kind": "boolean", "value": true}`

## People filters

| ICP words | Filter | Notes |
|---|---|---|
| "VP Sales", "Head of RevOps" | `jobTitle` (textList, `mode: "contains"`) | The most precise persona filter. List 3 to 8 title variants. |
| "leaders", "decision-makers" | `seniority` (C Suite, VP, Head, Director, Manager, …) | Can match a past role: re-check the current title in the results |
| "sales team", "marketing" | `jobTitle` (textList, `mode: "contains"`) | Use title words such as "Sales" or "Marketing", with `seniority`. Send only filters `list_search_filters` lists |
| "in the US", "based in London" | `country`, `personState`, `personCity` | Where the person is |
| "US companies" | `companyCountry`, `companyState`, `companyCity` | Where the company is |
| "fintech", "SaaS" | `companyIndustry` (589 options) | Use several neighbouring industries. Use `companyIndustryGroup` only if `list_search_filters` lists it. |
| "50–200 people" | `companySizeBand` (1-10 … 10001+) | |
| "10 to 50 million in revenue" | `companyRevenueBand` | Values like "$10M - $20M"; read the options |
| "funded", "Series B+" | `companyFundingRounds`, `companyTotalFunding` (numberRange) | A static fact, not a recent event. For recent rounds use `signal-outbound`. |
| "founded after 2018" | `companyFoundedYear` (numberRange) | |
| "new in role" | `monthsInRole` (numberRange, e.g. 0–4) | Powers the new-leader play |
| "used to work at …" | `pastCompany` (textList) | Powers the customer-alumni play |
| "at these accounts" | `specificCompanies` (textList) | Company names or domains |
| "has an email or phone" | `hasEmail`, `hasPhone` (boolean) | Raises contact hit rates later |
| "named person" | `personName` | Pair with `specificCompanies` |

## Company filters

`industry`, `employeeCount`, `sizeBand`, `country`, `state`, `city`, `postalCode`, `revenueBand`, `companyType`, `keywords` (textList over the description), `name`, `hasLiveDomain`, `foundedYear`, `totalFunding`, `fundingRounds`. Use `industryGroup` only if `list_search_filters` lists it.

## Worked example

"VPs and Heads of Sales at 50–500 person US software companies, not our customers, max 2 per company":

```json
{
  "filters": {
    "jobTitle": {"kind": "textList", "include": ["VP Sales", "Vice President of Sales", "Head of Sales", "VP Revenue", "Chief Revenue Officer"],
                 "exclude": ["AVP", "EVP", "Area", "Associate", "Fractional", "Regional", "Development", "Engineering", "Operations", "Enablement"], "mode": "contains"},
    "seniority": {"kind": "multiSelect", "include": ["C Suite", "VP", "Head"]},
    "companySizeBand": {"kind": "multiSelect", "include": ["51-200", "201-500"]},
    "companyCountry": {"kind": "textList", "include": ["US"]},
    "country": {"kind": "textList", "include": ["United States"]},
    "companyIndustry": {"kind": "multiSelect", "include": ["Software Development", "Information Technology"]}
  },
  "exclusions": [{"kind": "list", "projectId": "<do-not-contact table id>", "columnId": "<domain column id>", "matches": "company"}],
  "perCompanyLimit": 2,
  "limit": 25
}
```

Check `companyIndustry` and `companyCountry` values against the live options first: the option list is what the index enforces.

## Unpacking the person record (saved search tables)

A table created from a search holds a JSON `Person record` column; read its column id with `list_columns`. Add one Formula per field you need. The keys are snake_case:

```json
{"templateId": "formula", "header": "Company domain",
 "taskConfig": {"formula": {"expression": "(() => { try { return JSON.parse(@{<Person record id>}).company_domain || '' } catch (e) { return '' } })()"}}}
```

Keys include `company_domain` and `role_started_at`. To see every key, read one row's `Person record` with `get_row` before adding more Formulas. Formulas run only when named: trigger them with `columnIds` and `maxCostUsd: 0`.

## Reading results

- Each record has `fields`:
  - person: `linkedinUrl`, `firstName`, `lastName`, `title`, `seniority`, `function`, `location`
  - company: `companyName`, `companyDomain`, `companySizeBand`, `companyIndustry`
  - `roleStartedAt`
- Results come in the index's own order, not by relevance, so the first page is not a sample. Page through before judging quality.
- `approximateTotal` is the market size for the filters.
