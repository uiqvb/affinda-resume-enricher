# Why we built it this way

Every choice below is here to answer a hard question before someone asks it.

Each card reads the same way:

> ✅ **what we do**  ·  💡 **why**  ·  🚫 **what we chose against**

<br/>

---

### 1. We add notes. We never edit Affinda.

✅ Wrap Affinda's answer. Put our notes in a separate box beside it.

💡 If we are ever wrong, we break nothing. And we can prove the original is untouched.

🚫 Not: changing Affinda's fields in place.

<br/>

### 2. Rules, not AI (for now)

✅ Match a small, fixed set of cue words.

💡 Rules are fast, free, and explainable. Every answer points at the exact words. No AI
cost, no waiting, no data leaving the box.

🚫 Not: an AI model in v1. That is saved for later, and only for the hard leftovers.

<br/>

### 3. We note every item, not just the bad ones

✅ Write a note for every skill, degree, and cert. Tag each one `warning` or `info`.

💡 The customer can then filter. It is easier to filter than to recover a signal we threw away.

🚫 Not: only reporting problems and hiding the "this is genuinely strong" cases.

<br/>

### 4. When unsure, stay quiet

✅ If no cue matches, the item is `info`, never a `warning`.

💡 A false alarm on a good person is the costly mistake. A quiet miss is cheap. We proved
it: **zero false alarms across 300 resumes.**

🚫 Not: guessing "completed" or "valid" from weak evidence.

<br/>

### 5. One folder per thing we check

✅ Skill, education, and certification each live in their own folder. Shared tools sit
below them. Arrows only point down.

💡 Adding a new check in v2 is one new folder and one new line. No framework needed.

🚫 Not: a heavy layered design, or one big tangled file.

<br/>

### 6. Three separate answers per item

✅ `status` (what the text says), `severity` (warning or info), `confidence` (did we find it).

💡 Keeping them separate keeps the logic honest. Severity is a fixed lookup, so it can
never drift.

🚫 Not: blending them into one fuzzy score.

<br/>

### 7. Always keep the proof

✅ Save the exact words we matched, and where they are in the text.

💡 Anyone can check any answer in one glance. A highlight can point right at it.

🚫 Not: a verdict with no evidence behind it.

<br/>

### 8. A dash means different things in different places

✅ For skills a dash splits items apart (`Git — Linux`). For certs it joins an item to
its status (`CISSP — expired`), so we do not stop at it.

💡 This single fix lifted degree and cert results from about 30% to 76 to 88%.

🚫 Not: one rule for dashes everywhere (it hid cert statuses or merged skills).

<br/>

### 9. Test on real parser output, set the bar after seeing the numbers

✅ Score against 300 resumes actually parsed by Affinda. Decide "good enough" after
seeing real results, not before.

💡 Honest numbers beat a number we hoped for. Tricky multi-item cases are set aside and
counted, not hidden.

🚫 Not: self-graded claims or cherry-picked examples.

<br/>

---

## How we got here

```
  Day 1   Ideation    183 resumes, 4 rounds        found the 3 real gaps
  Day 2   Planning    300 resumes parsed by Affinda proved the gaps, locked the design
  Day 3   Build       the engine, 34 tests
  Day 4   Finalize    CLI, API, Docker, full eval, these docs
```

Every number in this project comes from code you can re-run. Nothing is hand-counted.

<br/>

---

## Where v2 goes

The resumes v1 is unsure about are saved as `unknown`. That pile is the map for what
comes next. Each item below is just a new folder plus a new line:

```
  0.  TOP PRIORITY: bind the "basic" cue to the skill token.
      Real resumes exposed stray-word false alarms ("Accounting, Basic,
      Budgeting" tags Budgeting basic; "Basic First Aid" tags First Aid).
      Fix: only accept "basic" when it attaches to the skill, not just nearby.
  1.  a check for fake employment dates
  2.  a flag for skills the text has but Affinda dropped
  3.  typo-tolerant matching on the key "bad" cues
  4.  an AI step, used ONLY on the "unknown" pile
  5.  more cue words, grown from real resumes (never invented)
```

**Three rules never change, no matter what v2 adds:**

```
  ·  never edit Affinda's data
  ·  never trade away precision on good people
  ·  always keep the proof
```
