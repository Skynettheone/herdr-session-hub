# Native layout and theme contract

The Dock header action creates a 380px native sidebar in a new personal layout
copy, preserving the full existing tree and original files. Repeated Dock reveals
an existing Hub, including hidden ancestor stacks. `mod.open` alone is a 440px
dialog; installation uses `place=none`. Actual sidebar/update/rollback captures
and acceptance are in NATIVE_ACCEPTANCE.md.

The UI follows Herdr's native panel vocabulary: a compact header, semantic
surfaces and borders, retained native text fields, focusable native buttons,
small provider/profile controls and a scrollable history list. There is no web
view, CSS/DOM, external UI framework or fixed light/dark color palette.

- At 760 logical pixels and above, a 340-pixel history column sits beside the
  conversation detail. Below that width, selecting a row opens detail in place
  with a persistent Back control. Pagination and source status stay out of the
  conversation scroll region.
- Session rows prioritize the title, provider/profile and compact recency. Project
  headings use the final folder name; complete source paths stay in Details.
- Selection loads a bounded read-only preview asynchronously. Slow/error results
  are scoped to the selected conversation, so a previous response cannot replace
  another conversation's preview.
- Conversation, Details and Organize separate reading from technical metadata
  and metadata edits. The native continuation action stays at the bottom with
  relevant profile/version/project-trust guidance.
- Settings separates Profiles, Agents, Search and Portability. Profile setup is guided;
  advanced JSON is disclosed explicitly rather than being the primary workflow.
  Secondary list filters and diagnostics are disclosed on demand.

`theme()` is read on every render. `semanticTheme()` resolves missing aliases
through other Herdr tokens; it does not guess a palette from brightness. Text,
backgrounds, hover/selection, borders, warning colors and primary button text all
come from that active semantic theme. Navigation icons use native tinted SVGs. Agent icons use Herdr
`Program.tint` to choose a themed mask or original full-color image. Font family is
inherited from Herdr. Valid community themes get the same semantic projection as
Herdr's built-in panels; controls retain semantic colors while original full-color brand artwork is
preserved, matching Herdr's own agent menu.

Unit/host-mock checks cover dark, light and partial community token maps,
responsive navigation and state isolation. The renewed native pass covered dark,
paper and custom community-format themes, including a 420px pane and a separate
wide pane. Exhaustive control coverage remains a release gate.
No claim of universal contrast for malformed or intentionally low-contrast user
palettes is made; the mod respects the colors Herdr resolves for that theme.

## Renewed native visual checks — 2026-11-12

The visible isolated window confirmed real provider chips/icons, debounced search,
conversation preview, settings navigation and live catalog cards. Native testing
found and fixed the detail column's cross-axis height and a line-height value
interpreted as an 18× multiplier; transcript lines now use `18px`. Scroll cards
retain their intrinsic height. Continue is disabled until profile/version/trust
and SDK prerequisites hold.

`preview.png` is now a real populated dark-theme capture. `screenshots/light.png`
and `screenshots/community.png` are real isolated native renders, using paper and
a custom community-format fixture derived from the installed Atom One Dark
format. They are evidence of tested themes, not a claim that every community
palette has accessible contrast. No user histories appear in them.
