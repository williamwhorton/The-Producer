# Issue Type, Priority and Workstream migration

**Purpose:** Populate the **existing native GitHub Issue Type** and the personal-account **Priority / Workstream issue fields**. Do not create labels or another Project field to represent this data.

**Implementation:** `tools/sync_issue_metadata.py` and `.github/workflows/issue-metadata-backfill.yml`. **Tracks:** [#64](https://github.com/williamwhorton/The-Producer/issues/64).

## Field ownership

- **Type** is GitHub's native issue type (Feature, Bug, Task, Spike, Design Decision). It is not a label, an issue-title prefix, or a Project Status.
- **Priority** and **Workstream** are issue custom fields, not prose fields in the issue body. The script discovers **existing field IDs and option names** on the authenticated GitHub account, without guessing IDs or adding options.
- **Status** remains the separate GitHub Project single-select field, updated by `project-status-sync.yml`; do not use this migration to change statuses.

Existing issue titles and bodies retain some historical metadata as **one-time import hints**. After the native fields are set, trust the fields, not conflicting legacy text. In particular **#13, #14, #15 must be Task** (runnable, disposable proofs), while **#4 remains Spike** (engine investigation). The issue Type alone never forbids a Developer from producing an explicitly approved disposable experiment.

## One-time setup

**No token should be pasted into a chat, source code, PR, or GitHub issue.**

1. Review and merge the PR that introduces this migration. It must be on the default branch for GitHub Actions to run.
2. Reuse the **repository secret `PROJECTS_TOKEN`** configured for the existing board-status automation. The token must have `repo` access to write issues; `project` remains necessary for the original Projects workflow. **Additionally, the current GitHub API requires `read:user` on a classic PAT to list personal issue custom fields.** If the run fails with an error on `GET /user/issue-fields`, add `read:user` to the existing token's scopes (or generate/rotate a purpose-specific token with `repo`, `project`, `read:user`), and replace the `PROJECTS_TOKEN` repository secret. Do not reveal the token value.
3. Confirm your **Type** field has enabled options `Feature`, `Bug`, `Task`, `Spike`, `Design Decision` (as appropriate), and your issue custom fields are named exactly **Priority** and **Workstream**.
4. The initial import only uses **options that already exist**. If the Workstream field has only the initial five broad categories (`Design`, `Architecture`, `Infrastructure`, `Simulation`, `QA`), some UI/content/release work is grouped into related broad categories. Review the migration output and expand the existing Workstream options in GitHub if you want finer categories. The workflow never changes option definitions.

GitHub sources: [Issue types and fields on personal accounts](https://github.blog/changelog/2026-11-11-issue-types-and-fields-are-available-for-personal-accounts/), [Issue field REST API](https://docs.github.com/en/rest/issues/issue-field-values?apiVersion=2026-03-10), [Issue type API](https://docs.github.com/en/rest/repos/issue-types), [List your issue fields](https://docs.github.com/en/rest/users/issue-fields).

## First dry run

1. Open **The-Producer → Actions → Backfill Issue Type and Fields → Run workflow**.
2. Select the default branch, **`main`**.
3. Leave **dry_run = true**, **issue_numbers = blank** (all issues), and **replace_existing = false**.
4. Run it and read the **metadata** job logs. They display available Issue Types and the actual Priority and Workstream options, proposed changes, preserved existing fields and unsupported values. **No writes occur in dry-run mode.**
5. Check that #13/#14/#15 say **Type=Task** and #4 remains **Spike**; that Priority and Workstream proposals are reasonable; and that the workflow does not report missing scopes or fields. If fields are missing, fix your GitHub field configuration/token before applying.

## Apply verified changes

1. Run the workflow again with **dry_run = false**, **issue_numbers = blank**, **replace_existing = false**.
2. Existing nonempty **Type**, **Priority**, and **Workstream** are **preserved** by default, except the explicitly authorized #13/#14/#15 **Type corrections to Task**. Missing values are populated from old issue metadata and title/issue body declarations where a matching configured option exists.
3. The script reads each issue's fields after writing to verify the new values. It stops with an error on failed writes rather than silently claiming success. Check the logs.
4. Review the actual Issue Type/Priority/Workstream fields on #4, #13–#15, and a sample of design/implementation/release issues. **Only successful live Actions runs verify the migration.**

### To correct a specific manually populated field

Use `issue_numbers = 13,14,15` or another explicit comma-separated list. For those issues only, set `replace_existing = true` after reviewing the dry-run proposals, and run with `dry_run = false`.

Never run **replace_existing = true** on the entire backlog; the script intentionally refuses this to protect intentional manual triage.

## Ongoing issue creation

The new workflow also runs when an issue opens. Agents should first use the **actual Issue Type/Priority/Workstream fields** through a supported UI/API when possible. When an integration only supports title and body, the Lead can create an issue with an **intake block** such as:

```markdown
**Issue Type:** Task
**Priority:** High
**Workstream:** Architecture
```

This is an input used to populate native fields, **not a second classification scheme**. The workflow reads a new issue's explicit values and imports them where valid, then the Lead verifies them. For existing older issues, the importer understands legacy title prefixes like `[Feature]` and metadata in their bodies, solely for migration.

If the workflow cannot populate a field because its option does not exist, it records a warning. The Lead must correct the **actual field** via GitHub UI or a supported API, or request a new appropriate Workstream option. It should not invent one or create labels. New issues without any Type/Priority/Workstream information remain unclassified rather than guessed.

## Developer/Spike convention

Read the **approved deliverable**, not just the issue Type:

- **Task:** an approved specific deliverable, potentially a runnable proof or disposable test harness.
- **Spike:** an evidence-gathering investigation that **may include explicit code, scenes, tests, measurements and disposable experiments**. The Developer should execute those tasks when the issue approves them.
- **Design Decision:** investigate and propose alternatives; Creative Director approval is required before implementing undecided game systems.
- **Feature:** implemented, tested player-facing or simulation behavior after prerequisite decisions.
- **No type** automatically grants permission to choose a production engine or invent game mechanics.

#13–#15 can be assigned directly to the Developer. **No further architectural approval is needed for their disposable, explicitly approved prototype scope**. The production engine decision and any lasting systems remain gated by #4/ADR-0002 and the Creative Director.

## Verification

```bash
python3 -m unittest discover -s tests -p 'test_issue_metadata.py' -v
```

Passing offline tests is necessary but not sufficient: the real GitHub fields and token permissions must be validated with an Actions run. This migration is intentionally dry-run-first and does not modify existing Project Status or secretly create extra fields.
