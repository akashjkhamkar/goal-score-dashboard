# Score contract

Use this reference after the user agrees on score meaning and dimensions.
The contract is a reviewable product decision. Research informs it but does not automatically validate its weights or targets.

## Record the agreement

Record the goal, score interpretation, population or context, time horizon, and current evidence.
Record dimensions, units, weights, transformations, freshness limits, missing-data behavior, and version.
Record the user's accepted choices and the research URLs that support the selected signals.
Keep personal financial constraints separate unless the user wants them in the score.

For each dimension, distinguish an observation from its interpretation.
For example, practice minutes establish reported activity. They do not establish skill or future success.
Repeated demand and retention are different. Retention requires evidence about the same people or a valid aggregate retention measure.
A single viral event is not durable demand. An opportunity is not necessarily completed work or income.

## Missing evidence

Select one policy with the user:

| Policy | Meaning |
| --- | --- |
| `withhold` | Show no overall number until every dimension has usable evidence. |
| `range` | Show the possible rubric range while some dimensions remain unassessed. This is not a statistical confidence interval. |
| `evidence_floor` | Show only confirmed contributions. Missing dimensions add no confirmed points. Explain that this is an evidence score, not poor ability. |

Do not silently renormalize weights around missing dimensions.
Distinguish explicit zero, unmeasured activity, failed collection, and stale observations.
Preserve the last known observation with its timestamp when collection fails. Do not replace it with zero.
Apply the agreed freshness rule before calculating a current score.
A changed interpretation, weight, target, or missing-data policy requires a new contract version and a visible explanation.

## Bundled scorer

The scorer is a small reference implementation, not a predictive model.
It supports a linear baseline-to-target transformation and an ordinal rubric with exact levels.
Choose another implementation when the agreed model requires interactions, event aggregation, diminishing returns, or validated prediction.

Contract fields:

| Field | Rule |
| --- | --- |
| `schema_version` | `1` |
| `contract_version` | User-readable version string. |
| `goal` | User's goal. |
| `score_meaning` | What the number can suggest. |
| `scale.minimum`, `scale.maximum` | Integer display bounds, such as 1 and 1000. |
| `unknown_policy` | One policy from the table above. |
| `dimensions` | One to five dimensions with unique IDs. |
| Dimension `id`, `label`, `value_meaning` | Stable ID, display label, and interpretation of the input value. |
| Dimension `weight` | Positive relative weight. All declared weights normalize together, including unassessed dimensions. |
| Dimension `freshness_days` | Maximum observation age. Omit only when the measure does not expire. |
| Dimension `rubric` | One transformation below. |

Linear rubric: `{ "type": "linear", "baseline": 0, "target": 10 }`.
The normalized fraction is `(value - baseline) / (target - baseline)`, capped from 0 to 1.
A lower target supports a lower-is-better measure. Baseline and target must differ.
This is a product baseline, not an estimate of an unobserved user's starting point.

Level rubric: `{ "type": "levels", "levels": [{ "value": 0, "fraction": 0, "label": "No demonstrated example" }, { "value": 1, "fraction": 0.5, "label": "One supported example" }, { "value": 2, "fraction": 1, "label": "Repeated supported examples" }] }`.
Levels must use increasing values and nondecreasing fractions. The input must match an exact declared value.
The level definition determines whether a self-report or an external observation is sufficient.

Observation fields:

```json
{
  "schema_version": 1,
  "synthetic": false,
  "next_action": "One specific experiment justified by the weakest useful evidence.",
  "dimensions": {
    "dimension_id": {
      "value": 2,
      "status": "self_reported",
      "observed_at": "2026-01-01T12:00:00Z",
      "source": "User check-in",
      "notes": "A relevant observation and its limits."
    }
  }
}
```

Known statuses are `observed` and `self_reported`.
Missing statuses are `unassessed` and `unavailable`, with a null value.
Use an ISO timestamp with a timezone for every known observation.
Missing dimensions become unassessed. Undeclared dimension IDs and duplicate JSON keys are errors.

The overall score maps the weighted fraction onto the agreed scale.
Bounds assign unassessed fractions from 0 to 1 without changing known weights.
The scorer adds no probability interpretation, confidence estimate, or claim of causal improvement.
The generated state says `snapshot` until a separate verified integration exists.

## Commands

```text
python3 scripts/score.py --contract CONTRACT.json --observations OBSERVATIONS.json --output state.json
python3 scripts/init_dashboard.py --contract CONTRACT.json --observations OBSERVATIONS.json --output NEW_DIRECTORY
```

Use `--as-of ISO_TIMESTAMP` for a reproducible historical calculation or synthetic example.
The initializer creates a new directory with a read-only page and `state.json`.
The output must be served over HTTP. Opening `index.html` through a file URL does not reliably permit JSON fetching.

The example files under `assets/examples/` are synthetic and use a fictional language-learning goal.
Use them to exercise the tools. Do not publish them as a real user's evidence.
