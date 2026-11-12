# Native form acceptance — 2026-11-12

Scope: the remaining form gaps from FOLLOWUP_ACCEPTANCE.md, plus the user's
reported duplicate Pi labels. Actual Herdr 0.1.15, repository-local acceptance
app/core/home only. No provider login or production config is needed for this pass.

## Usability fixes

- Add/Edit opens a dedicated form instead of appending it after every profile.
- Save/Cancel remain visible while the fields scroll; Escape cancels the draft.
- Guided fields and Advanced JSON are separate views with one save action each.
  JSON has a multiline editor, formatted existing values and explicit guidance.
- Required ID/history/config fields validate before RPC; errors preserve drafts.
- A new draft cannot overwrite another saved profile. Existing IDs/providers
  are fixed. Switching agents clears stale account folders/commands/consent.
- Clicking the input frame explicitly focuses the retained native input state.
- Use original name clears only the Hub alias, with explanatory text.
- A single profile labelled the same as its provider is omitted from list/detail
  decoration. Meaningful profile names remain visible. Multiple targets remain
  selectable; duplicate labels include IDs to distinguish the targets.
- Conversation/Details/Organize use consistent adjacent text tabs. Organize no
  longer looks like an overflow menu or toggles back to Conversation on re-click.

## Observed native checks

| Control / flow | Result |
|---|---|
| Alias text input, Ctrl+A replacement and Save name | Passed; new name appeared and persisted in Hub metadata |
| Use original name | Passed; alias became empty without editing the source |
| Add profile | Passed; dedicated editor, no long profile list above it |
| Save empty guided form | Passed; specific ID validation, no profile created |
| Advanced JSON multiline typing | Passed; entered a synthetic malformed object |
| Save malformed JSON | Passed; visible invalid-JSON error, draft retained |
| Return to guided setup | Passed; normal fields returned, error cleared |
| Choose history folder | Passed; actual Windows folder picker appeared |
| Cancel folder picker with Escape | Passed; no path selected, no error, draft remained |
| Cancel unsaved new profile | Passed; returned to list without adding a profile |
| Edit synthetic Pi profile and save a new display label | Passed; label persisted, indexing stayed off, command verification retained |
| Provider/profile name rendering | List observed without repeated Pi; distinct Personal test label retained |

The synthetic Pi original's SHA-256 stayed unchanged after alias save/reset.
Its temporary profile label is Personal test, so the privacy test cannot be
confused with either real-account profile. No credential files were inspected.

## User-controlled privacy check

The user enabled only Personal test, the synthetic Pi profile. Both the native
screen and persisted flags confirmed the six other profiles remained Off. The
native Index conversations button processed 13,579 bytes with complete Pi
coverage; all other providers had zero indexed bytes. A body-only synthetic marker
returned zero metadata matches and one full-text match, in both the helper and
actual GUI. No real-account conversation text was indexed. Search-padding click
followed by typing also passed after the focused d0b19d5 fix. The user then cleared the test index and switched Personal test Off. A fresh
helper read verified all seven profiles Off, zero indexed rows and zero marker
matches. Original and preserved native-file hashes were unchanged; native status
reported errors=[]. The final screenshot attempt was interrupted by the user's
physical Escape key, so no post-cleanup screenshot is claimed. Cleanup verification
uses the persisted flags/index result, not an inferred click. The disposable app
and its dedicated core were subsequently stopped through exact-scoped CLI calls.
The computer-use skill prohibits automated in-app privacy-setting changes.

## Automated and review evidence

Twelve native-host test groups pass, including required-field validation without
writes, cancelled drafts, provider-switch state clearing, ID collision/retarget
refusal, original-name reset and duplicate-profile-label disambiguation. Installed
native SDK check and correctness lint passed. Hosted Windows CI and combined CodeQL on final code d0b19d5 both passed.

Review of the change confirms filesystem/account validation remains in the helper;
UI validation does not replace it. There is no new runtime dependency, shell,
network client, credential access, original-history write or production install.
Native SDK checks and GUI runs use separate isolated app homes. Tests avoid GUI
actions while the SDK checker is running under the same executable basename.
