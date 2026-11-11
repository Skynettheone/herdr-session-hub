import { View } from "gpui-kit";
import { InputState } from "gpui-base";
import { appHome, readTextFile, exec, run, theme, focused, spaces, nextCommand, pickFolder } from "herdr";
import { safeText, requestFor, launchArgs } from "./model.js";
import { renderPanel } from "./ui.js";

export default class SessionHub extends View {
  init(_props, cx) {
    this.query = ""; this.provider = "all"; this.profile = "";
    this.archived = false; this.removed = false; this.fullText = false; this.oldest = false;
    this.offset = 0; this.scanning = false; this.data = { rows: [], total: 0, profiles: [], statuses: [] };
    this.collapsed = {}; this.busy = false; this.error = ""; this.notice = "";
    this.detail = null; this.preview = null; this.settings = false; this.runtime = null;
    this.portable = null;
    this.loading = true; this.width = 380; this.settingsSection = "profiles"; this.detailSection = "conversation";
    this.generation = 0; this.handle = cx.focus_handle();
    this.previewGeneration = 0; this.reloadPending = false;
    this.search = InputState.new({ placeholder: "Search titles, projects, IDs…" });
    this.alias = InputState.new({ placeholder: "Display alias (Hub only)" });
    this.projectConfirm = InputState.new({ placeholder: "Type the exact project path to trust" });
    this.profileEditor = InputState.new({ placeholder: "Paste a profile JSON object" });
    this.bundlePath = InputState.new({ placeholder: "Absolute encrypted bundle file (.hsh)" });
    this.formProvider = "claude"; this.profileDraft = {}; this.detected = null;
    this.formFields = {};
    for (const [name, placeholder] of Object.entries({ id: "personal-claude", label: "Personal Claude",
      root: "Absolute session directory", configHome: "Provider config home (account directory)",
      executable: "Absolute CLI .exe", launchScript: "Pi launcher script (optional)" })) {
      this.formFields[name] = InputState.new({ placeholder });
    }
    for (const input of [this.search, this.alias, this.projectConfirm, this.profileEditor, this.bundlePath, ...Object.values(this.formFields)]) {
      input.on("focus",(_event,cx)=>{this.activeInput=input;cx.notify();});
      input.on("blur",(_event,cx)=>{if(this.activeInput===input)this.activeInput=null;cx.notify();});
    }
    this.search.on("change", (_event, cx) => {
      this.query = this.search.value(); this.offset = 0;
      const generation = ++this.generation;
      cx.timer.after(250, (cx) => { if (generation === this.generation) this.load(cx); });
    });
    this.search.on("submit", (_event, cx) => this.load(cx));
    this.search.on("focus",(_event,cx)=>{this.searchFocused=true;cx.notify();});
    this.search.on("blur",(_event,cx)=>{this.searchFocused=false;cx.notify();});
    cx.spawn(async (cx) => {
      try {
        const text = await readTextFile(appHome() + "/mods/session-hub/runtime.json");
        if (!text) throw new Error("Run the setup script to configure the local helper. No histories have been scanned.");
        const runtime = JSON.parse(text);
        if (runtime.schema !== 1 || !runtime.python || !runtime.helper || !runtime.state) throw new Error("Unsupported helper configuration");
        this.runtime = runtime;
        const version = await exec(runtime.herdr || "herdr-app", ["--version"], { timeout: 8000 });
        this.launchCompatible = version.code === 0 && version.stdout.trim() === "herdr-app 0.1.15";
        if (!this.launchCompatible) this.notice = "Herdr version is outside the tested SDK. History browsing is available; resume is disabled pending compatibility review.";
        const result = await this.rpc({ action: "list" });
        this.data = result;
      } catch (error) { this.error = safeText(error.message); }
      this.loading = false; cx.notify();
    });
    cx.spawn(async (cx) => {
      for (;;) {
        const command = await nextCommand();
        if (command.name === "focus" || command === "focus") this.search.focus();
        cx.notify();
      }
    });
  }

  async rpc(request) {
    if (!this.runtime) throw new Error("The local helper is not configured");
    const result = await exec(this.runtime.python, ["-I", this.runtime.helper, "--state", this.runtime.state,
      "rpc", JSON.stringify(request)], { timeout: 60000, cwd: this.runtime.base });
    let response;
    try { response = JSON.parse(result.stdout); }
    catch (_) { throw new Error("The helper returned invalid output; check its configured Python version"); }
    if (!response.ok) throw new Error(response.error || "Local operation failed");
    if (result.code !== 0) throw new Error("The helper exited with an error");
    return response.result;
  }

  perform(cx, request, then) {
    if (this.busy) return;
    this.busy = true; this.error = ""; cx.notify();
    cx.spawn(async (cx) => {
      try {
        const result = await this.rpc(request);
        if (then) await then(result, cx);
        const snapshot = request.action === "list" ? request : requestFor(this);
        const data = request.action === "list" ? result : await this.rpc(snapshot);
        this.publishList(data, snapshot);
      } catch (error) { this.error = safeText(error.message, 500); }
      finally {
        this.finishOperation(cx);
      }
    });
  }

  load(cx) {
    if (this.busy) { this.reloadPending = true; return; }
    this.perform(cx, requestFor(this));
  }
  publishList(data, snapshot) {
    if (JSON.stringify(snapshot) !== JSON.stringify(requestFor(this))) {
      this.reloadPending = true;
      return;
    }
    this.data = data;
    this.reloadPending = false;
    if (this.detail) this.detail = data.rows.find(row => row.key === this.detail.key) || null;
  }
  finishOperation(cx) {
    this.busy = false;
    this.scanning = false;
    if (this.reloadPending) { this.reloadPending = false; this.load(cx); }
    cx.notify();
  }
  refresh(cx, content = false) {
    if (this.busy) return;
    this.busy = true; this.scanning = true; this.scanCancelled = false; this.error = "";
    this.notice = content ? "Indexing a bounded pass through opted-in profiles." : "Scanning approved roots; original histories stay read-only.";
    cx.notify();
    cx.spawn(async (cx) => {
      try {
        let remaining = 0, batches = 0;
        do {
          const result = await this.rpc({ action: "refresh", content });
          const snapshot = requestFor(this);
          this.publishList(await this.rpc(snapshot), snapshot);
          remaining = Math.max(0, ...result.statuses.map(s => s.remaining || 0));
          this.notice = "Batch " + (++batches) + " · " + remaining + " sources remaining" + (content ? ". Huge histories may need another index pass." : "");
          cx.notify();
        } while (remaining > 0 && !this.scanCancelled && batches < 2000);
        if (this.scanCancelled) this.notice = "Stopped after the current batch; indexed results are preserved.";
      } catch (error) { this.error = safeText(error.message, 500); }
      finally { this.finishOperation(cx); }
    });
  }
  choose(row, cx) {
    this.detail = row; this.detailSection = "conversation"; this.preview = null; this.target = row.targets.length === 1 ? row.targets[0] : "";
    this.alias.set_value(row.alias || ""); this.projectConfirm.set_value(""); cx.notify();
    this.loadPreview(row,cx);
  }
  loadPreview(row,cx) {
    const generation = ++this.previewGeneration;
    const current = () => this.detail?.key === row.key && generation === this.previewGeneration;
    this.previewLoading = true; this.previewError = ""; cx.notify();
    cx.spawn(async cx=>{
      try { const result=await this.rpc({action:"preview",key:row.key}); if(current())this.preview=result; }
      catch(error){if(current())this.previewError=safeText(error.message,400);}
      finally {if(current())this.previewLoading=false;cx.notify();}
    });
  }
  annotate(cx, patch) { this.perform(cx, { action: "annotate", key: this.detail.key, ...patch }); }
  editProfile(profile, cx) {
    this.profileDraft = { ...profile }; this.formProvider = profile.provider; this.formOpen = true;
    for (const [name, field] of Object.entries(this.formFields)) field.set_value(name === "root" ? profile.roots?.[0] || "" : profile[name] || "");
    this.profileEditor.set_value(JSON.stringify(profile)); cx.notify();
  }
  saveProfile(cx) {
    const value = name => this.formFields[name].value().trim();
    const p = { ...this.profileDraft, provider: this.formProvider, id: value("id"), label: value("label"),
      roots: [value("root"), ...(this.profileDraft.roots || []).slice(1)], configHome: value("configHome"), executable: value("executable"),
      launchScript: value("launchScript") || undefined, content: !!this.profileDraft.content, enabled: this.profileDraft.enabled !== false };
    // Directory mappings are derived by the helper, never silently inherited from an edited provider.
    delete p.env;
    this.perform(cx, { action: "profile-save", profile: p }, () => { this.notice = "Profile saved. Check its CLI version, then refresh."; });
  }
  chooseFolder(cx, field) {
    cx.spawn(async cx => {
      try { const folder = await pickFolder({ prompt: "Use this explicit profile folder" }); if (folder) this.formFields[field].set_value(folder); }
      catch (_) { this.error = "Folder selection failed"; }
      cx.notify();
    });
  }
  portableTerminal(cx, action, apply = false) {
    const space = spaces().find(s => s.id === focused()?.space && !s.machine);
    const path = this.bundlePath.value().trim();
    if (!space || !this.launchCompatible || !path) { this.error = "Choose a local Herdr space and an absolute bundle file path"; cx.notify(); return; }
    run("tab.new", { space: space.id, name: "Session Hub metadata " + action, folder: this.runtime.base,
      argv: [this.runtime.python, "-I", this.runtime.helper, "--state", this.runtime.state, action, path, ...(apply ? ["--apply"] : [])] });
    this.notice = "An offline metadata terminal was requested. Enter the passphrase there; no transcripts are exported."; cx.notify();
  }
  resume(cx) {
    if (!this.launchCompatible) { this.error = "Resume requires the tested Herdr 0.1.15 SDK"; cx.notify(); return; }
    const row = this.detail;
    const space = spaces().find(s => s.id === focused()?.space && !s.machine);
    if (!space) { this.error = "Select a local Herdr space before resuming"; cx.notify(); return; }
    this.perform(cx, { action: "resume", key: row.key, profile: this.target }, (spec) => {
      run("tab.new", launchArgs(spec, row, space.id));
      this.notice = "Native resume requested — continuity is unverified. Check the session ID and previous context in the agent.";
    });
  }
  key(event, cx) {
    if (event.key === "escape") { this.detail = null; this.settings = false; cx.notify(); }
    if (event.key === "f5") { this.refresh(cx); cx.stop_propagation(); }
    if ((event.key === "f" && event.modifiers?.control) || (event.key === "/" && !this.activeInput)) {
      this.search.focus(); cx.stop_propagation();
    }
    if (!this.activeInput && !this.detail && ["up", "down"].includes(event.key)) {
      const delta = event.key === "up" ? -1 : 1;
      this.selected = Math.max(0, Math.min(this.data.rows.length - 1, (this.selected ?? -1) + delta));
      cx.notify(); cx.stop_propagation();
    }
    if (!this.activeInput && event.key === "enter" && !this.detail && this.data.rows[this.selected]) this.choose(this.data.rows[this.selected], cx);
  }

  render(cx) { return renderPanel(this, cx, theme()); }
}
