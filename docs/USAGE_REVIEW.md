# Usage review — 2026-11-12

Baseline selected by the user: `54c7809`. Reviewed implementation snapshot:
`316a499`; fixes are recorded in subsequent conventional commits. The
[code-review skill](C:/Users/tharu/.agents/skills/code-review/SKILL.md) assigned
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

No material scope creep was reported. Unavailable live quotas, Copilot usage,
ambiguous Codex fork accounting and removed legacy Gemini records stay explicit.

Review totals: Standards 2 findings (worst P2), Spec 2 findings (worst P1);
all four have fixes and regression coverage. CI and native acceptance evidence
are maintained separately; neither the review nor a green scan guarantees that
every possible provider history is supported.
