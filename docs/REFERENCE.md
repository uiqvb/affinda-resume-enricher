# The deeper details

Four questions a careful reader will ask. Answered one at a time.

```
   1.  Isn't this already in Affinda?        (short answer: no, we checked)
   2.  What bugs did you find in Affinda?    (4 real ones)
   3.  What exactly do I get back?           (the full output menu)
   4.  Where is it weak?                      (honest limits)
```

<br/>

---

## 1. "Isn't this already in Affinda?"

**No. We checked Affinda's own documented schema.**

The three things we add simply **do not exist** as fields in it. The key set is fixed,
so these are not just empty on our test data. The slots are not there at all.

```
   What we add                 Does Affinda's schema have it?
   ─────────────────────────   ──────────────────────────────
   skill   claim strength      ✗  no
   degree  completion status   ✗  no
   cert    validity status     ✗  no
```

So we are **not** redoing Affinda's job. We fill gaps it was never built to fill.

<br/>

---

## 2. "What bugs did you find in Affinda?"

While testing, we found 4 real parser bugs. These are **separate** from our product.
They are worth sending back to Affinda. They also explain why some items in our results
show up as "dropped by Affinda" (we cannot enrich what never arrived).

```
┌────┬──────────────────────────────────────────────┬──────────────────┐
│ #  │ The bug                                      │ Type             │
├────┼──────────────────────────────────────────────┼──────────────────┤
│ 1  │ Mid skills (Azure, Tableau, Spark) get       │ silently drops   │
│    │ dropped depending on wording.                │ a real skill     │
│    │ "8+ years of Azure" and Azure vanishes.      │                  │
├────┼──────────────────────────────────────────────┼──────────────────┤
│ 2  │ "Bar admission" is never extracted.          │ silently drops   │
│    │ 7 tries, 0 extracted.                        │ a real cert      │
├────┼──────────────────────────────────────────────┼──────────────────┤
│ 3  │ "withdrew 2020" is stored as a graduation    │ writes a WRONG   │
│    │ end-date. An unfinished degree looks done.   │ value            │
├────┼──────────────────────────────────────────────┼──────────────────┤
│ 4  │ "Juris Doctor (JD)" comes back cut off as    │ truncation +     │
│    │ "Juris Doctor (JD" and tagged as a master's. │ wrong label      │
└────┴──────────────────────────────────────────────┴──────────────────┘
```

**This connects to our numbers.** In the 300-resume test, Affinda never surfaced:

```
   11 skills      10 degrees      7 certs
```

Those are the "dropped" rows in the results (the skills are Azure, Tableau, Spark, from
bug 1). We cannot enrich what never arrived.

> **One honest subtlety.** Affinda sometimes *renames* a skill. "AWS" comes back as
> "Amazon Web Services", with the original wording kept in a `text` field. We match on
> that original wording, so those are enriched normally. They are **not** counted as
> drops. Only skills Affinda left out entirely are counted above.

> Full write-up with every reproducible ID lives in the process repo.

<br/>

---

## 3. "What exactly do I get back?"

The output is always this shape:

```
EnrichedJSON
├── originalJSON      Affinda's answer, copied, never changed
└── enrichmentJSON
    ├── version
    ├── checksRun       ["skill", "education", "certification"]
    ├── skills          [ one note per skill ]
    ├── education       [ one note per degree ]
    ├── certifications  [ one note per cert ]
    └── summary         [ plain-English warning lines ]
```

Each **note** has the same 6 fields:

```
   entryIndex    which item in Affinda's list (0 = first)
   entity        the item's name, copied back
   status        what the text says   (see the menu below)
   confidence    high  or  low
   severity      warning  or  info
   evidence      the exact words + where they are
```

The full **status menu** (every value you can receive):

```
            ⚠️  warning (worth a look)              ✅  info (fine / neutral)
          ─────────────────────────────────       ──────────────────────────────
  SKILL     no_experience, learning,                strong, intermediate, plain
            lapsed, basic
  DEGREE    in_progress, expected, incomplete,       completed, unknown
            deferred, not_awarded
  CERT      expired, revoked, suspended, pending     active, unknown
```

`plain` and `unknown` mean "we found nothing worth saying". They are always `info`.

<br/>

---

## 4. "Where is it weak?" (shown with examples)

The one real weak spot: **we only understand wording we have seen before.** Here is
exactly what that looks like, in plain examples.

<br/>

**Weak spot 1: wording we have never seen, so we stay silent.**

```
   Résumé says:   "SQL is pretty rusty these days"
   A person reads:  weak, out of practice
   What we do:      nothing. We don't know the word "rusty", so we say nothing.
```

We **miss** it. We would rather miss it than guess and get it wrong.

<br/>

**Weak spot 2: a single word can fool us.**

```
   Résumé says:   "Perl is not my strong suit"
   A person reads:  weak
   What we do:      we spot the word "strong" and mark Perl as strong. Backwards.

   Résumé says:   "CISSP certificate, not renewed"
   A person reads:  lapsed
   What we do:      we spot the word "renewed" and call it still valid.
```

Now and then an odd phrase tricks us into marking a problem as "fine".

<br/>

**The one mistake we never make: wrongly accusing a good person.**

```
   Résumé says:   "Expert in Python, 9 years"
   What we do:      we mark it strong.  ✅  Correct, and we will NEVER turn this
                    into a warning.
```

> Think of a smoke alarm that sometimes misses real smoke, but **never shrieks when the
> air is clean.** Our worst mistake is staying quiet about a real problem. We never
> invent a problem that is not there.

<br/>

**A couple of smaller things:**

```
  ·  Tiny symbol-heavy names like "C++", "C#", ".NET" are hard to pin down,
     so we handle them cautiously and sometimes skip them.

  ·  We tested on résumés we wrote ourselves (then ran through Affinda). We have
     not yet run a big pile of real strangers' résumés, so read the results as
     "works on our examples", not a guarantee in the wild.
```

<br/>

We checked all of this with a fresh set of résumés written in wording we had never used
before. It confirmed the picture above: lots of quiet misses on unusual wording, but not
a single good person wrongly flagged. See
[`../eval/results/BLIND_REPORT.md`](../eval/results/BLIND_REPORT.md).

Teaching the tool more wording is the main job of v2 (see the roadmap in
[`DECISIONS.md`](DECISIONS.md)).
