const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');
const slice=(a,b)=>{const i=source.indexOf(a),j=source.indexOf(b,i+1);assert.ok(i>=0&&j>i,a);return source.slice(i,j);};
const card=(id,type='unit')=>({id,name:id,type,undead:true,_xlwInstanceId:id});
function fixture(own=true){
 const g={console,structuredClone,turn:4,isMultiplayer:false,field:Object.fromEntries(['player_front','player_back','enemy_front','enemy_back'].map(z=>[z,Array(5).fill(null)])),deck:[],graveyard:[],hand:[],enemyGraveyard:[],logBattle(){},render(){},shuffles:0,shuffle(){g.shuffles++;},xlwIsUndeadCard:c=>!!c?.undead,xlwFactionDecisionKey:()=> 'test',xlwOnCardEntersGraveyard:async(c,side)=>g.entered.push([c.id,side]),entered:[]};g.window=g;g.XLW_ENEMY={hand:[],deck:[],grave:g.enemyGraveyard};vm.createContext(g);
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/duel_consistency.js'),'utf8'),g);
 vm.runInContext(slice('// Shared top-of-deck effects.','window.xlwTriggerSktImmediateEffects ='),g);
 g.zone=(own?'player':'enemy')+'_front';g.unit={card:card('source')};g.field[g.zone][0]=g.unit;
 g.ownDeck=()=>own?g.deck:g.XLW_ENEMY.deck;g.ownGrave=()=>own?g.graveyard:g.XLW_ENEMY.grave;
 g.setDeck=a=>{if(own)g.deck=a;else g.XLW_ENEMY.deck=a;};g.setGrave=a=>{if(own)g.graveyard=a;else g.XLW_ENEMY.grave=g.enemyGraveyard=a;};
 g.run=kind=>g.xlwResolveUndeadRecycle(g.unit.card,g.zone,0,own,kind);return g;
}
for(const own of [true,false])for(const amount of [0,1,2])test(`priest chooses ${amount} live undead units then mills the real top: ${own}`,async()=>{
 const g=fixture(own),a=card('a'),b=card('b'),c=card('c'),magic=card('skeleton-spell','magic');g.setGrave([a,b,c,magic]);g.setDeck([card('bottom'),card('top-a'),card('top-b')]);let n=0;
 g.xlwChooseFactionAction=async(local,key,title,msg,options)=>{assert.equal(local,own);assert.ok(options.filter(o=>o.card).every(o=>o.card.type==='unit'));return n++<amount?0:-1;};
 await g.run('priest');assert.equal(n,amount===2?2:amount+1);assert.equal(g.shuffles,amount?1:0);assert.equal(g.entered.length,2);assert.ok(g.entered.every(([,side])=>side===own));assert.equal(g.ownDeck()[0].id,'bottom');assert.ok(g.ownGrave().includes(magic));
 assert.deepEqual(Array.from(g.entered,([id])=>id),amount===0?['top-b','top-a']:amount===1?['a','top-b']:['b','a']);assert.equal(g.XLW_deckTopPending.size,0);
});
for(const own of [true,false])for(const size of [0,1,2])test(`priest handles ${size} cards with no eligible grave: ${own}`,async()=>{
 const g=fixture(own);g.setDeck(Array.from({length:size},(_,i)=>card('top'+i)));g.setGrave([card('spell','magic')]);g.xlwChooseFactionAction=async()=>assert.fail('No target chooser expected');await g.run('priest');assert.equal(g.ownDeck().length,0);assert.equal(g.entered.length,size);assert.ok(!g.ownGrave().includes(undefined));
});
for(const own of [true,false])for(const kind of ['nurse','chicken'])for(const mode of ['cloned','removed','changed-type','reset'])test(`${kind} revalidates its live source after selection: ${own}/${mode}`,async()=>{
 const g=fixture(own),target=card('target'),keep=card('keep');const set=kind==='chicken'?g.setDeck:g.setGrave;set([target,keep]);g.xlwChooseFactionAction=async(local,key,title,msg,options)=>{assert.equal(local,own);set(mode==='removed'?[keep]:mode==='changed-type'?[{...target,type:'magic'},keep]:structuredClone([target,keep]));if(mode==='reset')g.XLW_deckTopPending.clear();return 0;};
 await g.run(kind);const moved=mode==='cloned';assert.equal((kind==='chicken'?g.ownGrave():g.ownDeck()).some(c=>c.id==='target'),moved);assert.ok((kind==='chicken'?g.ownDeck():g.ownGrave()).some(c=>c.id==='keep'));assert.equal(g.shuffles,moved?1:0);assert.equal(g.entered.length,kind==='chicken'&&moved?1:0);assert.equal(g.XLW_deckTopPending.size,0);
});
for(const kind of ['nurse','chicken'])test(`${kind} ignores undead spells and non-undead units`,async()=>{
 const g=fixture(),spell=card('spell','magic'),living={...card('living'),undead:false};(kind==='chicken'?g.setDeck:g.setGrave)([spell,living]);g.xlwChooseFactionAction=async()=>assert.fail('No eligible units');await g.run(kind);assert.equal(g.shuffles,0);assert.equal(g.entered.length,0);assert.equal((kind==='chicken'?g.ownDeck():g.ownGrave()).length,2);
});
test('priest reads the current deck and grave after the first grave trigger replaces both arrays',async()=>{
 const g=fixture();g.setDeck([card('bottom'),card('middle'),card('first')]);g.xlwOnCardEntersGraveyard=async(c)=>{g.entered.push(c.id);if(c.id==='first'){g.setDeck([card('replacement')]);g.setGrave(structuredClone(g.ownGrave()));}};await g.run('priest');assert.deepEqual(g.entered,['first','replacement']);assert.deepEqual(Array.from(g.ownGrave(),c=>c.id),['first','replacement']);assert.equal(g.ownDeck().length,0);
});
test('priest stops safely if the first grave trigger empties the deck',async()=>{
 const g=fixture();g.setDeck([card('bottom'),card('first')]);g.xlwOnCardEntersGraveyard=async c=>{g.entered.push(c.id);g.setDeck([]);};await g.run('priest');assert.deepEqual(g.entered,['first']);assert.deepEqual(Array.from(g.ownGrave(),c=>c.id),['first']);
});
test('priest cannot mill cards from a new game after a grave trigger resets pending work',async()=>{
 const g=fixture();g.setDeck([card('bottom'),card('first')]);g.xlwOnCardEntersGraveyard=async()=>{g.XLW_deckTopPending.clear();g.setDeck([card('new-game')]);};assert.equal(await g.run('priest'),false);assert.equal(g.ownDeck()[0].id,'new-game');assert.equal(g.ownGrave().length,1);
});
test('a mill diverted out of the grave does not fire its grave trigger',async()=>{
 const g=fixture();g.setDeck([card('first')]);const grave=[];grave.push=()=>0;g.setGrave(grave);await g.run('priest');assert.equal(g.entered.length,0);assert.equal(g.ownDeck().length,0);
});
test('duplicate execution cannot open another chooser while the first effect is pending',async()=>{
 const g=fixture();g.setGrave([card('a')]);let done,calls=0;g.xlwChooseFactionAction=()=>{calls++;return new Promise(r=>done=r);};const first=g.run('nurse');await Promise.resolve();assert.equal(await g.run('nurse'),false);done(0);await first;assert.equal(calls,1);assert.equal(g.ownDeck().length,1);
});
for(const [kind,id]of [['priest','C-SKT-0053'],['nurse','SSR-SKT-0027'],['chicken','R-SKT-0006-PROMO']])test(`catalogue variant dispatches through the guarded ${kind} resolver`,async()=>{
 const g=fixture();g.unit.card=card(id);let called;g.xlwResolveUndeadRecycle=async(...args)=>called=args;vm.runInContext(slice('window.xlwTriggerSktImmediateEffects =','window.xlwUnitHasPoison ='),g);await g.xlwTriggerSktImmediateEffects(g.unit.card,g.zone,0,true);assert.equal(called[4],kind);assert.equal(called[3],true);
});
for(const kind of ['priest','nurse','chicken'])test(`mirrored ${kind} resolution uses one controller decision and identical card transfers`,async()=>{
 const a=fixture(true),b=fixture(false);for(const g of [a,b]){g.setDeck([card('bottom'),card('top')]);g.setGrave([card('a'),card('b')]);vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/faction_choices.js'),'utf8'),g);}
 let decisions=0,ac,bc;ac=a.XLWFactionChoices.create({choose:async()=>{decisions++;return 0;},send:m=>bc.receive(m)});bc=b.XLWFactionChoices.create({choose:()=>assert.fail('Peer must not choose'),send:m=>ac.receive(m)});a.xlwChooseFactionAction=ac.choose;b.xlwChooseFactionAction=bc.choose;
 await Promise.all([a.run(kind),b.run(kind)]);assert.equal(decisions,kind==='priest'?2:1);assert.deepEqual(Array.from(a.ownDeck(),c=>c.id),Array.from(b.ownDeck(),c=>c.id));assert.deepEqual(Array.from(a.ownGrave(),c=>c.id),Array.from(b.ownGrave(),c=>c.id));
});
