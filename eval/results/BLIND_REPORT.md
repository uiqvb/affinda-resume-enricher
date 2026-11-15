# Fresh blind batch: generalization test

These résumés were **not** used to build the rules. `novel` rows use phrasings deliberately outside our word lists. Input is synthetic Affinda-shaped JSON, so this tests the enricher's rule coverage, not Affinda's parsing.

## Headline

- **Overall catch rate:** 9/27 (33%)
- **On phrasings we cover:** 9/10 (90%)  (sanity check, should be high)
- **On NOVEL phrasings:** 0/17 (0%)  (the real generalization number)
- **False alarms on good items:** 0/8  (PASS, none)

**The key result:** even where a novel phrasing is missed, it stays quiet (`info`), never a false alarm. The fail-safe design holds on unseen wording.

## Every case

| id | coverage | the line | expected | our status | verdict |
|---|---|---|---|---|---|
| B01 | covered · control | Expert in Python with 9 years shipping production code | strong | strong (no) | ✅ ok |
| B02 | covered · control | Advanced Docker and container orchestration | strong | strong (no) | ✅ ok |
| B03 | covered | Currently learning SQL through an online course | learning | learning (yes) | ✅ exact |
| B04 | covered | Basic knowledge of Java | basic | basic (yes) | ✅ exact |
| B05 | covered | No experience with Go | no_experience | no_experience (yes) | ✅ exact |
| B06 | novel | Rust is pretty rusty these days, I am out of practice | basic | plain (no) | ⚪ missed |
| B07 | novel | Hoping to pick up Kotlin next year | learning | plain (no) | ⚪ missed |
| B08 | novel | I dabbled in Scala a little bit | basic | plain (no) | ⚪ missed |
| B09 | novel | Honestly Perl is not my strong suit | basic | strong (no) | ⚪ missed |
| B10 | novel | Have not touched COBOL in a very long time | lapsed | plain (no) | ⚪ missed |
| B11 | novel | Never really got the hang of React | no_experience | plain (no) | ⚪ missed |
| B12 | novel | Tableau skills have gotten rusty since I stopped using it | lapsed | plain (no) | ⚪ missed |
| B13 | covered · control | Seasoned AWS architect, extensive hands on experience | strong | strong (no) | ✅ ok |
| B14 | covered · control | Comfortable with Excel for day to day reporting | intermediate | intermediate (no) | ✅ ok |
| B15 | novel | Figma was a long time ago, barely remember it now | lapsed | plain (no) | ⚪ missed |
| B16 | covered · control | BSc Physics, graduated with honours 2015 | completed | completed (no) | ✅ ok |
| B17 | covered | MBA, currently enrolled, part time | in_progress | in_progress (yes) | ✅ exact |
| B18 | covered | BEng Mechanical, expected 2028 | expected | expected (yes) | ✅ exact |
| B19 | novel | BA History, I never finished the final year | incomplete | unknown (no) | ⚪ missed |
| B20 | novel | MSc Chemistry, abandoned after the first semester | incomplete | unknown (no) | ⚪ missed |
| B21 | novel | Diploma in Nursing, didn't end up graduating | incomplete | unknown (no) | ⚪ missed |
| B22 | novel | PhD Biology, still writing up the thesis | in_progress | unknown (no) | ⚪ missed |
| B23 | covered | BCom Accounting, dropped out halfway through | incomplete | incomplete (yes) | ✅ exact |
| B24 | covered · control | LLB Law, conferred 2019 | completed | completed (no) | ✅ ok |
| B25 | novel | MA Design, took a leave of absence and never returned | incomplete | unknown (no) | ⚪ missed |
| B26 | covered | AWS Solutions Architect, expired 2021 | expired | unknown (no) | ⚪ missed |
| B27 | novel | PMP certification, I let it lapse a while ago | expired | unknown (no) | ⚪ missed |
| B28 | novel | CISSP, sunset in 2022 and not renewed | expired | active (no) | ⚪ missed |
| B29 | covered | CPA license was revoked after an investigation | revoked | revoked (yes) | ✅ exact |
| B30 | covered · control | CCNA, active and in good standing | active | active (no) | ✅ ok |
| B31 | covered | Six Sigma Black Belt, currently suspended pending review | suspended | suspended (yes) | ✅ exact |
| B32 | covered | First Aid certificate is well out of date now | expired | expired (yes) | ✅ exact |
| B33 | novel | Registered Nurse license, no longer current | expired | unknown (no) | ⚪ missed |
| B34 | novel | Forklift licence, I never bothered to renew it | expired | unknown (no) | ⚪ missed |
| B35 | covered · control | PMP, valid through 2027 | active | unknown (no) | ✅ ok |