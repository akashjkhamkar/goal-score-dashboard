---
name: goal-score-dashboard
description: Help a user define, research, and agree on a personal goal score, then build a minimal dashboard with up to five sub-scores and explicit input sources. Use for goal tracking and progress dashboards, not for assigning a person's worth or inventing a success probability.
---

# Goal Score Dashboard

Turn a personal goal into an explained, useful number. Keep the user's interpretation of progress central.
Default to a read-only screen with one score, two to five dimensions, one next action, and an update timestamp.
Adapt the number of dimensions when the goal needs fewer. Respect an explicit preference for another interface.

## 1. Understand the goal

Ask what the user wants to achieve and why it matters. Establish the current position, time horizon, and practical constraints.
Reuse information already supplied. Ask the next useful question, not a long intake questionnaire.
Separate a deadline or income requirement from the full meaning of success unless the user makes it the definition.

## 2. Agree on what the number means

Discuss what a higher score should suggest and what decisions it should help the user make.
Distinguish progress, demonstrated readiness, documented evidence, and a calibrated probability.
Use a transparent progress rubric by default. Do not call it a probability without relevant outcome data and validation.

Agree on the scale, direction, baseline, update period, and treatment of missing data.
Offer up to three interpretations when the meaning is unclear. Discuss tradeoffs in plain language.
Obtain agreement before fixing the meaning. Do not treat silence as agreement.
Preserve earlier authorization. Do not ask again when the user already selected an interpretation.

## 3. Research useful evidence

Research the goal's real context before proposing numerical dimensions or thresholds.
Prefer original studies, direct interviews, official data, and documented histories.
Use connected sources when they provide relevant user-specific context and access is authorized.
Include different routes and stalled or interrupted cases when available. State selection and visibility bias.
Separate association from causation. Separate an observed sequence from a repeatable formula.
Record source URLs, dates, populations, useful signals, and limits.
Do not present expert judgment or product thresholds as fitted research findings.
When good data is unavailable, state the gap and propose an explicitly provisional rubric.

## 4. Agree on the controlling dimensions

Propose two to five broad dimensions that explain the main changes in the score.
Avoid overlapping categories that reward the same behavior twice.
Distinguish effort, output, observable response, and outcomes when they mean different things for this goal.
Do not let an easy counter replace the outcome the user cares about.

Explain each dimension's meaning, evidence, scoring rule, weight, and likely failure modes.
Show one weak, one intermediate, and one strong example. Explain what could lower the score.
Ask the user to revise or accept the dimensions and weights before implementation.
If the user delegates these choices, make a reasonable proposal and label it provisional.

Read [the score contract](references/score-contract.md) when formalizing the agreed rubric or using the bundled scorer.
Keep evidence collection separate from scoring policy. Version later changes to the policy.

## 5. Decide the input and update path

Map each dimension to accessible sources. Identify self-reports, public observations, private analytics, and missing inputs separately.
Accept plain-language check-ins when useful. Preserve the relevant original text and extract only explicit facts.
Do not infer zero activity from an omitted detail. Ask one follow-up when ambiguity changes the interpretation materially.
Keep a source counter, its timestamp, and its unit together. Do not confuse views, unique people, clicks, retention, or income.

Agree on scan cadence, timezone, reply channel, access, freshness, and failure behavior.
Explain whether scans require a running laptop, cloud execution, or a paid service before promising unattended operation.
A hosted dashboard does not establish a hosted scanner, notification channel, or reply handler.
Keep credentials out of generated code, observations, prompts, and browser bundles.

Read [the update path](references/update-path.md) for recurring scans, chat replies, shared storage, or cross-device use.
Proceed with useful local work while a required connection is unavailable. Name the incomplete part clearly.

## 6. Build and verify the dashboard

Use the available app-building workflow. If Sites is available, use its skill for hosting and publication.
Otherwise choose an appropriate supported stack or deliver a local artifact. Do not assume a provider or invent credentials.

Keep the screen small: one overall score, up to five sub-scores, one next action, and the last update.
Put methodology behind a collapsed explanation. Add forms, charts, history, and settings only when requested or necessary.
Show a low supported score honestly. Keep unmeasured dimensions unassessed.
A score rewards evidence under the agreed rubric. It does not measure a person's worth or guarantee an outcome.

The bundled template supports a read-only snapshot and two scoring primitives. Use it when that fits the agreed contract.
Do not force a complex rubric into the template. Implement and explain a different model when needed.

```text
python3 scripts/score.py --contract CONTRACT.json --observations OBSERVATIONS.json --output state.json
python3 scripts/init_dashboard.py --contract CONTRACT.json --observations OBSERVATIONS.json --output NEW_DIRECTORY
```

The initializer refuses an existing output directory. The bundled example is synthetic. Do not seed a real user's dashboard with it.
The generated snapshot is not a live integration. Connect a verified writer and reader before claiming automatic updates.

Test score bounds, unknowns, stale evidence, corrections, duplicate inputs, and changes that should affect the result.
Verify the actual input-to-storage-to-score-to-screen path. Use a real initial observation when authorized.
For periodic updates, verify writer access without the authoring session and preserve the existing schedule when it covers the task.
Check the phone layout when mobile use matters. Explain any unverified notification or installation behavior.

Finish with the working dashboard or artifact, its current evidence limits, and the input channel the user should use next.
