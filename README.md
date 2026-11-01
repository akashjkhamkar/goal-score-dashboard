# Goal Score Dashboard

A reusable Codex skill for turning a personal goal into an explained progress score and a minimal dashboard.

## Workflow

1. Understand the user's goal and constraints.
2. Agree on what the number should suggest.
3. Research relevant evidence and its limits.
4. Agree on up to five dimensions and their weights.
5. Choose input sources, check-ins, and an honest update path.
6. Build and verify the dashboard.

The skill defaults to one overall score, two to five sub-scores, and one next action. It distinguishes documented progress from a validated probability of success.

## Use

Place the `goal-score-dashboard` folder in your Codex skills directory, usually `~/.codex/skills/`.

Invoke it with:

```text
Use $goal-score-dashboard to help me define progress toward my goal and build a minimal dashboard.
```

Start with a real goal. The skill discusses score meaning before it fixes dimensions or builds an app.

## Included

- [SKILL.md](goal-score-dashboard/SKILL.md): the conversation and build workflow.
- A score contract and input/update guidance.
- A dependency-free Python reference scorer.
- A minimal read-only HTML/CSS/JavaScript template.
- Synthetic example inputs and behavior tests.

The scripts require Python 3.10 or later. Viewing the generated dashboard requires an HTTP server and a browser. Python's standard library is sufficient for the bundled scripts.

```sh
python3 goal-score-dashboard/scripts/test_score.py
python3 goal-score-dashboard/scripts/init_dashboard.py \
  --contract goal-score-dashboard/assets/examples/contract.json \
  --observations goal-score-dashboard/assets/examples/observations.json \
  --as-of 2026-01-02T12:00:00Z \
  --output example-dashboard
python3 -m http.server 8000 --directory example-dashboard
```

The example is fictional and visibly marked synthetic. It is not a user's actual progress.

## Update modes

The bundled template is a snapshot. It does not configure account access, scheduled scans, chat ingestion, push notifications, or cloud execution. Those need a verified source-to-storage-to-screen integration in the chosen environment.

A hosted dashboard does not mean the collector runs without a laptop. The skill requires this dependency to be made clear before promising unattended updates.

Do not publish a local snapshot as a live integration. Keep credentials out of browser code and exported skill files.
