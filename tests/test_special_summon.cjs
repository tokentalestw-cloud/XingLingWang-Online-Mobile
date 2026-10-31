const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'static/special_summon.js'),'utf8'),game=fs.readFileSync(path.join(root,'static/game_v8.js'),'utf8');
const scope={};vm.runInNewContext(source,{window:scope,Uint8Array,Float32Array});const api=scope.XLWSpecialSummon;let tests=0;
for(const id of ['R-VLG-0012','ASSR-VLG-0012','SSR-VLG-0012']){assert.equal(api.match({id}).key,'yuki');tests++;}
for(const card of [null,{id:'R-VLG-0013',name:'座敷童子',deck:'妖怪村莊'},{name:'雪女',deck:'藝術品'},{name:'超級雪女',deck:'妖怪村莊'}]){assert.equal(api.match(card),null);tests++;}
assert.equal(api.match({name:'雪女',faction:'妖怪村莊'}).key,'yuki');tests++;
const flakes=api.snowParticles(844,390,64,()=>.5);assert.equal(flakes.length,64);assert.ok(flakes.every(f=>f.x>=0&&f.x<=844&&f.y>=0&&f.y<=390&&f.speed>0&&f.size>0));tests++;
assert.ok(api.snowParticles(844,390,1,()=>.9)[0].speed>api.snowParticles(844,390,1,()=>.1)[0].speed);tests++;

// Exercise real fallback lifecycle without GPU/video: skip, deadline, hidden page,
// repeated calls, and cancellation must all settle and remove presentation state.
function fixture(reduced=false){
 let id=0,raf=0;const timers=new Map(),events=new Map(),removed=new Set(),nodes=[];
 const context2d={translate(){},rotate(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},setTransform(){},save(){},restore(){},clearRect(){},drawImage(){}};
 const node=tag=>{const n={tag,dataset:{},style:{},classList:{add(){},remove(){}},clientWidth:844,clientHeight:390,isConnected:true,setAttribute(){},appendChild(child){nodes.push(child);},remove(){this.isConnected=false;removed.add(this);},addEventListener(){},focus(){this.focused=true;},getContext(type){return type==='2d'?context2d:null;},querySelector(selector){return this.parts[selector];},querySelectorAll(selector){return selector==='.xlw-yuki-snow'?this.snow:[];}};return n;};
 const doc={hidden:false,activeElement:node('old'),body:{appendChild:n=>nodes.push(n)},createElement(tag){const n=node(tag);if(tag==='div'){n.parts={};for(const key of ['.xlw-yuki-owner','.xlw-yuki-performer','.xlw-yuki-poster','.xlw-yuki-video','button'])n.parts[key]=node(key.includes('video')?'canvas':'element');n.snow=[node('canvas'),node('canvas')];}return n;},addEventListener:(name,fn)=>events.set(name,fn),removeEventListener:(name)=>events.delete(name)};
 const g={document:doc,devicePixelRatio:1,matchMedia:()=>({matches:reduced}),addEventListener:(name,fn)=>events.set(name,fn),removeEventListener:name=>events.delete(name),xlwPlaySFX(){}};
 vm.runInNewContext(source,{window:g,document:doc,Float32Array,setTimeout:(fn,ms)=>{const key=++id;timers.set(key,{fn,ms});return key;},clearTimeout:key=>timers.delete(key),requestAnimationFrame:()=>++raf,cancelAnimationFrame(){}});
 return {api:g.XLWSpecialSummon,doc,nodes,timers,events,removed,run(ms){const timer=[...timers.values()].find(t=>t.ms===ms);assert.ok(timer,'deadline '+ms);timer.fn();}};
}
module.exports=(async()=>{
 for(const how of ['skip','deadline','hidden','cancel']){const f=fixture();const p=f.api.play({id:'R-VLG-0012'},{zone:'player_front',idx:0});assert.equal(f.api.play({id:'R-VLG-0012'},{zone:'player_front',idx:0}),p);const overlay=f.nodes[0];assert.equal(overlay.dataset.renderMode,'poster');if(how==='skip'){overlay.parts.button.onclick();f.run(240);}if(how==='deadline'){f.run(4500);f.run(240);}if(how==='hidden'){f.doc.hidden=true;f.events.get('visibilitychange')();}if(how==='cancel')f.api.cancel();assert.equal(await p,true);assert.equal(overlay.isConnected,false);assert.equal(f.events.size,0);assert.equal(f.timers.size,0);assert.equal(f.doc.activeElement.focused,true);tests++;}
 const reduced=fixture(true);const p=reduced.api.play({id:'R-VLG-0012'});reduced.run(1700);reduced.run(80);assert.equal(await p,true);tests++;
 assert.equal(await api.play({name:'其他卡'}),false);tests++;

 // Use the actual special-card branch in the game, with a deferred renderer.
 const start=game.indexOf('async function playTributeSummonAnimation('),end=game.indexOf("  window.xlwPlaySFX?.",start);
 const hook=game.slice(start,end)+'\n}';
 for(const reject of [false,true]){const card={id:'R-VLG-0012'},field={player_front:[{card}]},before=JSON.stringify(field);let release;const renderPromise=new Promise((yes,no)=>release=reject?()=>no(Error('simulated media failure')):yes);const states=[];const w={XLW_animatingTributeSlots:new Set(),XLWSpecialSummon:{match:api.match,play:()=>renderPromise}};const ctx={window:w,field,render:()=>states.push(w.XLW_animatingTributeSlots.size),console:{warn(){}}};vm.runInNewContext(hook,ctx);const pending=ctx.playTributeSummonAnimation('player_front',0,true);assert.equal(w.XLW_animatingTributeSlots.size,1);release();await pending;assert.equal(w.XLW_animatingTributeSlots.size,0);assert.equal(JSON.stringify(field),before);assert.deepEqual(states,[1,0]);tests++;}
 new vm.Script(game);console.log(`${tests} special-card matching, snow depth, playback cleanup and game-state isolation checks: PASS`);
})();
