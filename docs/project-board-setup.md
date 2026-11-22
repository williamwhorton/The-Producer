# GitHub Project board setup (manual step)

GitHub Issues are created by the setup workflow, but the connected GitHub integration currently does not expose a Projects-v2 board creation action.

1. In GitHub, visit your profile's **Projects** and create a new **Board** named **The Producer — Development**.
2. Link `williamwhorton/The-Producer` as the project repository; add the initial issues.
3. Configure a single-select **Status** field with: Backlog, Ready, In Progress, In Review, Blocked, Done.
4. Add fields: Priority (P0/P1/P2), Workstream (Design, Architecture, Infrastructure, Simulation, QA), and Requires human approval (Yes/No).
5. Set default view to board grouped by Status. Avoid automatically moving issues to Done when a PR is opened; acceptance requires review and actual test evidence.
6. Use issue dependencies and links to show work that must not begin before design approval.

Suggested initial statuses: Game-vision review and local-agent workflow validation can enter Ready when accepted by the Creative Director. Engine evaluation is Backlog until criteria are approved; gameplay implementations remain Backlog until architecture choices are made.

Do not treat this file as evidence the actual GitHub Project board has been created.