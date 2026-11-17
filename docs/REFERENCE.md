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

> Full write-up with every reproducible ID, plus the two bugs we fixed in our own code:
> [`BUGS.md`](BUGS.md).

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
    └── summary         [ plain-English lines, one per needsReview item ]
```

Each **note** has the same 6 fields:

```
   entryIndex    which item in Affinda's list (0 = first)
   entity        the item's name, copied back
   status        what the text says   (see the menu below)
   confidence    high  or  low
   needsReview   yes  or  no
   evidence      the exact words + where they are
```

The full **status menu** (every value you can receive):

```
            ⚠️  needsReview: yes (worth a look)     ✅  needsReview: no (fine / neutral)
          ─────────────────────────────────       ──────────────────────────────
  SKILL     no_experience, learning,                strong, intermediate, plain
            lapsed, basic
  DEGREE    in_progress, expected, incomplete,       completed, unknown
            deferred, not_awarded
  CERT      expired, revoked, suspended, pending     active, unknown
```

`plain` and `unknown` mean "we found nothing worth saying". They are always `needsReview: no`.

<br/>

---

## 4. "Where is it weak?" (shown with examples)

Two honest weak spots. **One:** we only understand wording we have seen before. **Two:**
on real résumés a stray "basic" can land on the wrong skill. Here is exactly what both
look like, in plain examples.

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

**Weak spot 3: on real résumés, a stray "basic" can flag a clean skill.**

This one we only saw once we ran **real** strangers' résumés. Real skills often arrive as
one big comma list, and the word "basic" shows up for reasons that have nothing to do
with the skill next to it.

```
   Résumé says:   "Skills: Accounting, Basic, Budgeting, Data Entry"
                  (the person listed "Basic" as its own skill)
   What we do:      we see "basic" sitting beside "Budgeting" and tag Budgeting basic.
                    Wrong. The "basic" was never about Budgeting.

   Résumé says:   "Basic First Aid Certification"   (a course name)
   What we do:      we tag the nearby "First Aid" skill as basic. But "Basic First Aid"
                    is just the name of the course, not a weakness.
```

So on real data the **`basic` tag is our low-precision spot.** Good news: it is only ever
the *mildest* tag. The severe ones (`no experience`, `lapsed`, `expired`, `revoked`)
did **not** false-alarm, and degrees and certs stayed completely clean.

<br/>

**What we DON'T get wrong, even on real résumés.**

```
   ·  The severe warnings never fired on a clean item (0 across 18 real résumés).
   ·  Degrees: 0 false flags.   Certs: 0 false flags.
   ·  "Expert in Python, 9 years"  ->  marked strong, and never turned into a warning.
```

> Think of a smoke alarm. On real résumés ours will, now and then, **chirp "basic"** at
> clean air (the stray-word problem above). But it does not scream "FIRE" (the severe
> warnings) unless there really is smoke. The loud alarms stay trustworthy; the quiet
> "basic" chirp needs a human glance.

<br/>

**A smaller thing:**

```
  ·  Tiny symbol-heavy names like "C++", "C#", ".NET" are hard to pin down,
     so we handle them cautiously and sometimes skip them.
```

<br/>

We checked all of this two ways. First with a **fresh blind set** of résumés written in
wording we had never used before: lots of quiet misses on unusual wording, but no false
alarms on clean synthetic data. See
[`../eval/results/BLIND_REPORT.md`](../eval/results/BLIND_REPORT.md).

Then with **18 real strangers' résumés** parsed by Affinda. That is where the stray-"basic"
problem showed up: 23 `basic` chirps across 1,378 items, most of them stray-word matches,
and zero severe false alarms. Every one is listed with its résumé clause in
[`../eval/results/REAL_REPORT.md`](../eval/results/REAL_REPORT.md).

Teaching the tool more wording is the main job of v2 (see the roadmap in
[`DECISIONS.md`](DECISIONS.md)).
