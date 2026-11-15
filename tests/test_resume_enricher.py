"""Resume Enricher test suite — the safety net.

Every test reads like a sentence: "given THIS resume text, the tool should say
THAT". If you change a rule and a test goes red, the test name tells you exactly
which promise you broke.

Run it from inside the `resume_enricher/` folder:

    python -m unittest discover -s tests        # run everything
    python tests/test_resume_enricher.py            # same thing, direct

No extra libraries needed — this uses Python's built-in `unittest`.
"""
from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

# Make sure the package is importable when run directly (adds the folder that
# holds the `resume_enricher/` package to the search path).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from resume_enricher import enrich
from resume_enricher.modules.skill._classify import classify_skill
from resume_enricher.shared.locator import locate
from resume_enricher.shared.matching import exact_token_find, normalize, normalize_mapped
from resume_enricher.shared.models import build_evidence, severity_of
from resume_enricher.shared.validators import deep_copy, ensure_untouched, validate_input


def _text_at(raw: str, span) -> str:
    """Pull the characters a span points at, so we can check highlights are exact."""
    return raw[span[0]:span[1]]


# ---------------------------------------------------------------------------
# 1. The text helpers (matching.py)
# ---------------------------------------------------------------------------
class TextCleaning(unittest.TestCase):
    def test_cleaning_lowercases_and_collapses_but_keeps_word_gaps(self):
        cleaned, _ = normalize_mapped("Go,  SQL!")
        self.assertEqual(cleaned, "go sql")

    def test_index_map_points_each_clean_char_back_to_the_original(self):
        cleaned, index_map = normalize_mapped("Go,  SQL!")
        self.assertEqual(index_map, [0, 1, 2, 5, 6, 7])  # the famous jump 2 -> 5

    def test_normalize_drops_affindas_parenthetical_note(self):
        self.assertEqual(normalize("Python (Programming Language)"), "python")

    def test_whole_word_find_will_not_match_inside_a_bigger_word(self):
        self.assertEqual(exact_token_find("communication", "c"), -1)
        self.assertEqual(exact_token_find("c and java", "c"), 0)


# ---------------------------------------------------------------------------
# 2. The finder (locator.py)
# ---------------------------------------------------------------------------
class Finder(unittest.TestCase):
    def test_finds_the_word_and_the_span_is_exact_despite_messy_spacing(self):
        raw = "No experience   with SQL."
        clause, clause_start, span = locate("SQL", raw)
        self.assertEqual(_text_at(raw, span), "SQL")      # highlight is exact
        self.assertIn("SQL", clause)                      # sentence contains it
        # clause_start points at where the trimmed sentence begins
        self.assertEqual(raw[clause_start:clause_start + 2], "No")

    def test_finds_a_word_split_up_by_spaces(self):
        clause, _, span = locate("SQL", "Proficiency: S Q L")
        self.assertIsNotNone(span)

    def test_returns_all_none_when_the_word_is_absent(self):
        self.assertEqual(locate("Kubernetes", "Skills: SQL, Python"), (None, None, None))

    def test_sentence_stops_at_a_boundary(self):
        clause, _, _ = locate("BSc", "BSc Computer Science (withdrew 2016). Next sentence.")
        self.assertNotIn("Next sentence", clause)


# ---------------------------------------------------------------------------
# 3. The skill precision guard (the heart of the product)
# ---------------------------------------------------------------------------
class SkillPrecisionGuard(unittest.TestCase):
    CLAUSE = "no experience with SQL, expert in Python, learning Excel"

    def test_each_skill_reads_only_its_own_piece_of_the_sentence(self):
        self.assertEqual(classify_skill(self.CLAUSE, "SQL")[0], "no_experience")
        self.assertEqual(classify_skill(self.CLAUSE, "Python")[0], "strong")
        self.assertEqual(classify_skill(self.CLAUSE, "Excel")[0], "learning")

    def test_python_is_not_dragged_down_by_sqls_negative_cue(self):
        # The whole point: "no experience" must NOT leak onto Python.
        self.assertNotEqual(classify_skill(self.CLAUSE, "Python")[0], "no_experience")

    def test_a_joining_word_also_acts_as_a_wall(self):
        clause = "no experience with SQL but expert in Python"
        self.assertEqual(classify_skill(clause, "SQL")[0], "no_experience")
        self.assertEqual(classify_skill(clause, "Python")[0], "strong")

    def test_a_skill_with_no_cue_words_is_plain(self):
        self.assertEqual(classify_skill("Tools: SQL", "SQL"), ("plain", None, None))


# ---------------------------------------------------------------------------
# 4. Education & certification statuses (status_engine.py + rules)
# ---------------------------------------------------------------------------
class EducationStatus(unittest.TestCase):
    def _status(self, qualification, raw):
        out = enrich({"data": {"education": [{"qualification": qualification}], "rawText": raw}})
        return out["enrichmentJSON"]["education"][0]["status"]

    def test_withdrawn_degree_is_incomplete(self):
        self.assertEqual(self._status("BSc Physics", "BSc Physics (withdrew 2016)."), "incomplete")

    def test_graduated_degree_is_completed(self):
        self.assertEqual(self._status("BSc Physics", "BSc Physics, graduated 2015."), "completed")

    def test_future_dated_degree_is_expected(self):
        future = date.today().year + 2
        self.assertEqual(self._status("BSc Physics", f"BSc Physics, expected {future}."), "expected")

    def test_expected_word_without_a_future_year_is_not_treated_as_expected(self):
        # "expected" only counts with a real future year, else it must not win.
        self.assertNotEqual(self._status("BSc Physics", "BSc Physics, expected 1999."), "expected")


class CertificationStatus(unittest.TestCase):
    def _status(self, name, raw):
        out = enrich({"data": {"certifications": [{"name": name}], "rawText": raw}})
        return out["enrichmentJSON"]["certifications"][0]["status"]

    def test_expired_certificate(self):
        self.assertEqual(self._status("AWS SA", "AWS SA (expired 2021)."), "expired")

    def test_revoked_certificate(self):
        self.assertEqual(self._status("CPA License", "CPA License was revoked."), "revoked")

    def test_valid_certificate_is_active(self):
        self.assertEqual(self._status("AWS SA", "AWS SA, valid and current."), "active")


# ---------------------------------------------------------------------------
# 5. The severity menu (models.py)
# ---------------------------------------------------------------------------
class SeverityMenu(unittest.TestCase):
    def test_a_bad_status_is_a_warning(self):
        self.assertEqual(severity_of("skill", "no_experience"), "warning")

    def test_a_fine_status_is_info(self):
        self.assertEqual(severity_of("skill", "strong"), "info")

    def test_an_unknown_status_fails_loudly(self):
        with self.assertRaises(ValueError):
            severity_of("skill", "totally_made_up")


# ---------------------------------------------------------------------------
# 6. The evidence (proof) is always lined up with its highlight
# ---------------------------------------------------------------------------
class EvidenceAlignment(unittest.TestCase):
    def test_every_highlight_points_at_the_exact_text_it_claims(self):
        raw = (
            "Skills: no experience with SQL, expert in Python, learning Excel. "
            "Education: BSc Computer Science (withdrew 2016). "
            "Certifications: AWS Certified Solutions Architect (expired 2021)."
        )
        sample = {
            "data": {
                "skills": [{"name": "SQL"}, {"name": "Python"}, {"name": "Excel"}],
                "education": [{"qualification": "BSc Computer Science"}],
                "certifications": [{"name": "AWS Certified Solutions Architect"}],
                "rawText": raw,
            }
        }
        enrichment = enrich(sample)["enrichmentJSON"]
        for key in ("skills", "education", "certifications"):
            for item in enrichment[key]:
                ev = item["evidence"]
                if ev["rawTextSpan"] is not None:
                    # the characters at the span must equal the evidence text
                    self.assertEqual(_text_at(raw, ev["rawTextSpan"]), ev["text"])

    def test_build_evidence_falls_back_to_the_entity_when_no_cue_matched(self):
        ev = build_evidence("SQL", matched=None, match_pos=None, clause_start=None, entity_span=(3, 6))
        self.assertEqual(ev.text, "SQL")
        self.assertEqual(ev.rawTextSpan, (3, 6))


# ---------------------------------------------------------------------------
# 7. The safety guards (validators.py) and the "never touch the original" promise
# ---------------------------------------------------------------------------
class SafetyGuards(unittest.TestCase):
    def test_rejects_data_that_is_not_a_dictionary(self):
        with self.assertRaises(ValueError):
            validate_input(["not", "a", "dict"])

    def test_rejects_data_missing_its_data_section(self):
        with self.assertRaises(ValueError):
            validate_input({"nope": 1})

    def test_rejects_a_section_that_is_the_wrong_shape(self):
        with self.assertRaises(ValueError):
            validate_input({"data": {"skills": "should be a list"}})

    def test_accepts_a_sparse_resume_with_missing_sections(self):
        validate_input({"data": {}})   # no error = pass

    def test_the_original_is_never_changed(self):
        original = {"data": {"skills": [{"name": "SQL"}], "rawText": "no experience with SQL"}}
        before = deep_copy(original)
        enrich(original)
        self.assertEqual(original, before)   # byte-for-byte identical afterwards

    def test_ensure_untouched_catches_a_sneaky_change(self):
        a = {"data": {"x": 1}}
        b = {"data": {"x": 2}}
        with self.assertRaises(AssertionError):
            ensure_untouched(a, b)


# ---------------------------------------------------------------------------
# 8. The whole pipeline (enrich / main)
# ---------------------------------------------------------------------------
class FullPipeline(unittest.TestCase):
    SAMPLE = {
        "data": {
            "skills": [{"name": "SQL"}, {"name": "Python"}, {"name": "Excel"}],
            "education": [{"qualification": "BSc Computer Science"}],
            "certifications": [{"name": "AWS Certified Solutions Architect"}],
            "rawText": (
                "Skills: no experience with SQL, expert in Python, learning Excel. "
                "Education: BSc Computer Science (withdrew 2016). "
                "Certifications: AWS Certified Solutions Architect (expired 2021)."
            ),
        }
    }

    def test_output_keeps_the_original_and_adds_an_enrichment_block(self):
        out = enrich(self.SAMPLE)
        self.assertIn("originalJSON", out)
        self.assertIn("enrichmentJSON", out)
        self.assertEqual(out["originalJSON"], self.SAMPLE)

    def test_one_enrichment_per_item_a_complete_mirror(self):
        e = enrich(self.SAMPLE)["enrichmentJSON"]
        self.assertEqual(len(e["skills"]), 3)
        self.assertEqual(len(e["education"]), 1)
        self.assertEqual(len(e["certifications"]), 1)

    def test_summary_lists_exactly_the_warnings(self):
        e = enrich(self.SAMPLE)["enrichmentJSON"]
        # 4 warnings expected: SQL, Excel, BSc, AWS (Python is info, not a warning)
        self.assertEqual(len(e["summary"]), 4)

    def test_a_missing_raw_text_drops_confidence_but_does_not_crash(self):
        out = enrich({"data": {"skills": [{"name": "SQL"}]}})
        item = out["enrichmentJSON"]["skills"][0]
        self.assertEqual(item["confidence"], "low")
        self.assertEqual(item["status"], "plain")


if __name__ == "__main__":
    unittest.main(verbosity=2)
