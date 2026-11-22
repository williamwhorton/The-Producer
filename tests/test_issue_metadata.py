"""Offline contract tests for the one-time native GitHub issue metadata migration."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "tools" / "sync_issue_metadata.py"
spec = importlib.util.spec_from_file_location("issue_metadata", PATH)
meta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(meta)


def entry(name, options):
    return {"name": name, "id": len(name), "data_type": "single_select",
            "options": [{"id": i, "name": o} for i, o in enumerate(options)]}


FIELDS = {
    "priority": entry("Priority", ["Urgent", "High", "Medium", "Low"]),
    "workstream": entry("Workstream", ["Design", "Architecture", "Infrastructure", "Simulation", "QA"]),
}
TYPES = meta.VALID_TYPES


class ParsingTests(unittest.TestCase):
    def test_explicit_prototype_task_not_spike(self):
        for number in [13, 14, 15]:
            result = meta.parse_issue_metadata(
                number, "[Spike] Disposable prototype",
                "**Workstream:** Architecture · **Priority:** High"
            )
            self.assertEqual(result["type"], "Task")
            self.assertEqual(result["workstream"], ("Architecture",))
            self.assertEqual(result["priority"], "High")

    def test_parent_architecture_stays_spike(self):
        self.assertEqual(
            meta.parse_issue_metadata(
                4, "[Architecture] Evaluate candidate engine",
                "**Priority:** High · **Workstream:** Architecture"
            )["type"],
            "Spike",
        )

    def test_legacy_priority_and_last_correction(self):
        result = meta.parse_issue_metadata(
            17, "[Design] Pacing",
            "**Priority:** P1\nMore details\n**Priority:** High (replaces legacy)"
        )
        self.assertEqual(result["priority"], "High")
        self.assertEqual(result["type"], "Design Decision")

    def test_new_issue_uses_structured_intake_not_title_prefix(self):
        result = meta.parse_issue_metadata(
            100, "Prototype lighting behavior",
            "**Issue Type:** Task\n**Priority:** High\n**Workstream:** Architecture",
        )
        self.assertEqual(result["type"], "Task")
        self.assertEqual(result["priority"], "High")
        self.assertEqual(result["workstream"], ("Architecture",))

    def test_missing_values_not_guessed(self):
        result = meta.parse_issue_metadata(100, "Untyped", "No metadata")
        self.assertIsNone(result["type"])
        self.assertIsNone(result["priority"])
        self.assertEqual(result["workstream"], ())

    def test_ambiguous_workstream_uses_valid_existing_option(self):
        self.assertEqual(
            meta.select_option(
                FIELDS["workstream"],
                meta.WORKSTREAM_CANDIDATES["Presentation / UI"]
            ),
            "Design",
        )
        self.assertEqual(
            meta.select_option(FIELDS["workstream"], ("Unrecognized",)),
            None,
        )

    def test_explicit_issue_numbers(self):
        self.assertEqual(meta.parse_numbers("13, 14,15"), {13, 14, 15})
        self.assertIsNone(meta.parse_numbers(""))
        with self.assertRaises(meta.MetadataError):
            meta.parse_numbers("13,anything")


class PlanningTests(unittest.TestCase):
    def test_do_not_replace_existing_fields_or_type(self):
        issue = {
            "number": 40, "title": "[Feature] House view",
            "body": "**Priority:** High\n**Workstream:** Presentation / UI",
            "type": {"name": "Task"}
        }
        existing = [
            {"issue_field_name": "Priority", "single_select_option": {"name": "Low"}},
            {"issue_field_name": "Workstream", "single_select_option": {"name": "QA"}},
        ]
        typ, changes = meta.plan_changes(issue, existing, FIELDS, TYPES)
        self.assertIsNone(typ)
        self.assertEqual(changes, [])

    def test_explicit_prototype_type_corrected_even_when_occupied(self):
        issue = {
            "number": 13, "title": "Build Godot prototype",
            "body": "**Priority:** High · **Workstream:** Architecture",
            "type": {"name": "Spike"},
        }
        typ, changes = meta.plan_changes(issue, [], FIELDS, TYPES)
        self.assertEqual(typ, "Task")
        self.assertEqual(
            {f["value"] for f in changes},
            {"High", "Architecture"},
        )

    def test_report_unknown_type_without_guess(self):
        issue = {
            "number": 13, "title": "Build Godot prototype",
            "body": "**Priority:** High · **Workstream:** Architecture",
            "type": None,
        }
        typ, _ = meta.plan_changes(issue, [], FIELDS, {"Feature", "Bug"})
        self.assertIsNone(typ)

    def test_no_unrelated_field_removal(self):
        issue = {
            "number": 39, "title": "[Feature] Observation system",
            "body": "**Priority:** High\n**Workstream:** Presentation / UI",
            "type": None,
        }
        existing = [
            {"issue_field_name": "Effort", "value": 3},
        ]
        typ, changes = meta.plan_changes(issue, existing, FIELDS, TYPES)
        self.assertEqual(typ, "Feature")
        self.assertEqual({f["value"] for f in changes}, {"High", "Design"})


if __name__ == "__main__":
    unittest.main()
