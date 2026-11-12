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

Settings → Search is staged with all profiles Off. The user was asked to enable
only Personal test, the synthetic Pi profile. Index/search/clear/off results will
be recorded after that step is observed; they are not inferred from a request.
The computer-use skill prohibits automated in-app privacy-setting changes.

## Automated and review evidence

Twelve native-host test groups pass, including required-field validation without
writes, cancelled drafts, provider-switch state clearing, ID collision/retarget
refusal, original-name reset and duplicate-profile-label disambiguation. Installed
native SDK check and correctness lint passed. Hosted Windows CI on df50a84 passed;
combined CodeQL on the same commit also passed.

Review of the change confirms filesystem/account validation remains in the helper;
UI validation does not replace it. There is no new runtime dependency, shell,
network client, credential access, original-history write or production install.
Native SDK checks and GUI runs use separate isolated app homes. Tests avoid GUI
actions while the SDK checker is running under the same executable basename.
