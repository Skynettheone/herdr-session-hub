# Usage acceptance — 2026-11-12

This extends the existing History/continuation acceptance. It does not turn the
development candidate into a published production release. Final runtime CI and
package identifiers are recorded in RELEASE_REPORT.md.

## Accounting and source safety

The final local pipeline passed **76 Python tests** (53 existing + 23 Usage),
**17 host UI groups**, Ruff, installed Herdr 0.1.15 SDK validation and offline
locked-wheel checks. Native sources are synthetic, in `.dev/usage-lab`; no real
account prompts, credential reads or provider commands are needed for Usage.

An independent closed-form fixture oracle (not the parser/aggregator) checked
all four presets, channel totals, event counts, USD estimates, summed chart
buckets and model totals. It passed again after the approved cache rebuild:

| Range | Recorded events | Uncached input | Output | Cache read | Cache write | Known estimated USD |
|---|---:|---:|---:|---:|---:|---:|
| 24h | 5 | 7,500 | 936 | 30,000 | 2,250 | 0.019680 |
| 7d | 35 | 356,910 | 44,602 | 1,427,640 | 107,070 | 0.936824 |
| 30d | 150 | 1,652,355 | 206,491 | 6,609,420 | 495,690 | 4.337132 |
| 90d | 450 | 4,960,545 | 619,906 | 19,842,180 | 1,488,105 | 13.020503 |

These are artificial fixture rates/counters, not someone's provider bill. The
fixtures deliberately omit Pi/OpenCode backend metadata; explicitly entered
`unknown/model` fixture rates allow oracle comparison and the coverage warning
remains visible. Real unknown prices are never assigned fixture rates.

Regression cases include streaming/copy deduplication before date filtering,
Codex cumulative/reset/cache/reasoning counters and invalid gaps, huge integers,
unknown/partial prices, distinct local stores, equal project basenames, edited
roots, missing initial roots, committed record budgets, active append/partial
tails, rewrite guards, zstd rollouts, concurrent mutation, quiescent OpenCode
message accounting without source SHM creation, and Gemini rewind/checkpoint
billing retention. See USAGE_REVIEW.md for six reviewed findings and fixes.

## Native GUI pass

Actual copied Herdr 0.1.15 and its own core ran with a separate app home,
`HC_SESSION`, HOME/USERPROFILE/APPDATA/XDG directories. Only this exact returned
test window was used for controls. No production installer or config target was
used. Keyboard/mouse capture occasionally returned an unrelated foreground app;
those captures were not acted on or saved as evidence. Selection was refreshed.

Verified: History/Usage navigation, loading/first-use and completion feedback,
provider/profile selection, 24-hour/custom UTC entry and inclusive end-date
application, token/cost/recorded-limit views, native path charts, token mix,
model/day/project breakdown navigation, average/trimmed-average controls,
rate-form validation, native numeric typing/selection/save, existing-rate
selection, model-row rate editing, notice/error dismissal and aggregate-report
feedback. Trim updates retain the scroll body; model-row editing reveals its
heading. Provider line styles stay stable when filters change and have matching
legend samples; the shaded selected total is labeled separately.

The user explicitly approved the two remaining removal tests. Native **Remove
local rate** removed only `opencode:unknown/synthetic-opencode`; a read-only
state check confirmed absence. Native Save restored the same four rates.
Native **Clear numeric usage cache** left zero numeric cache entries, retained
rates and left every conversation-search flag Off. Native Refresh rebuilt the
same oracle totals. All synthetic original hashes matched afterward.
Final native status reported `errors: []`; only the disposable app/core were
closed. Synthetic fixtures and encrypted local test state were retained.

Dark, Paper light and Atom One Dark community-format themes were inspected;
wide and 360/500-pixel side panels were inspected. Labels/values/notes have equal
card heights. Numeric breakdowns supplement the chart's semantic colors and
line patterns. This is representative native acceptance, not proof of every
combination or deliberately low-contrast community palette.

Genuine, unedited captures:
[custom range](screenshots/usage-custom.png),
[light-theme breakdown](screenshots/usage-light.png),
[community-theme chart](screenshots/usage-community.png).

## Compatibility and package boundary

The new rollback SDK check exposed Herdr 0.1.14's missing `ScrollHandle` export.
Guarded namespace access now allows History, Usage and the header to load without
that optional handle. Actual **0.1.14 and 0.1.15 SDK checks pass**; interactive
Usage testing is on **0.1.15**. Automatic form-reveal scrolling is available on
the newer SDK. Existing exact-version continuation gates remain; older/future
SDKs do not gain native continuation authorization. The earlier actual updater /
backup-rollback results remain in NATIVE_ACCEPTANCE.md; this new check is not
misrepresented as another complete interactive updater cycle.

The offline disposable install smoke passed first installation, upgrade backup,
uninstall WhatIf, state retention, explicit Hub-only purge and unchanged
layout/key/original sentinels. Final archive checks use a fresh extraction,
manifest validation, runtime/script/test byte comparison and an isolated helper
invocation. No release/gallery publication or production installation occurred.

Live account-wide quotas, exact subscription bills, Copilot persisted usage,
ambiguous Codex fork accounting, removed legacy Gemini records and arbitrary
middle-of-file edits during append remain documented boundaries. Distinct
company-account identity isolation remains unverified because no second account
was available. See USER_GUIDE.md and USAGE_DESIGN.md before interpreting totals.
