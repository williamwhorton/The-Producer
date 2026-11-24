# GitHub Project Status automation

**Issue:** [#11](https://github.com/williamwhorton/The-Producer/issues/11)
**Workflow:** `.github/workflows/project-status-sync.yml`
**Script:** `tools/sync_project_status.py`

This is an **issue-centric** workflow. GitHub Issues contain requirements and acceptance; the GitHub Project's **Status** field reports progress. Agents issue short status commands as part of work, rather than expecting the Creative Director to watch the board.

## One-time setup — complete walkthrough

The workflow is stored in `.github/workflows/project-status-sync.yml`, and it runs **in this repository** to update a **user-owned GitHub Project**. GitHub's standard `GITHUB_TOKEN` cannot perform the required personal Projects v2 field updates. A personal access token (classic) with `project` and `repo` scopes is the method documented by GitHub for this setup.

**Do not share a personal access token in ChatGPT, an issue, PR, source file, commit, terminal transcript, or screenshot.** Store it only in the GitHub Actions **repository secret** described below. This is a one-time setup; regular board maintenance should then be automated.

### Step 1 — Identify the Project number and verify Status options

1. Sign in as `williamwhorton` on GitHub. Open **your profile → Your projects**, and open *The Producer* development board.
2. Read the Project URL from the browser's address bar. For example, `https://github.com/users/williamwhorton/projects/3` has Project number **`3`**. Use **your actual number**, not the example. This is **not** an issue number, repository number, or project name.
3. On the Project page, open the **top-right three-dot menu (⋯) → Settings**. Under **Fields**, locate the **Status** single-select field.
4. Confirm that its option labels are **exactly** (including capitalization and spacing):
   - `Backlog`
   - `Ready`
   - `In Progress`
   - `In Review`
   - `Blocked`
   - `Done`
5. Add or rename any missing options using the field editor, then **Save**. Do not create a second Status field; this workflow targets the field with the name `Status`. Additional options may exist, but all six listed are required.
6. Confirm the Project belongs to your **personal user account**, rather than an organization. The script explicitly queries `user(login: "williamwhorton")`. Organization-owned Projects require a code adjustment before use.

GitHub guide: [About single-select fields](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-single-select-fields).

### Step 2 — Create a personal access token (classic)

The token must be created by a GitHub account that **has access to edit this Project and its repository** (normally `williamwhorton`).

1. Click your **profile picture → Settings** on GitHub. These are your **personal account settings**, not the repository settings.
2. Scroll down the left sidebar and select **Developer settings**.
3. Select **Personal access tokens → Tokens (classic)**.
4. Click **Generate new token → Generate new token (classic)**. Do **not** choose **Fine-grained tokens** for these instructions; the code and GitHub's example use a classic token.
5. In **Note**, enter something recognizable, such as `The Producer — Project status sync`.
6. Choose a limited **Expiration** (for example, **90 days**, or whatever period you intend to manage). When it expires, the sync will stop until you renew the token and replace the repository secret.
7. Under **Select scopes**, select **`repo`** and **`project`**. You do **not** need to select unrelated scopes such as `admin:org`, `workflow`, or `delete_repo`.
8. Scroll down and click **Generate token**.
9. **Copy the token immediately** into a secure temporary location for the next step. GitHub does not let you retrieve the full token value after leaving this page.

**Security tradeoff:** Classic PATs with `repo` can access more than this one repository, so this is a relatively broad credential. GitHub's official Projects + Actions documentation recommends `project` and `repo` for this pattern. Keep the token expiration limited, never expose it in logs, and consider replacing it with a narrowly scoped GitHub App if this workflow grows.

Official references: [Creating a personal access token (classic)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) and [Automating Projects using Actions](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions).

### Step 3 — Store the token as a repository Actions secret

1. Open the **[The-Producer repository](https://github.com/williamwhorton/The-Producer)**.
2. Select **Settings** in the repository's top navigation (if hidden, check the **⋯** menu).
3. In the left sidebar, under **Security**, choose **Secrets and variables → Actions**.
4. Select the **Secrets** tab.
5. Under **Repository secrets**, click **New repository secret**.
6. Enter **Name:** `PROJECTS_TOKEN` (all capitals, exactly as written).
7. Enter **Secret:** paste the personal access token created in Step 2.
8. Click **Add secret**.

Do not place this token in a **Variable**, commit, issue, or PR. Once stored, its value is hidden. You may verify that the **name** `PROJECTS_TOKEN` appears, but GitHub will not display the secret's actual value.

Shortcut: [The-Producer → Actions secrets and variables](https://github.com/williamwhorton/The-Producer/settings/secrets/actions).

### Step 4 — Create the repository Actions variable

On the same repository page:

1. Open the **Variables** tab (beside Secrets).
2. Under **Repository variables**, click **New repository variable**.
3. Enter **Name:** `PROJECT_NUMBER` (all capitals, exactly as written).
4. Enter **Value:** the **numeric Project number** from Step 1, for example `3` **only if your Project URL actually ends in `/3`**. No `#`, URL, quotes, or extra text.
5. Click **Add variable**.

The workflow reads `PROJECTS_TOKEN` from **Secrets** and `PROJECT_NUMBER` from **Variables**. Reversing these locations will prevent it from running.

Shortcut: [The-Producer → Actions variables](https://github.com/williamwhorton/The-Producer/settings/variables/actions).

### Step 5 — Merge PR #12; then run the initial synchronization

**Do not attempt the initial run until PR #12 has merged into `main`.** The workflow's **Run workflow** control appears after the workflow file exists on the default branch. Merging PR #12 also closes Issue #11 because the PR contains `Closes #11`.

1. Review and merge [PR #12](https://github.com/williamwhorton/The-Producer/pull/12) when satisfied with its code and permissions. (This is a human approval step, not automatic.)
2. Open the repository's **Actions** tab.
3. In the **All workflows** list on the left, click **Sync GitHub Project Status**.
4. On the right, click **Run workflow**.
5. Choose branch **`main`** in the workflow dropdown.
6. In the input named **`bootstrap_statuses`**, enter exactly:

   ```text
   4=In Progress,5=Blocked
   ```

   This assigns the active architecture spike **#4** to In Progress and its dependent simulation work **#5** to Blocked. **Do not include #11:** merging this PR closes #11, and specifying `11=In Progress` for a closed issue makes reconciliation fail.
7. Click the final **Run workflow** button to submit.
8. Select the newest run; open its **sync** job and **Update Project Status** step. Confirm a green success check and inspect the logged `#N: previous -> new` transitions.
9. Return to the Project board. Verify:
   - Issue **#2** → **Done** (closed).
   - Issue **#4** → **In Progress** (initial override).
   - Issue **#5** → **Blocked** (initial override).
   - Issue **#11** → **Done** (closed after this PR merges).
   - Other open issues → **Backlog**, unless they had an existing non-Done status.

Afterward, a new issue, an accepted closure, a linked PR, or an owner-authored `/status ...` comment triggers the workflow automatically.

**Important:** `bootstrap_statuses` is an **override**, not a permanent configuration. **Leave it blank** on subsequent routine reconciliations unless you deliberately need to correct one specific issue. Otherwise a stale input can overwrite newer progress.

GitHub guide: [Manually running a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

### Step 6 — Confirm an ordinary status transition

After the successful initial run, test the comment-driven path using a **non-destructive** transition on an open issue:

1. Choose an open issue that should be in its current status (for example, **#4** while architecture work is active).
2. Leave a **new, standalone issue comment** containing exactly `/status In Progress` (no markdown fence or extra prose). Post it while signed in as **`williamwhorton`**.
3. Go to **Actions → Sync GitHub Project Status** and verify that the comment-triggered run succeeded.
4. Confirm the issue remains **In Progress** on the Project board. Logs may say `already In Progress`, which counts as success.

Only owner-authored standalone status comments trigger these changes. If an agent's GitHub CLI is not authenticated as `williamwhorton`, it must report the required transition rather than claim it changed the board.

### Troubleshooting and credential maintenance

| Symptom | Check |
|---|---|
| **No Run workflow button** | PR #12 must be merged; select the workflow from **Actions** on the repository and make sure Actions is enabled. The workflow must exist on `main`. |
| **Missing PROJECTS_TOKEN** | Create the secret under **Repository Settings → Secrets and variables → Actions → Secrets**. Check the exact name; secret values cannot be viewed after creation. |
| **Set PROJECT_NUMBER** | Create the variable under **Variables**, using digits from the **Project URL**, not an issue or repository number. |
| **Project not found / token lacks access** | Verify the Project belongs to `williamwhorton`, the number is correct, token scopes include `project` and `repo`, and the token's account has edit access. |
| **Status field / options missing** | Open the Project's settings and check the `Status` field's six exact option names. |
| **Comment does not move a card** | The comment must be authored by `williamwhorton`, have exactly one `/status ...` command, and be on an **issue** rather than a PR conversation. Inspect the Actions run logs. |
| **Token expired or revoked** | Generate a new classic PAT with `repo` and `project`, then **update** the `PROJECTS_TOKEN` repository secret. Never paste the old or new value into an issue. |
| **First reconciliation fails** | Remove overrides for any **closed** issue; the workflow requires closed issues to stay **Done**. Re-run from the Actions tab after correcting configuration. |

**Security and completion:** The secret must never appear in version control. The workflow checks out only trusted default-branch code, not untrusted PR-head code. Configuration is **not verified** until a successful Actions run is observed and the board reflects its results.

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

- **Lead / Creative Director:** `Ready` after bounded scope and prerequisites are recorded for the two-day queue. An undispatched successor may wait in Ready; use `Blocked` for claimed work that needs intervention and `Backlog` on deferral.
- **Developer/Architect:** `In Progress` when actually starting; `Blocked` when waiting on a concrete prerequisite.
- **Reviewer:** `In Review` when reviewing without a PR; a ready PR with a closing reference already does this automatically.
- **Done** is tied to **issue closure** after acceptance; attempting `/status Done` on an open issue fails instead of making misleading board state.
- Agents must verify the resulting board value, not just successful comment posting. In [queue mode](agent-orchestration.md#run-the-ready-queue), the trusted host posts and reads back claims and handoffs; Build and Reviewer do not need direct Project access. If the host cannot verify auth, scope or the expected Status, it stops dispatch and retains the evidence.

For security, status comments are accepted only when posted by the repository's owner, and PR-triggered transitions require the PR to originate from the same repository. Do not add arbitrary status commands to untrusted PR descriptions.

## Reconciliation and failure recovery

- Status writes are serialized with a multi-run Actions queue so unrelated pending events are not replaced by normal overlap. A delayed PR or comment job does not override a newer explicit owner status command.
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
