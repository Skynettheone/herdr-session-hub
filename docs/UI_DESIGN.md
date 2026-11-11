# Native layout and theme contract

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
- Settings separates Profiles, Search and Portability. Profile setup is guided;
  advanced JSON is disclosed explicitly rather than being the primary workflow.
  Secondary list filters and diagnostics are disclosed on demand.

`theme()` is read on every render. `semanticTheme()` resolves missing aliases
through other Herdr tokens; it does not guess a palette from brightness. Text,
backgrounds, hover/selection, borders, warning colors and primary button text all
come from that active semantic theme. Icons use native tinted SVGs. Font family is
inherited from Herdr. Valid community themes get the same semantic projection as
Herdr's built-in panels; the mod never paints branded provider colors over them.

Unit/host-mock checks cover dark, light and partial community token maps,
responsive navigation and state isolation. The redesigned initial layout rendered
in the actual installed Herdr GUI. Full interactive community-theme visual review
was interrupted when the user stopped Computer Use and remains a release gate.
No claim of universal contrast for malformed or intentionally low-contrast user
palettes is made; the mod respects the colors Herdr resolves for that theme.
