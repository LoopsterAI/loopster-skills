# CRM audit checks (free)

Run these on the rows you read from the import table. They make no paid calls and need no table: the audit is a local script on the rows you read.

**Reading the rows:**
- **More than about 500 records:** use `export_table` with `format: "jsonl"`, then poll `get_export` and download `resultUrl` to a local file (free; 20 exports an hour). Each line is one row keyed by column name, with `_row_id`.
- **A small table, or no way to download a file:** use `list_rows` (paged with `page` and `pageSize`; use `cursor` only when you filter or sort). CRM import tables are wide, so use a `pageSize` of 100 or less and ask only for the columns the checks read (`columns`). Read the default detailed format, because `concise` shortens long values.
- A large page can come back with fewer rows than `pageSize`, and the answer says so in `warnings`. If you see that, read the table again from the start with a smaller `pageSize`, or rows are skipped.
- At the end, check that the rows you read match the row total in `get_status`.

**Running the checks:**
- **Over a few hundred records:** write the rows to a local file (the export, or the pages you read) and compute the checks with a short script. Don't do it by reading.
- **No code execution available:** audit a random sample of 500, and say it's a sample.
- The rows you read are a snapshot, and so is the working copy table made later in Step 3. For a monthly refresh, re-read the CRM import table first, so you work on current records.

## Normalize first

- **Email:** trim, lower-case.
- **Domain:**
  - from the website: lower-case, strip `http(s)://`, `www.` and any path;
  - from the email: the part after `@`.
- **LinkedIn URL:** `https://www.linkedin.com/in/<handle>`. Lower-case the handle, and strip query strings and the trailing slash.
- **Names:** trim. Collapse spaces. Drop emojis and titles.

## Checks

| Check | Rule | Severity |
|---|---|---|
| Missing email | empty | high for outbound |
| Personal email | domain in gmail.com, googlemail.com, yahoo.com, outlook.com, hotmail.com, live.com, icloud.com, me.com, aol.com, proton.me, protonmail.com, gmx.com, mail.com | medium |
| Role inbox | local part in info, sales, hello, contact, admin, support, team, marketing, office | medium |
| Malformed email | not `x@y.z` | high |
| Domain mismatch | email domain ≠ company domain (ignore personal emails) | medium: often a job change or an agency |
| Missing LinkedIn URL | empty | medium: blocks the free routes |
| Missing title / company / industry / size / country | empty | low to medium |
| Duplicate contact | same normalized email; or same LinkedIn URL; or same first + last name + company domain | high |
| Duplicate company | same normalized domain | high |

## Health score

The share of records with:
- a valid work email;
- a name;
- a company domain;
- a LinkedIn URL;
- no duplicate.

Report it before and after fixes.

## Duplicate output

Group duplicates, and for each group list the record ids with their last-modified date, if the import has it. Most CRMs merge in their own UI, so give the user the list and the suggested survivor (the most complete or most recent record). Don't delete records through write-back.
