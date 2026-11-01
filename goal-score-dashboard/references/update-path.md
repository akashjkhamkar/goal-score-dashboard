# Input and update path

Read this before promising periodic scans, chat replies, cross-device state, or notifications.

## Select an execution mode

| Mode | What works | What remains necessary |
| --- | --- | --- |
| Snapshot | A read-only dashboard of a generated state. | A manual or external update followed by actual delivery to the reader. |
| Local automation | Local files, a local browser, and desktop tools when the host is available. | State the host, app, network, and awake requirements. Verify platform behavior. |
| Hosted automation | Scheduled work without the user's laptop, using supported cloud access. | A hosted scanner, authorized writer, persistent store, and verified schedule. |

A deployed page proves only that a page is hosted.
An installed Home Screen icon proves neither background execution nor push notifications.
A saved schedule proves configuration, not a successful run.
A public source may block unattended access even when it works in an interactive browser.

## Source plan

For each input, record:

1. Exact source and owner, including a user-supplied account URL when needed.
2. Available fields, units, and whether they are public, private, or self-reported.
3. Acquisition method, access scope, and supported runtime.
4. Cadence, timezone, freshness limit, and handling of unavailable data.
5. Evidence identifier, deduplication rule, correction rule, and storage location.
6. The dimension adapter that converts evidence into the agreed input value.

Do not search for a guessed personal account when the user has not supplied or authorized one.
Store timestamps and source provenance with the observations.
Keep platform audiences separate unless a valid deduplication method exists.
Use matched item IDs for trends. An upload's cumulative views are not views gained during the observation period.

## Plain-language check-ins

Choose a channel the user can actually reach, such as the current chat or an authorized messaging integration.
A read-only dashboard does not need its own form.
Preserve relevant original text and extract explicit dates, activity, durations, results, and difficulty.
Keep uncertain fields unknown. Do not infer ability from time spent or improvement from difficulty alone.
Show a brief interpretation only when useful. Ask one follow-up if the ambiguity changes the score materially.
Use stable record IDs. Retry safely. Preserve correction history rather than silently overwriting unrelated evidence.
Never ingest example text or test sessions as actual user activity.

## Data flow

Implement and document this complete flow:

`source or check-in → authorized collector → evidence store → agreed scoring policy → score snapshot → read-only dashboard`

Use shared server storage for cross-device state. Device-local storage is not synchronization.
Use a writer available to the selected runtime. Do not place a write secret in the browser.
Keep credentials out of source, schedule prompts, observations, and screenshots.
Preserve the existing audience. Do not make an app public to get a writer working.
Reuse an existing schedule that covers the work. Do not create duplicate daily reminders.

When using Sites, read its storage, identity, and recurring-update references as needed.
Use supported service access for an owner-private updater. Never reuse a development bypass as production authorization.
Routine evidence updates should update data without rebuilding or republishing the app.
If a supported unattended access path is unavailable, state that limit and provide the working snapshot or local mode.

## End-to-end verification

Use real, authorized initial evidence where possible.
Write through the same authorization and runtime path the scheduled job will use.
Read the persisted record and resulting snapshot back.
Verify that an independent browser session shows the new result.
Test retries, explicit zero, unknown fields, stale evidence, and corrections.
Keep synthetic tests isolated from production. Remove no real records to clean a test.

For a claim of phone-independent operation, verify that the collector and writer do not need local files or a desktop browser.
For a claim of notifications, verify the actual delivery channel and user permission separately.
For installation claims, distinguish manifest setup, browser-width checks, and physical-device testing.

Report which pieces work, which remain unverified, and where the user should send the next input.
Do not claim an automatic update because a local JSON file changed or a schedule was saved.
