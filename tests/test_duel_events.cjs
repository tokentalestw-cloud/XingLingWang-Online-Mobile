const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/duel_events.js'),'utf8');
const feedback=fs.readFileSync(path.join(__dirname,'../static/battle_feedback.js'),'utf8');
function create(){
  const timers=new Map();let id=0;
  const context=vm.createContext({setTimeout(fn){timers.set(++id,fn);return id;},clearTimeout(key){timers.delete(key);},Date,console});
  vm.runInContext(feedback,context);vm.runInContext(source,context);
  return {api:context.XLWDuelEvents,timers};
}
const card=(id,name=id)=>({id,name,image:'/static/card_images/a.jpeg'});
const unit=id=>({card:card(id),tapped:false,attacking:false});
function state(){return {active:true,turn:1,phase:'召喚階段',myTurn:true,sides:{
  player:{front:Array(5).fill(null),back:Array(5).fill(null),grave:[],exile:[],extra:[],hand:4,deck:16},
  enemy:{front:Array(5).fill(null),back:Array(5).fill(null),grave:[],exile:[],extra:[],hand:4,deck:16}}};}
function changes(api,raw,change){const before=api.capture(raw);change(raw);return api.diff(before,api.capture(raw));}
test('public summon, movement, attacks, posture and equipment are observed without mutating rules',()=>{
  const {api}=create(),raw=state();
  let events=changes(api,raw,s=>s.sides.player.front[2]=unit('a'));
  assert.equal(events[0].kind,'summon');assert.match(events[0].detail,/第 3 欄/);
  events=changes(api,raw,s=>{s.sides.player.back[2]=s.sides.player.front[2];s.sides.player.front[2]=null;});
  assert.deepEqual(Array.from(events,e=>e.kind),['move']);
  events=changes(api,raw,s=>{s.sides.player.back[2].attacking=true;s.sides.player.back[2].target={zone:'enemy_front',idx:2};});
  assert.equal(events[0].kind,'attack');
  events=changes(api,raw,s=>{s.sides.player.back[2].attacking=false;s.sides.player.back[2].tapped=true;});
  assert.equal(events[0].kind,'tap');
  events=changes(api,raw,s=>{s.sides.player.back[2].atkModifier=3;s.sides.player.back[2].equipments=['價值拳'];});
  assert.deepEqual(Array.from(events,e=>e.kind),['stats','equip']);
  const unchanged=JSON.stringify(raw);api.observe(raw);assert.equal(JSON.stringify(raw),unchanged);
});
test('grave/exile changes preserve identical copies and do not double report field departure',()=>{
  const {api}=create(),raw=state();raw.sides.enemy.front[0]=unit('same');raw.sides.enemy.front[1]=unit('same');
  let events=changes(api,raw,s=>{s.sides.enemy.front[1]=null;s.sides.enemy.grave.push(card('same'));});
  assert.deepEqual(Array.from(events,e=>e.kind),['grave']);assert.equal(events[0].side,'enemy');
  events=changes(api,raw,s=>s.sides.enemy.grave.push(card('same')));
  assert.equal(events.length,1);assert.equal(events[0].kind,'grave');
  events=changes(api,raw,s=>{s.sides.enemy.front[0]=null;s.sides.enemy.exile.push(card('same'));});
  assert.equal(events[0].kind,'exile');assert.equal(events.length,1);
});
test('hidden hands and decks remain counts, including draw and extra-zone transfer',()=>{
  const {api}=create(),raw=state();raw.secret={hand:[card('secret')]};
  let events=changes(api,raw,s=>{s.sides.enemy.hand+=2;s.sides.enemy.deck-=2;});
  assert.equal(events[0].kind,'draw');assert.match(events[0].detail,/2 張/);
  assert.equal(events[0].card,null);assert(!JSON.stringify(api.capture(raw)).includes('secret'));
  raw.sides.enemy.extra=[card('extra')];
  events=changes(api,raw,s=>{s.sides.enemy.extra=[];s.sides.enemy.hand++;});
  assert.deepEqual(Array.from(events,e=>e.kind),['hand','extra']);
});
test('duplicate renders, quiet recovery and mulligan create no phantom actions',()=>{
  const {api}=create(),raw=state();api.observe(raw);api.observe(raw);
  assert.equal(api.diagnostics().history,0);
  assert.equal(api.diff(api.capture(raw),api.capture({...raw,quiet:true})).length,0);
  raw.sides.player.front[0]=unit('a');api.observe({...raw,quiet:true});api.observe({...raw,quiet:false});
  assert.equal(api.diagnostics().history,0);
  raw.phase='戰術佈陣';api.observe(raw);assert.equal(api.diagnostics().history,1);
  api.reset();assert.equal(api.diagnostics().history,0);
});
test('both perspectives derive matching public events from the same resolved state',()=>{
  const {api}=create(),a=state(),b=state();
  const fromA=changes(api,a,s=>{s.sides.player.front[3]=unit('x');s.sides.player.grave.push(card('spell'));});
  const fromB=changes(api,b,s=>{s.sides.enemy.front[3]=unit('x');s.sides.enemy.grave.push(card('spell'));});
  assert.deepEqual(Array.from(fromA,e=>[e.kind,e.card.id,e.detail]),Array.from(fromB,e=>[e.kind,e.card.id,e.detail]));
  assert(fromA.every(e=>e.side==='player'));assert(fromB.every(e=>e.side==='enemy'));
});
test('long games have bounded display queues and no per-event network or replay delay',()=>{
  const {api,timers}=create(),raw=state();api.observe(raw);
  for(let i=0;i<1000;i++){raw.sides.player.front[0]=unit('card-'+i);api.observe(raw);}
  assert(api.diagnostics().queued<=6);assert(api.diagnostics().history<=24);assert(timers.size<=1);
  assert(!/WebSocket|\.send\(/.test(source),'presentation must not add network traffic');
  assert(!/await/.test(source),'render/replay must not await the presentation queue');
  api.reset();assert.equal(timers.size,0);
});
test('effect log snapshots avoid replays and reverse player perspective',()=>{
  const {api}=create();api.observe(state());
  const lines=['T1 | 我方【芭蕉樹】效果：召喚芭蕉精'];
  api.syncLogs(lines);const first=api.diagnostics().history;assert.equal(first,1);
  api.syncLogs(lines);assert.equal(api.diagnostics().history,first);
  api.syncLogs(['T2 | 我方【芭蕉樹】效果：召喚芭蕉精'],true);assert.equal(api.diagnostics().history,first);
});
