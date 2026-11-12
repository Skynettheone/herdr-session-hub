# Usage in the History panel

Research checkpoint: 2026-11-12. This is an additive feature, not a claim that
the existing release candidate already includes usage verification.

## Confirmed sources and boundaries

T3 Code was studied at MIT-licensed commit
`3c6864235487147fd5667786152f400a75251fca`. The implementation here is independent
Python and native GPUI; no React chart or server implementation is copied.

- [User-facing semantics](https://github.com/pingdotgg/t3code/blob/3c6864235487147fd5667786152f400a75251fca/docs/user/usage.md)
- [Transcript reader](https://github.com/pingdotgg/t3code/blob/3c6864235487147fd5667786152f400a75251fca/apps/server/src/usage/usageTranscriptReader.ts)
- [Deduplication and aggregation](https://github.com/pingdotgg/t3code/blob/3c6864235487147fd5667786152f400a75251fca/apps/server/src/usage/usageAggregation.ts)
- [Codex accounting](https://github.com/pingdotgg/t3code/blob/3c6864235487147fd5667786152f400a75251fca/apps/server/src/provider/Drivers/codexUsage.ts)
- [Claude accounting](https://github.com/pingdotgg/t3code/blob/3c6864235487147fd5667786152f400a75251fca/apps/server/src/provider/Drivers/claudeUsage.ts)
- [Pi accounting](https://github.com/pingdotgg/t3code/blob/3c6864235487147fd5667786152f400a75251fca/packages/provider-pi/src/server/usage.ts)
- [OpenCode accounting](https://github.com/pingdotgg/t3code/blob/3c6864235487147fd5667786152f400a75251fca/packages/provider-opencode/src/server/usage.ts)
- [Chart reference](https://github.com/pingdotgg/t3code/blob/3c6864235487147fd5667786152f400a75251fca/apps/web/src/components/usage/UsageProviderChart.tsx)

Installed baseline: Herdr GUI 0.1.15/core 0.1.20, Claude 2.1.322, Codex 0.164.0,
Pi 1.1.0, OpenCode 1.3.17, Gemini 0.49.0; Python 3.14.3. Copilot's installed
shim is not a working CLI. Native drawing uses the installed `PathBuilder` and
`window.paint_path` SDK, not a browser, generated screenshot or web chart.

Token channels are disjoint. Claude/Pi supply uncached input, output, cache read
and cache write. Codex input includes cache, and output includes reasoning.
OpenCode output excludes reasoning. Gemini input includes cached input and its
candidate output excludes thoughts. Unknown or inconsistent records must be
reported as incomplete, not silently estimated. Copilot `assistant.usage` is
explicitly ephemeral in the verified SDK; ordinary persisted history cannot
provide its usage and must show unavailable.

API-equivalent cost is not a subscription bill. Positive provider-reported USD
costs may be used. Otherwise exact provider/model local rates supplied by the
user price the four token channels per million; unknown pricing remains unknown.
No remote pricing fetch, credential reading, account probing or fabricated quota.
Codex rate-limit snapshots, when present in local history, are labeled recorded
with their timestamp. They are not live account limits. Other limits are unavailable.

## Implementation and acceptance plan

History / Usage switches retain independent filters in the same native panel.
Usage adapts from a narrow side panel to a wide dashboard, follows semantic theme
tokens, and provides accessible numeric values alongside native graphs.
Periods: 24 hours, 7/30/90 days and a validated custom range. Buckets and custom
dates use explicitly labeled UTC. Views: tokens, estimated cost and recorded limits.
Breakdowns: model, day and project; session averages optionally trim 10% at each end.

Only enabled, explicitly configured profile roots are read. Shared physical files
and stable billed event IDs are deduplicated before date filtering. No content
search opt-in is changed. Numeric/model/time-only cache data is encrypted in Hub's
DPAPI store, excluded from portable metadata. Reads, events, source count and
refresh work are bounded. Append guards detect rewrites; partial lines, malformed
histories, compressed replay limits and concurrent writers remain visible in
coverage. Interrupted refreshes retain committed work and can continue.

Codex cumulative counters must not be summed as individual requests. Repeated
snapshots are skipped; a first or restarted counter uses only an attributable
last request. Ambiguous gaps and fork inheritance are excluded with coverage
warnings. This conservative boundary is preferable to inflated totals.

Required gates: adversarial parser/accounting fixtures, incremental and encrypted
state integration tests, host UI behavior tests, installed SDK check, disposable
native GUI interaction/graph checks, manual security review, essential CI and
freshly extracted package verification. Production installation and publication
remain separate approval gates.
