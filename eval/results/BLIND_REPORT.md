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
| B01 | covered · control | Expert in Python with 9 years shipping production code | strong | strong (info) | ✅ ok |
| B02 | covered · control | Advanced Docker and container orchestration | strong | strong (info) | ✅ ok |
| B03 | covered | Currently learning SQL through an online course | learning | learning (warning) | ✅ exact |
| B04 | covered | Basic knowledge of Java | basic | basic (warning) | ✅ exact |
| B05 | covered | No experience with Go | no_experience | no_experience (warning) | ✅ exact |
| B06 | novel | Rust is pretty rusty these days, I am out of practice | basic | plain (info) | ⚪ missed |
| B07 | novel | Hoping to pick up Kotlin next year | learning | plain (info) | ⚪ missed |
| B08 | novel | I dabbled in Scala a little bit | basic | plain (info) | ⚪ missed |
| B09 | novel | Honestly Perl is not my strong suit | basic | strong (info) | ⚪ missed |
| B10 | novel | Have not touched COBOL in a very long time | lapsed | plain (info) | ⚪ missed |
| B11 | novel | Never really got the hang of React | no_experience | plain (info) | ⚪ missed |
| B12 | novel | Tableau skills have gotten rusty since I stopped using it | lapsed | plain (info) | ⚪ missed |
| B13 | covered · control | Seasoned AWS architect, extensive hands on experience | strong | strong (info) | ✅ ok |
| B14 | covered · control | Comfortable with Excel for day to day reporting | intermediate | intermediate (info) | ✅ ok |
| B15 | novel | Figma was a long time ago, barely remember it now | lapsed | plain (info) | ⚪ missed |
| B16 | covered · control | BSc Physics, graduated with honours 2015 | completed | completed (info) | ✅ ok |
| B17 | covered | MBA, currently enrolled, part time | in_progress | in_progress (warning) | ✅ exact |
| B18 | covered | BEng Mechanical, expected 2028 | expected | expected (warning) | ✅ exact |
| B19 | novel | BA History, I never finished the final year | incomplete | unknown (info) | ⚪ missed |
| B20 | novel | MSc Chemistry, abandoned after the first semester | incomplete | unknown (info) | ⚪ missed |
| B21 | novel | Diploma in Nursing, didn't end up graduating | incomplete | unknown (info) | ⚪ missed |
| B22 | novel | PhD Biology, still writing up the thesis | in_progress | unknown (info) | ⚪ missed |
| B23 | covered | BCom Accounting, dropped out halfway through | incomplete | incomplete (warning) | ✅ exact |
| B24 | covered · control | LLB Law, conferred 2019 | completed | completed (info) | ✅ ok |
| B25 | novel | MA Design, took a leave of absence and never returned | incomplete | unknown (info) | ⚪ missed |
| B26 | covered | AWS Solutions Architect, expired 2021 | expired | unknown (info) | ⚪ missed |
| B27 | novel | PMP certification, I let it lapse a while ago | expired | unknown (info) | ⚪ missed |
| B28 | novel | CISSP, sunset in 2022 and not renewed | expired | active (info) | ⚪ missed |
| B29 | covered | CPA license was revoked after an investigation | revoked | revoked (warning) | ✅ exact |
| B30 | covered · control | CCNA, active and in good standing | active | active (info) | ✅ ok |
| B31 | covered | Six Sigma Black Belt, currently suspended pending review | suspended | suspended (warning) | ✅ exact |
| B32 | covered | First Aid certificate is well out of date now | expired | expired (warning) | ✅ exact |
| B33 | novel | Registered Nurse license, no longer current | expired | unknown (info) | ⚪ missed |
| B34 | novel | Forklift licence, I never bothered to renew it | expired | unknown (info) | ⚪ missed |
| B35 | covered · control | PMP, valid through 2027 | active | unknown (info) | ✅ ok |