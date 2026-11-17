# Bugs we found

Two kinds of bugs turned up while building and testing this.

```
   Part A.  Bugs in Affinda's parser     4 found   (worth reporting to Affinda)
   Part B.  Bugs in our own code         2 found   (both fixed)
```

> **Honesty note.** All résumés were synthetic, and each one was parsed once through the
> Affinda Sandbox (schema v1.0). These results are reproducible on these inputs. They
> are not production rates.

<br/>

---

## Part A. Bugs in Affinda's parser

These are separate from what the enricher adds. The enricher fills in fields Affinda
never had. These bugs are cases where Affinda **dropped, cut off, or got a value
wrong**.

```
┌────┬──────────────────────────────────────┬──────────────────┬───────────────────┐
│ #  │ The bug                              │ Type             │ Can we enrich it? │
├────┼──────────────────────────────────────┼──────────────────┼───────────────────┤
│ 1  │ Mid-tier skills get dropped          │ silently drops   │ flag only         │
│ 2  │ "Bar admission" is never extracted   │ silently drops   │ no                │
│ 3  │ "withdrawn" year saved as grad date  │ wrong value      │ partly            │
│ 4  │ Degree name cut off + wrong level    │ truncation       │ no                │
└────┴──────────────────────────────────────┴──────────────────┴───────────────────┘
```

<br/>

### Bug 1. Mid-tier skills get dropped depending on wording

Top skills are almost always extracted. Mid-tier skills (Azure, Tableau, Spark)
disappear depending on the words around them.

```
   Skill        extracted          Skill        extracted
   ──────────   ─────────          ──────────   ─────────
   Python       9 / 9              Spark        6 / 8
   Java         9 / 9              Tableau      4 / 8
   SQL          9 / 9              Azure        3 / 8
   AWS          9 / 9              Kubernetes   8 / 8
```

**The sharp cases.** In every one, the word is in `rawText`:

- `S041` "Exposure to Azure" in a plain skills list. Azure is dropped.
- `S046` "Brief exposure to Tableau" in a plain skills list. Tableau is dropped.
- `S005` "8+ years of Azure" is dropped, but "8+ years of Java" in the same résumé is kept.
- `S010` "Strong Tableau experience". Tableau is dropped.

**Why it looks like a threshold issue.** The same skills come through fine in other
wordings ("Solid Spark", "Working knowledge of Azure", "Basic Tableau"). So Affinda
knows these skills. The words around them seem to push the skill under a cut-off.

**Impact.** A candidate with real Azure experience drops out of skill search, and nobody
is told.

<br/>

### Bug 2. "Bar admission" is never extracted

A real legal credential is missing from the output **every time**: 7 tries, 0
extracted.

- IDs: `C010` `C022` `C034` `C046` `C058` `C070` `C082`
- It is the **only** certification name that was ever dropped in the 100-cert set.

**Impact.** The whole credential is gone, not just its status. It looks like a gap in
Affinda's certification vocabulary.

<br/>

### Bug 3. A "withdrawn" year is saved as a graduation date

When a degree line gives the year someone **left**, Affinda puts it in
`education[].dateRange.end`. That is the same field a graduation date uses. An
unfinished degree then looks finished.

```
   Résumé says:   Juris Doctor (JD), Lakeside College, withdrawn 2020
   Affinda says:  end.date = 2020-01-01          (reads as "graduated 2020")
```

- `E053` is the clearest example.
- It happens in **9 / 9** "withdrawn" degrees and **2 / 12** "incomplete" ones.
- More arguable: **11 / 11** "expected 2029" degrees come back with `end 2029`, which
  reads like a future graduation.

**Impact.** This is a wrong value, not a missing one. Our enricher adds the real status
(`incomplete`), but the misleading date stays in Affinda's data. We never edit it.

<br/>

### Bug 4. Degree name cut off, and the level is wrong

```
   Résumé says:   Juris Doctor (JD)
   Affinda says:  "Juris Doctor (JD"      level = master
```

- `E053`. The closing bracket is lost, and a JD (a doctoral-level degree) is tagged as a
  master's.
- Affinda's own sample response in its docs shows the same kind of cut-off
  (`"Bachelor of"`). So the truncation looks like known behaviour. The wrong level is
  the firmer half of this bug.

<br/>

### Not a bug: certificates show up under `certifications`

We first logged this as a bug, then took it back. Affinda's docs say that education
entries at certificate level (for example "Certificate IV in Cybersecurity") are moved
to `certifications` on purpose.

What it means for us: our education check **also reads `certifications`**.

<br/>

### How this shows up in our results

In the 300-résumé test, Affinda never returned:

```
   11 skills      10 degrees      7 certs
```

Those are the "Affinda dropped it" rows in [`eval/results/results_table.md`](../eval/results/results_table.md).
The 11 skills are Azure, Tableau and Spark (bug 1). We cannot enrich what never arrived.

<br/>

---

## Part B. Bugs in our own code (both fixed)

### Fix 1. Dashes were cutting off the qualifier

```
   Résumé says:   CISSP — expired 2022
   We read:       CISSP                 ← clause stopped at the dash
   Result:        "expired" never seen, so the cert was marked unknown
```

**Cause.** The locator treated dashes (`—` `–`) and bullets (`•` `·`) as the end of a
clause. Résumés often put the status right after a dash.

**Fix.** The education and certification checks now use their own boundary set
(`STATUS_BOUNDARIES` = `. ; ! ? newline |`), which has no dashes or bullets. The skill
check keeps the dashes, because it needs them to split lists like "Git — Linux — Agile".

```
   Recall before fix  →  after fix
   ─────────────────     ─────────
   Education   ~30%   →  76%
   Certs       ~29%   →  88%
```

<br/>

### Fix 2. The test harness missed renamed skills

```
   Résumé says:   AWS
   Affinda says:  name = "Amazon Web Services",  text = "AWS"
   Harness:       looked for "AWS" in name only → "Affinda dropped it"   ✗ wrong
```

**Cause.** Affinda sometimes renames a skill and keeps the original wording in `text`.
The harness only matched on the name, so it counted 8 correctly enriched AWS cases as
drops. The enricher itself was fine. It already used `text`.

**Fix.** The harness now matches on the name **and** the `text` field (exact match
first, then substring).

```
   Skill recall before fix  →  after fix
   ───────────────────────     ─────────
   41 / 47 = 87%            →  46 / 52 = 88%
   "dropped" skills  19     →  11  (the real ones, bug 1)
```

False alarms stayed at **zero** before and after both fixes.
