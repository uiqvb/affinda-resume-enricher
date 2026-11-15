# Real resumes: precision / sanity check

**18 genuine resumes** (CC0 source, parsed by the Affinda Sandbox), run through the enricher. These have **no answer key**, so this is not a scored recall test. It checks two things a human can verify on sight:

1. When we raise a warning, is it right?  (**precision**)
2. Do we ever flag a clean item?  (**false alarms**)

## At a glance

| | Skills | Degrees | Certs | Total |
|---|---|---|---|---|
| Items enriched | 1302 | 45 | 31 | **1378** |
| Warnings raised | 23 | 0 | 0 | **23** |

Out of **1378** enriched items, we raised **23 warnings**. Every one is listed below with the exact resume clause, so you can judge it yourself. Everything not listed we left as neutral `info` (no accusation).

## What this run told us (the honest read)

- **Every warning was the mildest kind:** `basic` x23. No `no_experience`, `lapsed`, `expired` or `revoked` false alarms fired on real data.
- **Degrees and certs: 0 warnings, 0 false alarms** across 45 degrees and 31 certs.
- **The `basic` rule is where real data bites us.** On our clean synthetic tests it never false-alarmed. Real resumes break that, because the word "basic" shows up in three places that are NOT a weakness claim:
    1. **As its own skill in a comma dump:** `Accounting, Basic, Budgeting, Data Entry` - Affinda lists each comma item as a skill, so "Basic" sits next to unrelated skills and bleeds onto them.
    2. **Inside a proper course / cert name:** `Basic First Aid`, `EMT - Basic`, `Basic Combat Trauma Training`, `Basic Offshore Safety Induction`. These are credential names, not self-assessments.
    3. **Describing a job task:** `performed basic emergency treatment`, `basic compressor build lines`. The task was entry-level, the person is not.
- **A few are actually correct**, e.g. `Mandarin Chinese - Basic Conversational` really does say basic. But most of the 23 are stray-word matches, so on real resumes the `basic` cue is **low precision**.
- **Takeaway:** the fail-safe design (never fires the severe warnings wrongly) held. But the blanket claim "we never flag a clean item" does **not** survive real messy resumes for the `basic` cue. v2 fix: only accept `basic` when the word is bound to the skill token, not merely nearby.

## Per resume

| resume | warnings | skills | degrees | certs |
|---|---|---|---|---|
| 26888302.pdf | **3** | 117 | 3 | 0 |
| 27502951.pdf | 0 | 67 | 3 | 1 |
| 27512470.pdf | 0 | 79 | 1 | 0 |
| 27902692.pdf | 0 | 67 | 1 | 6 |
| 28020046.pdf | **1** | 82 | 1 | 0 |
| 28186635.pdf | **5** | 62 | 2 | 1 |
| 28383893.pdf | **2** | 107 | 2 | 1 |
| 29161565.pdf | **2** | 42 | 4 | 3 |
| 29167286.pdf | 0 | 54 | 3 | 3 |
| 29221006.pdf | **3** | 104 | 2 | 2 |
| 29534737.pdf | **2** | 49 | 2 | 0 |
| 29595906.pdf | 0 | 19 | 2 | 5 |
| 30148777.pdf | 0 | 93 | 2 | 1 |
| 31536294.pdf | **1** | 74 | 9 | 2 |
| 31605080.pdf | 0 | 38 | 1 | 0 |
| 32720816.pdf | 0 | 53 | 3 | 0 |
| 33627938.pdf | **1** | 88 | 2 | 1 |
| 26819872.pdf | **3** | 107 | 2 | 5 |

## Every warning we raised (judge each on sight)

For each one: the item, what we marked it, and the exact words on the resume that triggered it.

### SKILL  (23 warnings)

| resume | item | we marked | the clause we matched |
|---|---|---|---|
| 26888302.pdf | Films | `basic` | ...g Skills API, approach, attention to detail, basic, color, hardware, content, conversion, data... |
| 26888302.pdf | Detail Oriented | `basic` | ...g Skills API, approach, attention to detail, basic, color, hardware, content, conversion, data... |
| 26888302.pdf | basic statisticaltools | `basic` | ...trategic experimental data foranalysis; used basic statisticaltools and route cause analysis. P... |
| 28020046.pdf | MandarinChinese | `basic` | ...nt (Read, Write and Speak) MandarinChinese - Basic Conversational(Speak) German - Basic Convers... |
| 28186635.pdf | First Aid | `basic` | ...1999 OSHA30 EPARRP DOEWeatherizationTactics Basic Fire FightingBasic First Aid Certification H... |
| 28186635.pdf | First Aid Certification | `basic` | ...1999 OSHA30 EPARRP DOEWeatherizationTactics Basic Fire FightingBasic First Aid Certification H... |
| 28186635.pdf | DOEWeatherizationTactics | `basic` | ...1999 OSHA30 EPARRP DOEWeatherizationTactics Basic Fire FightingBasic First Aid Certification H... |
| 28186635.pdf | EPARRP | `basic` | ...1999 OSHA30 EPARRP DOEWeatherizationTactics Basic Fire FightingBasic First Aid Certification H... |
| 28186635.pdf | Fire FightingBasic | `basic` | ...1999 OSHA30 EPARRP DOEWeatherizationTactics Basic Fire FightingBasic First Aid Certification H... |
| 28383893.pdf | emergencymedicaltreatment | `basic` | ...ibility oflong-termserious injury. Performed basic emergencymedicaltreatment. Administered card... |
| 28383893.pdf | NationalRegistryEmergencyMedicalTechnician - Basic | `basic` | ...NationalRegistryEmergencyMedicalTechnician - Basic Advanced Cardiac Life Support Provider Preho... |
| 29161565.pdf | facility decommissioning | `basic` | ...ol department in a variety ofareas including limited facility decommissioning, and aircraftcarrie... |
| 29161565.pdf | radiological control | `basic` | ...ol department in a variety ofareas including limited facility decommissioning, and aircraftcarrie... |
| 29221006.pdf | Human Resources Concepts | `basic` | ...9 Languages Read Spanish Skills Accounting, Basic, Budgeting, Budget, Data Entry, English, Fin... |
| 29221006.pdf | NursingBusiness | `basic` | ...S Grade: 05 Education 6 2009 NursingBusiness Some College GPA: GPA: 3.0 GPA: 3.0 OfAMaximum4.0... |
| 29221006.pdf | NursingOrganizationalLeadership | `basic` | ...tion 12 2012 NursingOrganizationalLeadership Some College GPA: GPA: 2.0 GPA: 2.0 OfAMaximum4.0... |
| 29534737.pdf | basic compressor build lines | `basic` | ...nsible for daily production needs within the basic compressor build lines. Reviewed production... |
| 29534737.pdf | Responsible for | `basic` | ...nsible for daily production needs within the basic compressor build lines. Reviewed production... |
| 31536294.pdf | Safety Induction and EmergencyTraining | `basic` | ...SIETÂ Helicopter Underwater Escape Training Basic Offshore Safety Induction and EmergencyTrain... |
| 33627938.pdf | Basic IndustrialSecurity for the Government Security Specialist Curriculum | `basic` | ...alIndustrialSecurity ProgramCourse and Exam; Basic IndustrialSecurity for the Government Securi... |
| 26819872.pdf | Trauma Care | `basic` | ...me GovernmentalDetention/ Hostage Detention, Basic Combat Trauma Training for TacticalOperator,... |
| 26819872.pdf | Computer Literacy | `basic` | ...ing to travel or relocate. Skills Air Force, Basic, Computer literate, delivery, directing, doc... |
| 26819872.pdf | Basic Combat Trauma Training for TacticalOperator | `basic` | ...me GovernmentalDetention/ Hostage Detention, Basic Combat Trauma Training for TacticalOperator,... |

### DEGREE  (0 warnings)

_None._

### CERT  (0 warnings)

_None._

## How to read this

- **A correct warning** = the clause really does say the skill is weak, the degree unfinished, or the cert expired.
- **A false alarm** = the clause is clean but we flagged it anyway (for example a stray word like "basic" sitting next to an unrelated skill).
- Real resumes are messy free text, so a few stray-word matches here are the honest cost of keyword rules. They are listed openly above rather than hidden in a percentage.
