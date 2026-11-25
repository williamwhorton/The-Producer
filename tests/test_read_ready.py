import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import read_ready, ready_selection


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
    def run_cli(self, responses=(), number="7", *, select=False, local=None):
        # Mock the process boundary, preserving gh --slurp's nested REST arrays
        # and per-page GraphQL envelopes rather than passing flattened records.
        responses = [
            value if isinstance(value, subprocess.CompletedProcess)
            else subprocess.CompletedProcess([], 0, json.dumps(value), "")
            for value in responses
        ]
        stdout, stderr = io.StringIO(), io.StringIO()
        with (patch.dict(os.environ, {"PROJECT_NUMBER": number}),
              patch.object(read_ready.sys, "argv", ["read_ready.py"] + (["--select"] if select else [])),
              patch.object(read_ready.subprocess, "run", side_effect=responses) as run,
              patch.object(ready_selection, "local_work", return_value=local or {}),
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

    def test_native_workstream_and_approval_in_diagnostic(self):
        for workstreams, approval, expected in (
            (["Architecture"], "No", "Architecture; Requires human approval: No"),
            (["Architecture", "Simulation"], "Yes", "Architecture, Simulation; Requires human approval: Yes"),
            (["Architecture"], None, "Architecture; Requires human approval: (not set)"),
        ):
            with self.subTest(workstreams=workstreams, approval=approval):
                code, out, err, _ = self.run_cli([
                    [project_page(item(30))],
                    *assignment(30, fields=fields_for(workstreams=workstreams, approval=approval),
                                type={"name": "Feature"}),
                ])
                self.assertEqual((code, err), (0, ""))
                self.assertIn(f"Type: Feature; Priority: High; Workstream: {expected}", out)

    def test_invalid_native_options_are_unavailable_in_diagnostic(self):
        for workstream_rows in invalid_workstreams():
            with self.subTest(rows=workstream_rows):
                code, out, err, _ = self.run_cli([
                    [project_page(item(30))],
                    *assignment(30, fields=fields_for(workstreams=None) + workstream_rows),
                ])
                self.assertEqual((code, err), (0, ""))
                self.assertIn("Workstream: (unavailable); Requires human approval: No", out)

        code, out, err, _ = self.run_cli([
            [project_page(item(30))],
            *assignment(30, fields=fields_for(approval=None) + [approval_with_false_multi_options()]),
        ])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("Workstream: Architecture; Requires human approval: (unavailable)", out)

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

    def test_pilot_reads_multiple_statuses_from_one_project_snapshot(self):
        page = project_page(item(14, status="progress-id"), item(15),
                            item(16, repo="other/repository", status="progress-id"))
        project = page["data"]["user"]["projectV2"]
        project["field"]["options"].append({"name": "In Progress", "id": "progress-id"})
        with patch.object(read_ready, "gh_json", return_value=[page]):
            _, _, cards = read_ready.project_issues(7, status_names=("Ready", "In Progress"))
            self.assertEqual(cards, {"Ready": [15], "In Progress": [14]})
            with self.assertRaisesRegex(read_ready.ReadError, "one In Review option"):
                read_ready.project_issues(7, status_names=("Ready", "In Review"))

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


def blocker(number, state="open", reason=None, repo=read_ready.REPOSITORY):
    return {"number": number, "state": state, "state_reason": reason,
            "html_url": f"https://github.com/{repo}/issues/{number}"}


def single_field(name, value):
    return {"data_type": "single_select", "issue_field_name": name,
            "single_select_option": {"name": value}}


def workstream_field(names):
    # The #104 excerpt includes a string value, but the option list is authoritative.
    return {"data_type": "multi_select", "issue_field_name": "Workstream",
            "value": names[0], "multi_select_options": [{"name": name} for name in names]}


def fields_for(*, priority="High", workstreams=("Architecture",), approval="No"):
    fields = [single_field("Priority", priority)]
    if workstreams is not None:
        fields.append(workstream_field(workstreams))
    if approval is not None:
        fields.append(single_field("Requires human approval", approval))
    return fields


def invalid_workstreams():
    valid = workstream_field(["Architecture"])
    return [
        [{**valid, "multi_select_options": options}]
        for options in (None, [], {"name": "Architecture"}, ["Architecture"],
                        [{"name": "Architecture"}, {}], [{"name": " "}], [{"name": 42}],
                        valid["multi_select_options"] * 2)
    ] + [[{**valid, "single_select_option": {}}],
         [valid, single_field("Workstream", "Simulation")]]


def approval_with_false_multi_options():
    return {**single_field("Requires human approval", "No"), "multi_select_options": False}


def assignment(number, *, blockers=(), fields=None, **changes):
    declaration = "native" if blockers else "none"
    issue = {
        "number": number, "state": "open", "title": f"Work {number}", "type": {"name": "Task"},
        "labels": [{"name": "agent:developer"}], "assignees": [],
        "body": f"Selection-ready implementation; prerequisites: {declaration}\n\n"
                "## Acceptance criteria\n- Deliver a tested change.",
        "issue_dependencies_summary": {
            "blocked_by": len({b["html_url"] for b in blockers if b.get("state") == "open"}),
            "total_blocked_by": len({b["html_url"] for b in blockers}),
            "blocking": 0, "total_blocking": 0,
        },
        **changes,
    }
    return issue, [fields_for() if fields is None else fields], [list(blockers)]


def pr(number, branch="feature", *, body=None, draft=False, links=()):
    return {"number": number, "headRefName": branch, "isDraft": draft,
            **({"body": body} if body is not None else {}),
            "closingIssuesReferences": {
                "nodes": [{"number": n, "repository": {"nameWithOwner": repo}} for n, repo in links],
                "pageInfo": {"hasNextPage": False},
            }}


def pr_page(*prs, more=False, cursor="pr-cursor"):
    return {"data": {"repository": {"pullRequests": {
        "nodes": prs, "pageInfo": {"hasNextPage": more, "endCursor": cursor if prs else None},
    }}}}


def issue_prs(*prs):
    return {"data": {"repository": {"issue": {
        "closedByPullRequestsReferences": {"nodes": prs},
    }}}}


def closing_pr(**changes):
    return {"__typename": "PullRequest", "number": 99, "merged": True, "baseRefName": "main",
            "repository": {"nameWithOwner": read_ready.REPOSITORY},
            "mergedBy": {"login": read_ready.OWNER}, **changes}


def closure(closer, *, actor=read_ready.OWNER, author=read_ready.OWNER, editor=None, body=""):
    return {"data": {"repository": {"issue": {
        "state": "CLOSED", "stateReason": "COMPLETED", "body": body,
        "author": {"login": author}, "editor": {"login": editor} if editor else None,
        "timelineItems": {"nodes": [
            {"__typename": "ClosedEvent", "actor": {"login": actor}, "closer": closer}
        ]},
    }}}}


class SelectionTests(unittest.TestCase):
    run_cli = ReadReadyTests.run_cli

    def select(self, assignments, *extra, local=None, items=None):
        numbers = [row[0]["number"] for row in assignments]
        board = [project_page(*(items if items is not None else map(item, reversed(numbers))))]
        return self.run_cli([board, *(value for row in assignments for value in row), *extra],
                            select=True, local=local)

    def test_issue_side_cross_repository_open_pr_excludes_candidate(self):
        for draft in (False, True):
            with self.subTest(draft=draft):
                url = "https://github.com/other/repo/pull/21"
                code, out, err, calls = self.select(
                    [assignment(42)], pr_page(), issue_prs({"isDraft": draft, "url": url}),
                )
                self.assertEqual((code, err), (0, ""))
                kind = "draft PR" if draft else "PR"
                self.assertIn(f'SKIP #42 "Work 42": existing open {kind} {url}; Lead triage', out)
                self.assertIn("No eligible work.", out)
                self.assertIn("number=42", calls[-1])
                self.assertIn(f"query={ready_selection.ISSUE_PRS}", calls[-1])

    def test_pr_body_examples_without_native_links_do_not_exclude_candidate(self):
        code, out, err, _ = self.select(
            [assignment(42)],
            pr_page(pr(21, body="Use `Closes #42` as an example.\n\n> Fixes #42\n\n```\nCloses #42\n```")),
            issue_prs(),
        )
        self.assertEqual((code, err), (0, ""))
        self.assertIn('Next issue: #42 "Work 42"', out)
        self.assertNotIn("SKIP #42", out)

    def test_ranking_counts_unique_direct_successors_with_no_other_blockers(self):
        rows = [
            assignment(10, fields=fields_for(priority="Urgent")),
            assignment(11, fields=fields_for(priority="Low"), type={"name": "Spike"}),
            assignment(12, fields=fields_for(priority="Urgent")),
            assignment(13, blockers=[blocker(11), blocker(11)]),
            assignment(14, blockers=[blocker(10), blocker(11)]),
            assignment(15, blockers=[blocker(10)], assignees=[{"login": "director", "type": "User"}]),
            assignment(16, blockers=[blocker(13)]),
        ]
        code, out, err, _ = self.select(rows, pr_page(), *(issue_prs() for _ in range(6)),
                                        items=[*(item(n) for n in range(16, 9, -1)),
                                               item(13), item(3, "other/repo"),
                                               item(4, kind="PULL_REQUEST"), item(5, status="done")])
        self.assertEqual((code, err), (0, ""))
        self.assertIn('  #11 "Work 11" — unlocks 1 Ready issue(s); Low', out)
        self.assertLess(out.index('  #11 "'), out.index('  #10 "'))
        self.assertLess(out.index('  #10 "'), out.index('  #12 "'))
        self.assertIn('Next issue: #11 "Work 11"', out)
        self.assertEqual(out.count("WAIT #13 "), 1)
        self.assertIn("WAIT #16 ", out)
        self.assertIn("human or unverified assignee", out)

    def test_metadata_scope_and_legacy_are_not_inferred(self):
        rows = [
            assignment(1, type=None, body="**Issue Type:** Task"),
            assignment(2, fields=fields_for(priority="P0")),
            assignment(3, fields=fields_for(workstreams=None)),
            assignment(4, fields=fields_for(approval="Yes")),
            assignment(5, fields=fields_for(approval=None)),
            assignment(6, body="## Dependencies\nPrevious work must finish before this."),
            assignment(7, blockers=[blocker(1)],
                        body="Selection-ready implementation; prerequisites: none\n\nDeliver tests."),
            assignment(8, type={"name": "Design Decision"}),
            assignment(9, labels=[]),
            assignment(10, state="closed"),
            assignment(11, fields=fields_for() + fields_for()),  # duplicate field names
            assignment(12, issue_dependencies_summary={"total_blocked_by": 1}),
        ]
        code, out, err, calls = self.select(rows)
        self.assertEqual((code, err, len(calls)), (0, "", 1 + 3 * len(rows)))
        reasons = ("native Type", "native Priority", "native Workstream", "approval is outstanding",
                   "native Requires human approval", "legacy prerequisite reconciliation not confirmed",
                   "disagrees with native Blocked by", "Design Decision is human-owned",
                   "missing agent:developer", "not open", "ambiguous native Priority", "count unavailable")
        for number, reason in enumerate(reasons, 1):
            self.assertRegex(out, rf"SKIP #{number} [^\n]+{reason}")
        self.assertIn("No eligible work.", out)

    def test_native_workstream_and_approval_in_selection(self):
        rows = [
            assignment(30, type={"name": "Feature"}, fields=fields_for(workstreams=["Architecture"])),
            assignment(31, fields=fields_for(workstreams=["Architecture", "Simulation"])),
            assignment(32, fields=fields_for(workstreams=None) + [single_field("Workstream", "Simulation")]),
            assignment(33, fields=fields_for(approval="Yes")),
            assignment(34, fields=fields_for(approval=None) + [single_field("Human Approval Required", "No")]),
        ]
        code, out, err, _ = self.select(rows, pr_page(), issue_prs(), issue_prs(), issue_prs())
        self.assertEqual((code, err), (0, ""))
        for number in (30, 31, 32):
            self.assertIn(f'  #{number} "Work {number}" — unlocks 0', out)
        self.assertIn('Next issue: #30 "Work 30"', out)
        self.assertIn('SKIP #33 "Work 33": human approval is outstanding', out)
        self.assertIn('SKIP #34 "Work 34": missing or ambiguous native Requires human approval', out)

    def test_pilot_metadata_does_not_bypass_missing_native_dependencies(self):
        row = assignment(30, type={"name": "Feature"},
                         body="Selection-ready implementation; prerequisites: native\n\nDeliver one fixture.")
        code, out, err, calls = self.select([row])
        self.assertEqual((code, err, len(calls)), (0, "", 4))
        self.assertIn('SKIP #30 "Work 30": ambiguous prerequisite reconciliation or '
                      "declaration disagrees with native Blocked by", out)
        self.assertIn("No eligible work.", out)

    def test_empty_unused_option_members_preserve_selection(self):
        for unused_multi_options in (None, []):
            with self.subTest(unused_multi_options=unused_multi_options):
                priority, workstream, approval = fields_for()
                workstream["single_select_option"] = None
                approval["multi_select_options"] = unused_multi_options
                code, out, err, _ = self.select(
                    [assignment(30, fields=[priority, workstream, approval])], pr_page(), issue_prs(),
                )
                self.assertEqual((code, err), (0, ""))
                self.assertIn('Next issue: #30 "Work 30"', out)

    def test_invalid_native_options_fail_closed(self):
        invalid_approvals = (
            [single_field("Requires human approval", "")],
            [single_field("Requires human approval", "no")],
            [single_field("Requires human approval", " No")],
            [{"data_type": "single_select", "issue_field_name": "Requires human approval",
              "single_select_option": "No"}],
            [{**workstream_field(["No"]), "issue_field_name": "Requires human approval"}],
            [approval_with_false_multi_options()],
            [single_field("Requires human approval", "No"), single_field("Requires human approval", "Yes")],
        )
        for name, fields in (
            ("Workstream", [fields_for(workstreams=None) + rows for rows in invalid_workstreams()]),
            ("Requires human approval", [fields_for(approval=None) + rows for rows in invalid_approvals]),
        ):
            for values in fields:
                with self.subTest(name=name, values=values):
                    code, out, err, calls = self.select([assignment(30, fields=values)], pr_page(), issue_prs())
                    self.assertEqual((code, err), (0, ""))
                    self.assertIn(f'SKIP #30 "Work 30": missing or ambiguous native {name}', out)
                    self.assertIn("No eligible work.", out)
                    self.assertEqual(len(calls), 4)

    def test_implementation_declaration_must_be_first_nonempty_unindented_line(self):
        marker = "Selection-ready implementation; prerequisites: none"
        for misplaced in (f"```\n{marker}\n```", f"> {marker}", f"    {marker}",
                          f"## Example\n{marker}", f"{marker} "):
            with self.subTest(misplaced=misplaced):
                code, out, err, _ = self.select([
                    assignment(1, body=f"{misplaced}\n\n## Dependencies\nWait for #98 before starting."),
                ], pr_page(), issue_prs())
                self.assertEqual((code, err), (0, ""))
                self.assertRegex(out, r"SKIP #1 .*prerequisite reconciliation")
                self.assertIn("No eligible work.", out)

        code, out, err, _ = self.select([
            assignment(1, body=f"\n \n{marker}\n\nDeliver tests."),
            assignment(2, body=f"{marker}\n \n"),
        ], pr_page(), issue_prs())
        self.assertEqual((code, err), (0, ""))
        self.assertIn('Next issue: #1 "Work 1"', out)
        self.assertRegex(out, r"SKIP #2 .*approved implementation .*not confirmed")

    def test_closed_dependencies_need_direct_accepted_completion(self):
        rows = [
            assignment(1, blockers=[blocker(90, "closed", "completed")]),
            assignment(2, blockers=[blocker(91, "closed", "completed")]),
            assignment(3, blockers=[blocker(92, "closed", "not_planned")]),
            assignment(4, blockers=[blocker(93, "closed", "completed", "other/repo")]),
            assignment(5, blockers=[blocker(90, "closed", "completed")]),
            assignment(6, blockers=[blocker(94, "closed", "completed")]),
        ]
        code, out, err, calls = self.select(
            rows, pr_page(), issue_prs(), closure(closing_pr()),
            issue_prs(), closure(None, body="\n \nSelection completion: non-code\n\nDocumented outcome."),
            issue_prs(), issue_prs(), issue_prs(), issue_prs(),
            subprocess.CompletedProcess([], 1, json.dumps({
                "data": {"repository": {"issue": None}},
                "errors": [{"type": "NOT_FOUND", "path": ["repository", "issue"],
                            "message": "Could not resolve to an Issue with the number of 94."}],
            }), "gh: Could not resolve to an Issue with the number of 94."),
        )
        self.assertEqual((code, err, len(calls)), (0, "", 1 + 4 * len(rows) + 4))
        for number in (1, 2, 5):
            self.assertIn(f'  #{number} "Work {number}" — unlocks 0', out)
        self.assertRegex(out, r"WAIT #3 .*not_planned")
        self.assertRegex(out, r"WAIT #4 .*external or inaccessible")
        self.assertRegex(out, r"WAIT #6 .*prerequisite inaccessible")
        self.assertTrue(any("number=90" in command for command in calls))

    def test_unaccepted_closures_remain_waiting(self):
        for payload in (
            closure(closing_pr(merged=False)), closure(closing_pr(baseRefName="develop")),
            closure(closing_pr(mergedBy={"login": "someone-else"})),
            closure(closing_pr(repository={"nameWithOwner": "other/The-Producer"})),
            closure({"__typename": "Commit"}), closure(None),
            closure(None, actor="not-owner", body="Selection completion: non-code"),
            closure(None, editor="not-owner", body="Selection completion: non-code"),
        ):
            with self.subTest(payload=payload):
                code, out, err, _ = self.select(
                    [assignment(3, blockers=[blocker(98, "closed", "completed")])], pr_page(), issue_prs(), payload,
                )
                self.assertEqual((code, err), (0, ""))
                self.assertRegex(out, r"WAIT #3 .*no owner-accepted closing merge")
                self.assertIn("No eligible work.", out)

    def test_misplaced_non_code_completion_declaration_remains_waiting(self):
        marker = "Selection completion: non-code"
        for body in (f"```\n{marker}\n```", f"> {marker}", f"    {marker}",
                     f"## Example\n{marker}", f"{marker} "):
            with self.subTest(body=body):
                code, out, err, _ = self.select(
                    [assignment(1, blockers=[blocker(90, "closed", "completed")])],
                    pr_page(), issue_prs(), closure(None, body=body),
                )
                self.assertEqual((code, err), (0, ""))
                self.assertRegex(out, r"WAIT #1 .*no owner-accepted closing merge")
                self.assertIn("No eligible work.", out)

    def test_pr_pagination_drafts_native_links_branches_and_local_duplicates(self):
        rows = [assignment(number) for number in range(1, 7)]
        # In this 31-PR scan the first page serializes nested hasNextPage: false
        # before the outer hasNextPage: true, just as requested by OPEN_PRS.
        code, out, err, calls = self.select(
            rows, pr_page(pr(20, "agent/issue-1-old", draft=True),
                          pr(21, links=[(2, read_ready.REPOSITORY), (6, "other/repo")]),
                          pr(22, "agent/issue-60-other"), *(pr(n) for n in range(23, 50)),
                          more=True, cursor="outer-page-1"),
            pr_page(pr(50, "agent/issue-3"), cursor="outer-page-2"),
            issue_prs(),
            local={4: "existing local run issue-4; Lead triage", 5: "existing registered worktree; Lead triage"},
        )
        self.assertEqual((code, err), (0, ""))
        for number, reason in enumerate(("draft PR #20", "PR #21", "PR #50", "local run", "worktree"), 1):
            self.assertRegex(out, rf"SKIP #{number} .*{reason}")
        self.assertIn('Next issue: #6 "Work 6"', out)
        first, second = [command for command in calls if f"query={ready_selection.OPEN_PRS}" in command]
        self.assertFalse(any(arg.startswith("endCursor=") for arg in first))
        self.assertEqual(second, first + ["-f", "endCursor=outer-page-1"])
        self.assertNotIn("--paginate", first)
        self.assertNotIn("--slurp", first)

    def test_open_pr_pagination_errors_fail_closed(self):
        first = pr_page(pr(70), more=True)
        second_error = {"data": {"repository": None}, "errors": [{"message": "permission denied"}]}
        for pages, error in (
            ([pr_page(pr(70), more=True, cursor=None)], "missing or invalid cursor"),
            ([first, pr_page(pr(71), more=True)], "repeated cursor"),
            ([first, second_error], "GraphQL error"),
            ([first, subprocess.CompletedProcess([], 1, "", "Forbidden (HTTP 403)")], "HTTP 403"),
        ):
            with self.subTest(error=error):
                code, out, err, calls = self.select([assignment(1)], *pages)
                self.assertEqual((code, out), (1, ""))
                self.assertIn("Open pull requests: ", err)
                self.assertIn(error, err)
                self.assertEqual(sum(f"query={ready_selection.OPEN_PRS}" in cmd for cmd in calls), len(pages))

    def test_selection_fails_closed_on_api_auth_and_incomplete_pr_reads(self):
        incomplete = pr(75)
        incomplete["closingIssuesReferences"]["pageInfo"]["hasNextPage"] = True
        for payload, error in (
            (subprocess.CompletedProcess([], 4, "", "auth details"), "authentication failed"),
            ({"errors": [{"message": "permission denied"}]}, "GraphQL error"),
            (pr_page(incomplete), "closing issue links could not be fully verified"),
        ):
            with self.subTest(error=error):
                code, out, err, _ = self.select([assignment(1)], payload)
                self.assertEqual((code, out), (1, ""))
                self.assertIn(error, err)
        for payload, error in (
            (subprocess.CompletedProcess([], 4, "", "auth details"), "authentication failed"),
            ({"data": {"repository": {"issue": None}}}, "closing issue links could not be verified"),
        ):
            with self.subTest(error=error):
                code, out, err, _ = self.select([assignment(1)], pr_page(), payload)
                self.assertEqual((code, out), (1, ""))
                self.assertIn("Linked pull requests for #1:", err)
                self.assertIn(error, err)
        code, out, err, _ = self.select(
            [assignment(1, blockers=[blocker(98, "closed", "completed")])], pr_page(), issue_prs(),
            subprocess.CompletedProcess([], 1, "", "Forbidden (HTTP 403)"),
        )
        self.assertEqual((code, out), (1, ""))
        self.assertIn("Closure of prerequisite #98", err)
        self.assertIn("HTTP 403", err)

    def test_local_runner_conventions_use_primary_checkout_even_from_linked_checkout(self):
        with tempfile.TemporaryDirectory() as root:
            primary = Path(root) / "The-Producer"
            child = primary.with_name("The-Producer-agent-5-abc")
            detached = primary.with_name("The-Producer-review-6-stamp-pr15")
            legacy = primary.with_name("The-Producer-issue-7-old")
            run_home = primary.with_name(".The-Producer-agent-runs")
            for name in ("issue-3", "issue-4-review-pr-15-stamp", "issue-8-history-stamp"):
                (run_home / name).mkdir(parents=True)
            trees = [
                {"path": primary, "branch": "refs/heads/main"},
                {"path": child, "branch": "refs/heads/agent/issue-5-abc"},
                {"path": detached, "detached": ""},
                {"path": legacy, "branch": "refs/heads/legacy"},
            ]
            with (patch.object(ready_selection.Path, "cwd", return_value=child),
                  patch.object(ready_selection, "registered_worktrees", return_value=trees) as worktrees,
                  patch.object(ready_selection, "run_cmd", return_value="https://github.com/" + read_ready.REPOSITORY)):
                found = ready_selection.local_work()
            worktrees.assert_called_once_with(child)
            self.assertEqual(set(found), {3, 4, 5, 6, 7})
            self.assertEqual(len(list(run_home.iterdir())), 3)


if __name__ == "__main__":
    unittest.main()
