# Follow-up acceptance — 2026-11-12

Scope: collapsible History beside Files/Changes, Gemini continuation, real-account
profile routing, native GUI checks, manual security assessment and final packaging.
All app/core/config/state targets are disposable repository-local directories.
The production configuration and existing provider histories were not test targets.

## Native panel

The actual Herdr GUI created a new `session-hub-workspace-2` personal layout from
the previous Hub layout. Its generated left-hand wrapper was removed only in
that new copy. One History view now shares the native right-hand Files/Changes
stack. The shipped tabs mod, previous layout, settings and keys remain untouched.

Observed in the native GUI: Dock creates/selects the new copy; History's header
chip collapses and reopens the same view; its own collapse button hides the panel;
Files and Changes still select their original native panels; returning to History
retains the loaded conversations. Host tests additionally prove repeat docking
does not duplicate History, nested hidden panes are revealed, custom unsupported
layouts fail clearly, and the header role never starts another index/scan.

`tabs.js` is an Apache-2.0 adapter of the exact pinned native header, not a
replacement of the shipped mod. The untouched installed header matches
`b22936225403f38f0e6f38dd2f2fe4b444a85988/defaults/mods/tabs/main.js` byte-for-byte
after newline normalization: SHA-256
`d1368ee4c1dd588adca3c20e015f8bf41c7e99e4b9591c910cc4aba14c90fe26`.
License/provenance are retained in THIRD_PARTY_NOTICES.md and the adapter header.

## Gemini 0.49.0

The native CLI created a disposable session against a loopback Gemini-protocol
fixture. A headless `--session-file` experiment restored context but imported it
under a new UUID. Hub now uses **`--resume <native UUID>`**. Native transport
`<session_context>` setup blocks are omitted from preview/title/search.

The real Hub button opened Gemini in the original Unicode/space-containing cwd
with the selected profile. A new `VERIFY_CONTEXT` prompt returned `CONTINUITY_OK`
only when prior native history contained the earlier synthetic nonce. The
original UUID, cwd and normal helper wrapper were verified; live ownership was
detected. No injected active-probe bypass was used. This is native continuity
with a local model fixture, not a Google cloud-account authentication test.

Known native limitation: 0.49 left four files with the same UUID after the test
resumes. A separate unfiltered scan verified Hub rejects all ambiguous copies.
Hub does not guess a winning source, delete originals or silently import/fork.
The single-source continuation test had an explicit narrow/exclusion profile;
duplicate refusal is a tested fallback, not universal repeated-resume acceptance.
An initial headless create returned a Windows libuv assertion after producing
its response/history. Subsequent headless and interactive continuation succeeded.
No automatic provider update was performed.

## Available real-account coverage

The user performed native Claude sign-ins in two separate disposable config homes.
Only native auth-status metadata was inspected; raw identities and credentials
were not logged or committed. Both profiles are authenticated with the **same**
identity; the user confirmed no separate company account is available.

Each profile created its own native conversation through the real cloud service,
with tools disabled and a distinct synthetic marker. Both responses matched their
own marker. The personal profile is also authenticated under the exact GUI base
environment. An unsigned third profile reported not logged in, proving the tested
configuration does not fall back to the signed-in stores. Hub never reads/copies
auth files. Separate company-identity isolation cannot be claimed with this account.

The interactive real-account Hub launch reached Claude's ordinary first-launch
security notice. Automated acknowledgement was rejected; the user completed it
manually. A fresh cloud prompt containing no marker then returned the personal
conversation's original marker. The normal helper wrapper, original cwd and native
ID were retained, and the second profile's marker was absent. Only redacted
booleans were retained in evidence. The completed test tab was closed. No bypass,
credential inspection, real conversation export or logout/revocation was performed.

## GUI coverage boundary

The earlier form gaps below are superseded by FORM_ACCEPTANCE.md: native alias
save/reset, guided field typing/save, required-field guidance, malformed JSON,
picker opening/cancellation and Cancel have now passed after the usability fixes.
The subsequent suite has twelve host groups. Privacy controls remain user-owned.


Existing native evidence covers search/debounce, provider filtering, previews,
settings/catalog, dark/light/community-format themes, a narrow pane and multiple
views. This follow-up adds the actual header/stack integration and Gemini launch.
Eleven host test groups exercise the remaining controller paths: profile forms and
invalid JSON, aliases, archive/removal/restore, copy actions, indexing, encrypted
metadata terminal requests, errors, async races and isolated pane state.

The follow-up native pass also exercised approved removal → Include removed →
restore, archive → Archived view → unarchive, Details scrolling, copy-ID and
copy-project feedback, notice dismissal, and the profile edit form at a 300px
panel width. The synthetic Pi row ended with archived=false and removed=false;
its original SHA-256 was unchanged. Native status ended with errors=[].

The automation provider returned stale/unavailable accessibility indexes and did
not establish reliable text-input focus in scrolled forms. A folder-picker
attempt changed only an unsaved content-consent draft; Save was never pressed,
and a direct Hub read confirmed persisted Pi content=false. Form typing,
alias save/reset, picker cancellation and native invalid-JSON submission are
therefore **not marked passed**. Controller/backend regressions cover these
paths, but a human native form pass remains required before release. No privacy
or authentication barrier was bypassed. Final genuine captures show the History
tab and its collapsed state without real account information.

Host tests are not substitutes for every native click. Native security/privacy
controls and deletion actions require user handling/confirmation; no claim of
exhaustive interaction in every possible theme, host state or authentication flow
is made. Exact remaining native actions are recorded alongside final results.

## Manual security assessment

The user declined Daybreak and requested manual review. Findings and regression
evidence are in SECURITY_REVIEW.md. This is an implementer-led manual assessment,
not an independent human audit. The public OSV query sent only the three locked
PyPI package names/versions, not code or user data; all three returned no listed
advisories at query time. This is a point-in-time result, not a vulnerability-free
guarantee. Existing essential CodeQL CI remains separate from the manual review.
