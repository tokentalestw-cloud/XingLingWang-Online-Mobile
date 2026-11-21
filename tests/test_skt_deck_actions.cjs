const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');const slice=(a,b)=>{const i=source.indexOf(a),j=source.indexOf(b,i+1);assert.ok(i>=0&&j>i);return source.slice(i,j);};
const card=(id,props={})=>({id,name:id,type:'unit',_xlwInstanceId:id,...props});
function fixture(own=true){const g={console,structuredClone,field:Object.fromEntries(['player_front','player_back','enemy_front','enemy_back'].map(z=>[z,Array(5).fill(null)])),deck:[],hand:[],graveyard:[],enemyGraveyard:[],turn:7,logBattle(){},render(){},shuffle(){g.shuffles++;},shuffles:0,xlwFactionDecisionKey:()=> 'deck-action',revealed:[],entered:[]};g.window=g;g.XLW_ENEMY={deck:[],hand:[],grave:g.enemyGraveyard};vm.createContext(g);vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/duel_consistency.js'),'utf8'),g);vm.runInContext(slice('function xlwIsFieldMagic(','async function xlwResolveAries(')+slice('// Remaining skull deck actions','// End remaining skull deck actions.'),g);g.zone=(own?'player':'enemy')+'_front';g.unit={card:card('source')};g.field[g.zone][0]=g.unit;g.xlwChooseFactionAction=async()=>0;g.xlwRevealCard=async(c,side)=>g.revealed.push([c.id,side]);g.xlwOnCardEntersGraveyard=async(c,side)=>g.entered.push([c.id,side]);g.ownDeck=()=>own?g.deck:g.XLW_ENEMY.deck;g.ownHand=()=>own?g.hand:g.XLW_ENEMY.hand;g.setDeck=a=>{if(own)g.deck=a;else g.XLW_ENEMY.deck=a;};g.run=mill=>g.xlwResolveSktDeckAction(g.unit.card,g.zone,0,own,mill);return g;}
const fieldCard=id=>card(id,{type:'magic',magic_type:'場地'});
for(const own of [true,false])for(const size of [0,1,3])test(`messenger mills the real top from both players, with ${size} source cards: ${own}`,async()=>{
 const g=fixture(own);g.setDeck(Array.from({length:size},(_,i)=>card('own'+i)));const other=own?'enemy':'player';if(own)g.XLW_ENEMY.deck=[card('enemy-bottom'),card('enemy-top')];else g.deck=[card('enemy-bottom'),card('enemy-top')];await g.run(true);assert.equal(g.ownDeck().length,Math.max(0,size-1));assert.deepEqual(g.entered,size?[['own'+(size-1),own],['enemy-top',!own]]:[['enemy-top',!own]]);assert.equal((other==='enemy'?g.XLW_ENEMY.deck:g.deck)[0].id,'enemy-bottom');assert.equal(g.XLW_deckTopPending.size,0);
});
for(const own of [true,false])test(`messenger refreshes opposing deck and grave after its first grave trigger: ${own}`,async()=>{
 const g=fixture(own);g.setDeck([card('own-top')]);g.xlwOnCardEntersGraveyard=async(c,side)=>{g.entered.push([c.id,side]);if(side===own){if(own){g.XLW_ENEMY.deck=[card('new-opponent')];g.XLW_ENEMY.grave=g.enemyGraveyard=[card('new-grave')];}else{g.deck=[card('new-opponent')];g.graveyard=[card('new-grave')];}}};await g.run(true);assert.deepEqual(g.entered,[['own-top',own],['new-opponent',!own]]);assert.deepEqual(Array.from(own?g.XLW_ENEMY.grave:g.graveyard,c=>c.id),['new-grave','new-opponent']);
});
test('messenger cannot continue into a new game after the first grave trigger resets it',async()=>{
 const g=fixture();g.deck=[card('old')];g.XLW_ENEMY.deck=[card('old-enemy')];g.xlwOnCardEntersGraveyard=async()=>{g.XLW_deckTopPending.clear();g.XLW_ENEMY.deck=[card('new-match')];};assert.equal(await g.run(true),false);assert.equal(g.XLW_ENEMY.deck[0].id,'new-match');assert.equal(g.XLW_ENEMY.grave.length,0);
});
test('messenger does not pop unknown placeholders or add undefined grave entries',async()=>{
 const g=fixture();g.deck=[null];g.XLW_ENEMY.deck=[];await g.run(true);assert.equal(g.deck.length,1);assert.equal(g.graveyard.length,0);assert.equal(g.entered.length,0);
});
test('messenger does not fire a grave trigger for a card diverted out of grave',async()=>{
 const g=fixture();g.deck=[card('wheel-card')];g.graveyard.push=()=>0;await g.run(true);assert.equal(g.entered.length,0);assert.equal(g.deck.length,0);
});
for(const own of [true,false])for(const mode of ['normal','cloned','removed','not-field','reset','cancel'])test(`gravedigger revalidates the field card in the current deck: ${own}/${mode}`,async()=>{
 const g=fixture(own),c=fieldCard('target'),keep=card('keep',{type:'magic'});g.setDeck([c,keep]);g.xlwChooseFactionAction=async(local,key,title,msg,options)=>{assert.equal(local,own);assert.equal(options.length,1);if(mode==='cloned')g.setDeck(structuredClone(g.ownDeck()));if(mode==='removed')g.setDeck([keep]);if(mode==='not-field')c.magic_type='裝備';if(mode==='reset')g.XLW_deckTopPending.clear();return mode==='cancel'?null:0;};const success=['normal','cloned'].includes(mode);assert.equal(await g.run(false),success);assert.equal(g.ownHand().length,success?1:0);assert.equal(g.shuffles,success?1:0);assert.ok(g.ownDeck().some(c=>c.id==='keep'));assert.equal(g.XLW_deckTopPending.size,0);
});
for(const reveal of [true,false])test(`gravedigger follows its printing's reveal wording: ${reveal}`,async()=>{
 const g=fixture(),c=fieldCard('field');g.unit.card.effect_text=reveal?'尋找1場地卡展示並加入手牌':'尋找1場地卡加入手牌';g.deck=[c];let seen=false;g.xlwRevealCard=async chosen=>{seen=true;assert.equal(chosen,c);assert.equal(g.hand.length,0);assert.equal(g.deck[0],c);};await g.run(false);assert.equal(seen,reveal);assert.equal(g.hand[0],c);assert.equal(g.shuffles,1);
});
for(const mode of ['cloned','removed','reset','not-field'])test(`gravedigger revalidates again after reveal effects: ${mode}`,async()=>{
 const g=fixture(),c=fieldCard('field');g.unit.card.effect_text='展示';g.deck=[c,card('keep')];g.xlwRevealCard=async()=>{if(mode==='cloned'){g.deck=structuredClone(g.deck);g.hand=[card('new-hand')];}if(mode==='removed')g.deck=[card('keep')];if(mode==='reset'){g.XLW_deckTopPending.clear();g.deck=[fieldCard('new-match')];}if(mode==='not-field')c.magic_type='裝備';};await g.run(false);assert.equal(g.hand.some(c=>c.id==='field'),mode==='cloned');assert.equal(g.shuffles,mode==='cloned'?1:0);if(mode==='cloned')assert.equal(g.hand[0].id,'new-hand');
});
test('duplicate gravedigger execution cannot select or transfer a second card concurrently',async()=>{
 const g=fixture();g.deck=[fieldCard('one'),fieldCard('two')];let done,calls=0;g.xlwChooseFactionAction=()=>{calls++;return new Promise(r=>done=r);};const first=g.run(false);await Promise.resolve();assert.equal(await g.run(false),false);done(0);await first;assert.equal(calls,1);assert.equal(g.hand.length,1);
});
for(const [id,mill]of [['SKT-0005',true],['NY-SKT-0015-新年',false],['R-SKT-0015-PROMO',false]])test(`catalogue ${id} dispatches through the guarded deck action`,async()=>{
 const g=fixture();let args;g.xlwResolveSktDeckAction=async(...a)=>args=a;g.unit.card=card(id);vm.runInContext(slice('window.xlwTriggerSktImmediateEffects =','window.xlwUnitHasPoison ='),g);await g.xlwTriggerSktImmediateEffects(g.unit.card,g.zone,0,true);assert.equal(args[4],mill);
});
