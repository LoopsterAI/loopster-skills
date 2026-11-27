"""Build and lint the Loopster skills pack.

python3 -I tools/build.py          lint, sync shared references, build dist/ (per-skill zips + AGENTS.md)
python3 -I tools/build.py --check  lint only; exit 1 on any problem

Rules enforced:
- frontmatter uses only the portable fields (name, description, license, compatibility, metadata, allowed-tools)
- name == folder, lowercase-hyphen, <= 64 chars; description <= 1024 chars
- shared/*.md copied into every skill's references/ (each skill folder stands alone)
- shared/steps/*.md copied into the skills listed in shared/steps/steps.json, and checked unchanged there
- no mention of products or people we must never name (list kept outside the repo; no list, no build),
  no real person's LinkedIn profile or post, and no internal test notes
- descriptions carry no < or >
- every line or paragraph with a dollar figure is followed (same block or next) by the pricing sentence
- every relative reference in SKILL.md (references/x.md) exists
- SKILL.md under 500 lines
"""
import io
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "loopster", "skills")
SHARED = os.path.join(ROOT, "shared")
STEPS_DIR = os.path.join(SHARED, "steps")


def steps_map():
    """shared/steps/steps.json: step file -> the skills that carry it (a workflow and its small skills)."""
    path = os.path.join(STEPS_DIR, "steps.json")
    if not os.path.exists(path):
        return {}
    import json
    return {k: v for k, v in json.load(open(path)).items() if k.endswith(".md")}
DIST = os.path.join(ROOT, "dist")
PORTABLE = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
# Names that must never appear in the pack: products we don't name, and the people on the team. The list is never
# committed: it comes from tools/forbidden-names.txt (git-ignored, one regex per line) or LOOPSTER_FORBIDDEN (comma
# separated). Without either the build refuses to run, so a checkout without the list can't pass unchecked.
_FORBIDDEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forbidden-names.txt")
if os.environ.get("LOOPSTER_FORBIDDEN"):
    FORBIDDEN = [x.strip() for x in os.environ["LOOPSTER_FORBIDDEN"].split(",") if x.strip()]
elif os.path.exists(_FORBIDDEN_FILE):
    FORBIDDEN = [l.strip() for l in open(_FORBIDDEN_FILE) if l.strip() and not l.startswith("#")]
else:
    FORBIDDEN = []
# A person's profile or post: the pack and its evals name no real person (use a made-up slug in examples).
PEOPLE = [r"linkedin\.com/(?:in|posts)/(?!example\b|jane-doe\b|john-doe\b)[\w%-]+"]
# Wording that doesn't belong in a public pack: internal test notes, and product behaviour stated as a complaint.
STALE = [r"\btested live\b", r"\bin testing\b", r"\bnot (been )?run live\b", r"\bhidden table\b",
         r"\bshows? (it|the column|this column|any [\w`-]+ column) at zero\b", r"\bnot even `?maxCostUsd",
         r"\bno working cap\b", r"maxCostUsd`? doesn't (limit|stop)"]
PRICING = "Real usage depends on your use case and settings, so always check the final cost estimate before you run."


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm, body = m.group(1), text[m.end():]
    keys, data, cur = [], {}, None
    for line in fm.split("\n"):
        if re.match(r"^[A-Za-z][\w-]*:", line):
            k, v = line.split(":", 1)
            keys.append(k)
            data[k] = v.strip()
            cur = k
        elif cur and line.startswith(" "):
            data[cur] += "\n" + line
    return (keys, data), body


def lint_skill(folder, problems):
    path = os.path.join(SKILLS, folder, "SKILL.md")
    if not os.path.exists(path):
        problems.append(f"{folder}: no SKILL.md")
        return
    text = open(path).read()
    fm, body = frontmatter(text)
    if not fm:
        problems.append(f"{folder}: no frontmatter")
        return
    keys, data = fm
    extra = set(keys) - PORTABLE
    if extra:
        problems.append(f"{folder}: non-portable frontmatter fields {sorted(extra)}")
    name = data.get("name", "")
    if name != folder:
        problems.append(f"{folder}: name '{name}' must equal the folder name")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append(f"{folder}: name must be lowercase-hyphen, <= 64 chars")
    desc = data.get("description", "")
    if not desc or len(desc) > 1024:
        problems.append(f"{folder}: description missing or over 1024 chars ({len(desc)})")
    if re.search(r"[<>]", desc):
        problems.append(f"{folder}: description must not contain < or > (skill uploads reject it)")
    if len(text.splitlines()) > 500:
        problems.append(f"{folder}: SKILL.md over 500 lines")
    for ref in set(re.findall(r"`?(references/[\w.\-]+)`?", text)):
        if not os.path.exists(os.path.join(SKILLS, folder, ref)) and not os.path.exists(os.path.join(SHARED, os.path.basename(ref))):
            problems.append(f"{folder}: missing {ref}")


def lint_text(path, problems):
    rel = os.path.relpath(path, ROOT)
    text = open(path, encoding="utf-8").read()
    for pat in FORBIDDEN:
        if re.search(pat, text, re.I):
            problems.append(f"{rel}: forbidden name matches /{pat}/")
    for pat in PEOPLE:
        m = re.search(pat, text, re.I)
        if m:
            problems.append(f"{rel}: names a real person's profile: {m.group(0)!r}")
    if rel.endswith(".py"):
        return  # scripts: names and profiles only
    for pat in STALE:
        m = re.search(pat, text, re.I)
        if m:
            problems.append(f"{rel}: wording not fit for a public pack: {m.group(0)!r}")
    if rel.startswith("evals/") or rel.endswith(".json"):
        return  # internal test prompts and manifests carry no customer-facing prices
    # Every section (text between headings) that gives a dollar figure must also carry the pricing sentence.
    # Code fences count too: an example output with a price needs the sentence in the same section.
    sections = re.split(r"\n(?=#{1,6} )", re.sub(r"```[a-z]*\n|```", "", text))
    for sec in sections:
        sec_prices = re.sub(r"\$\d[\d.,]*\s?[MKkB]\b", "", sec)  # revenue or funding bands like $10M are not prices
        sec_prices = re.sub(r"\b(over|above:?) \$\d+\b(?![.,]\d)", "", sec_prices)  # spend thresholds like "over $25" are not prices
        if re.search(r"\$\d", sec_prices) and PRICING not in sec:
            first = next((l for l in sec.splitlines() if re.search(r"\$\d", l)), "")
            problems.append(f"{rel}: section with a dollar figure but no pricing sentence: {first.strip()[:90]!r}")


def sync_shared():
    for folder in sorted(f for f in os.listdir(SKILLS) if not f.startswith(".")):
        d = os.path.join(SKILLS, folder)
        if not os.path.isdir(d):
            continue
        refs = os.path.join(d, "references")
        os.makedirs(refs, exist_ok=True)
        for f in os.listdir(SHARED):
            if f.endswith(".md"):
                shutil.copyfile(os.path.join(SHARED, f), os.path.join(refs, f))
    for f, skills in steps_map().items():
        for folder in skills:
            refs = os.path.join(SKILLS, folder, "references")
            if os.path.isdir(os.path.dirname(refs)):
                os.makedirs(refs, exist_ok=True)
                shutil.copyfile(os.path.join(STEPS_DIR, f), os.path.join(refs, f))


def check_steps(problems):
    """Every listed skill exists and carries the step file unchanged (a copy edited by hand would drift)."""
    for f, skills in steps_map().items():
        src = open(os.path.join(STEPS_DIR, f)).read()
        for folder in skills:
            copy = os.path.join(SKILLS, folder, "references", f)
            if not os.path.isdir(os.path.join(SKILLS, folder)):
                problems.append(f"shared/steps/steps.json: no skill folder {folder}")
            elif not os.path.exists(copy) or open(copy).read() != src:
                problems.append(f"{folder}/references/{f}: differs from shared/steps/{f} (edit the shared file, then build)")


def build_dist():
    os.makedirs(DIST, exist_ok=True)
    agents = ["# Loopster skills for any AI agent", "",
              "Connect the Loopster MCP server (https://app.loopster.ai/api/mcp), then follow the skill that matches the job.",
              "Wherever a skill says `references/<file>.md`, that file is in this document: the shared files at the top,",
              "and each skill's own files right after its section. It is large: load it for Loopster work only.", ""]
    shared_names = {f for f in os.listdir(SHARED) if f.endswith(".md")} | set(steps_map())
    for f in sorted(os.listdir(SHARED)):
        if f.endswith(".md"):
            agents += [f"<!-- references/{f} -->", open(os.path.join(SHARED, f)).read().strip(), ""]
    for f in sorted(steps_map()):
        agents += [f"<!-- references/{f} -->", open(os.path.join(STEPS_DIR, f)).read().strip(), ""]
    for folder in sorted(f for f in os.listdir(SKILLS) if not f.startswith(".")):
        d = os.path.join(SKILLS, folder)
        if not os.path.isdir(d):
            continue
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for base, _, files in os.walk(d):
                for f in sorted(files):
                    full = os.path.join(base, f)
                    z.write(full, os.path.join(folder, os.path.relpath(full, d)))
        open(os.path.join(DIST, f"{folder}.zip"), "wb").write(buf.getvalue())
        (_, data), body = frontmatter(open(os.path.join(d, "SKILL.md")).read())
        agents += [f"## {folder}", "", data.get("description", ""), "", body.strip(), ""]
        refs = os.path.join(d, "references")
        for rf in (sorted(os.listdir(refs)) if os.path.isdir(refs) else []):
            if rf.endswith(".md") and rf not in shared_names:
                agents += [f"<!-- {folder}/references/{rf} -->", open(os.path.join(refs, rf)).read().strip(), ""]
    open(os.path.join(DIST, "AGENTS.md"), "w").write("\n".join(agents))


def main():
    check_only = "--check" in sys.argv
    if not FORBIDDEN:
        print("PROBLEMS:\n - no forbidden-names list: put it in tools/forbidden-names.txt (git-ignored) or LOOPSTER_FORBIDDEN")
        sys.exit(1)
    problems = []
    if not check_only:
        sync_shared()
    for folder in sorted(f for f in os.listdir(SKILLS) if not f.startswith(".")):
        if os.path.isdir(os.path.join(SKILLS, folder)):
            lint_skill(folder, problems)
    check_steps(problems)
    for base, _, files in os.walk(ROOT):
        # evals/results holds raw run transcripts (git-ignored), not shipped text
        if "/.git" in base or base.startswith(DIST) or "/evals/results" in base:
            continue
        for f in files:
            if f.endswith((".md", ".json", ".py")) and "research" not in base:
                lint_text(os.path.join(base, f), problems)
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    if not check_only:
        build_dist()
    n = len([f for f in os.listdir(SKILLS) if not f.startswith(".") and os.path.isdir(os.path.join(SKILLS, f))])
    print(f"OK: {n} skills linted" + ("" if check_only else ", shared references synced, dist/ built"))


if __name__ == "__main__":
    main()
