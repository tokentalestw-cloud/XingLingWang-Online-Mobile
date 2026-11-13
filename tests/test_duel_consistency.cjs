const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'static/game_v8.js'),'utf8'),mergeSource=fs.readFileSync(path.join(root,'static/duel_consistency.js'),'utf8');let tests=0;const queueMicrotask=fn=>Promise.resolve().then(fn);
function section(a,b){return source.slice(source.indexOf(a),source.indexOf(b,source.indexOf(a)));}
function context(){const g={console,Date,Math,Map,Set,structuredClone,WebSocket:{OPEN:1},setTimeout(){return 1;},clearTimeout(){},queueMicrotask,field:Object.fromEntries(['player_front','player_back','enemy_front','enemy_back'].map(z=>[z,Array(5).fill(null)])),hand:[],deck:[],graveyard:[],enemyGraveyard:[],playerExileZone:[],enemyExileZone:[],playerExtraDeck:[],enemyExtraDeck:[],spellChainStack:[],isMultiplayer:true,isMyTurn:true,phase:'召喚階段',turn:3,render(){},renderStablePanel(){},clearModes(){},setStatus(){},logBattle(){},xlwSanitizeGoatCardTypes(){},xlwOnMagicCardCast:async()=>{},isUnitSilenced:()=>false,hideSpellChainUI(){},showSpellChainUI(){},sendFullGameStateToOpponent(){},playerBonusScore:0,enemyBonusScore:0,$:()=>({dataset:{}})};g.window=g;g.XLW_ENEMY={hand:[],deck:[],grave:g.enemyGraveyard};g.ws={readyState:1,send(){}};g.document ||= { getElementById: () => null }; vm.createContext(g);vm.runInContext(source.slice(source.indexOf("// Faction state uses"), source.indexOf("// ===== 6. 召喚與獻祭召喚系統 =====", source.indexOf("// Faction state uses"))),g);vm.runInContext(section('function xlwHasInnateWheelEntry(', 'function xlwAddWheelEntry('),g);vm.runInContext(mergeSource,g);return g;}
const card=(uid,id='SAME')=>({_xlwInstanceId:uid,id,name:id,type:'unit'});
for(const role of ['player1','player2']){
 let g=context(),m=g.XLWDuelConsistency,p=card('peace'),x=card('x');
 assert.equal(m.mergeOwned([x],[p,x],[p,x],'hand').length,1);tests++;
 const a=card('a'),b=card('b');const result=m.mergeOwned([a,b],[a,b],[b],'hand');assert.equal(result.length,1);assert.equal(result[0]._xlwInstanceId,'b');tests++;
 const top=card('top'),d=card('d'),drawn=card('drawn');const current=[d,top];assert.equal(m.mergeOwned(current,[d,top,drawn],[d,drawn],'deck').length,1);tests++;
 // A repeated peer patch must not re-add a card after it has since been played.
 const returned=card('return');let h=m.mergeOwned([],[],[returned],'return');assert.equal(h.length,1);h=[];assert.equal(m.mergeOwned(h,[],[returned],'return').length,0);tests++;
 const localDraw=card('draw');assert.equal(m.mergeOwned([localDraw],[],[],'draw').length,1);tests++;
 // Same object in a preset deck represents two physical copies.
 const shared={id:'copy',name:'copy'};const cards=[shared,shared];m.identify(cards);assert.notEqual(cards[0]._xlwInstanceId,cards[1]._xlwInstanceId);tests++;
 const copies=[a,b];m.removeCard(copies,{...a});assert.equal(copies[0]._xlwInstanceId,'b');tests++;
 const from=[a,b], to=[];
 assert.equal(m.moveKnownCard(from,to,{...a})._xlwInstanceId,'a');
 assert.equal(m.moveKnownCard(from,to,{...a}),null);
 assert.equal(from[0]._xlwInstanceId,'b');
 assert.equal(to.length,1);
 from.push({...a});
 assert.equal(m.moveKnownCard(from,to,{...a}),null);
 assert.equal(from.length,1);
 assert.equal(to.length,1);tests++;
}
module.exports=(async()=>{
 for(const role of ['player1','player2']){
  const g=context();let animations=0,publish=0;g.hand=[{id:'NMG-0009',name:'和平巨人',type:'magic',effect_text:''},card('keep')];g.xlwShowSpellActivationOverlay=async()=>{animations++;};g.sendFullGameStateToOpponent=()=>publish++;g.promptNextChainAction=()=>queueMicrotask(()=>g.XLW_pendingSpellResolve({countered:false}));
  vm.runInContext(section('async function castSpell(handIndex)','// 點手牌的獻祭怪'),g);
  const first=g.castSpell(0),second=g.castSpell(0);await Promise.all([first,second]);assert.equal(animations,1);assert.equal(g.hand.length,1);assert.equal(g.graveyard.length,1);assert.equal(g.XLW_enemyCannotAttackOnNextTurn,true);assert.equal(g.XLW_castSpellBusy,false);tests++;
  // Early special branches must return rather than casting a second time.
  const q=context();let n=0;q.hand=[{id:'R-FMS-0017',name:'小四喜',type:'magic'},card('keep')];q.xlwCheckMahjongCombo=()=>true;q.xlwShowSpellActivationOverlay=async()=>n++;q.castSpellChain=async(c,fn)=>fn();q.exileCard=c=>q.playerExileZone.push(c);q.renderScore=()=>{};vm.runInContext(section('async function castSpell(handIndex)','// 點手牌的獻祭怪'),q);await q.castSpell(0);assert.equal(n,1);assert.equal(q.hand.length,1);tests++;
 }
 // Both phones receive the chain, but only the caster pays Bomber's deck cost.
 for(const initialOwner of ['me','opponent']){
  const g=context(),bomber={id:'NEU-0025',name:'魔法炸彈客',type:'unit',_xlwInstanceId:'bomb'};g.deck=[card('d1'),card('d2')];g.XLW_ENEMY.deck=[card('e1'),card('e2')];g.hand=[card('another-bomb','NEU-0025')];g.spellChainStack=[{card:{id:'NMG-0009',name:'和平巨人'},owner:initialOwner},{card:bomber,owner:initialOwner==='me'?'opponent':'me'}];g.exileCard=(c,o)=>(o==='player'?g.playerExileZone:g.enemyExileZone).push(c);
  vm.runInContext(section('function resolveLocalSpellChain()','// ===== 🌌'),g);g.resolveLocalSpellChain();g.resolveLocalSpellChain();assert.equal(g.XLW_ENEMY.deck.length,initialOwner==='me'?1:2);assert.equal(g.deck.length,2);assert.equal(g.hand.length,1);tests++;
 }
 // Banana protection applies to either player's adjacent target.
 for(const side of ['player','enemy']){const g=context();vm.runInContext(section('function isUnitAttackProtected(','// 我方是否可宣告進攻'),g);g.field[side+'_front'][2]={card:{id:'SSR-ART-0025',name:'牆壁上的香蕉'}};assert.equal(g.isUnitAttackProtected(side+'_back',1),true);assert.equal(g.isUnitAttackProtected(side+'_front',3),true);assert.equal(g.isUnitAttackProtected(side+'_front',0),false);tests++;}
 // Exercise the actual manual and automatic declarations, not just the aura helper.
 for(const automatic of [false,true]){const g=context();g.phase='進攻宣言';const attacker={card:{id:'att',name:'進攻者'},tapped:false};g.field.player_front[1]=attacker;g.field.enemy_front[1]={card:{id:'aunt',name:'觀光阿姨'}};g.field.enemy_front[2]={card:{id:'SSR-ART-0025',name:'牆壁上的香蕉'}};g.selectedAttacker={zone:'player_front',idx:1};g.xlwCardHasKeyword=()=>false;g.xlwUnitHasRanged=()=>false;g.xlwIsAttackBlockedByClea=()=>false;g.hasFlying=()=>false;g.XLW_isShieldUnit=()=>false;g.hasArmorBreak=()=>false;g.xlwTriggerSubsituteNinja=async()=>{};g.xlwOnPlayerUnitTapped=async()=>{};g.XLW_DEFENSE_RULE={};vm.runInContext(section('function isUnitAttackProtected(','// 我方是否可宣告進攻'),g);if(automatic){vm.runInContext(section('function xlwIsFlyingGoat(', 'async function changeActionPhase('),g);vm.runInContext(section('async function xlwAutoDeclarePlayerAttacks()','async function xlwTogglePlayerAttack('),g);await g.xlwAutoDeclarePlayerAttacks();}else{vm.runInContext(section('async function selectPlayerTarget(','window.selectPlayerTarget = selectPlayerTarget;'),g);await g.selectPlayerTarget('enemy_front',1);}assert.equal(!!attacker.attacking,false);assert.equal(attacker.tapped,false);tests++;}
 // External Banana protection remains even when the protected unit itself is silenced.
 {const g=context();g.isUnitSilenced=u=>u.card.id==='aunt';g.field.enemy_front[2]={card:{id:'SSR-ART-0025',name:'牆壁上的香蕉'}};const aunt={card:{id:'aunt',name:'觀光阿姨'}};g.field.enemy_front[1]=aunt;vm.runInContext(section('function isUnitAttackProtected(','// 我方是否可宣告進攻'),g);vm.runInContext(section('function isUnitIndestructible(','function isUnitMagicImmune('),g);assert.equal(g.isUnitIndestructible(aunt,'enemy_front',1),true);tests++;}
 // Counter declaration supplies the latest owner deck, and has already removed its hand cost.
 {const g=context();vm.runInContext(section('function xlwSpellOwnerCollections()','// 魔法反制與連鎖連線輔助函式'),g);const keep=card('another','NEU-0025');assert.equal(g.xlwAcceptSpellOwnerCollections({hand:[keep],deck:[card('latest-top')],graveyard:[],exile:[],extra:[]}),true);assert.equal(g.XLW_ENEMY.hand.length,1);assert.equal(g.XLW_ENEMY.deck[0]._xlwInstanceId,'latest-top');tests++;}
 // Selection remains valid if a network snapshot replaced graveyard objects while choosing.
 for(const owner of ['player','enemy']){const g=context(),snow={...card('snow','R-VLG-0012'),name:'雪女',faction:'妖怪村莊'};g.graveyard=[snow];g.enemyGraveyard=[{...snow}];g.XLW_ENEMY.grave=g.enemyGraveyard;g.showXLWChoiceModal=async()=>{g.graveyard=structuredClone(g.graveyard);return 0;};g.ws.send=raw=>{const msg=JSON.parse(raw);queueMicrotask(()=>g.XLW_samuraiRecoveryWaiters.get(msg.requestId)(msg.cards[0]));};vm.runInContext(section('async function xlwRecoverSamuraiCard(','async function resolveUnitCombat('),g);await g.xlwRecoverSamuraiCard(owner);assert.equal((owner==='player'?g.hand:g.XLW_ENEMY.hand)[0].name,'雪女');assert.equal((owner==='player'?g.graveyard:g.enemyGraveyard).length,0);tests++;}
 // Grave selection survives a replacement snapshot and never removes an unrelated card.
 for (const effect of ['aries', 'magic']) {
   for (const remains of [true, false]) {
     const g = context();
     const spell = {...card('spell','NMG-0012'), name:'山羊術', type:'magic'};
     const other = card('other');
     g.graveyard = [spell, other];
     g.showXLWChoiceModal = async () => {
       g.graveyard = remains ? [structuredClone(spell), other] : [other];
       return 0;
     };
     g.xlwCheckGraveyardTax = async () => true;
     g.shuffle = () => {};
     if (effect === 'aries') {
       vm.runInContext(section('async function xlwResolveAries(', 'window.xlwTriggerSktImmediateEffects ='), g);
       await g.xlwResolveAries(true);
     } else {
       vm.runInContext(section('window.xlwRetrieveMagicFromGrave =', 'window.xlwApplySageBuff ='), g);
       await g.xlwRetrieveMagicFromGrave(true);
     }
     assert.deepEqual(g.graveyard.map(c => c._xlwInstanceId), ['other']);
     assert.deepEqual(g.hand.map(c => c._xlwInstanceId), remains ? ['spell'] : []);
     tests++;
   }
 }
 // A stale card choice cannot transfer another card from the live pile.
 for (const effect of ['candy', 'goat', 'lawyer', 'field']) {
   for (const stillPresent of [true, false]) {
     const g = context();
     const selected = {...card('chosen','CND-0001'), faction:'甜點王國', type:'magic', name:'山羊術', magic_type:'場地'};
     const other = {...card('other'), type:'magic', name:'法術保護'};
     const pile = effect === 'field' ? 'deck' : 'graveyard';
     g[pile] = [selected, other];
     g.field.player_front[0] = {card:{id: effect === 'candy' ? 'SR-CND-0069' : 'C-EVL-0061'}};
     g.showXLWConfirm = async () => true;
     g.showXLWChoiceModal = async (_title, _message, choices) => {
       if (effect === 'field') assert.equal(choices.length, 1);
       g[pile] = stillPresent ? [structuredClone(selected), other] : [other];
       return 0;
     };
     g.shuffle = () => {};
     if (effect === 'candy') {
       vm.runInContext(section('window.xlwCheckCandyAdvisorSwallow =', '// 15. SR-EWD-0065'), g);
       await g.xlwCheckCandyAdvisorSwallow(true);
     } else if (effect === 'goat') {
       vm.runInContext('async function run(card, isPlayer) {' + section('// 1. 魔法山羊 (GOT-0001', '// 2. ',) + '}', g);
       await g.run({id:'GOT-0001'}, true);
     } else if (effect === 'lawyer') {
       vm.runInContext('async function run(isPlayer, side) {' + section('// E. C-EVL-0061', '// F. C-CRB-0027') + '}', g);
       await g.run(true, 'player_');
     } else {
       vm.runInContext(section('function xlwIsFieldMagic(', 'async function xlwResolveAries('), g);
       vm.runInContext('async function run(cid, isPlayer, myDeck, name) {' + section('// 3. 造墓者小布', '// 4. 除屍雞') + '}', g);
       await g.run('R-SKT-0015', true, g.deck, '造墓者小布');
     }
     assert.deepEqual(g[pile].map(c => c._xlwInstanceId), ['other']);
     assert.deepEqual(g.hand.map(c => c._xlwInstanceId), stillPresent ? ['chosen'] : []);
     tests++;
   }
 }
 // An authoritative-looking old draw flag cannot pay a second two-card draw cost.
 {const g=context();g.deck=[card('1'),card('2'),card('3'),card('4')];g.xlwCheckBananaMarquisMovement=async()=>{};g.xlwResolveTurnStartEffects=async()=>{};g.sendFullGameStateToOpponent=()=>{};vm.runInContext(section('async function performPlayerTurnStartDraw()','window.XLW_playerNeedsToDraw = false;'),g);await g.performPlayerTurnStartDraw();await g.performPlayerTurnStartDraw();assert.equal(g.deck.length,2);assert.equal(g.hand.length,2);g.turn++;await g.performPlayerTurnStartDraw();assert.equal(g.hand.length,4);tests++;}
 console.log(`${tests} bidirectional spell, card identity, stale collection, Bomber, Banana and Samurai regressions: PASS`);
})();
