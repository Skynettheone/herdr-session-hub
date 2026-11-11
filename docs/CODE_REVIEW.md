# Source review — 2026-11-12

The code-review skill ran separate Standards and Spec reviews against the
requirements baseline `ecaa73d..HEAD`, followed by review of the working expansion.
These are source reviews, not an independent security audit. The sections retain
the two review axes; a passing source check does not close native release gates.

## Standards

The final reviewer reported these areas addressed: shared-source FTS authorization;
recovery retaining current state until replacement; partial byte/record coverage;
snapshot-aware UI requests, input focus and preview generations; independent parser
modules with fixed-path isolated imports; Copilot subagent exclusion; and authoritative
Herdr icon tint/full-color handling.

Its remaining P2 finding was startup overwriting an early filtered response. Startup
now uses `requestFor`/`publishList`, and a delayed-initial-response regression passes.
The earlier monolithic parser/repeated-switch concern was a design judgement;
provider parsing now has a fixed registry and separate modules. OpenCode's bounded
immutable database operations remain grouped in the helper, with dedicated tests.

Standards disposition: **0 reported actionable findings left unresolved**. The most
serious original issue was profile-specific search privacy (P1), now regression-tested.

## Spec

The final reviewer confirmed the search/refresh race fixes and nine host groups
(eight at the time of its last run). It reproduced two new expansion defects:
Copilot `agentId` subagent content/cwd contamination and Gemini's cumulative message
budget after a checkpoint. Both are fixed with explicit fixture assertions.

The earlier FTS opt-out, cross-chunk AND semantics, keep-local-with-no-annotation,
and dropped-search findings are fixed and tested. Live catalog/custom-agent
recognition and artwork handling were assessed as correctly integrated.

The reviewer explicitly accepted that Copilot continuation and unknown/Cursor/Amp
history are presented as unavailable. These remain capability limits, not feature
passes. Native continuation, exact active ownership and real Herdr updater testing
remain open requirements, detailed in FEATURE_STATUS.md. No unsupported reader or
resume command is substituted for them.

Spec disposition: **0 reported implementation defects left unresolved; 3 main
acceptance areas still open** (native continuation/profile isolation, precise active
ownership, actual Herdr update/rollback). The worst original implementation defect
on this axis was FTS privacy (P1), now fixed.

Summary: Standards 0 unresolved actionable findings; Spec 0 unresolved reported
implementation defects with the above acceptance gaps. No production-ready or
independent-security-audit claim follows from this review.
