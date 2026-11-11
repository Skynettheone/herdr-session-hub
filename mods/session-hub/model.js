// Pure panel state helpers; native host calls stay in the View instance.
export const providers = ["all", "claude", "codex", "opencode", "pi"];
export function safeText(value, limit = 300) {
  return String(value ?? "").replace(/[\u0000-\u0008\u000b-\u001f\u007f\u200b-\u200f\u202a-\u202e\u2066-\u2069]/g, "").slice(0, limit);
}
export function groupRows(rows, collapsed = {}) {
  const groups = new Map();
  for (const row of rows) {
    const key = row.cwd || "Unknown project";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  return [...groups].map(([path, rows]) => ({ path, rows, collapsed: !!collapsed[path] }));
}
export function requestFor(state) {
  return { action: "list", query: state.query, provider: state.provider,
    profile: state.profile, archived: state.archived, removed: state.removed,
    fullText: state.fullText, oldest: state.oldest, offset: state.offset };
}
export function canPage(offset, total) { return { previous: offset > 0, next: offset + 60 < total }; }
export function semanticTheme(raw) {
  // Resolve only through Herdr semantics. Never inject a light/dark palette over
  // a community theme; Herdr supplies the complete resolved theme at render time.
  return { ...raw, chrome: raw.chrome || raw.surface || raw.background,
    surface: raw.surface || raw.background, raised: raw.raised || raw.surface,
    hover: raw.hover || raw.selected || raw.surface, selected: raw.selected || raw.selection || raw.hover,
    muted: raw.muted || raw.foreground, dim: raw.dim || raw.muted || raw.foreground,
    border: raw.border || raw.input || raw.surface, input: raw.input || raw.border,
    accent: raw.accent || raw.solid || raw.foreground,
    solid: raw.solid || raw.accent, solid_foreground: raw.solid_foreground || raw.accent_foreground || raw.background,
    blocked: raw.blocked || raw.ansi3 || raw.foreground, idle: raw.idle || raw.muted || raw.foreground };
}
export const providerName = p => ({claude:"Claude Code",codex:"Codex",opencode:"OpenCode",pi:"Pi"}[p] || p);
export const projectName = path => path ? path.split(/[\\/]/).filter(Boolean).at(-1) || path : "Unknown project";
export function shortTime(value, now = Date.now()) {
  if (!value) return "Time unknown";
  const time = new Date(value).getTime();
  if (!Number.isFinite(time)) return "Time unknown";
  const days = Math.floor((now - time) / 86400000);
  if (days < 0) return value.slice(0, 10);
  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days}d ago`;
  return `${["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][new Date(time).getMonth()]} ${new Date(time).getDate()}`;
}
export function launchArgs(spec, record, space) {
  if (!spec || !Array.isArray(spec.argv) || !spec.argv.length || !spec.folder || !space || space.includes("/")) {
    throw new Error("Select a local Herdr space and a valid launch target");
  }
  return { name: safeText(record.title || "Session", 60), folder: spec.folder, argv: spec.argv, space };
}
