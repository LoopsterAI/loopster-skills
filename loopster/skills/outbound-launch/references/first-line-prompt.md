# First-line prompt (AI column)

The first line fills the campaign's `{FIRST_LINE}`. The campaign's message template carries the pain, proof and call to action, so the line only has to earn the second sentence.

## Before the prompt: one input column

Lists come from different plays, and some columns may be missing or skipped. Build one Formula column, `Signal text`, that combines whatever exists, with a fallback, and point the prompt at that one column. For example:

```js
(() => { const pick = (...v) => v.map(x => String(x ?? '').trim()).find(x => x && x !== 'none');
  return pick(@{<Opener id>}, @{<Engagement topic id>}, @{<Company summary id>}) || 'none'; })()
```

List each of those mentions in `optionalMentions` (`update_column`). If a column doesn't exist on this list, leave it out of the Formula.

## The prompt

Don't pass the person's name. Models tend to greet with it even when told not to. Fill the `<…>` from `loopster-context.md`.

```
You write the first line of a cold message to a <title> at @{<Company id>}.
What we know (may be "none"): @{<Signal text id>}
What we help with: <one-line offer from context>. The problem they likely feel: <pain from context>.

Write ONE sentence, 12 to 22 words, that connects the most specific fact above to a consequence for someone in their seat.
Rules:
- Do not restate their job title or start date.
- Do not start with "Stepping into", "Starting as", "Taking over", "Congrats", "I saw", "I noticed", "Hope".
- No greeting, no name, no year, no exclamation marks, no hype words (<avoid list>).
- Plain, peer-to-peer, specific. If the fact is "none", write about the problem, not about them.
Return only the sentence.
```

## Good and bad (for calibration)

- **Bad:** "Stepping into the role of VP of Sales at Acme in August means selling analytics software for finance teams." It restates the title and date, is templated, and says nothing they don't know.
- **Better:** "Selling analytics software to finance teams usually means a long list of budget owners nobody has mapped yet." A fact, then a consequence, in their world.
- **Better:** "Hedge-fund buyers rarely take a first call without a peer reference, which makes the first 50 accounts the hard part." Specific to a fund-tech seller.

## Review before scale

1. **Sameness check:** read the 10 test lines together. If 3 or more share an opening or structure, change the prompt (add the opener to the banned list) and rerun with `force: true`. If the lines come from a Function, change its AI step in a new sandbox, publish after a yes, then rerun with `force: true`.
2. **Skeptical-buyer check** (top tier only, so trigger it on the top-tier `rowId`s only): a second AI column, or your own review:

```
You are a <title> at @{<Company id>}. You get 40 cold messages a week. Read this opening line:
"@{<First line id>}"
Reply with JSON only: {"verdict": "keep|fix", "why": "one short reason"}.
Mark fix if it sounds automated or templated, flatters, guesses, gets a fact wrong, restates their title, shows a scraping tell (odd capitalisation, a company suffix like "Inc."), or could have been sent to anyone.
```

If more than 1 in 10 come back `fix`, change the prompt and rerun. Don't hand-edit single lines.

## As a Function

When both checks pass and the user approves the lines, save the column as a Function (`SKILL.md`, Step 2, items 2 and 7). Run both checks again on the first 10 lines of the next list, even though the prompt is proven.
