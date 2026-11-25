import io
import json
import os
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from tools import read_ready


def project_page(*nodes, more=False, field=True):
    return {"data": {"user": {"projectV2": {
        "title": "Fixture board",
        "url": "https://github.com/users/williamwhorton/projects/7",
        "field": {"options": [{"name": "Ready", "id": "ready-id"}]} if field else None,
        "items": {"nodes": nodes, "pageInfo": {
            "hasNextPage": more, "endCursor": "fixture-cursor" if nodes else None,
        }},
    }}}}


def item(number, repo=read_ready.REPOSITORY, *, kind="ISSUE", status="ready-id"):
    return {
        "type": kind,
        "fieldValueByName": {"optionId": status} if status else None,
        "content": {"number": number, "repository": {"nameWithOwner": repo}} if kind == "ISSUE" else {},
    }


class ReadReadyTests(unittest.TestCase):
    def run_cli(self, responses=(), number="7"):
        # Mock the process boundary, preserving gh --slurp's nested REST arrays
        # and per-page GraphQL envelopes rather than passing flattened records.
        responses = [
            value if isinstance(value, subprocess.CompletedProcess)
            else subprocess.CompletedProcess([], 0, json.dumps(value), "")
            for value in responses
        ]
        stdout, stderr = io.StringIO(), io.StringIO()
        with (patch.dict(os.environ, {"PROJECT_NUMBER": number}),
              patch.object(read_ready.sys, "argv", ["read_ready.py"]),
              patch.object(read_ready.subprocess, "run", side_effect=responses) as run,
              redirect_stdout(stdout), redirect_stderr(stderr)):
            code = read_ready.main()
        return code, stdout.getvalue(), stderr.getvalue(), [call.args[0] for call in run.call_args_list]

    def test_project_and_rest_pagination_with_native_values(self):
        issue = {
            "number": 98, "title": "Read Ready",
            "labels": [{"name": "agent:developer"}],
            "assignees": [{"login": "director", "type": "User"}, {"login": "robot[bot]", "type": "Bot"}],
            "type": {"name": "Task"},
        }
        fields = [
            [{"issue_field_id": 42, "issue_field_name": "Priority", "data_type": "single_select",
              "value": 17, "single_select_option": {"id": 17, "name": "High"}}],
            [{"issue_field_id": 43, "issue_field_name": "Workstream", "data_type": "single_select",
              "value": 18, "single_select_option": {"id": 18, "name": "Infrastructure"}}],
        ]
        blockers = [
            [{"number": 12, "state": "open", "state_reason": "reopened"}],
            [{"number": 13, "state": "closed", "state_reason": "not_planned",
              "html_url": "https://github.com/other/repo/issues/13"}],
        ]
        code, out, err, commands = self.run_cli([
            [project_page(item(1, status="backlog-id"), item(2, kind="PULL_REQUEST"),
                          item(3, "other/repository"), more=True),
             project_page(item(98))],
            issue, fields, blockers,
        ])
        self.assertEqual((code, err), (0, ""))
        self.assertIn('#98 "Read Ready"', out)
        self.assertIn("agent:developer: yes; human assignees: @director", out)
        self.assertNotIn("robot", out)
        self.assertIn("Type: Task; Priority: High; Workstream: Infrastructure", out)
        self.assertIn("#12: open; reason: reopened", out)
        self.assertIn("#13: closed; reason: not_planned — https://github.com/other/repo/issues/13", out)
        board, rest_issue, rest_fields, rest_blockers = commands
        self.assertIn("graphql", board)
        self.assertIn("after: $endCursor", read_ready.PROJECT_QUERY)
        self.assertIn("archivedStates: [NOT_ARCHIVED]", read_ready.PROJECT_QUERY)
        for command in (board, rest_fields, rest_blockers):
            self.assertIn("--paginate", command)
            self.assertIn("--slurp", command)
        for command in (rest_issue, rest_fields, rest_blockers):
            self.assertEqual(command[command.index("--method") + 1], "GET")
        self.assertTrue(rest_fields[-1].endswith("/98/issue-field-values?per_page=100"))
        self.assertTrue(rest_blockers[-1].endswith("/98/dependencies/blocked_by?per_page=100"))

    def test_missing_values_do_not_use_issue_body_or_project_fields(self):
        code, out, err, _ = self.run_cli([
            [project_page(item(99), item(98))],
            {"title": "Blank type", "type": None, "labels": [], "assignees": [],
             "body": "**Priority:** Urgent\n**Issue Type:** Task"},
            [[]], [[{"number": 52, "state": "open", "state_reason": None}]],
            {"title": "Unavailable metadata"},
            [[{"issue_field_id": 42, "data_type": "single_select", "value": 17}]],
            [[{"number": 51, "state": "closed"}]],
        ])
        self.assertEqual((code, err), (0, ""))
        self.assertLess(out.index("#99"), out.index("#98"))
        self.assertIn("agent:developer: no; human assignees: (none)", out)
        self.assertIn("Type: (not set); Priority: (not set); Workstream: (not set)", out)
        self.assertIn("#52: open; reason: (not set)", out)
        self.assertIn("agent:developer: (unavailable); human assignees: (unavailable)", out)
        self.assertIn("Type: (unavailable); Priority: (unavailable); Workstream: (unavailable)", out)
        self.assertIn("#51: closed; reason: (unavailable)", out)
        self.assertNotIn("Urgent", out)

    def test_empty_ready_is_success_only_after_a_complete_board_read(self):
        code, out, err, calls = self.run_cli([[project_page(item(3, status=None))]])
        self.assertEqual((code, err, len(calls)), (0, "", 1))
        self.assertIn("No Ready issues for this repository.", out)

        for page, message in [
            (project_page(more=True), "pagination"),
            (project_page(field=False), "Status field"),
            (project_page(item(5, kind="REDACTED", status=None)), "inaccessible item"),
            ({"data": {"user": {"projectV2": None}}}, "check PROJECT_NUMBER"),
            ({"errors": [{"message": "GraphQL error"}]}, "GraphQL API error"),
        ]:
            with self.subTest(message=message):
                code, out, err, _ = self.run_cli([[page]])
                self.assertEqual((code, out), (1, ""))
                self.assertIn(message, err)

    def test_configuration_and_api_failures_never_print_empty_or_partial_reports(self):
        code, out, err, calls = self.run_cli(number="")
        self.assertEqual((code, out, calls), (2, "", []))
        self.assertIn("Configuration error", err)

        auth = subprocess.CompletedProcess([], 4, "", "secret diagnostic must not be printed")
        code, out, err, _ = self.run_cli([auth])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("authentication failed", err)
        self.assertNotIn("secret diagnostic", err)

        forbidden = subprocess.CompletedProcess([], 1, "", "Forbidden (HTTP 403)")
        code, out, err, _ = self.run_cli([
            [project_page(item(98), item(99))],
            {"title": "First issue"}, [[]], [[]],
            {"title": "Second issue"}, [[]], forbidden,
        ])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("#99/dependencies/blocked_by: GitHub API/CLI error (HTTP 403)", err)


if __name__ == "__main__":
    unittest.main()
