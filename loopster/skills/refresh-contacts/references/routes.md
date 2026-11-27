# Contact routes and prices

Prices are Loopster's per-input list prices when the action runs on Loopster's managed account, read from `list_capabilities` on 2026-10-25. Always read the live `cost` before quoting, because prices change. On the user's own connected account (their key), nothing is charged to the Loopster wallet. "On result" means the provider charges only when it finds something.

The **Function step?** column says whether a Function can take that route as a step. A route marked No runs as a capability (`run_capability`) or a table column. Every step in a Function runs for every input, so a mobile or personal-email Function holds one paid provider step; only the email waterfall step stops at its first hit.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Work email

| Order | templateId | Needs | List price | Function step? |
|---|---|---|---|---|
| 1 | `loopster-data-find-work-email` | `linkedin_url` | free | Yes |
| 2 | `icypeas-find-email` | `firstname`, `lastname`, `domainOrCompany` | $0.0064 | Yes |
| 3 | `findymail-find-name` | `name`, `domain` | $0.0127 | Only as a provider inside the email waterfall step |
| 3 | `findymail-find-business-profile` | `linkedin_url` | $0.0127 | No |
| alt | `reverse-contact-find-work-email` | `linkedin_url` or `full_name` + `company_domain` | $0.0195 | Yes |
| alt | `better-contact-find-work-email` | LinkedIn URL or name + company | $0.034 | Yes |
| alt | `surfe-find-work-email` | LinkedIn URL or name + company | $0.034 | Yes |
| alt | `contactout-find-work-email` | `linkedin_url` | $0.039 | No |
| alt | `full-enrich-find-work-email` | LinkedIn URL or name + company | $0.0476 | Yes |
| alt | `wiza-find-work-email` | profile URL or name + company | $0.052 | Yes |
| own key | `hunter-find-email`, `prospeo-email-finder` | name + domain or company | wallet $0 | `hunter-find-email` Yes; `prospeo-email-finder` No |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Mobile phone

| Order | templateId | Needs | List price | Function step? |
|---|---|---|---|---|
| 1 | `loopster-data-find-phone-number` | `linkedin_url` | free | Yes |
| 2 | `ai-ark-find-mobile-phone` | LinkedIn URL, or domain + full name | $0.013 | Yes |
| 3 | `findymail-find-mobile-phone` | `linkedin_url` | $0.0871 | No |
| alt | `wiza-find-mobile-phone` | profile URL or name + company | $0.13 | Yes |
| alt | `contactout-find-mobile-phone` | `linkedin_url` | $0.2783 | No |
| alt | `surfe-find-mobile-phone`, `better-contact-find-mobile-phone` | LinkedIn URL or name + company | $0.3208 | Yes |
| alt | `full-enrich-find-mobile-phone` | LinkedIn URL or name + company | $0.7467 | Yes |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Personal email

| Order | templateId | Needs | List price | Function step? |
|---|---|---|---|---|
| 1 | `loopster-data-find-personal-email` | `linkedin_url` | free | Yes |
| 2 | `full-enrich-find-personal-email` | LinkedIn URL or name + company | $0.0468 | Yes |
| 3 | `surfe-find-personal-email` | LinkedIn URL or name + company | $0.0676 | Yes |
| alt | `aviato-find-personal-email` | `linkedin_url` | $0.0871 | Yes |
| alt | `contactout-find-personal-email` | `linkedin_url` | $0.1296 | No |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Getting a LinkedIn URL first (unlocks the free route)

| templateId | Needs | List price | Function step? |
|---|---|---|---|
| `loopster-data-email-to-linkedin` | `email` | free | Yes |
| `icypeas-email-to-linkedin` | `email` | $0.0325 | No |
| `surfe-find-profile` | name + company | $0.0127 | Yes |

`icypeas-email-to-linkedin` is not a Function step (Icypeas goes in a Function only as its email finder), so keep it a capability (`run_capability`). `surfe-find-profile` can be a Function step.

Or search Loopster Data with `search_people`, using `personName` + `specificCompanies` (free).

Don't use an AI web research column (`find-linkedin-url` "Find LinkedIn profile URL", `ai-web` or any `-web` model) for this until the routes above have run. It lists at about $0.18 a row or more, and is for the few rows they can't answer.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Email checks

As table columns, `zero-bounce-validate-email` and `icypeas-verify-email` run on Loopster's account when their settings include `execution_mode: "managed"`. As capabilities (and `findymail-verify-email` in any form), they run on the user's own key, or on Loopster's account only after it is saved as the provider's default (`list_provider_defaults` shows which). Otherwise `run_capability` answers 400. Ask the user before saving a default.

`zero-bounce-validate-email`, `icypeas-verify-email` and `findymail-verify-email` cannot be Function steps. `clearout-phone-validate-phone` can.

| templateId | Needs | List price | Function step? |
|---|---|---|---|
| `zero-bounce-validate-email` | `email` | $0.0065 | No |
| `findymail-verify-email` | `email` | $0.0043 | No |
| `icypeas-verify-email` | `email` | $0.0043 | No |
| `reoon-verify-email` | `email` | own key | No |
| `clearout-phone-validate-phone` (phone: carrier and line type) | `phone` | $0.0065 | Yes |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## When a paid action is refused for "no account"

Actions marked `connection: optional` run on the user's own key, or on Loopster's account if the workspace saved Loopster as that provider's default. With neither, `run_capability` answers 400 and nothing runs. Ask the user before saving a default (`set_provider_default` with `account: "loopster"`), because it applies to every column created afterwards for that provider.
