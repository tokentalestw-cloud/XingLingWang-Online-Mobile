const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');const slice=(a,b)=>{const i=source.indexOf(a),j=source.indexOf(b,i+1);assert.ok(i>=0&&j>i);return source.slice(i,j);};
const card=(id,props={})=>({id,name:id,type:'unit',undead:true,_xlwInstanceId:id,...props});
function fixture(own=true){const g={console,structuredClone,field:Object.fromEntries(['player_front','player_back','enemy_front','enemy_back'].map(z=>[z,Array(5).fill(null)])),graveyard:[],enemyGraveyard:[],deck:[],hand:[],turn:6,isMyTurn:own,isMultiplayer:false,logBattle(){},render(){},isUnitSilenced:u=>!!u.silenced,xlwIsUndeadCard:c=>!!c?.undead,xlwFactionDecisionKey:(u,z,r,n)=>[u.card.id,r,n].join(':'),xlwBlueStarRequirement:c=>c.blocked?'blocked':'',xlwResolvePG2Summon:async()=>{},sendFullGameStateToOpponent(){}};g.window=g;g.XLW_ENEMY={grave:g.enemyGraveyard};vm.createContext(g);vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/duel_consistency.js'),'utf8'),g);vm.runInContext(slice('// Coffin Ship loads physical','// End Coffin Ship loading.')+slice('// Coffin Ship replaces the ordinary','async function kidnapCard('),g);g.zone=(own?'player':'enemy')+'_front';g.ship={card:card('SR-SKT-0050'),summonedTurn:5};g.field[g.zone][0]=g.ship;g.grave=()=>own?g.graveyard:g.XLW_ENEMY.grave;g.setGrave=a=>{if(own)g.graveyard=a;else g.XLW_ENEMY.grave=g.enemyGraveyard=a;};g.xlwChooseFactionAction=async(local,key,title,msg,options)=>options[0].value;g.load=()=>g.xlwLoadCoffin(g.ship,g.zone,0,own);g.release=()=>g.cleanUnitLeavingField(g.ship,g.zone);return g;}
for(const own of [true,false])for(const count of [0,1,2,3,4])test(`ship loads at most three physical undead units from ${count} candidates: ${own}`,async()=>{
 const g=fixture(own);g.setGrave([...Array.from({length:count},(_,i)=>card('u'+i)),card('spell',{type:'magic'}),card('living',{undead:false})]);let calls=0;g.xlwChooseFactionAction=async(local,key,title,msg,options)=>{calls++;assert.equal(local,own);assert.ok(options.every(o=>o.card.type==='unit'&&o.card.undead));return 0;};await g.load();assert.equal(g.ship.kidnappedCards.length,Math.min(3,count));assert.equal(g.grave().length,Math.max(0,count-3)+2);assert.equal(calls,Math.min(3,count));assert.equal(g.XLW_deckTopPending.size,0);
});
for(const mode of ['cloned','removed','source-left','reset','changed-type'])test(`ship revalidates loading targets after each choice: ${mode}`,async()=>{
 const g=fixture(),target=card('target');g.setGrave([target]);g.xlwChooseFactionAction=async()=>{if(mode==='cloned')g.setGrave(structuredClone(g.grave()));if(mode==='removed')g.setGrave([]);if(mode==='changed-type')target.type='magic';if(mode==='source-left')g.field[g.zone][0]=null;if(mode==='reset')g.XLW_deckTopPending.clear();return 0;};await g.load();assert.equal(g.ship.kidnappedCards.length,mode==='cloned'?1:0);assert.equal(g.XLW_deckTopPending.size,0);
});
test('ship preserves a borrowed captive holder and never exceeds its three-card capacity',async()=>{
 const g=fixture();g.ship.kidnappedCards=[card('old-a'),card('old-b')];g.setGrave([card('borrowed',{originalOwner:'enemy'}),card('unused')]);await g.load();await g.load();assert.equal(g.ship.kidnappedCards.length,3);assert.equal(g.ship.kidnappedCards[2].originalOwner,'enemy');assert.equal(g.grave()[0].id,'unused');
});
test('duplicate loading cannot open a second chooser',async()=>{
 const g=fixture();g.setGrave([card('a')]);let done,calls=0;g.xlwChooseFactionAction=()=>{calls++;return new Promise(r=>done=r);};const first=g.load();await Promise.resolve();assert.equal(await g.load(),false);done(0);await first;assert.equal(calls,1);assert.equal(g.ship.kidnappedCards.length,1);
});
for(const own of [true,false])test(`all three captives get separate placement decisions and enter tapped: ${own}`,async()=>{
 const g=fixture(own),owner=own?'player':'enemy';g.ship.kidnappedCards=[0,1,2].map(i=>card('held'+i,{originalOwner:owner}));const keys=[];g.xlwChooseFactionAction=async(local,key,title,msg,options)=>{assert.equal(local,own);assert.equal(title,'棺材船：釋放單位');keys.push(key);return 0;};await g.release();assert.equal(g.ship.kidnappedCards.length,0);assert.equal(keys.length,3);assert.equal(new Set(keys).size,3);for(let i=0;i<3;i++){assert.equal(g.field[g.zone][i].card.id,'held'+i);assert.equal(g.field[g.zone][i].tapped,true);}assert.equal(g.grave().length,0);assert.equal(g.XLW_deckTopPending.size,0);
});
test('released cards return to their own holders boards',async()=>{
 const g=fixture();g.ship.kidnappedCards=[card('mine',{originalOwner:'player'}),card('theirs',{originalOwner:'enemy'})];const controllers=[];g.xlwChooseFactionAction=async(local,key,title,msg,options)=>{controllers.push(local);return 0;};await g.release();assert.equal(g.field.player_front[0].card.id,'mine');assert.equal(g.field.enemy_front[0].card.id,'theirs');assert.deepEqual(controllers,[true,false]);
});
test('a full board puts all three captives into the current grave',async()=>{
 const g=fixture();g.ship.kidnappedCards=[0,1,2].map(i=>card('held'+i,{originalOwner:'player'}));for(const z of ['player_front','player_back'])g.field[z].fill({card:card('occupied')});g.xlwChooseFactionAction=()=>assert.fail('No free slots');await g.release();assert.equal(g.grave().length,3);
});
test('front priority is recomputed separately for every released captive',async()=>{
 const g=fixture();g.field.player_front.fill({card:card('occupied')});g.field.player_front[0]=g.ship;g.ship.kidnappedCards=[0,1,2].map(i=>card('held'+i,{originalOwner:'player'}));const rows=[];g.xlwChooseFactionAction=async(local,key,title,msg,options)=>{rows.push(options[0].boardTarget.zone);return 0;};await g.release();assert.deepEqual(rows,['player_front','player_back','player_back']);
});
for(const mode of ['occupied','blue-condition-changed','front-freed'])test(`release cannot overwrite or use a stale invalid placement: ${mode}`,async()=>{
 const g=fixture(),held=card('held',{originalOwner:'player'});g.ship.kidnappedCards=[held];if(mode==='front-freed'){g.field.player_front.fill({card:card('occupied')});g.field.player_back[0]=g.ship;g.zone='player_back';}g.xlwChooseFactionAction=async(local,key,title,msg,options)=>{const t=options[0].boardTarget;if(mode==='occupied')g.field[t.zone][t.idx]={card:card('new-unit')};if(mode==='blue-condition-changed')held.blocked=true;if(mode==='front-freed'){assert.equal(t.zone,'player_back');g.field.player_front[1]=null;}return 0;};
 await g.release();assert.equal(g.grave()[0],held);
});
test('slot confirmation after a new game cannot place an old captive',async()=>{
 const g=fixture();g.ship.kidnappedCards=[card('held',{originalOwner:'player'})];g.xlwChooseFactionAction=async()=>{g.XLW_deckTopPending.clear();return 0;};await g.release();assert.equal(g.field.player_front.filter(Boolean).length,0);assert.equal(g.grave().length,0);
});
test('silenced ship retains ordinary one-captive release',async()=>{
 const g=fixture();g.ship.silenced=true;g.ship.kidnappedCards=[0,1,2].map(i=>card('held'+i,{originalOwner:'player'}));await g.release();assert.equal(g.field.player_front.filter(Boolean).length,1);assert.equal(g.grave().length,2);
});
test('a grave officer still sends captives to grave instead of summoning',async()=>{
 const g=fixture();g.field.player_back[0]={card:card('SSSR-NMS-0050')};g.ship.kidnappedCards=[0,1,2].map(i=>card('held'+i,{originalOwner:'player'}));await g.release();assert.equal(g.field.player_front.filter(Boolean).length,0);assert.equal(g.grave().length,3);
});
test('repeated leave callbacks cannot release captives twice',async()=>{
 const g=fixture();g.ship.kidnappedCards=[0,1,2].map(i=>card('held'+i,{originalOwner:'player'}));await Promise.all([g.release(),g.release()]);assert.equal(g.field.player_front.filter(Boolean).length,3);assert.equal(g.grave().length,0);
});
test('an invalid legacy spell captive is buried rather than summoned as a unit',async()=>{
 const g=fixture();g.ship.kidnappedCards=[card('spell',{type:'magic',originalOwner:'player'})];await g.release();assert.equal(g.grave()[0].id,'spell');assert.equal(g.field.player_front.filter(Boolean).length,0);
});
test('a released summon trigger replacing the grave cannot strand a later blocked captive',async()=>{
 const g=fixture();g.ship.kidnappedCards=[card('first',{originalOwner:'player'}),card('blocked',{originalOwner:'player',blocked:true})];g.xlwResolvePG2Summon=async()=>g.setGrave([card('fresh')]);await g.release();assert.deepEqual(Array.from(g.grave(),c=>c.id),['fresh','blocked']);
});
test('pending release is cleared before its final online snapshot',async()=>{
 const g=fixture();g.isMultiplayer=true;g.ship.kidnappedCards=[card('held',{originalOwner:'player'})];let size;g.sendFullGameStateToOpponent=()=>size=g.XLW_deckTopPending.size;await g.release();assert.equal(size,0);
});
test('a reset during the first summon hook prevents later old-game placements',async()=>{
 const g=fixture();g.ship.kidnappedCards=[0,1,2].map(i=>card('held'+i,{originalOwner:'player'}));g.xlwResolvePG2Summon=async()=>{g.XLW_deckTopPending.clear();g.field.player_front=Array(5).fill(null);};await g.release();assert.equal(g.field.player_front.filter(Boolean).length,0);assert.equal(g.grave().length,0);
});
test('mirrored ship release asks the holder once per captive and preserves all three placements',async()=>{
 const a=fixture(true),b=fixture(false);for(const [g,owner]of [[a,'player'],[b,'enemy']]){g.ship.kidnappedCards=[0,1,2].map(i=>card('held'+i,{originalOwner:owner}));vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/faction_choices.js'),'utf8'),g);}
 let ac,bc,calls=0;ac=a.XLWFactionChoices.create({choose:async()=>{calls++;return 0;},send:m=>bc.receive(m)});bc=b.XLWFactionChoices.create({choose:()=>assert.fail('Peer must not open owner choices'),send:m=>ac.receive(m)});a.xlwChooseFactionAction=ac.choose;b.xlwChooseFactionAction=bc.choose;await Promise.all([a.release(),b.release()]);assert.equal(calls,3);assert.deepEqual(Array.from(a.field.player_front.filter(Boolean),u=>u.card.id),['held0','held1','held2']);assert.deepEqual(Array.from(b.field.enemy_front.filter(Boolean),u=>u.card.id),['held0','held1','held2']);
});
