# Production readiness — 2026-11-12

## Current decision: native ports required

The user explicitly declined Windows-only production scope and requires macOS
and Linux ports first. Portable core/installers/locked bundles and native OS CI
now exist; native Herdr GUI/provider acceptance on those desktops is unavailable
in this environment. POSIX continuation stays disabled. See PORT_ACCEPTANCE.md
for exact targets and evidence. `releaseReady=false` remains correct; scope
selection itself is no longer the outstanding decision.

The candidate is verified for the scope below, but remains **0.1.0-rc.1**. This
inventory supersedes historical open-task lists; it separates defects we can
fix locally from unavailable evidence and deliberate capability boundaries.
Production installation, a release tag, and gallery publication remain separate
user decisions. None was performed by this follow-up.

## Local gaps addressed

| Area | Current evidence |
|---|---|
| Native continuation | Claude, Codex, Pi, OpenCode and Gemini retained ID/cwd/profile and prior context through the actual Hub button; real-cloud Claude continuation also passed. See NATIVE_ACCEPTANCE.md and FOLLOWUP_ACCEPTANCE.md. |
| Native controls | History forms, organization, picker cancellation and user-controlled search consent/index/clear passed. Usage filters, rates, reports, cache clear/rebuild and representative dark/light/community/narrow layouts passed. See FORM_ACCEPTANCE.md and USAGE_ACCEPTANCE.md. |
| Herdr update / rollback | Actual isolated 0.1.14→0.1.15 update, backup rollback and re-update passed. Both SDK checks pass; continuation remains disabled outside 0.1.15. |
| Manual security review | Requested manual assessment and agent reviews completed; reported defects fixed. CodeQL is supplementary. No external human audit is claimed or silently substituted. |
| Package integrity | Follow-up rejects empty/incomplete manifests, missing/altered/unlisted payloads, duplicate/case-alias/unsafe paths, links and private development files. File/count/manifest budgets bound verification. Builder checks staging and fresh extraction; installer checks before target writes. |
| Interrupted upgrades | Follow-up prepares a unique runtime per install, preserves the previous runtime, serializes installers, restores the old mod after an ordinary failed final swap, and refuses unresolved power-loss receipts. Explicit recovery is in USER_GUIDE.md. |

The follow-up changes installer/build validation only. Previously verified native
panel, launch and accounting source is unchanged; no repeated cloud prompt or
privacy-control test is necessary to validate these script changes. Final test,
CI and artifact receipts are recorded in RELEASE_REPORT.md.

## Evidence that cannot be manufactured locally

| Boundary | What is needed to expand the claim | Current behavior |
|---|---|---|
| Distinct personal/company cloud identities | Two authorized accounts and user-handled native login; the user has only one identity | Separate real stores and unsigned negative control passed. Do not advertise verified enterprise identity separation. Hub does not read credentials or infer the account. |
| Copilot native continuation | A working standalone CLI, supported authenticated test setup and native continuity acceptance | Installed shim has no real CLI; history reader remains available, continuation disabled. Ordinary persisted logs omit usage. |
| Cursor, Amp and other Herdr agents | Verified offline source contracts, fixtures and installed CLI continuation tests | Catalog recognition with specific unavailable-reader/resume status; no guessed disk reader or command. |
| macOS/Linux desktops / other architectures / UNC / WSL | Native GUI/continuation acceptance on the implemented port targets; separate native port work for other architectures | Windows x64 desktop acceptance passed. Linux x64/macOS arm64 helpers and native key stores pass OS CI; their continuation remains disabled pending desktop tests. Unsupported architectures and paths are rejected. |
| Other provider / Herdr builds | Version-specific source/help/SDK checks and disposable native acceptance | Exact researched versions and fingerprints gate launch. Unknown ownership/version blocks rather than silently launching. |
| Independent human audit / publisher signature | An external reviewer or maintainer-controlled signing identity | Manual assessment and checksums exist. Neither is an independent audit or publisher signature. No private signing key is generated or borrowed. |

These are limits on release claims, not tests that another fixture or green CI
can turn into real-account, real-OS or independent-review evidence.

## Deliberate, guarded feature limits

- Original-history deletion, native transcript migration/restore and remote sync
  are unavailable. Hub-only removal and encrypted metadata file exchange work.
  Enabling the unavailable operations would require separately reviewed provider
  APIs, backup/recovery, explicit consent and end-to-end testing. They are not
  necessary for local browsing and are not described as implemented sync.
- Live ownership uses the tested Codex native lock and conservative image/Node
  checks for other CLIs. Uncertainty disables continuation; unrelated live
  processes can over-block. No universal mixed/custom-build ownership claim.
- Gemini 0.49 duplicate native IDs fail closed. Whole-conversation projection is
  bounded at 2 MiB / 10,000 messages; raising the limit without complete replay
  would risk stale content. Ambiguous Codex forks/gaps and oversized/compressed
  budgets report incomplete Usage. They are not silently estimated.
- Usage is **recorded local usage**, with explicit coverage and API-equivalent
  known cost. It is not an account bill or live quota dashboard. Unknown prices
  remain unknown. Numeric cache guards do not audit arbitrary middle-of-file
  edits combined with growth; clear/refresh is the documented full reread.
- Community semantic colors are respected; deliberately inaccessible palettes
  cannot be guaranteed accessible. Representative real GUI combinations passed;
  exhaustive permutations are not a finite release test.

## Release decision

There is no known failing regression in the recorded supported scope. Broad
claims of all-agent support, enterprise isolation, unlimited transcript coverage
or independent certification remain unjustified. Keep `releaseReady=false`
until native desktop acceptance for the requested macOS/Linux scope is recorded.
The user confirmed no additional desktops are currently available.
Do not remove safeguards or enable destructive/sync behavior to make a checklist
look complete. A production install is not needed to make that decision.
