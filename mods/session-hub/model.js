// Pure panel state helpers; native host calls stay in the View instance.
export const providers = ["all", "claude", "codex", "opencode", "pi", "copilot", "gemini"];
export function sessionProfiles(row, profiles) {
  const targets = row.targets.map(id => ({id, label: safeText(profiles.find(p => p.id === id)?.label || id, 80).trim()}));
  const normalize = value => value.trim().toLowerCase();
  if (targets.length === 1 && [row.provider, providerName(row.provider)].some(name => normalize(name) === normalize(targets[0].label))) return [];
  return targets.map(target => ({...target, label: targets.filter(p => normalize(p.label) === normalize(target.label)).length > 1 ? `${target.label} (${target.id})` : target.label}));
}
export function sidebarLayout(value) {
  let original = JSON.parse(JSON.stringify(value));
  if (!original || typeof original !== "object" || !original.id || !original.type) throw new Error("Herdr did not return a valid layout");
  // Upgrade only the exact wrapper created by older Hub builds, in a NEW copy.
  if(original.id.startsWith("session-hub-layout") && original.children?.length===2 &&
     original.children[0].id?.startsWith("session-hub-sidebar") && original.children[0].content?.mod==="session-hub") {
    const wrapper=original;original=wrapper.children[1];
    for(const [key,value] of Object.entries(wrapper))if(!["id","type","children"].includes(key))original[key]=value;
  }
  const nodes = [];
  let existingRoute;
  const visit = (node, parents=[]) => {
    nodes.push(node);
    const route=[...parents,node];
    if(!existingRoute&&node.content?.mod==="session-hub"&&node.content?.props?.role!=="tabs")existingRoute=route;
    for (const child of node.children || []) visit(child,route);
  };
  visit(original);
  const tabs=nodes.find(node=>node.id==="tabs"&&(node.content?.mod==="tabs"||(node.content?.mod==="session-hub"&&node.content?.props?.role==="tabs")));
  const body=nodes.find(node=>node.id==="panel-body"&&node.type==="stack");
  const panel=nodes.find(node=>node.id==="panel"&&node.children?.includes(body));
  if (existingRoute && (!body?.children?.includes(existingRoute.at(-1)) || tabs?.content?.props?.role==="tabs")) {
    const reveal=[];
    for(let i=0;i<existingRoute.length;i++) {
      const node=existingRoute[i];reveal.push({name:"layout.show",args:{id:node.id}});
      if(node.type==="stack"&&existingRoute[i+1])reveal.push({name:"layout.select",args:{stack:node.id,child:existingRoute[i+1].id}});
    }
    return {existing:existingRoute.at(-1).id,reveal};
  }
  const ids = new Set(nodes.map(node => node.id));
  const unique = base => { let key=base, n=1; while(ids.has(key))key=base+"-"+(n++); ids.add(key); return key; };
  if(!tabs||!body||!panel)throw new Error("This layout has no standard Files/Changes area. Open History as a dialog or use a compatible personal layout.");
  const history=existingRoute?.at(-1)||{id:unique("session-hub-history"),type:"block",content:{mod:"session-hub",props:{panel:panel.id}}};
  if(!existingRoute)body.children.push(history);
  history.content.props={...history.content.props,panel:panel.id};
  tabs.content={mod:"session-hub",props:{...tabs.content?.props,role:"tabs"}};
  panel.hidden=false;body.active=history.id;
  return {layout:original};
}
export function agentCatalog(native = []) {
  const catalog = new Map(native.filter(p => p?.key && Array.isArray(p.run)).map(p => [p.key, { ...p,
    history: providers.includes(p.key), name: safeText(p.name || providerName(p.key), 60) }]));
  for (const key of providers.slice(1)) if (!catalog.has(key)) catalog.set(key, {key, name:providerName(key), installed:false, history:true});
  return [...catalog.values()];
}
export function historyCapability(agent) {
  if (!agent.history) return "History unavailable: no verified offline adapter. Herdr can still start this agent.";
  if (agent.key === "copilot") return "Local history supported. Native continuation is disabled until a real CLI is verified.";
  if (agent.key === "gemini") return "Local history supported within the replay budget. Original project requires an explicit matching path.";
  return "Local history supported. Native continuation requires a verified profile and trusted project.";
}
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
export const providerName = p => ({claude:"Claude Code",codex:"Codex",opencode:"OpenCode",pi:"Pi",copilot:"Copilot",gemini:"Gemini",cursor:"Cursor",amp:"Amp"}[p] || p);
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
