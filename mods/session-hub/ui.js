import { div, svg } from "gpui-kit";
import { h_flex, v_flex, Button, Input } from "gpui-base";
import { semanticTheme, safeText, groupRows, providers, providerName, projectName, shortTime, canPage } from "./model.js";

export function renderPanel(v, cx, rawTheme) {
  const t = semanticTheme(rawTheme), wide = (v.width || 380) >= 760;
  const text = (value, color = t.foreground, size = 12) => div().min_w(0).text_size(size).text_color(color).child(safeText(value, 4000));
  const icon = (name, color = t.muted, size = 14) => svg("mods/session-hub/icons/" + name + ".svg").w(size).h(size).flex_none().text_color(color);
  const badge = (label, color = t.muted) => text(label, color, 10).px(5).py(2).rounded(4).bg(t.raised);
  const button = (id, label, action, options = {}) => {
    const disabled = !!options.disabled || (v.busy && id !== "cancel-scan");
    const el = Button.new(id).accessibility_label(options.label || label).disabled(disabled).selected(!!options.selected)
      .h(options.height || 28).px(options.iconOnly ? 7 : 9).flex().items_center().justify_center().gap(6).rounded(6).text_size(11.5)
      .text_color(disabled ? t.dim : options.primary ? t.solid_foreground : options.selected ? t.accent : t.foreground)
      .when(!!options.primary, e => e.bg(disabled ? t.raised : t.solid))
      .when(!!options.selected && !options.primary, e => e.bg(t.selected))
      .when(!!options.outline, e => e.border_1().border_color(t.border))
      .when(disabled, e => e.cursor_not_allowed()).when(!disabled, e => e.cursor_pointer().hover(s => s.bg(options.primary ? t.solid : t.hover)))
      .on_click((_event, cx) => { if (!disabled) action(cx); });
    if (options.icon) el.child(icon(options.icon, options.primary ? t.solid_foreground : options.selected ? t.accent : t.muted));
    if (!options.iconOnly) el.child(label);
    return el;
  };
  const input = (state, id) => div().id(id || "field-" + (state === v.search ? "search" : "input")).h(34).flex_none().px(10)
    .flex().items_center().rounded(7).bg(t.surface).border_1().border_color(state === v.search && v.searchFocused ? t.accent : t.input)
    .child(Input.new(state).w_full().text_size(12).text_color(t.foreground));
  const label = value => text(value, t.muted, 11).font_medium();
  const section = (title, description) => v_flex().gap(10).p(14).rounded(9).bg(t.surface).border_1().border_color(t.border)
    .child(text(title, t.foreground, 13).font_semibold()).when(!!description, e => e.child(text(description, t.muted, 11.5)));
  const empty = (title, description, action) => v_flex().items_center().justify_center().gap(10).p(24).flex_1().min_h(150)
    .child(div().p(12).rounded(12).bg(t.surface).child(icon("history", t.muted, 24)))
    .child(text(title, t.foreground, 14).font_semibold()).child(text(description, t.muted).text_center())
    .when(!!action, e => e.child(action));
  const profilesFor = row => row.targets.map(id => v.data.profiles.find(p => p.id === id)?.label || id).join(", ");
  const root = v_flex().id("session-hub-root").track_focus(v.handle).on_key_down((e, cx) => v.key(e, cx))
    .on_size_change((size, cx) => { if (Math.abs((v.width || 0) - size.width) > 1) { v.width = size.width; cx.notify(); } })
    .size_full().min_w(0).min_h(0).rounded(10).overflow_hidden().bg(t.chrome).border_1().border_color(t.border).text_color(t.foreground).text_size(12);
  const back = v.settings || (v.detail && !wide);
  root.child(h_flex().h(46).flex_none().px(12).gap(8).items_center().border_b_1().border_color(t.border)
    .child(back ? button("back", "Back to history", cx => { v.settings = false; v.detail = null; cx.notify(); }, {icon:"back",iconOnly:true}) : icon("history",t.muted,17))
    .child(text(v.settings ? "History settings" : "History",t.foreground,14).font_semibold())
    .when(!v.settings, e => e.child(badge(String(v.data.total))))
    .child(div().flex_1())
    .child(button("refresh", v.busy ? "Working" : "Refresh history", cx => v.refresh(cx), {icon:"refresh",iconOnly:true}))
    .child(button("settings", "History settings", cx => { v.settings = !v.settings; v.detail = null; cx.notify(); }, {icon:"settings",iconOnly:true,selected:v.settings})));
  if (v.error) root.child(h_flex().px(13).py(9).gap(8).items_center().bg(t.surface).border_b_1().border_color(t.border)
    .child(icon("alert",t.blocked)).child(text(v.error,t.blocked,11.5).flex_1())
    .child(button("dismiss-error","Dismiss error",cx=>{v.error="";cx.notify();},{icon:"close",iconOnly:true})));
  if (v.scanning) root.child(h_flex().px(12).py(7).gap(7).items_center().bg(t.surface)
    .child(icon("refresh",t.accent).spin(900)).child(text(v.notice,t.muted,11).flex_1())
    .child(button("cancel-scan","Stop",cx=>{v.scanCancelled=true;cx.notify();})));
  else if (v.notice) root.child(h_flex().px(13).py(7).gap(8).items_center().border_b_1().border_color(t.border)
    .child(text(v.notice,t.muted,11).flex_1()).child(button("dismiss-notice","Dismiss",cx=>{v.notice="";cx.notify();},{icon:"close",iconOnly:true})));

  function listPane() {
    const pane = v_flex().min_h(0).min_w(0).flex_1();
    pane.child(v_flex().flex_none().px(12).pt(12).pb(8).gap(9)
      .child(h_flex().h(34).px(10).gap(8).items_center().rounded(7).bg(t.surface).border_1().border_color(v.searchFocused?t.accent:t.input)
        .child(icon("search")).child(Input.new(v.search).flex_1().min_w(0).text_size(12).text_color(t.foreground))
        .when(!!v.query, e=>e.child(button("clear-search","Clear search",cx=>{v.search.set_value("");v.query="";v.offset=0;v.load(cx);},{icon:"close",iconOnly:true}))))
      .child(h_flex().gap(3).flex_wrap().children(providers.map(p=>button("provider-"+p,p==="all"?"All":p==="claude"?"Claude":providerName(p),cx=>{
        v.provider=p;v.offset=0;v.load(cx);
      },{selected:v.provider===p,height:25})))));
    pane.child(h_flex().px(12).pb(8).gap(3).items_center()
      .child(button("profile-picker",v.data.profiles.find(p=>p.id===v.profile)?.label||"All profiles",cx=>{v.profileMenuOpen=!v.profileMenuOpen;cx.notify();},{icon:"profiles",selected:!!v.profile}))
      .child(div().flex_1())
      .child(button("archive-filter",v.archived?"Archived":"History",cx=>{v.archived=!v.archived;v.offset=0;v.load(cx);},{selected:v.archived}))
      .child(button("more-filters","View options",cx=>{v.moreFilters=!v.moreFilters;cx.notify();},{icon:"more",iconOnly:true,selected:v.moreFilters})));
    if (v.profileMenuOpen) pane.child(h_flex().px(12).pb(9).gap(4).flex_wrap()
      .child(button("profile-all","All profiles",cx=>{v.profile="";v.profileMenuOpen=false;v.offset=0;v.load(cx);},{selected:!v.profile,outline:true}))
      .children(v.data.profiles.map(p=>button("profile-"+p.id,p.label,cx=>{v.profile=p.id;v.profileMenuOpen=false;v.offset=0;v.load(cx);},{selected:v.profile===p.id,outline:true}))));
    if (v.moreFilters) pane.child(v_flex().mx(12).mb(8).p(9).gap(5).rounded(7).bg(t.surface).border_1().border_color(t.border)
      .child(text("View & search",t.muted,10.5).font_medium())
      .child(h_flex().gap(4).flex_wrap()
        .child(button("fts-filter","Search conversation text",cx=>{v.fullText=!v.fullText;v.offset=0;v.load(cx);},{selected:v.fullText,outline:true}))
        .child(button("removed-filter","Include removed",cx=>{v.removed=!v.removed;v.load(cx);},{selected:v.removed,outline:true}))
        .child(button("sort",v.oldest?"Oldest first":"Recent first",cx=>{v.oldest=!v.oldest;v.load(cx);},{icon:"sort",outline:true})))
      .when(v.fullText,e=>e.child(text("Content search uses only profiles you opted in to index.",t.muted,11))));
    const body = v_flex().id("history-list").flex_1().min_h(0).overflow_y_scrollbar().px(6).pb(6).gap(3);
    if (v.loading) body.child(empty("Loading history","Reading your local index…"));
    else if (!v.data.rows.length) body.child(empty(v.data.profiles.length?"No conversations match":"Your history, in one place",
      v.data.profiles.length?"Try another provider or clear your filters. Refresh to find new conversations.":"Connect a provider profile to browse conversations from this computer.",
      button("empty-action",v.data.profiles.length?"Clear filters":"Add a profile",cx=>{
        if(!v.data.profiles.length){v.settings=true;v.formOpen=true;}
        else{v.provider="all";v.profile="";v.query="";v.search.set_value("");v.archived=false;v.removed=false;v.load(cx);}cx.notify();
      },{primary:true})));
    for(const group of groupRows(v.data.rows,v.collapsed)) {
      body.child(Button.new("group-"+group.path).accessibility_label("Project "+group.path).h(30).w_full().px(7).flex().gap(7).items_center()
        .text_color(t.muted).cursor_pointer().on_click((_e,cx)=>{v.collapsed[group.path]=!v.collapsed[group.path];cx.notify();})
        .child(icon(group.collapsed?"chevron-right":"chevron-down",t.muted,10)).child(icon("folder",t.muted,13))
        .child(text(projectName(group.path),t.muted,11).font_medium().flex_1().truncate()).child(text(String(group.rows.length),t.dim,10)));
      if(!group.collapsed) for(const row of group.rows) {
        const selected = v.detail?.key===row.key || v.data.rows[v.selected]?.key===row.key;
        body.child(Button.new("session-"+row.key).accessibility_label(row.title+"; "+providerName(row.provider)+"; "+profilesFor(row))
          .w_full().h(67).px(9).flex().gap(9).items_center().rounded(8).bg(selected?t.selected:t.chrome).cursor_pointer()
          .hover(s=>s.bg(t.hover)).on_click((_e,cx)=>v.choose(row,cx))
          .child(div().w(28).h(28).flex_none().flex().items_center().justify_center().rounded(7).bg(t.surface)
            .text_size(9.5).font_semibold().text_color(selected?t.accent:t.muted).child(({claude:"CL",codex:"CX",opencode:"OC",pi:"PI"})[row.provider]))
          .child(v_flex().flex_1().min_w(0).gap(6)
            .child(text(row.title,t.foreground,12.5).font_medium().truncate())
            .child(h_flex().gap(5).items_center().child(text(providerName(row.provider),t.muted,10.5))
              .child(text("·",t.dim,10)).child(text(profilesFor(row),t.muted,10.5).flex_1().truncate())
              .when(!!row.stale,e=>e.child(text("Stale",t.blocked,10))).when(!row.stale,e=>e.child(text(shortTime(row.lastConversationAt),t.muted,10))))));
      }
    }
    pane.child(body);
    const page=canPage(v.offset,v.data.total);
    pane.child(h_flex().h(35).flex_none().px(10).gap(5).items_center().border_t_1().border_color(t.border)
      .child(text(v.data.total?`${v.offset+1}–${Math.min(v.offset+60,v.data.total)} of ${v.data.total}`:"No conversations",t.muted,10.5).flex_1())
      .child(button("previous","Previous page",cx=>{v.offset=Math.max(0,v.offset-60);v.load(cx);},{icon:"back",iconOnly:true,disabled:!page.previous}))
      .child(button("next","Next page",cx=>{v.offset+=60;v.load(cx);},{icon:"forward",iconOnly:true,disabled:!page.next})));
    return pane;
  }

  function detailPane(row) {
    if(!row) return empty("Pick a conversation","Read its history, choose a profile, and continue in a new Herdr tab.");
    const profile=v.data.profiles.find(p=>p.id===v.target), trusted=profile?.trustedProjects?.includes(row.cwd);
    const pane=v_flex().flex_1().min_w(0).min_h(0).bg(t.surface);
    pane.child(v_flex().px(16).pt(15).pb(11).gap(9).flex_none()
      .child(text(row.title,t.foreground,15).font_semibold())
      .child(h_flex().gap(6).items_center().child(icon("folder",t.muted,13))
        .child(text(projectName(row.cwd),t.muted,11.5).truncate().flex_1())
        .child(button("copy-cwd","Copy project path",cx=>{cx.write_to_clipboard(row.cwd||"");v.notice="Project path copied";cx.notify();},{icon:"copy",iconOnly:true})))
      .child(h_flex().gap(5).flex_wrap().child(badge(providerName(row.provider)))
        .children(row.targets.map(id=>button("target-"+id,v.data.profiles.find(p=>p.id===id)?.label||id,cx=>{v.target=id;cx.notify();},{selected:v.target===id,height:24})))));
    pane.child(h_flex().px(12).gap(3).border_b_1().border_color(t.border)
      .child(button("conversation-tab","Conversation",cx=>{v.detailSection="conversation";cx.notify();},{selected:!v.detailSection||v.detailSection==="conversation"}))
      .child(button("details-tab","Details",cx=>{v.detailSection="details";cx.notify();},{selected:v.detailSection==="details"}))
      .child(div().flex_1()).child(button("organize-tab","Organize",cx=>{v.detailSection=v.detailSection==="organize"?"conversation":"organize";cx.notify();},{icon:"more",selected:v.detailSection==="organize"})));
    const scroll=v_flex().id("detail-body").flex_1().min_h(0).overflow_y_scrollbar().p(14).gap(12);
    if(v.detailSection==="details") {
      for(const [name,value] of [["Session ID",row.nativeId],["Project path",row.cwd||"Unknown"],["Source",row.sourcePath],["Last conversation",row.lastConversationAt||"Unknown"],
        ["Timestamp coverage",row.timestampCoverage],["File changed",row.fileModifiedAt||"Unknown"],["Content indexed",`${row.indexBytes||0} bytes · ${row.indexComplete?"complete":"partial / not indexed"}`],
        ["Resume outcome",row.receipt?.state||"Not requested"]]) scroll.child(v_flex().gap(4).child(label(name)).child(text(value,t.foreground,11.5)));
      scroll.child(button("copy-id","Copy session ID",cx=>{cx.write_to_clipboard(row.nativeId);v.notice="Session ID copied";cx.notify();},{icon:"copy",outline:true}));
    } else if(v.detailSection==="organize") {
      scroll.child(section("Display name","Only changes the name shown in Session Hub.").child(input(v.alias,"alias-input"))
        .child(button("save-alias","Save name",cx=>v.annotate(cx,{alias:v.alias.value()}),{primary:true})));
      scroll.child(section("Organization","Your provider's conversation stays unchanged.")
        .child(h_flex().gap(6).flex_wrap().child(button("archive",row.archived?"Unarchive":"Archive",cx=>v.annotate(cx,{archived:!row.archived}),{icon:"archive",outline:true}))
          .child(button("remove",row.removed?"Restore to history":"Remove from Hub",cx=>v.annotate(cx,{removed:!row.removed}),{outline:true})))
        .child(text("Original deletion is unavailable in this version.",t.muted,11)));
      scroll.child(section("Portable organization","Apply labels and archive state from an encrypted metadata import.")
        .child(button("detail-portable","Review imported metadata",cx=>v.perform(cx,{action:"portable-list"},r=>{v.portable=r;}),{outline:true}))
        .children([...(v.portable?.foreign||[]),...(v.portable?.conflicts||[])].filter(i=>i.provider===row.provider&&i.nativeId===row.nativeId).map((item,i)=>v_flex().gap(7)
          .child(text("Incoming name: "+(item.alias||"(empty)"),t.muted))
          .child(h_flex().gap(5).flex_wrap()
            .child(button("portable-keep-"+i,"Keep local",cx=>v.perform(cx,{action:"portable-apply",key:row.key,portableKey:item.key,conflictChoice:"keep-local"}),{outline:true}))
            .child(button("portable-use-"+i,"Use imported",cx=>v.perform(cx,{action:"portable-apply",key:row.key,portableKey:item.key,conflictChoice:"use-imported"}),{primary:true}))))));
    } else {
      scroll.child(h_flex().gap(7).items_center().child(icon("lock",t.muted,12)).child(text("Read-only preview · "+(v.preview?.partial?"partial history":"text messages only"),t.muted,10.5).flex_1())
        .child(button("preview","Reload preview",cx=>v.loadPreview(row,cx),{icon:"refresh",iconOnly:true})));
      if(v.previewLoading) scroll.child(text("Loading conversation…",t.muted));
      else if(v.previewError) scroll.child(text(v.previewError,t.blocked,11.5));
      else if(!v.preview?.messages?.length) scroll.child(empty("No preview available","Metadata is still available in Details."));
      for(const [i,m] of (v.preview?.messages||[]).entries()) scroll.child(v_flex().id("turn-"+i).p(12).gap(8).rounded(8).bg(m.role==="user"?t.raised:t.surface)
        .when(m.role!=="user",e=>e.border_1().border_color(t.border))
        .child(text(m.role==="user"?"You":"Assistant",m.role==="user"?t.accent:t.muted,10.5).font_medium())
        .child(text(m.text,t.foreground,12).line_height(18)));
      if(v.preview?.partial) scroll.child(text("This bounded excerpt is not the complete provider context.",t.muted,11));
    }
    pane.child(scroll);
    const resumeArea=v_flex().flex_none().p(12).gap(8).border_t_1().border_color(t.border).bg(t.chrome);
    if(row.stale) resumeArea.child(text("This source is stale. Refresh before continuing.",t.blocked,11));
    else if(!v.target) resumeArea.child(text("Choose the profile to continue with.",t.muted,11));
    else if(!profile?.versionVerified) resumeArea.child(h_flex().gap(6).items_center()
      .child(text("Check this profile's installed command first.",t.muted,11).flex_1())
      .child(button("verify-"+profile.id,"Check version",cx=>v.perform(cx,{action:"verify-version",profile:profile.id},r=>{v.notice=r.verified?"Provider command verified":"Command version is unsupported";}),{outline:true})));
    else if(!trusted) resumeArea.child(v_flex().gap(6).child(text("Trust this project before its provider loads hooks and configuration.",t.muted,11))
      .child(input(v.projectConfirm,"project-trust-input"))
      .child(button("trust-project","Trust exact project path",cx=>v.perform(cx,{action:"trust-project",key:row.key,profile:v.target,confirmation:v.projectConfirm.value()}),{outline:true})));
    resumeArea.child(button("resume","Continue in Herdr",cx=>v.resume(cx),{primary:true,icon:"forward",height:34,disabled:!v.target||row.stale}))
      .child(text("Opens a native agent tab. Context remains unverified until checked.",t.muted,10));
    pane.child(resumeArea);
    return pane;
  }

  function settingsPane() {
    const tabs=h_flex().px(12).py(9).gap(4).border_b_1().border_color(t.border);
    for(const [id,name] of [["profiles","Profiles"],["search","Search"],["portability","Portability"]]) tabs.child(button("settings-"+id,name,cx=>{v.settingsSection=id;cx.notify();},{selected:(v.settingsSection||"profiles")===id}));
    const body=v_flex().id("settings-body").flex_1().min_h(0).overflow_y_scrollbar().p(14).gap(12);
    const page=v.settingsSection||"profiles";
    if(page==="profiles") {
      body.child(h_flex().gap(8).items_center().child(text("Connected profiles",t.foreground,13).font_semibold().flex_1())
        .child(button("new-profile","Add profile",cx=>{v.profileDraft={};v.formOpen=true;for(const f of Object.values(v.formFields))f.set_value("");cx.notify();},{icon:"plus",outline:true})));
      for(const p of v.data.profiles) body.child(v_flex().p(12).gap(8).rounded(8).bg(t.surface).border_1().border_color(t.border)
        .child(h_flex().gap(7).items_center().child(text(p.label,t.foreground,12.5).font_medium().flex_1()).child(badge(providerName(p.provider))))
        .child(text(p.cliVersion||(p.versionVerified?"Command verified":"Command not checked"),t.muted,11))
        .child(h_flex().gap(5).child(button("edit-"+p.id,"Edit profile",cx=>v.editProfile(p,cx),{outline:true}))
          .child(button("verify-"+p.id,"Check version",cx=>v.perform(cx,{action:"verify-version",profile:p.id},r=>{v.notice=r.verified?"Provider command verified":"Command version is unsupported";}),{outline:true}))));
      if(v.formOpen||!v.data.profiles.length) {
        const form=section(v.profileDraft.id?"Edit profile":"Connect a profile","Use a separate profile for each account. Credentials stay with the provider.");
        form.child(h_flex().gap(3).flex_wrap().children(providers.filter(p=>p!=="all").map(p=>button("form-provider-"+p,providerName(p),cx=>{v.formProvider=p;v.profileDraft={};cx.notify();},{selected:v.formProvider===p}))));
        form.child(label("Profile ID")).child(input(v.formFields.id,"profile-id-input")).child(label("Display label")).child(input(v.formFields.label,"profile-label-input"));
        for(const [field,heading,buttonId] of [["root","Session directory","pick-root"],["configHome","Account / config directory","pick-config"]]) form.child(label(heading))
          .child(h_flex().gap(6).child(input(v.formFields[field],field+"-input").flex_1())
            .child(button(buttonId,"Choose folder",cx=>v.chooseFolder(cx,field),{icon:"folder",iconOnly:true,outline:true})));
        form.child(label("Provider command")).child(input(v.formFields.executable,"executable-input"))
          .child(button("detect-command","Detect installed command",cx=>v.perform(cx,{action:"probe"},r=>{
            const found=r.providers[v.formProvider];v.formFields.executable.set_value(found.executable||"");v.formFields.launchScript.set_value(found.launchScript||"");
            v.notice=found.installed?"Command found. Select the account folders explicitly.":found.state;
          }),{icon:"search",outline:true}));
        if(v.formProvider==="pi") form.child(label("Pi launcher script")).child(input(v.formFields.launchScript,"pi-script-input"));
        form.child(button("content-opt-in",v.profileDraft.content?"Conversation search enabled":"Metadata search only",cx=>{v.profileDraft.content=!v.profileDraft.content;cx.notify();},{selected:!!v.profileDraft.content,outline:true}))
          .child(text("Conversation search is optional. Indexed text stays encrypted on this computer.",t.muted,11))
          .child(button("save-profile-form","Save profile",cx=>v.saveProfile(cx),{primary:true}))
          .child(button("advanced-profile","Advanced configuration",cx=>{v.advanced=!v.advanced;cx.notify();},{icon:v.advanced?"chevron-down":"chevron-right"}));
        if(v.advanced) form.child(text("Multiple roots and excluded paths can be configured as profile JSON.",t.muted,11)).child(input(v.profileEditor,"profile-json-input"))
          .child(button("save-profile","Save profile JSON",cx=>{
            try{v.perform(cx,{action:"profile-save",profile:JSON.parse(v.profileEditor.value())});}catch(_){v.error="Profile JSON is invalid";cx.notify();}
          },{outline:true}));
        body.child(form);
      }
    } else if(page==="search") {
      body.child(section("Conversation search","Choose the profiles whose conversation text you want searchable. Metadata search works without opting in.")
        .children(v.data.profiles.map(p=>h_flex().gap(8).items_center().child(text(p.label,t.foreground).flex_1())
          .child(button("profile-content-"+p.id,p.content?"Enabled":"Off",cx=>v.perform(cx,{action:"profile-save",profile:{...p,content:!p.content}}),{selected:!!p.content,outline:true})))));
      body.child(section("Search index","Large histories are processed in bounded passes. Partial coverage stays visible in conversation details.")
        .child(h_flex().gap(6).flex_wrap().child(button("index-batch","Index conversations",cx=>v.refresh(cx,true),{primary:true,icon:"refresh"}))
          .child(button("clear-content","Clear search index",cx=>v.perform(cx,{action:"clear-content"},()=>{v.notice="Conversation search index cleared. Metadata and originals remain.";}),{outline:true})))
        .child(text("Clearing removes indexed conversation text and its accessible backup. It does not erase metadata titles or original histories.",t.muted,11)));
    } else {
      body.child(section("Encrypted metadata","Move aliases, archive state and organization between computers. Provider conversations and credentials are never included.")
        .child(label("Bundle file (.hsh)")).child(input(v.bundlePath,"bundle-input"))
        .child(button("export-bundle","Export metadata",cx=>v.portableTerminal(cx,"export"),{primary:true,icon:"export"}))
        .child(h_flex().gap(6).flex_wrap().child(button("preview-bundle","Preview import",cx=>v.portableTerminal(cx,"import"),{outline:true}))
          .child(button("apply-bundle","Apply reviewed import",cx=>v.portableTerminal(cx,"import",true),{outline:true})))
        .child(text("A local terminal asks for your passphrase. Preview before applying; conflicting values stay separate.",t.muted,11)));
      body.child(section("Imported organization","Link matching imported metadata from a conversation's Organize tab. Imported metadata never makes a native session resumable.")
        .child(button("portable-list","Review imported metadata",cx=>v.perform(cx,{action:"portable-list"},r=>{v.portable=r;}),{outline:true}))
        .children([...(v.portable?.foreign||[]),...(v.portable?.conflicts||[])].map(item=>v_flex().gap(4).child(text(item.alias||"Unnamed metadata",t.foreground)).child(text(providerName(item.provider)+" · "+item.nativeId,t.muted,10.5)))));
      body.child(text("Native transcript migration, original deletion and remote sync are unavailable.",t.muted,11));
    }
    return v_flex().flex_1().min_h(0).child(tabs).child(body);
  }

  if(v.settings) root.child(settingsPane());
  else if(wide) root.child(h_flex().flex_1().min_h(0)
    .child(v_flex().w(340).flex_none().h_full().border_r_1().border_color(t.border).child(listPane()))
    .child(detailPane(v.detail)));
  else root.child(v.detail?detailPane(v.detail):listPane());
  if(!v.settings) {
    const partial=v.data.statuses.some(s=>s.state!=="ready");
    root.child(Button.new("source-status").accessibility_label("Source diagnostics").h(30).flex_none().px(12).flex().gap(7).items_center()
      .border_t_1().border_color(t.border).bg(t.chrome).cursor_pointer().on_click((_e,cx)=>{v.showDiagnostics=!v.showDiagnostics;cx.notify();})
      .child(icon(partial?"alert":"lock",partial?t.blocked:t.muted,11))
      .child(text(partial?"Some sources need attention":"On this computer · read-only sources",partial?t.blocked:t.muted,10.5).flex_1())
      .child(icon(v.showDiagnostics?"chevron-down":"chevron-right",t.muted,10)));
    if(v.showDiagnostics) root.child(v_flex().p(10).gap(5).bg(t.surface).children(v.data.statuses.map(s=>text(s.profile+": "+s.state+(s.remaining?" · "+s.remaining+" remaining":"")+(s.reason?" · "+s.reason:""),s.state==="ready"?t.muted:t.blocked,10.5))));
  }
  return root;
}
