import { div, PathBuilder, Background } from "gpui-kit";
import { h_flex, v_flex } from "gpui-base";
import { providerName } from "./model.js";

export function amount(value, money = false) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "Unavailable";
  if (money) {const [whole,fraction]=value.toFixed(value && value < .01 ? 4 : 2).split(".");return "$"+whole.replace(/\B(?=(\d{3})+(?!\d))/g,",")+"."+fraction;}
  for (const [scale,suffix] of [[1e12,"T"],[1e9,"B"],[1e6,"M"],[1e3,"K"]]) {
    if (value >= scale) return (value/scale).toFixed(value/scale>=100?0:1).replace(/\.0$/,"")+suffix;
  }
  return Number.isInteger(value)?String(value):value.toFixed(1);
}

export function plotPoints(values, maximum) {
  const scale = maximum > 0 ? maximum : 1, count = values.length;
  return values.map((value,index)=>[count>1?index*100/(count-1):50,100-Math.max(0,Math.min(scale,value||0))*100/scale]);
}

export function renderUsage(v, cx, kit) {
  const {t,text,button,input,section,agentIcon} = kit;
  const wide = (v.width||380)>=760, data=v.usageData, totals=data?.totals;
  const metric=v.usageMetric, money=metric==="cost";
  const reload=(cx,patch)=>{Object.assign(v,patch);v.loadUsage(cx);};
  const pane=v_flex().id("usage-view").flex_1().min_h(0).min_w(0);
  const filters=v_flex().flex_none().px(12).py(10).gap(8).border_b_1().border_color(t.border);
  filters.child(h_flex().gap(4).flex_wrap().items_center()
    .child(button("usage-scope",v.usageProfile?v.data.profiles.find(p=>p.id===v.usageProfile)?.label||"Selected profile":"All profiles",cx=>{v.usageScopeOpen=!v.usageScopeOpen;cx.notify();},{selected:!!v.usageProfile,icon:"profiles"}))
    .child(button("usage-provider",v.usageProvider==="all"?"All providers":providerName(v.usageProvider),cx=>{v.usageProviderOpen=!v.usageProviderOpen;cx.notify();},{selected:v.usageProvider!=="all",agent:v.usageProvider==="all"?null:v.usageProvider}))
    .child(div().flex_1())
    .child(button("usage-copy","Copy aggregate report",cx=>v.copyUsage(cx),{icon:"copy",iconOnly:true,disabled:!data})));
  if(v.usageScopeOpen)filters.child(h_flex().gap(3).flex_wrap()
    .child(button("usage-profile-all","All profiles",cx=>{v.usageScopeOpen=false;reload(cx,{usageProfile:""});},{selected:!v.usageProfile,outline:true}))
    .children(v.data.profiles.filter(p=>p.enabled).map(p=>button("usage-profile-"+p.id,p.label,cx=>{v.usageScopeOpen=false;reload(cx,{usageProfile:p.id});},{selected:v.usageProfile===p.id,outline:true}))));
  if(v.usageProviderOpen)filters.child(h_flex().gap(3).flex_wrap().children(["all","claude","codex","pi","opencode","gemini","copilot"].map(p=>button("usage-provider-"+p,p==="all"?"All":providerName(p),cx=>{
    v.usageProviderOpen=false;reload(cx,{usageProvider:p,usageModel:""});
  },{selected:v.usageProvider===p,agent:p==="all"?null:p,outline:true}))));
  filters.child(h_flex().gap(3).flex_wrap().items_center().children([["24h","24h"],["7d","7 days"],["30d","30 days"],["90d","90 days"],["custom","Custom"]].map(([key,label])=>button("usage-period-"+key,label,cx=>{
    if(key==="custom"){v.usagePeriod=key;cx.notify();}else reload(cx,{usagePeriod:key});
  },{selected:v.usagePeriod===key,height:25}))).child(text("UTC",t.dim,10)));
  if(v.usagePeriod==="custom")filters.child(v_flex().gap(6)
    .child(text("From / through (inclusive), YYYY-MM-DD · UTC",t.muted,10.5))
    .child(h_flex().gap(6).child(input(v.usageFields.start,"usage-start").flex_1()).child(input(v.usageFields.end,"usage-end").flex_1()))
    .child(button("usage-apply-dates","Apply dates",cx=>v.loadUsage(cx),{primary:true})));
  pane.child(filters);
  const body=v_flex().id("usage-body").flex_1().min_h(0).min_w(0).overflow_y_scrollbar().when(!!v.usageScroll,e=>e.track_scroll(v.usageScroll)).p(wide?20:12).gap(14);
  if(!data) {
    if(v.usageLoading)return pane.child(body.child(section("Loading usage","Reading your local numeric cache…")));
    body.child(section("Your usage, on this computer","Explore tokens, cache activity and estimated cost from your configured history folders.")
      .child(text("Refresh reads numeric usage without enabling conversation search. No account credentials or network access.",t.muted,11.5))
      .child(button("usage-first-refresh","Refresh recorded usage",cx=>v.loadUsage(cx,true),{primary:true,icon:"refresh"})));
    return pane.child(body);
  }
  body.child(h_flex().gap(3).flex_wrap().items_center()
    .children(["tokens","cost","limits"].map(key=>button("usage-metric-"+key,key==="cost"?"Est. cost":key==="tokens"?"Tokens":"Limits",cx=>{v.usageMetric=key;cx.notify();},{selected:metric===key})))
    .child(div().flex_1()).child(button("usage-prices","Model rates",cx=>{v.usagePrices=!v.usagePrices;cx.notify();},{selected:v.usagePrices,icon:"settings"})));
  if(v.usageLoading)body.child(text("Updating this view…",t.muted,11));
  if(!data.lastRefresh && !v.usagePrices) {
    body.child(section("Ready to read recorded usage","No usage has been scanned yet. Read numeric counters from your approved local history folders to build this dashboard.")
      .child(button("usage-first-refresh","Refresh recorded usage",cx=>v.loadUsage(cx,true),{primary:true,icon:"refresh"}))
      .child(text("Conversation search stays off. No credentials or network requests.",t.muted,11)));
    return pane.child(body);
  }
  if(data.pending || Object.keys(data.coverage||{}).length)body.child(v_flex().p(11).gap(4).rounded(7).bg(t.surface).border_1().border_color(t.border)
    .child(text("Partial recorded coverage",t.blocked,12).font_medium())
    .child(text("Totals include only available, attributable local records. "+(data.pending?data.pending+" histories await refresh. ":"")+"See Coverage & privacy for exclusions.",t.muted,11)));
  if(v.usageModel)body.child(h_flex().gap(5).flex_wrap().child(text("Model: "+v.usageModel,t.accent,11))
    .child(button("usage-clear-model","Show all models",cx=>reload(cx,{usageModel:""}),{outline:true})));
  body.child(text(data.start.slice(0,16).replace("T"," ")+" — "+data.end.slice(0,16).replace("T"," ")+" UTC",t.dim,10.5));
  if(v.usagePrices)return pane.child(body.child(prices()));

  function card(label,value,note) {
    return v_flex().min_w(0).flex_1().h(124).min_h(124).p(13).gap(6).rounded(8).bg(t.surface).border_1().border_color(t.border)
      .child(text(label,t.muted,10.5).font_medium().h(16).flex_none())
      .child(text(value,t.foreground,wide?23:20).font_semibold().h(31).flex_none())
      .child(text(note||"",t.muted,10.5).h(32).flex_none());
  }
  function pair(a,b) {return h_flex().gap(10).items_stretch().child(a).child(b);}
  function drawChart() {
    const rows=data.timeline||[], values=rows.map(r=>money?r.cost:r.tokens);
    const max=Math.max(0,...values.map(x=>x||0)), peak=max>0?Math.pow(10,Math.floor(Math.log10(max)))*Math.ceil(max/Math.pow(10,Math.floor(Math.log10(max)))):1;
    const chart=section(money?"Daily estimated API cost":"Processed tokens over time",money?"Known USD cost only · subscription charges differ":"Uncached input + output + cache reads + cache writes");
    if(money && totals.cost===null) return chart.child(text("No price is available for these records. Add exact model rates below to estimate cost.",t.muted,11.5));
    const axis=v_flex().w(46).h(180).flex_none().justify_between().items_end().pr(6)
      .child(text(amount(peak,money),t.dim,10)).child(text(amount(peak/2,money),t.dim,10)).child(text(money?"$0":"0",t.dim,10));
    const plot=div().id("usage-plot").h(180).min_w(0).flex_1().relative();
    for(const y of [0,50,100]) {
      const path=PathBuilder.stroke(.7).move_to("0%",y+"%").line_to("100%",y+"%").build();
      plot.child(window.paint_path(path,t.border).absolute().top(0).left(0).size_full());
    }
    const points=plotPoints(values,peak), area=PathBuilder.fill().move_to("0%","100%");
    for(const [x,y] of points)area.line_to(x+"%",y+"%");
    area.line_to("100%","100%").close();
    plot.child(window.paint_path(area.build(),Background.solid(t.accent).opacity(.10)).absolute().top(0).left(0).size_full());
    const colors=[t.accent,t.foreground,t.blocked,t.muted,t.solid,t.dim];
    const seriesStyle=provider=>Math.max(0,["claude","codex","pi","opencode","gemini","copilot"].indexOf(provider));
    const stroke=(index,width)=>{const line=PathBuilder.stroke(width);if(index)line.dash_array([Math.max(2,7-index),index+2]);return line;};
    for(const provider of data.providers||[]) {
      const index=seriesStyle(provider.key),line=stroke(index,1.8);
      const series=plotPoints(rows.map(r=>money?r.series?.[provider.key]?.cost:r.series?.[provider.key]?.tokens),peak);
      series.forEach(([x,y],i)=>i?line.line_to(x+"%",y+"%"):line.move_to(x+"%",y+"%"));
      plot.child(window.paint_path(line.build(),colors[index%colors.length]).absolute().top(0).left(0).size_full());
    }
    chart.child(h_flex().gap(2).child(axis).child(plot));
    const date=value=>value?.includes("T")?value.slice(5,16).replace("T"," "):value?.slice(5)||"";
    chart.child(h_flex().pl(48).justify_between().child(text(date(rows[0]?.key),t.dim,10))
      .child(text(date(rows[Math.floor(rows.length/2)]?.key),t.dim,10)).child(text(date(rows.at(-1)?.key),t.dim,10)));
    chart.child(text("Shaded area: selected total · Lines: individual providers",t.muted,10.5));
    chart.child(h_flex().gap(5).flex_wrap().children((data.providers||[]).map(p=>{
      const index=seriesStyle(p.key),sample=stroke(index,2).move_to("0%","50%").line_to("100%","50%").build();
      return button("usage-legend-"+p.key,providerName(p.key)+" · "+amount(money?p.cost:p.tokens,money),cx=>reload(cx,{usageProvider:p.key}),{agent:p.key,outline:true,label:providerName(p.key)+"; "+amount(money?p.cost:p.tokens,money)+"; line pattern "+(index+1)})
        .child(window.paint_path(sample,colors[index]).w(18).h(8).flex_none());
    })));
    return chart;
  }
  function limits() {
    const box=section("Recorded provider limits","Local snapshots only. Refresh reads history; it does not contact your account.");
    const snapshots=new Map();
    for(const item of data.limits||[]) {const key=item.provider+":"+item.scope+":"+item.window;if(!snapshots.has(key))snapshots.set(key,item);}
    if(!snapshots.size)box.child(text("No limit snapshot is recorded for this selection.",t.muted,12));
    for(const item of snapshots.values()) {
      const remaining=Math.max(0,100-item.used), age=Math.max(0,(Date.now()-Date.parse(item.at))/3600000);
      const profiles=(item.profiles||[]).map(id=>v.data.profiles.find(p=>p.id===id)?.label||id).join(", ");
      box.child(v_flex().gap(7).py(5).child(h_flex().gap(6).items_center().child(agentIcon(item.provider))
        .child(text(providerName(item.provider)+" · "+(item.minutes>=1440?amount(item.minutes/1440)+" days":amount(item.minutes)+" min"),t.foreground,11.5).flex_1())
        .child(text(remaining.toFixed(0)+"% left",t.foreground,11.5).font_medium()))
        .child(text(profiles||"Local profile",t.muted,10.5))
        .child(div().h(6).rounded(3).bg(t.raised).child(div().h_full().w(remaining+"%").rounded(3).bg(t.accent)))
        .child(text("Recorded "+item.at.slice(0,16).replace("T"," ")+" UTC · "+(age>1?Math.floor(age)+"h old":"under 1h old"),t.muted,10.5))
        .child(text("Reset reported: "+item.resetsAt.slice(0,16).replace("T"," ")+" UTC",t.muted,10.5)));
    }
    box.child(text("Claude, Pi, OpenCode, Gemini and Copilot live limits are unavailable here. Account-wide limits cannot be inferred from token totals.",t.muted,11));
    return box;
  }
  if(metric==="limits")body.child(limits());
  else {
    const headline=money?amount(totals.cost,true):amount(totals.tokens);
    const coverage=totals.pricedEvents+" / "+totals.events+" events priced";
    body.child(pair(card(money?"KNOWN EST. COST":"PROCESSED TOKENS",headline,money?coverage:amount(totals.events)+" recorded usage events"),
      card("SESSIONS",amount(totals.sessions),"With recorded usage in this period")));
    const metrics=[card("UNCACHED INPUT",amount(totals.input)),card("OUTPUT",amount(totals.output)),
      card("CACHE HIT RATE",totals.cacheHit===null?"Unavailable":(totals.cacheHit*100).toFixed(1)+"%","Cache reads / read input"),
      card("CACHE READ",amount(totals.cacheRead),totals.savings!==null?amount(totals.savings,true)+" est. savings at local rates":"Tokens served from cache")];
    if(wide)body.child(h_flex().gap(10).items_stretch().children(metrics));else{body.child(pair(metrics[0],metrics[1]));body.child(pair(metrics[2],metrics[3]));}
    if(money)body.child(text("API-equivalent USD estimate, not your bill. "+coverage+". Unknown prices are excluded, never treated as free.",totals.pricedEvents<totals.events?t.blocked:t.muted,11.5));
    body.child(drawChart());
    const mix=section("Tokens by type");
    const channels=[["input","Uncached input",t.accent],["cacheRead","Cache read",t.muted],["cacheWrite","Cache write",t.blocked],["output","Output",t.foreground]];
    mix.child(h_flex().h(7).rounded(3).overflow_hidden().bg(t.raised).children(channels.filter(([key])=>totals[key]>0).map(([key,,color])=>div().h_full().w((totals[key]/Math.max(1,totals.tokens)*100)+"%").bg(color))));
    mix.child(h_flex().gap(9).flex_wrap().children(channels.map(([key,name,color])=>h_flex().gap(5).items_center().child(div().w(6).h(6).rounded(2).bg(color)).child(text(name+" "+amount(totals[key]),t.muted,11)))));
    body.child(mix);
    const avg=data.averages||{};
    body.child(section("Per session","Includes archived and hidden histories with recorded usage; empty sessions are excluded.")
      .child(h_flex().gap(4).flex_wrap().child(button("usage-average","Average",cx=>reload(cx,{usageTrim:false}),{selected:!v.usageTrim}))
        .child(button("usage-trim","Trim 10%",cx=>reload(cx,{usageTrim:true}),{selected:v.usageTrim})))
      .child(text(amount(avg.tokens)+" tokens · "+amount(avg.events)+" usage events · "+(avg.cost===null?"Cost unavailable":amount(avg.cost,true)+" est. cost"),t.foreground,12.5))
      .child(text(amount(avg.sessions)+" sessions in average"+(avg.trimmed?" · "+avg.trimmed+" trimmed from both tails":""),t.muted,10.5)));
    const breakdown=section("Breakdown");
    breakdown.child(h_flex().gap(3).flex_wrap().children([["models","Model"],["timeline","Day / hour"],["projects","Project"]].map(([key,label])=>button("usage-breakdown-"+key,label,cx=>{v.usageBreakdown=key;cx.notify();},{selected:v.usageBreakdown===key}))));
    const rows=(data[v.usageBreakdown]||[]).filter(r=>v.usageBreakdown!=="timeline" || r.events>0);
    if(!rows.length)breakdown.child(text("No recorded usage in this range. Refresh, or choose another profile or period.",t.muted,11.5));
    for(const [index,row] of rows.entries()) {
      const model=v.usageBreakdown==="models", project=v.usageBreakdown==="projects";
      const duplicates=project && rows.filter(r=>r.label===row.label).length>1;
      const key=model?row.key.slice(row.key.indexOf(":")+1):project?(row.label||row.key)+(duplicates?" · "+row.key.slice(0,6):""):row.key;
      const line=v_flex().py(7).gap(5).border_b_1().border_color(t.border);
      line.child(h_flex().gap(6).items_center().when(model,e=>e.child(agentIcon(row.key.slice(0,row.key.indexOf(":")))))
        .child(text(key,t.foreground,12).truncate().flex_1()).child(text(amount(money?row.cost:row.tokens,money),t.foreground,12).font_medium()));
      line.child(h_flex().gap(6).flex_wrap().items_center().child(text(amount(row.events)+" events · "+(totals.tokens?row.tokens/totals.tokens*100:0).toFixed(1)+"% of tokens",t.muted,10.5))
        .child(div().flex_1()).when(model,e=>e.child(button("usage-model-"+index,"Filter",cx=>reload(cx,{usageModel:row.key}),{height:23,outline:true}))
          .child(button("usage-rate-"+index,row.pricedEvents===row.events?"Rates":"Add rate",cx=>v.editUsageRate(row.key,cx),{height:23,outline:true}))));
      if(row.cost!==null || row.pricedEvents<row.events)line.child(text(amount(row.cost,true)+" known est. cost · "+row.pricedEvents+"/"+row.events+" events priced",t.muted,10.5));
      breakdown.child(line);
    }
    if(data.breakdownOmitted)breakdown.child(text(data.breakdownOmitted+" further model/project groups omitted; narrow the selection.",t.blocked,11));
    body.child(breakdown);
  }
  function prices() {
    const rates=section("Local model rates","Exact provider/model prices in USD per million tokens. Check your provider's pricing; no rate is downloaded automatically.");
    rates.child(h_flex().gap(3).flex_wrap().children(["claude","codex","pi","opencode","gemini"].map(p=>button("usage-rate-provider-"+p,providerName(p),cx=>{v.usageRateProvider=p;cx.notify();},{selected:(v.usageRateProvider||"claude")===p,agent:p}))));
    rates.child(text("Model identifier",t.muted,11)).child(input(v.usageFields.model,"usage-rate-model"));
    for(const [name,label] of [["input","Uncached input"],["output","Output (includes reasoning)"],["cacheRead","Cache read"],["cacheWrite","Cache write"]])
      rates.child(h_flex().gap(9).items_center().child(text(label,t.muted,11).flex_1()).child(input(v.usageFields[name],"usage-rate-"+name).w(128)));
    rates.child(text("Enter 0 explicitly only for a known free channel. A local rate overrides provider-reported cost for that exact model.",t.muted,11));
    rates.child(h_flex().gap(6).flex_wrap().child(button("usage-save-rate","Save rates",cx=>v.saveUsageRate(cx),{primary:true}))
      .child(button("usage-remove-rate","Remove local rate",cx=>v.saveUsageRate(cx,true),{outline:true}))
      .child(button("usage-close-rates","Close",cx=>{v.usagePrices=false;cx.notify();},{outline:true})));
    for(const key of Object.keys(data.rates||{}))rates.child(button("usage-edit-"+key,key,cx=>v.editUsageRate(key,cx),{outline:true}));
    return rates;
  }
  const coverage=section("Coverage & privacy");
  coverage.child(text(data.sources+" configured local histories · "+data.pending+" awaiting refresh",data.pending?t.blocked:t.muted,11.5));
  if(!data.sources)coverage.child(text("Add an enabled profile in History settings, then refresh recorded usage.",t.muted,11));
  if(data.pending || !data.lastRefresh)coverage.child(button("usage-refresh-records","Refresh recorded usage",cx=>v.loadUsage(cx,true),{primary:true,icon:"refresh"}));
  for(const [reason,count] of Object.entries(data.coverage||{}))coverage.child(text(count+" · "+reason,t.blocked,11));
  coverage.child(text(data.scope,t.muted,10.5));
  coverage.child(text("Numeric usage stays in encrypted Hub state. Original histories are read-only. No credentials, telemetry or network requests.",t.muted,10.5));
  if(data.lastRefresh)coverage.child(text("Last refresh "+data.lastRefresh.slice(0,16).replace("T"," ")+" UTC",t.dim,10));
  coverage.child(button("usage-clear-cache","Clear numeric usage cache",cx=>v.loadUsage(cx,false,{action:"usage-clear"}),{outline:true}));
  body.child(coverage);
  return pane.child(body);
}
