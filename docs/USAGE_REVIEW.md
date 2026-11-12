# Usage review — 2026-11-12

Baseline selected by the user: `54c7809`. Reviewed implementation snapshot:
`316a499`; fixes are recorded in subsequent conventional commits. The session's
`code-review` skill assigned
separate read-only standards/security and spec reviewers. The originating spec
was USAGE_DESIGN.md and the user's Usage/accuracy/theme requests. This is a
separate agent review within the implementer team, not an external human audit.

## Standards

1. **P2: oversized valid JSON integers could abort Usage refresh.** Numeric
   validation called `math.isfinite` before its bound check. Fixed by checking
   bounds first for token counts, timestamps, provider costs and limit percentages.
   Regression fixtures include `10**1000`, NaN, infinity, booleans and negatives.
2. **P2: failed initial discovery could appear as zero complete usage.** Fixed
   by merging scoped discovery failures/limits and not-yet-scanned profiles into
   the visible coverage report, even when no source record exists.
3. **Follow-up: changing profile folders could retain an old ready status.**
   Fixed by invalidating that profile's discovery status/targets and resetting
   both enumeration cursors. The reviewer reran the regression and confirmed it.

The reviewer found no added credential, network, shell-string or original-history
write path. Source reads remain scoped, numeric persistence remains encrypted,
and native drawing uses the installed SDK. No additional actionable standards
findings were reported; code-smell heuristics were assessed separately from
documented requirements.

## Spec

1. **P1: Gemini rewind silently removed recorded billing.** Fixed by separating
   billing-record extraction from active conversation replay. A fixture proves
   preview becomes empty after rewind while its recorded 120 tokens remain,
   including deduplication after a later repeated checkpoint.
2. **P2: Pi/OpenCode pricing lost the upstream provider identity.** Fixed with
   bounded backend-qualified model/rate identities and Pi billing deduplication.
   A fixture proves two backends sharing one model remain separately priced and
   old ambiguous prices do not apply. Missing backend identity is explicit.
3. **Follow-up: a complete-file Gemini journal could retry the same prefix after
   its record budget.** Fixed by reporting incomplete coverage without pending
   work when that complete-file budget is exhausted. The reviewer reran the
   greater-than-10,000-record regression and confirmed the fix.

No material scope creep was reported. Unavailable live quotas, Copilot usage,
ambiguous Codex fork accounting and removed legacy Gemini records stay explicit.

Review totals: Standards 3 findings (worst P2), Spec 3 findings (worst P1);
all six have fixes and regression coverage. Follow-up resolutions were confirmed
at `e00693e`. CI and native acceptance evidence
are maintained separately; neither the review nor a green scan guarantees that
every possible provider history is supported.
