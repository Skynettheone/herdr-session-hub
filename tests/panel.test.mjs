import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import { safeText, groupRows, requestFor, canPage, launchArgs, semanticTheme, shortTime, agentCatalog, historyCapability, sidebarLayout, sessionProfiles } from '../mods/session-hub/model.js';

const nativeLayout=()=>({id:'root',type:'row',theme:'custom',toast:'personal-toast',children:[
  {id:'sidebar',type:'block',content:{mod:'spaces'}},
  {id:'work',type:'column',children:[{id:'tabs',type:'block',content:{mod:'tabs'}},
    {id:'panel',type:'column',hidden:true,size:{px:368},children:[{id:'panel-body',type:'stack',active:'files',children:[
      {id:'files',type:'block',content:{mod:'files'}},{id:'changes',type:'block',content:{mod:'changes'}}]}]}]}]});

test('literal transcript display, grouping, pagination and safe local launch', () => {
  assert.deepEqual(sessionProfiles({provider:'pi',targets:['pi']},[{id:'pi',label:'Pi'}]),[]);
  assert.equal(sessionProfiles({provider:'pi',targets:['personal']},[{id:'personal',label:'Personal'}])[0].label,'Personal');
  assert.deepEqual(sessionProfiles({provider:'pi',targets:['personal','work']},[{id:'personal',label:'Pi'},{id:'work',label:'Pi'}]).map(p=>p.label),['Pi (personal)','Pi (work)']);
  assert.equal(safeText('hello\u202e\x1b; $(x)'), 'hello; $(x)');
  assert.equal(groupRows([{cwd:'C:/a'}, {cwd:'C:/a'}, {}]).length, 2);
  assert.deepEqual(canPage(60, 125), {previous:true, next:true});
  assert.throws(() => launchArgs({argv:['x'],folder:'C:/a'}, {}, 'remote/t1'));
  const argv = ['python.exe', 'C:/path with spaces/helper.py', 'literal; $(text)'];
  assert.deepEqual(launchArgs({argv,folder:'C:/a'}, {title:'hello'}, 's1').argv, argv);
});

// The host mock checks behavior after deferred actions, not only initial render.
async function panel(initialHook,props={},savedPanels=null) {
  const pending = [], controls = new Map(), requests = [], runs = [], clipboard = [], styles=[], artwork=[], paths=[];
  let palette={chrome:'chrome',surface:'surface',background:'background',foreground:'foreground',muted:'muted',dim:'dim',raised:'raised',border:'border',input:'input',hover:'hover',selected:'selected',accent:'accent',solid:'solid',solid_foreground:'solid_foreground'};
  const row = {key:'a'.repeat(64), title:'Synthetic history', cwd:'C:/Project', targets:['personal'], provider:'claude', formatSupported:true, nativeId:'11111111-2222-4333-8444-555555555555'};
  let data = {rows:[row],total:1,profiles:[{id:'personal',label:'Personal',provider:'claude',roots:['C:/Account/projects'],configHome:'C:/Account',enabled:true,versionVerified:true,trustedProjects:[]}],statuses:[]};
  let fail = false, layoutState=nativeLayout(),usageHook=null;
  const usageTotals={input:100,output:200,cacheRead:700,cacheWrite:50,tokens:1050,events:2,cost:null,pricedEvents:0,savings:null,sessions:1,cacheHit:.875};
  const usageData={totals:usageTotals,averages:{tokens:1050,events:2,cost:null,sessions:1,trimmed:0},
    models:[{key:'claude:test-model',...usageTotals}],projects:[{key:'Project',...usageTotals}],providers:[{key:'claude',...usageTotals}],
    timeline:[{key:'2026-11-10',...usageTotals,series:{claude:usageTotals}},{key:'2026-11-11',...usageTotals,series:{claude:usageTotals}}],
    start:'2026-11-10T00:00:00Z',end:'2026-11-12T00:00:00Z',timezone:'UTC',coverage:{},pending:0,sources:1,advanced:1,
    limits:[],rates:{},lastRefresh:'2026-11-12T00:00:00Z',scope:'Synthetic history'};
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
    const input={value:()=>value,set_value:v=>{value=v;},on:(name,fn)=>{handlers[name]=fn;},focus:()=>{input.focusCount=(input.focusCount||0)+1;},handlers,placeholder};
    inputs.push(input); return input;
  }};
  const cx={notify(){},focus_handle(){return {};},spawn(fn){pending.push(Promise.resolve().then(()=>fn(cx)));},
    timer:{after(_ms,fn){pending.push(Promise.resolve().then(()=>fn(cx)));}},stop_propagation(){},write_to_clipboard(t){clipboard.push(t);}};
  const host = {
    appHome:()=> 'C:/isolated', focused:()=>({space:'local'}), spaces:()=>[{id:'local',machine:null}], theme:()=>palette,
    props:()=>props,
    layout:()=>layoutState,
    panes:()=>[],window:()=>({buttons:true,platform:'windows'}),shared:()=>null,settings:()=>({zoom:1}),openOverlay:()=>{},
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
      if(req.action.startsWith('usage')) {
        if(usageHook)await usageHook(req);
        if(req.action==='usage-price') {const k=req.rateProvider+':'+req.rateModel;if(req.rate===null)delete usageData.rates[k];else usageData.rates[k]=req.rate;}
        result=usageData;
      }
      return {code:0,stdout:JSON.stringify({ok:true,result})};
    },
    run:(name,args)=>runs.push({name,args}),
  };
  const pathBuilder=()=>{let points=[];const chain={move_to(...p){points.push(p);return chain;},line_to(...p){points.push(p);return chain;},close(){return chain;},dash_array(){return chain;},build(){paths.push(points);return {points};}};return chain;};
  const context=vm.createContext({console,JSON,Map,Set,Date,Error,String,Object,Array,Math,Promise,
    window:{paint_path:()=>element()},localStorage:{getItem:()=>savedPanels,setItem(){}}});
  const synthetic = (exports) => new vm.SyntheticModule(Object.keys(exports), function(){for(const [name,value] of Object.entries(exports))this.setExport(name,value);},{context});
  const model=new vm.SourceTextModule(await fs.readFile(new URL('../mods/session-hub/model.js',import.meta.url),'utf8'),{context});
  const art = kind => path => {artwork.push({kind,path});return element();};
  const sources={'gpui-kit':synthetic({View:class{},div:element,svg:art('svg'),image:art('image'),PathBuilder:{fill:pathBuilder,stroke:pathBuilder},Background:{solid:()=>({opacity:()=>({})})}}), 'gpui-base':synthetic({v_flex:element,h_flex:element,ScrollHandle:{new:()=>({scroll_to_item(index){this.last=index;}})},Button:{new:element},InputState:inputState,TextareaState:inputState,Input:{new:element},Textarea:{new:element}}),herdr:synthetic(host),'./model.js':model};
  await model.link(()=>{});await model.evaluate();
  const usage=new vm.SourceTextModule(await fs.readFile(new URL('../mods/session-hub/usage.js',import.meta.url),'utf8'),{context});
  await usage.link(name=>sources[name]);await usage.evaluate();sources['./usage.js']=usage;
  const ui=new vm.SourceTextModule(await fs.readFile(new URL('../mods/session-hub/ui.js',import.meta.url),'utf8'),{context});
  await ui.link(name=>sources[name]);await ui.evaluate();sources['./ui.js']=ui;
  const tabs=new vm.SourceTextModule(await fs.readFile(new URL('../mods/session-hub/tabs.js',import.meta.url),'utf8'),{context});
  await tabs.link(name=>sources[name]);await tabs.evaluate();sources['./tabs.js']=tabs;
  const module=new vm.SourceTextModule(await fs.readFile(new URL('../mods/session-hub/main.js',import.meta.url),'utf8'),{context});
  await module.link(name=>sources[name]);await module.evaluate();
  const view=new module.namespace.default();view.init(props,cx);
  // init also starts an intentional command stream that remains pending.
  await pending[0]; await pending[1]; pending.splice(0,3);
  async function flush(){while(pending.length){const p=pending.shift();await p;}}
  await flush();
  function draw(){controls.clear();styles.length=0;view.render(cx);}
  function press(id){draw();assert.ok(controls.has(id),`visible control ${id}`);controls.get(id)({},cx);}
  async function click(id){press(id);await flush();draw();}
  return {view,cx,requests,runs,clipboard,inputs,draw,press,click,flush,row,styles,artwork,paths,usageData,usage:usage.namespace,setLayout(v){layoutState=v;},setListHook(fn){listHook=fn;},setUsageHook(fn){usageHook=fn;},setTheme(p){palette=p;},setFail(v){fail=v;}};
}

test('Usage preserves History filters and renders native graphs with explicit filters',async()=>{
  const p=await panel();p.view.query='retained';p.view.provider='pi';
  await p.click('view-usage');assert.equal(p.requests.at(-1).action,'usage');assert.ok(p.paths.length>0);
  await p.click('usage-provider');await p.click('usage-provider-claude');assert.equal(p.requests.at(-1).provider,'claude');
  await p.click('usage-scope');await p.click('usage-profile-personal');assert.equal(p.requests.at(-1).profile,'personal');
  await p.click('usage-period-7d');assert.equal(p.requests.at(-1).period,'7d');
  await p.click('usage-metric-cost');assert.equal(p.view.usageMetric,'cost');
  await p.click('usage-metric-limits');assert.equal(p.view.usageMetric,'limits');
  await p.click('usage-metric-tokens');await p.click('usage-trim');assert.equal(p.requests.at(-1).trim,true);
  const retained=p.view.usageData;p.view.usageTrim=false;p.view.loadUsage(p.cx);
  assert.equal(p.view.usageData,retained,'average-only updates must retain the scroll body while loading');await p.flush();
  await p.click('usage-breakdown-projects');assert.equal(p.view.usageBreakdown,'projects');
  await p.click('usage-breakdown-models');await p.click('usage-model-0');assert.equal(p.requests.at(-1).model,'claude:test-model');
  await p.click('usage-clear-model');assert.equal(p.requests.at(-1).model,'');
  await p.click('refresh');assert.ok(p.requests.some(r=>r.action==='usage-refresh'));assert.equal(p.view.busy,false);
  await p.click('view-history');assert.equal(p.view.query,'retained');assert.equal(p.view.provider,'pi');
});

test('Usage custom dates, rates, report, error recovery and keyboard isolation',async()=>{
  const p=await panel();await p.click('view-usage');
  await p.click('usage-period-custom');p.view.usageFields.start.set_value('2026-11-01');p.view.usageFields.end.set_value('2026-11-12');
  await p.click('usage-apply-dates');assert.equal(p.requests.at(-1).start,'2026-11-01');
  await p.click('usage-rate-0');assert.equal(p.view.usageFields.model.value(),'test-model');
  assert.equal(p.view.usageScroll.last,0,'a model-row rate editor must reveal its heading');
  await p.click('usage-save-rate');assert.ok(p.view.error.includes('all four'));assert.ok(p.view.usageFields.input.focusCount);
  for(const n of ['input','output','cacheRead','cacheWrite'])p.view.usageFields[n].set_value(n==='cacheRead'?'0':'1.25');
  await p.click('usage-save-rate');assert.equal(p.requests.at(-1).rate.cacheRead,0);assert.equal(p.requests.at(-1).rate.output,1.25);
  await p.click('usage-remove-rate');assert.equal(p.requests.at(-1).rate,null);
  p.view.usageFields.model.set_value('');await p.click('usage-save-rate');assert.ok(p.view.error.includes('model identifier'));assert.ok(p.view.usageFields.model.focusCount);
  await p.click('usage-close-rates');await p.click('usage-copy');assert.equal(JSON.parse(p.clipboard[0]).totals.tokens,1050);
  p.view.selected=0;p.view.key({key:'enter'},p.cx);assert.equal(p.view.detail,null);
  await p.click('usage-clear-cache');assert.equal(p.requests.at(-1).action,'usage-clear');
  p.setFail(true);await p.click('refresh');assert.equal(p.view.busy,false);assert.equal(p.view.scanning,false);assert.equal(p.view.error,'Synthetic failure');
  p.setFail(false);await p.click('refresh');assert.equal(p.view.error,'');
  assert.equal(p.usage.amount(.000127,true),'$0.0001');assert.equal(p.usage.amount(null,true),'Unavailable');
  assert.equal(p.usage.plotPoints([0,50,100],100)[1][1],50);
});

test('Usage graphs follow community tokens and narrow panes retain independent state',async()=>{
  const p=await panel(),other=await panel();
  p.view.width=360;
  p.setTheme({background:'community-bg',foreground:'community-fg',accent:'community-accent',solid:'community-solid',border:'community-border'});
  await p.click('view-usage');assert.ok(p.paths.length>0);assert.ok(p.styles.includes('community-accent'));
  assert.ok(p.styles.every(value=>!String(value).startsWith('#')));
  p.view.usagePeriod='90d';assert.equal(other.view.usagePeriod,'30d');assert.equal(other.view.hubView,'history');
  p.usageData.lastRefresh=null;await p.click('usage-period-7d');
  await p.click('usage-first-refresh');assert.ok(p.requests.some(r=>r.action==='usage-refresh'));
});

test('Usage stop preserves the completed batch and another refresh can finish',async()=>{
  const p=await panel();await p.click('view-usage');
  p.usageData.pending=2;
  p.setUsageHook(async request=>{if(request.action==='usage-refresh')p.press('cancel-scan');});
  await p.click('refresh');
  assert.equal(p.requests.filter(r=>r.action==='usage-refresh').length,1);
  assert.equal(p.view.usageData.totals.tokens,1050);assert.equal(p.view.busy,false);
  assert.ok(p.view.notice.startsWith('Stopped'));
  p.setUsageHook(null);p.usageData.pending=0;await p.click('refresh');
  assert.equal(p.view.scanCancelled,false);assert.equal(p.view.usageData.pending,0);
});

test('panel search, filters, pagination and grouping run after initial render', async()=>{
  const p=await panel();p.draw();
  await p.click('history-search-input');assert.ok(p.view.search.focusCount>0);
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
  assert.equal(p.view.notice,'History refreshed.');
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
  assert.equal(p.view.notice,'Search index updated. See Details for conversation coverage.');
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

test('profile editing isolates drafts, validates before saving and never retargets an existing ID',async()=>{
  const p=await panel();await p.click('settings');await p.click('new-profile');
  let writes=()=>p.requests.filter(r=>r.action==='profile-save').length;
  await p.click('save-profile-form');assert.match(p.view.error,/profile ID/);assert.equal(writes(),0);
  p.view.formFields.id.set_value('new-profile');await p.click('save-profile-form');
  assert.match(p.view.error,/history|histories/);assert.equal(writes(),0);
  p.view.formFields.root.set_value('C:/old-account/projects');
  p.view.formFields.configHome.set_value('C:/old-account');
  p.view.formFields.executable.set_value('C:/old-agent.exe');
  p.view.profileDraft={content:true,roots:['C:/old-account/projects'],trustedProjects:['C:/old-project']};
  await p.click('form-provider-pi');
  assert.equal(p.view.formFields.configHome.value(),'');assert.equal(p.view.formFields.root.value(),'');
  assert.equal(p.view.formFields.executable.value(),'');assert.equal(p.view.profileDraft.content,undefined);
  await p.click('advanced-profile');p.view.profileEditor.set_value('[]');await p.click('save-profile');
  assert.equal(p.view.error,'Profile JSON must be an object');assert.equal(writes(),0);
  p.view.profileEditor.set_value('{"id":"personal"}');await p.click('save-profile');
  assert.match(p.view.error,/already in use/);assert.equal(writes(),0);
  await p.click('cancel-profile');assert.equal(p.view.formOpen,false);
  await p.click('edit-personal');assert.equal(p.view.advanced,false);
  await p.click('advanced-profile');p.view.profileEditor.set_value('{"id":"another"}');await p.click('save-profile');
  assert.match(p.view.error,/differs/);assert.equal(writes(),0);
  p.view.key({key:'escape'},p.cx);assert.equal(p.view.formOpen,false);assert.equal(p.view.settings,true);
  await p.click('back');await p.click('session-'+p.row.key);await p.click('organize-tab');
  await p.click('alias-input');assert.ok(p.view.alias.focusCount>0);
  await p.click('reset-alias');assert.equal(p.requests.findLast(r=>r.action==='annotate').alias,'');
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

test('History uses one collapsible Files/Changes panel in a preserved personal layout',async()=>{
  const original=nativeLayout();
  const before=JSON.stringify(original),result=sidebarLayout(original);
  assert.equal(JSON.stringify(original),before);
  assert.deepEqual(result.layout.children[0],original.children[0]);
  const work=result.layout.children[1],body=work.children[1].children[0];
  assert.deepEqual(body.children.slice(0,2),original.children[1].children[1].children[0].children);
  assert.equal(work.children[0].content.props.role,'tabs');
  assert.equal(body.children.filter(n=>n.content.mod==='session-hub').length,1);
  assert.equal(body.active,'session-hub-history');
  assert.equal(result.layout.toast,'personal-toast');
  assert.equal(sidebarLayout(result.layout).existing,'session-hub-history');
  const upgraded=sidebarLayout({id:'session-hub-layout',type:'row',children:[{id:'session-hub-sidebar',type:'block',content:{mod:'session-hub'}},original]}).layout;
  assert.equal(upgraded.id,'root');assert.equal(upgraded.children[1].children[1].children[0].children.length,3);
  assert.throws(()=>sidebarLayout({id:'custom',type:'block',content:{tab:'active'}}),/no standard/);
  const hidden={id:'root',type:'row',children:[{id:'tabs',type:'stack',hidden:true,children:[{id:'history',type:'block',hidden:true,content:{mod:'session-hub'}}]}]};
  assert.ok(sidebarLayout(hidden).reveal.some(a=>a.name==='layout.select'&&a.args.stack==='tabs'&&a.args.child==='history'));
  assert.ok(sidebarLayout(hidden).reveal.some(a=>a.name==='layout.show'&&a.args.id==='tabs'));
  const p=await panel(undefined,{overlay:'mod-session-hub'});await p.click('dock-sidebar');
  const write=p.requests.find(r=>r.action==='write-layout');
  assert.equal(write.path,'C:/isolated/layouts/session-hub-workspace.json');
  assert.equal(write.expected,null);
  assert.ok(p.runs.some(r=>r.name==='layout.switch'&&r.args.name==='session-hub-workspace'));
  assert.ok(p.runs.some(r=>r.name==='closeOverlay'));
  const docked=await panel(undefined,{panel:'panel'});await docked.click('collapse-history');
  assert.ok(docked.runs.some(r=>r.name==='layout.hide'&&r.args.id==='panel'));
  const header=await panel(undefined,{role:'tabs'});header.draw();
  assert.equal(header.requests.length,0,'header role never starts another history scan');
  header.setLayout(result.layout);await header.click('panel-session-hub-history');
  assert.ok(header.runs.some(r=>r.name==='layout.hide'&&r.args.id==='panel'));
  work.children[1].hidden=true;await header.click('panel-session-hub-history');
  assert.ok(header.runs.some(r=>r.name==='layout.select'&&r.args.child==='session-hub-history'));
  assert.ok(header.runs.some(r=>r.name==='layout.show'&&r.args.id==='panel'));
});

test('native header tolerates corrupt or non-object saved panel preferences',async()=>{
  for(const saved of ['{','[]','null','true']) {
    const header=await panel(undefined,{role:'tabs'},saved);
    assert.equal(JSON.stringify(header.view.panels),'{}');header.draw();
    assert.equal(header.requests.length,0);
  }
});
