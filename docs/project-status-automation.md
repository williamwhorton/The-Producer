# GitHub Project Status automation

**Issue:** [#11](https://github.com/williamwhorton/The-Producer/issues/11)
**Workflow:** `.github/workflows/project-status-sync.yml`
**Script:** `tools/sync_project_status.py`

This is an **issue-centric** workflow. GitHub Issues contain requirements and acceptance; the GitHub Project's **Status** field reports progress. Agents issue short status commands as part of work, rather than expecting the Creative Director to watch the board.

## One-time setup (Creative Director)

GitHub Actions' ordinary repository token does not have sufficient access to update user-owned Projects v2. This workflow needs a Project-enabled token. **Do not put it in the repository or in a chat.**

1. Open your GitHub Project. Note the number at the end of its URL, e.g. `https://github.com/users/williamwhorton/projects/3` means `3`. This script assumes the Project is owned by the same **personal account** as the repository.
2. Under **The-Producer → Settings → Secrets and variables → Actions → Variables**, create a **repository variable** named `PROJECT_NUMBER` containing that number.
3. Under GitHub **Settings → Developer settings → Personal access tokens → Tokens (classic)**, create a token with `project` and `repo` scopes. Prefer a short expiration and rotate it as required. GitHub documents these scopes for Projects Actions integration; consider a dedicated GitHub App later if broader-token exposure is undesirable.
4. Under **The-Producer → Settings → Secrets and variables → Actions → Secrets**, create a **repository secret** named `PROJECTS_TOKEN` and paste the token there, not into an issue or pull request. The workflow uses it only from the trusted default branch and never checks out PR-head code in a privileged context.
5. Ensure the Project has a single-select field named **Status**, with **exactly named options** `Backlog`, `Ready`, `In Progress`, `In Review`, `Blocked`, and `Done` (additional options are fine).
6. **After merging this PR**, go to **Actions → Sync GitHub Project Status → Run workflow**, and supply `4=In Progress,5=Blocked` in the `bootstrap_statuses` input for the **first** reconciliation. The run will mark closed issue #2 Done and other open issues Backlog unless they have an existing active Status. It will explicitly set #4 and #5 as above. **Do not supply these bootstrap overrides on later routine reconciliation runs**; they would overwrite newer statuses.
7. Check that the workflow succeeded and verify #2, #4, and #5 on the board. **Until this completes, this automation is installed but not operationally validated.**

See [GitHub's official Projects Actions guide](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions) for token and project permissions.

## Automatic transitions

| Event | Project Status |
|---|---|
| New GitHub Issue | **Backlog** (automatically adds item to Project if needed) |
| Issue closed | **Done** |
| Issue reopened | **Backlog** |
| Non-draft PR opened or marked ready, with `Closes #N` / `Fixes #N` / `Resolves #N` in the body | Linked issue → **In Review** |
| Draft PR opened/converted to draft, with a closing keyword | Linked issue → **In Progress** |
| PR closed unmerged, with a closing keyword | Linked issue → **In Progress** |
| Issue closed after PR merge | **Done**, through the issue-closed event |

The workflow does **not** infer approval or readiness from priority, assignment, or a PR being created. A merged PR without a closing reference does **not** automatically close the issue.

## Agent-triggered transitions

For transitions not observable from GitHub events, the repository **owner** posts an issue comment containing **only** one of the following commands:

```text
/status Ready
/status In Progress
/status In Review
/status Blocked
/status Backlog
```

Use the GitHub UI, the connected GitHub integration, or an authenticated GitHub CLI:

```bash
gh issue comment 4 --repo williamwhorton/The-Producer --body "/status In Progress"
```

- **Lead:** `Ready` when scope, approvals and dependencies are in place; `Blocked` when dependencies prevent work; `Backlog` on deferral.
- **Developer/Architect:** `In Progress` when actually starting; `Blocked` when waiting on a concrete prerequisite.
- **Reviewer:** `In Review` when reviewing without a PR; a ready PR with a closing reference already does this automatically.
- **Done** is tied to **issue closure** after acceptance; attempting `/status Done` on an open issue fails instead of making misleading board state.
- Agents must confirm that posting succeeded. If GitHub CLI authentication or comment permissions are missing, report the missing transition so the Lead or ChatGPT's authorized GitHub connection can issue it. Never silently claim the board was updated.

For security, status comments are accepted only when posted by the repository's owner, and PR-triggered transitions require the PR to originate from the same repository. Do not add arbitrary status commands to untrusted PR descriptions.

## Reconciliation and failure recovery

- Run **Actions → Sync GitHub Project Status → Run workflow** with an **empty** bootstrap input whenever board items may be missing or closed issues were not moved to Done.
- Routine reconciliation adds missing issue cards, sets all closed issues Done, and keeps existing **non-Done** statuses on open issues so it won't erase manually or agent-set work stages. It resets erroneously Done open issues to Backlog.
- One-time manual overrides are supported with `ISSUE=STATUS` pairs separated by commas. Use only when correcting an existing status (e.g. `4=In Progress,5=Blocked`).
- If an event run fails, review its Actions logs for missing secret/variable, token permissions, missing Project option, or API error. Fix the cause and run reconciliation.
- The automation does **not** synchronize arbitrary manual board card moves back to issue comments or manage Project fields other than Status. The board remains the source of truth for status values.

## Verification

Local, network-free tests:

```bash
python -m unittest discover -s tests -p 'test_project_status_sync.py' -v
```

End-to-end verification requires a successful Actions run with `PROJECTS_TOKEN` and `PROJECT_NUMBER`. Passing unit tests alone cannot prove remote GraphQL permissions or board behavior.
