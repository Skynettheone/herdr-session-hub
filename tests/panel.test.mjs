import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import { safeText, groupRows, requestFor, canPage, launchArgs, semanticTheme, shortTime, agentCatalog, historyCapability, sidebarLayout } from '../mods/session-hub/model.js';

test('literal transcript display, grouping, pagination and safe local launch', () => {
  assert.equal(safeText('hello\u202e\x1b; $(x)'), 'hello; $(x)');
  assert.equal(groupRows([{cwd:'C:/a'}, {cwd:'C:/a'}, {}]).length, 2);
  assert.deepEqual(canPage(60, 125), {previous:true, next:true});
  assert.throws(() => launchArgs({argv:['x'],folder:'C:/a'}, {}, 'remote/t1'));
  const argv = ['python.exe', 'C:/path with spaces/helper.py', 'literal; $(text)'];
  assert.deepEqual(launchArgs({argv,folder:'C:/a'}, {title:'hello'}, 's1').argv, argv);
});

// The host mock checks behavior after deferred actions, not only initial render.
async function panel(initialHook,props={}) {
  const pending = [], controls = new Map(), requests = [], runs = [], clipboard = [], styles=[], artwork=[];
  let palette={chrome:'chrome',surface:'surface',background:'background',foreground:'foreground',muted:'muted',dim:'dim',raised:'raised',border:'border',input:'input',hover:'hover',selected:'selected',accent:'accent',solid:'solid',solid_foreground:'solid_foreground'};
  const row = {key:'a'.repeat(64), title:'Synthetic history', cwd:'C:/Project', targets:['personal'], provider:'claude', formatSupported:true, nativeId:'11111111-2222-4333-8444-555555555555'};
  let data = {rows:[row],total:1,profiles:[{id:'personal',label:'Personal',provider:'claude',enabled:true,versionVerified:true,trustedProjects:[]}],statuses:[]};
  let fail = false;
  let listHook = async request => { if(initialHook) { const hook=initialHook;initialHook=null;await hook(request,view,cx); } };
  function element(initial) {
    let id=initial;
    let proxy;
    proxy = new Proxy({}, {get(_, method) {
      if (method === 'then') return undefined;
      return (...args) => {
        if (method === 'id') id = args[0];
        if (['bg','text_color','border_color'].includes(method)) styles.push(args[0]);
        if (method === 'on_click') controls.set(id, args[0]);
        if (method === 'when' && args[0]) args[1](proxy);
        return proxy;
      };
    }});
    return proxy;
  }
  const inputs=[];
  const inputState = {new({value='',placeholder}={}) {
    const handlers={};
    const input={value:()=>value,set_value:v=>{value=v;},on:(name,fn)=>{handlers[name]=fn;},focus:()=>{},handlers,placeholder};
    inputs.push(input); return input;
  }};
  const cx={notify(){},focus_handle(){return {};},spawn(fn){pending.push(Promise.resolve().then(()=>fn(cx)));},
    timer:{after(_ms,fn){pending.push(Promise.resolve().then(()=>fn(cx)));}},stop_propagation(){},write_to_clipboard(t){clipboard.push(t);}};
  const host = {
    appHome:()=> 'C:/isolated', focused:()=>({space:'local'}), spaces:()=>[{id:'local',machine:null}], theme:()=>palette,
    props:()=>props,
    layout:()=>({id:'original',type:'block',theme:'community',content:{tab:'active'}}),
    writeTextFile:async(path,text,expected)=>{requests.push({action:'write-layout',path,text,expected});},
    closeOverlay:id=>runs.push({name:'closeOverlay',args:{id}}),
    readTextFile:async path=>path.includes('/layouts/')?null:JSON.stringify({schema:1,python:'python.exe',helper:'C:/helper.py',state:'C:/hub-state',base:'C:/'}),
    pickFolder:async()=> 'C:/Chosen folder',
    knownAgents:async()=>[{key:'claude',name:'Claude Code',icon:'icons/claude.svg',tint:false,run:['claude'],installed:true},
      {key:'cursor',name:'Cursor',icon:'icons/cursor.svg',tint:true,run:['agent'],installed:false},
      {key:'custom-agent',name:'Custom agent',run:['custom.exe'],installed:true}],
    nextCommand:()=>new Promise(()=>{}),
    exec:async(_exe,args)=>{
      if (args[0] === '--version') return {code:0,stdout:'herdr-app 0.1.15\n'};
      const req=JSON.parse(args.at(-1));requests.push(req);
      if(fail)return {code:1,stdout:JSON.stringify({ok:false,error:'Synthetic failure'})};
      let result=data;
      if(req.action==='list') { result={...data,querySnapshot:req.query||''};await listHook(req); }
      if(req.action==='preview')result={messages:[{role:'user',text:'literal $(text)'}],partial:true};
      if(req.action==='trust-project')data.profiles[0].trustedProjects=[req.confirmation];
      if(req.action==='resume')result={argv:['python.exe','literal arg'],folder:'C:/Project'};
      if(req.action==='refresh')result={advanced:1,statuses:[]};
      return {code:0,stdout:JSON.stringify({ok:true,result})};
    },
    run:(name,args)=>runs.push({name,args}),
  };
  const context=vm.createContext({console,JSON,Map,Set,Date,Error,String,Object,Array,Math,Promise});
  const synthetic = (exports) => new vm.SyntheticModule(Object.keys(exports), function(){for(const [name,value] of Object.entries(exports))this.setExport(name,value);},{context});
  const model=new vm.SourceTextModule(await fs.readFile(new URL('../mods/session-hub/model.js',import.meta.url),'utf8'),{context});
  const art = kind => path => {artwork.push({kind,path});return element();};
  const sources={'gpui-kit':synthetic({View:class{},div:element,svg:art('svg'),image:art('image')}), 'gpui-base':synthetic({v_flex:element,h_flex:element,Button:{new:element},InputState:inputState,Input:{new:element}}),herdr:synthetic(host),'./model.js':model};
  await model.link(()=>{});await model.evaluate();
  const ui=new vm.SourceTextModule(await fs.readFile(new URL('../mods/session-hub/ui.js',import.meta.url),'utf8'),{context});
  await ui.link(name=>sources[name]);await ui.evaluate();sources['./ui.js']=ui;
  const module=new vm.SourceTextModule(await fs.readFile(new URL('../mods/session-hub/main.js',import.meta.url),'utf8'),{context});
  await module.link(name=>sources[name]);await module.evaluate();
  const view=new module.namespace.default();view.init(props,cx);
  // init also starts an intentional command stream that remains pending.
  await pending[0]; await pending[1]; pending.splice(0,3);
  async function flush(){while(pending.length){const p=pending.shift();await p;}}
  await flush();
  function draw(){controls.clear();styles.length=0;view.render(cx);}
  async function click(id){draw();assert.ok(controls.has(id),`visible control ${id}`);controls.get(id)({},cx);await flush();draw();}
  return {view,cx,requests,runs,clipboard,inputs,draw,click,flush,row,styles,artwork,setListHook(fn){listHook=fn;},setTheme(p){palette=p;},setFail(v){fail=v;}};
}

test('panel search, filters, pagination and grouping run after initial render', async()=>{
  const p=await panel();p.draw();
  p.view.search.set_value('café');p.view.search.handlers.change({},p.cx);await p.flush();
  assert.equal(p.requests.at(-1).query,'café');
  await p.click('provider-codex');assert.equal(p.requests.at(-1).provider,'codex');
  await p.click('profile-picker');await p.click('profile-personal');assert.equal(p.requests.at(-1).profile,'personal');
  await p.click('more-filters');
  await p.click('fts-filter');assert.equal(p.requests.at(-1).fullText,true);
  await p.click('archive-filter');assert.equal(p.requests.at(-1).archived,true);
  await p.click('removed-filter');assert.equal(p.requests.at(-1).removed,true);
  await p.click('sort');assert.equal(p.requests.at(-1).oldest,true);
  await p.click('refresh');assert.ok(p.requests.some(r=>r.action==='refresh'));
  await p.click('group-C:/Project');assert.equal(p.view.collapsed['C:/Project'],true);
});

test('detail alias, archive, removal, copy, preview and explicit native launch',async()=>{
  const p=await panel();await p.click('session-'+p.row.key);
  await p.click('copy-cwd');assert.equal(p.clipboard[0],p.row.cwd);
  await p.click('details-tab');await p.click('copy-id');assert.equal(p.clipboard[1],p.row.nativeId);
  await p.click('conversation-tab');
  await p.click('preview');assert.equal(p.view.preview.messages.length,1);
  await p.click('organize-tab');
  p.view.alias.set_value('New alias');await p.click('save-alias');
  assert.ok(p.requests.some(r=>r.action==='annotate'&&r.alias==='New alias'));
  await p.click('archive');assert.ok(p.requests.some(r=>r.archived===true&&r.action==='annotate'));
  await p.click('remove');assert.ok(p.requests.some(r=>r.removed===true&&r.action==='annotate'));
  p.view.projectConfirm.set_value('C:/Project');await p.click('trust-project');
  assert.ok(p.requests.some(r=>r.action==='trust-project'&&r.confirmation==='C:/Project'));
  await p.click('resume');assert.equal(p.runs[0].name,'tab.new');
  assert.equal(p.runs[0].args.folder,'C:/Project');assert.match(p.view.notice,/unverified/);
  await p.click('back');assert.equal(p.view.detail,null);
});

test('settings, malformed profile JSON, indexing, failures and separate pane state',async()=>{
  const p=await panel(),other=await panel();
  await p.click('settings');assert.equal(other.view.settings,false);
  await p.click('new-profile');await p.click('advanced-profile');
  await p.click('save-profile');assert.equal(p.view.error,'Profile JSON is invalid');
  p.view.profileEditor.set_value('{"id":"work"}');await p.click('save-profile');
  assert.ok(p.requests.some(r=>r.action==='profile-save'));
  await p.click('verify-personal');assert.ok(p.requests.some(r=>r.action==='verify-version'));
  await p.click('edit-personal');assert.match(p.view.profileEditor.value(),/personal/);
  await p.click('pick-root');assert.equal(p.view.formFields.root.value(),'C:/Chosen folder');
  await p.click('content-opt-in');assert.equal(p.view.profileDraft.content,true);
  await p.click('save-profile-form');assert.ok(p.requests.some(r=>r.action==='profile-save'&&r.profile.roots?.[0]==='C:/Chosen folder'));
  await p.click('settings-portability');p.view.bundlePath.set_value('C:/metadata.hsh');await p.click('export-bundle');
  assert.deepEqual(Array.from(p.runs.at(-1).args.argv).slice(-2),['export','C:/metadata.hsh']);
  await p.click('preview-bundle');assert.equal(p.runs.at(-1).args.argv.at(-2),'import');
  await p.click('apply-bundle');assert.equal(p.runs.at(-1).args.argv.at(-1),'--apply');
  await p.click('settings-search');await p.click('index-batch');assert.ok(p.requests.some(r=>r.action==='refresh'&&r.content));
  await p.click('clear-content');assert.ok(p.requests.some(r=>r.action==='clear-content'));
  p.setFail(true);await p.click('clear-content');assert.equal(p.view.error,'Synthetic failure');assert.equal(p.view.busy,false);
});

test('semantic theme switching and responsive conversation layout',async()=>{
  const p=await panel();
  const dark={background:'#15191e',foreground:'#e4ebef',chrome:'#1b2027',surface:'#222933',raised:'#2e3743',hover:'#354455',selected:'#324454',border:'#405365',input:'#536778',muted:'#b1bec9',dim:'#889ba9',accent:'#a2d5cf',solid:'#a2d5cf',solid_foreground:'#152a29'};
  const light={background:'#fffaf2',foreground:'#342e29',chrome:'#f5eee1',surface:'#fffcf6',raised:'#e7dfd2',hover:'#e0d4c1',selected:'#d9ddc5',border:'#a29686',input:'#8f8172',muted:'#6a5c4e',dim:'#7f7161',accent:'#5b662b',solid:'#5b662b',solid_foreground:'#ffffff'};
  for(const theme of [dark,light]) {
    p.setTheme(theme);p.draw();
    assert.ok(p.styles.includes(theme.chrome));assert.ok(p.styles.includes(theme.foreground));
    assert.ok(p.styles.includes(theme.accent));
    assert.ok(p.styles.every(c=>Object.values(theme).includes(c)), 'all UI colors come from the active theme');
  }
  const minimal={background:'community-bg',foreground:'community-fg',surface:'community-surface',accent:'community-accent',accent_foreground:'community-on-accent',selection:'community-selection'};
  assert.equal(semanticTheme(minimal).solid_foreground,'community-on-accent');
  assert.equal(semanticTheme(minimal).selected,'community-selection');
  p.view.width=1000;p.draw();await p.click('session-'+p.row.key);
  assert.ok(p.view.detail);assert.ok(p.view.preview?.messages.length);
  p.view.width=360;p.draw();await p.click('back');assert.equal(p.view.detail,null);
  assert.equal(shortTime(null),'Time unknown');
});

test('latest search survives an in-flight list and a final refresh batch',async()=>{
  for(const refresh of [false,true]) {
    const p=await panel();let changed=false;
    p.setListHook(async request=>{
      if(request.query==='old'&&!changed){changed=true;p.view.query='latest';p.view.load(p.cx);}
    });
    p.view.query='old';
    if(refresh)p.view.refresh(p.cx);else p.view.load(p.cx);
    await p.flush();
    assert.equal(p.view.data.querySnapshot,'latest');
    assert.equal(p.view.busy,false);
  }
});

test('startup cannot replace an early filtered query with unfiltered results',async()=>{
  const p=await panel(async(_request,view,cx)=>{view.query='early search';view.load(cx);});
  assert.equal(p.view.data.querySnapshot,'early search');
});

test('typing path separators or arrows does not navigate away from a field',async()=>{
  const p=await panel();let focused=0;
  p.view.search.focus=()=>{focused++;};
  p.view.activeInput=p.view.formFields.root;
  p.view.key({key:'/'},p.cx);p.view.key({key:'down'},p.cx);
  assert.equal(focused,0);assert.equal(p.view.selected,undefined);
});

test('native agent catalog retains custom agents and renders original artwork',async()=>{
  const p=await panel();p.draw();
  assert.ok(p.artwork.some(a=>a.kind==='image'&&a.path==='mods/session-hub/assets/herdr-logo.svg'));
  assert.ok(p.artwork.some(a=>a.kind==='image'&&a.path==='icons/claude.svg'));
  await p.click('provider-gemini');assert.equal(p.requests.at(-1).provider,'gemini');
  await p.click('settings');await p.click('settings-agents');
  assert.ok(p.artwork.some(a=>a.kind==='svg'&&a.path==='icons/cursor.svg'));
  assert.equal(p.view.agents.find(a=>a.key==='custom-agent').history,false);
  assert.match(historyCapability(agentCatalog([{key:'amp',run:['amp']}])[0]),/unavailable/);
  await p.click('connect-gemini');assert.equal(p.view.formProvider,'gemini');
});

test('sidebar docking preserves the original tree and creates only a personal layout',async()=>{
  const original={id:'root',type:'row',theme:'custom',toast:'personal-toast',children:[{id:'session-hub-sidebar',type:'block',content:{mod:'spaces'}},{id:'work',type:'block',content:{tab:'active'}}]};
  const before=JSON.stringify(original),result=sidebarLayout(original);
  assert.equal(JSON.stringify(original),before);
  assert.deepEqual(result.layout.children[1],original);
  assert.notEqual(result.layout.children[0].id,'session-hub-sidebar');
  assert.equal(result.layout.toast,'personal-toast');
  assert.equal(sidebarLayout(result.layout).existing,result.layout.children[0].id);
  const hidden={id:'root',type:'row',children:[{id:'tabs',type:'stack',hidden:true,children:[{id:'history',type:'block',hidden:true,content:{mod:'session-hub'}}]}]};
  assert.ok(sidebarLayout(hidden).reveal.some(a=>a.name==='layout.select'&&a.args.stack==='tabs'&&a.args.child==='history'));
  assert.ok(sidebarLayout(hidden).reveal.some(a=>a.name==='layout.show'&&a.args.id==='tabs'));
  const p=await panel(undefined,{overlay:'mod-session-hub'});await p.click('dock-sidebar');
  const write=p.requests.find(r=>r.action==='write-layout');
  assert.equal(write.path,'C:/isolated/layouts/session-hub-workspace.json');
  assert.equal(write.expected,null);
  assert.ok(p.runs.some(r=>r.name==='layout.switch'&&r.args.name==='session-hub-workspace'));
  assert.ok(p.runs.some(r=>r.name==='closeOverlay'));
});
