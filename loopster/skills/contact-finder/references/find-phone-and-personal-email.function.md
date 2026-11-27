# Function designs: Find mobile phone and Find personal email

Build each of these in a table first. Make a scratch table (`autoplay: false`) with a plain `LinkedIn URL` column and the user's 3 sample people. Add the provider step as a column that reads it. Price it and ask first (house rules, section 4), then run 1 row, then the other 2. Next, run `create_function` with `fromTable` (`function-builder`, Step 2), and write the new `functionId` in the "Functions" section of `loopster-context.md` straight away. Then dry-run the publish, and run 3 real samples through the Function before a list.

Every step in a Function runs for every input, so each Function holds one paid provider step. Run the free Loopster Data lookup first as a capability with `maxCostUsd: 0` (SKILL.md, Step 1), then run the Function on the misses only. Prices and the order to try providers are in `routes.md`.

## Find mobile phone · Loopster skill

- Title: `Find mobile phone · Loopster skill`
- Description: `Built by the Loopster contact-finder skill 0.1.0. One paid mobile lookup, for people the free Loopster Data lookup missed. Safe to edit in Loopster.`
- Input: a `LinkedIn URL` column in the scratch table. `fromTable` turns it into the required `LinkedIn URL` Function input, and the input takes the column's header, so the header must be exactly `LinkedIn URL`. If the list has no URLs, get them first (`routes.md`, "Getting a LinkedIn URL first").
- Step: `ai-ark-find-mobile-phone`, header `Mobile phone`, reading the `LinkedIn URL` column as `@{<LinkedIn URL column id>}`.
  - Read the template's settings with `get_column_template` and pass them under `taskConfig`. Set `execution_mode: "managed"` where it is offered, or leave it off if the user has their own key for the provider.
  - Other providers a Function can take: `wiza-find-mobile-phone`, `surfe-find-mobile-phone`, `better-contact-find-mobile-phone`, `full-enrich-find-mobile-phone`. Use one per Function. `findymail-find-mobile-phone` and `contactout-find-mobile-phone` are not Function steps; use `run_capability`.
- Output: return the provider column. Check the output key with `get_function` after `fromTable`. A lookup that finds nothing still returns text such as `{"found":false}`, so read it as JSON.
- Optional check step: `clearout-phone-validate-phone`. Extract the number first with a Formula that parses the mobile step's JSON (or a field reference), and give Clearout that Formula's output. It runs for every input unless it has a run condition, so give it one that runs only when the mobile step found a number. Build it in the same scratch table and set the run condition on its column with `update_column` before `create_function` (`function-builder`, "Steps that run only sometimes"). The condition comes along. Return its output only with that condition in place.

## Find personal email · Loopster skill

- Title: `Find personal email · Loopster skill`
- Description: `Built by the Loopster contact-finder skill 0.1.0. One paid personal-email lookup, for people the free Loopster Data lookup missed. Safe to edit in Loopster.`
- Input: a `LinkedIn URL` column in the scratch table, as above. It becomes the required `LinkedIn URL` Function input. If the list has no LinkedIn URLs, get them first (`routes.md`, "Getting a LinkedIn URL first") and run only the people who now have one.
- Step: `full-enrich-find-personal-email`, header `Personal email`, reading the `LinkedIn URL` column as `@{<LinkedIn URL column id>}`. Settings as above.
  - Other providers a Function can take: `surfe-find-personal-email`, `aviato-find-personal-email`. Use one per Function. `contactout-find-personal-email` is not a Function step; use `run_capability`.
- Output: return the provider column. Check the output key with `get_function` after `fromTable`, and read the answer as JSON.

## Publish and run

1. `create_function` with `fromTable`: `columnIds` is the paid step's column (plus the Formula and Clearout columns if you built them), and `outputColumnIds` is the paid step's column (add the Clearout column only with its run condition in place). Write the new id in the "Functions" section straight away.
2. `publish_function` with `dryRun: true`. Show the contract (inputs, output key, cost per run) and ask before the live publish.
3. After a clear yes, publish live. Ask again before opening it to agents, because it is a separate yes. Then call `set_function_agent_access` with `agentAccess: true`.
4. Run 3 real samples through the published Function and compare them with the table cells (price them first and ask). Then run it as the work-email Function runs: 1, then 10, then 100 at a time, the wallet read after each batch, and a `run-function` column for more than about 25 people.
5. Write the Function's id and its measured cost per run in the "Functions" section of `loopster-context.md`.

Mobile numbers and personal emails carry consent rules in many regions. Ask what the user will use them for before they call or text (SKILL.md, "Respect consent").
