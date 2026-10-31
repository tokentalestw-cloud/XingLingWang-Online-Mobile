const assert=require('node:assert/strict'), fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const code=fs.readFileSync(path.join(__dirname,'../static/astral_audio.js'),'utf8');
const storage=new Map([['xlw_sfx_enabled','false']]);
const global={localStorage:{getItem:k=>storage.get(k)??null,setItem:(k,v)=>storage.set(k,v)}};
vm.runInNewContext(code,{window:global,console,Float32Array});
let checks=0;function check(fn){fn();checks++;}
function context(){
  const nodes=[],events=[];
  const param=()=>({value:0,setValueAtTime(v,t){assert.ok(Number.isFinite(v)&&t>=0);events.push(['set',v,t]);},linearRampToValueAtTime(v,t){assert.ok(Number.isFinite(v)&&t>=0);events.push(['linear',v,t]);},exponentialRampToValueAtTime(v,t){assert.ok(v>0&&t>=0);events.push(['exp',v,t]);},cancelScheduledValues(){},setTargetAtTime(v){events.push(['target',v]);}});
  const node=()=>{const n={gain:param(),frequency:param(),Q:param(),threshold:param(),knee:param(),ratio:param(),attack:param(),release:param(),connect(to){this.connected=to;},disconnect(){this.disconnected=true;},start(t){this.started=t;},stop(t){this.stopped=t;}};nodes.push(n);return n;};
  return {currentTime:0,sampleRate:22050,state:'running',destination:{},nodes,events,createGain:node,createBiquadFilter:node,createDynamicsCompressor:node,createOscillator:node,createBufferSource:node,createBuffer:(c,n)=>({getChannelData:()=>new Float32Array(n)})};
}
const settings=()=>({enabled:true,volume:.65,battle:.85,ui:.55});
for(const name of Object.keys(global.XLWAudio.bank))check(()=>{const ctx=context(),engine=global.XLWAudio.createEngine(ctx,settings());assert.equal(engine.play(name),true,name);assert.ok(engine.activeVoices>0&&engine.activeVoices<=6,name);assert.equal(engine.play(name),false,'duplicate '+name);engine.stop();assert.equal(engine.activeVoices,0);});
check(()=>{const ctx=context(),engine=global.XLWAudio.createEngine(ctx,settings());assert.equal(engine.play('missing'),false);assert.equal(engine.activeVoices,0);});
check(()=>{const ctx=context(),s=settings(),engine=global.XLWAudio.createEngine(ctx,s);s.enabled=false;assert.equal(engine.play('attack'),false);s.enabled=true;s.volume=0;assert.equal(engine.play('attack'),false);s.volume=.6;ctx.state='suspended';assert.equal(engine.play('attack'),false);});
check(()=>{const ctx=context(),engine=global.XLWAudio.createEngine(ctx,settings());engine.play('tribute');assert.equal(engine.play('summon'),false);ctx.currentTime=.7;assert.equal(engine.play('summon'),true);});
check(()=>{const ctx=context(),engine=global.XLWAudio.createEngine(ctx,settings());engine.play('attack');engine.play('victory');assert.equal(engine.activeVoices,6);assert.equal(engine.play('spell'),false);ctx.currentTime=2.6;assert.equal(engine.play('spell'),true);});
check(()=>{const ctx=context(),engine=global.XLWAudio.createEngine(ctx,settings());for(let i=0;i<100;i++){ctx.currentTime+=.3;engine.play('attack');}assert.ok(engine.activeVoices<=24);});
check(()=>{const ctx=context(),engine=global.XLWAudio.createEngine(ctx,settings());engine.play('spell');for(const n of ctx.nodes)if(n.onended)n.onended();assert.equal(engine.activeVoices,0);});
check(()=>{const ctx=context(),s=settings(),engine=global.XLWAudio.createEngine(ctx,s);engine.play('draw');assert.ok(ctx.events.some(e=>e[0]==='set'&&e[1]===0));assert.ok(ctx.events.some(e=>e[0]==='linear'&&e[1]===0));s.enabled=false;engine.setVolume();assert.ok(ctx.events.some(e=>e[0]==='target'&&e[1]===0));});
check(()=>{const ctx=context();ctx.state='suspended';const engine=global.XLWAudio.createEngine(ctx,settings(),{offline:true});assert.equal(engine.play('summon'),true);});
check(()=>{assert.equal(global.XLWAudio.settings.enabled,false);assert.equal(global.XLWAudio.settings.volume,.65);assert.equal(global.xlwPlaySFX('draw'),false);});
check(()=>{const bad={localStorage:{getItem(){throw Error('blocked');}}};vm.runInNewContext(code,{window:bad});assert.equal(bad.XLWAudio.settings.enabled,true);});
check(()=>{const handlers={},doc={hidden:false,addEventListener:(name,fn)=>handlers[name]=fn,getElementById:()=>null};let ctx;
 const g={document:doc,addEventListener(){},AudioContext:function(){ctx=context();ctx.resume=()=>{ctx.state='running';return Promise.resolve();};ctx.suspend=()=>{ctx.state='suspended';return Promise.resolve();};return ctx;}};
 vm.runInNewContext(code,{window:g,document:doc});assert.equal(g.XLWAudio.diagnostics.state,'locked');assert.equal(g.xlwPlaySFX('attack'),false);handlers.pointerdown();assert.equal(g.xlwPlaySFX('attack'),true);doc.hidden=true;handlers.visibilitychange();assert.equal(g.XLWAudio.diagnostics.activeVoices,0);assert.equal(g.xlwPlaySFX('spell'),false);doc.hidden=false;assert.equal(g.xlwPlaySFX('spell'),false);handlers.pointerdown();assert.equal(g.xlwPlaySFX('spell'),true);
});
check(()=>{const handlers={},doc={hidden:false,addEventListener:(name,fn)=>handlers[name]=fn,getElementById:()=>null};const g={document:doc,addEventListener(){},XLW_gameInProgress:true,AudioContext:function(){return context();}};
 vm.runInNewContext(code,{window:g,document:doc});handlers.pointerdown();const snap=n=>({player:{units:{a:{count:n}}},enemy:{units:{}}});g.XLWAudio.observeBattle(snap(3),true);assert.equal(g.XLWAudio.diagnostics.activeVoices,0);g.XLWAudio.observeBattle(snap(4),false);assert.equal(g.XLWAudio.diagnostics.activeVoices,4);g.XLWAudio.stop();g.XLWAudio.observeBattle(snap(4),false);assert.equal(g.XLWAudio.diagnostics.activeVoices,0);g.xlwGetBattleFeedbackState=()=>({multi:true,active:true,ready:false});assert.equal(g.xlwPlaySFX('spell'),false);
});
console.log(`${checks} audio synthesis, mixing, deduplication, cleanup and preference checks: PASS`);
