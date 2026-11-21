const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const game=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');
const section=(a,b)=>game.slice(game.indexOf(a),game.indexOf(b,game.indexOf(a)));
const scope={require,__dirname,console};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'test_unit_destruction.cjs'),'utf8').split('let tests = 0;')[0],scope);
const unit=(id,attack=3)=>({card:{id,name:id,type:'unit',attack,score:1},equipments:[],attacking:true,tapped:false});
const fresh=()=>{const g=scope.fixture();g.isMultiplayer=false;g.structuredClone=structuredClone;return g;};

test('official tie: only the attacker receives success, from either seat',async()=>{
 for(const side of ['player','enemy']){
  const g=fresh(),other=side==='player'?'enemy':'player',rewards=[];
  g.field[side+'_front'][0]=unit('attack');g.field[other+'_front'][0]=unit('defend');
  g.applyCombatSuccessReward=async(u)=>rewards.push(u.card.id);
  await g.resolveUnitCombat(side+'_front',0,other+'_front',0,other);
  assert.deepEqual(rewards,['attack']);
 }
});
test('successful effects see both untapped combatants, then defender destruction, attacker destruction, and fatigue',async()=>{
 const g=fresh(),order=[],a=unit('attack',5),d=unit('defend',2);a.poison=true;d.poison=true;
 g.field.player_front[0]=a;g.field.enemy_front[0]=d;
 g.applyCombatSuccessReward=async()=>{assert.equal(a.tapped,false);assert.equal(g.field.enemy_front[0],d);order.push('success');};
 const destroy=g.destroyUnit;g.destroyUnit=async(z,i,...args)=>{assert.equal(a.tapped,false);order.push(z);await destroy(z,i,...args);};
 await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
 assert.deepEqual(order,['success','enemy_front','player_front']);assert.equal(a.tapped,true);
});
test('piercing keeps the attacker upright between its two comparisons',async()=>{
 const g=fresh(),a=unit('attack',5),states=[];a.piercing=true;
 g.field.player_front[0]=a;g.field.enemy_front[0]=unit('front',1);g.field.enemy_back[0]=unit('back',1);
 g.checkUnitHasPiercing=u=>u.piercing;g.showCombatNumberAnimation=async()=>states.push(a.tapped);
 await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
 assert.deepEqual(states,[false,false]);assert.equal(a.tapped,true);
});
test('the attacker may select sneak before piercing, preventing the rear battle on recall',async()=>{
 const g=fresh(),a=unit('attack',5);a.piercing=true;a.sneak=true;
 g.field.player_front[0]=a;g.field.enemy_front[0]=unit('front',1);const rear=g.field.enemy_back[0]=unit('back',1);
 g.checkUnitHasPiercing=u=>u.piercing;g.xlwUnitHasSneak=u=>u.sneak;
 g.xlwBattleRuleChoice=async()=> 'sneak';g.showXLWConfirm=async()=>true;
 g.triggerSneakAttackSuccessEffects=async()=>{};
 await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
 assert.equal(g.field.player_front[0],null);assert.equal(g.field.enemy_back[0],rear);assert.equal(g.hand.length,1);
});
test('invalid or shielded target returns the attacker upright rather than spending the battle',async()=>{
 for(const kind of ['missing','shield']){
  const g=fresh(),a=unit('attack');a.tapped=true;g.field.player_front[0]=a;
  if(kind==='shield')g.field.enemy_front[0]=unit('shield','盾');
  await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');assert.equal(a.tapped,false);assert.equal(a.attacking,false);
 }
});

const helpers={};vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/rules_battle.js'),'utf8'),helpers);
const ctx={turn:7,attackerRole:'player1',attRow:'front',attIdx:2,defRow:'back',defIdx:2,stage:'before',multi:true};
function pair(){
 const states=[null,null],traffic=[];let clients;
 clients=[0,1].map(i=>helpers.XLWOfficialBattle.create({
  getDefense:()=>false,setDefense(){},activate:s=>states[i]=s,render(){},busy:()=>false,sync(){},
  send:msg=>{traffic.push(msg);clients[1-i].receive(msg);},choose:async()=> 'sneak'
 }));return{clients,states,traffic};
}
test('both phones must pass; one-sided pass cannot advance the battle',async()=>{
 const p=pair();let finished=0;const tasks=p.clients.map(c=>c.open(ctx).then(()=>finished++));
 p.states[0].pass();await Promise.resolve();assert.equal(finished,0);p.states[1].pass();await Promise.all(tasks);assert.equal(finished,2);
});
test('a spell resets both passes and old replies cannot close a newer priority window',async()=>{
 const p=pair();let finished=0;const tasks=p.clients.map(c=>c.open(ctx).then(()=>finished++));
 p.states[0].pass();const old=p.traffic[0];for(const state of p.states)state.resetPasses();
 p.clients[1].receive(old);p.states[1].pass();await Promise.resolve();assert.equal(finished,0);
 p.states[0].pass();await Promise.all(tasks);assert.equal(finished,2);
});
test('early ordered pass and early attacker choice are retained until the peer reaches that boundary',async()=>{
 const p=pair(),first=p.clients[0].open(ctx);p.states[0].pass();const second=p.clients[1].open(ctx);p.states[1].pass();await Promise.all([first,second]);
 const options=[{value:'pierce'},{value:'sneak'}];
 assert.equal(await p.clients[0].choose({...ctx,localAttacker:true},'x','x',options),'sneak');
 assert.equal(await p.clients[1].choose({...ctx,localAttacker:false},'x','x',options),'sneak');
});
test('an in-window spell snapshot updates existing references but never reuses a different unit',()=>{
 const a={card:{id:'same'},summonedTurn:3,oldBuff:true},b={card:{id:'other'}};
 const row=helpers.XLWOfficialBattle.mergeRow([a,b],[{card:{id:'same'},summonedTurn:3,atkModifier:2},{card:{id:'new'}}]);
 assert.equal(row[0],a);assert.equal(a.oldBuff,undefined);assert.equal(a.atkModifier,2);assert.notEqual(row[1],b);
});

test('countdown starts only on the empty-deck owners end phase and flips exactly five lanes',()=>{
 const g=fresh();Object.assign(g,{isGameOverFlag:false,isMyTurn:true,countdownActive:false,countdownRemaining:5,deck:[{}],executeGameOverCalculations:()=>g.ended=true});
 g.XLW_ENEMY.deck=[];
 vm.runInContext(section('function handleTurnEndCountdownLogic(','function executeGameOverCalculations('),g);
 g.handleTurnEndCountdownLogic(true);assert.equal(g.countdownActive,false);
 g.handleTurnEndCountdownLogic(false);assert.equal(g.countdownActive,true);assert.equal(g.countdownRemaining,4);
 for(let i=0;i<3;i++)g.handleTurnEndCountdownLogic(i%2===0);assert.equal(g.ended,undefined);
 g.handleTurnEndCountdownLogic(true);assert.equal(g.ended,true);
});
test('growth moves the old card to exile and combination material to the grave on either side',async()=>{
 for(const isPlayer of [true,false]){
  const g=fresh(),side=isPlayer?'player':'enemy',old={id:'old',name:'old'},target={id:'new',name:'new'};
  (isPlayer?g.playerExtraDeck:g.enemyExtraDeck).push(target);
  const u={card:old,devourCards:[{card:{id:'material'}}],isCombined:true,irrigation:3};
  g.field[side+'_front'][0]=u;
  vm.runInContext(section('window.xlwExecutePlantGrowth =','// 檢查某單位可成長'),g);
  await g.xlwExecutePlantGrowth(u,target,side+'_front',0,isPlayer);
  assert.equal((isPlayer?g.playerExileZone:g.enemyExileZone)[0],old);
  assert.equal((isPlayer?g.graveyard:g.enemyGraveyard)[0].id,'material');assert.equal(u.devourCards.length,0);
  assert.equal((isPlayer?g.playerExtraDeck:g.enemyExtraDeck).length,0);
 }
});
test('seed entry offers back slots only after every front slot is occupied',async()=>{
 for(const fullFront of [false,true]){
  const g=fresh(),seed={id:'seed',name:'魔法種子'};g.playerExtraDeck.push(seed);g.xlwIsUnitSeed=()=>true;
  if(fullFront)g.field.player_front.fill({card:{id:'occupied'}});
  g.xlwGetEmptyPlayerSlots=()=>['player_front','player_back'].flatMap(zone=>g.field[zone].flatMap((u,idx)=>u?[]:[{zone,idx}]));
  g.showXLWChoiceModal=async(_,__,choices)=>{assert.ok(choices.every(c=>c.boardTarget.zone===(fullFront?'player_back':'player_front')));return choices[0].value;};
  vm.runInContext(section('window.xlwSummonPlantFromExtraDeck =','// 單位成長核心'),g);
  const result=await g.xlwSummonPlantFromExtraDeck('seed',true);assert.equal(result.slot.zone,fullFront?'player_back':'player_front');
 }
});

test('hand-limit continuation waits after end effects and never repeats them when the final card is exiled',async()=>{
 const f={require,__dirname,console,structuredClone};vm.runInNewContext(fs.readFileSync(path.join(__dirname,'test_end_turn_settlement.cjs'),'utf8').split('module.exports =')[0],f);
 const {g}=f.fixture(),order=[];g.xlwResolveExpansionTurnEnd=async()=>{order.push('end');g.hand=Array.from({length:11},(_,id)=>({id}));};
 g.resolveDecayStatus=async()=>order.push('decay');g.handleTurnEndCountdownLogic=()=>order.push('countdown');
 const task=g.endPlayerTurnAndRunEnemy();
 for(let i=0;i<30;i++)await Promise.resolve();
 assert.deepEqual(order,['end','decay']);assert.equal(g.XLW_exileExcessHandActive,true);assert.equal(g.XLW_isPlayerTurnEnding,true);
 g.hand.pop();g.XLW_exileExcessHandActive=false;g.XLW_handLimitResolve();await task;
 assert.deepEqual(order,['end','decay','countdown']);assert.equal(g.XLW_isPlayerTurnEnding,false);
});

test('printed tribute category remains required despite a discount to zero',async()=>{
 const g=fresh();Object.assign(g,{phase:'戰術佈陣',hand:[],getCardTributeCost:()=>0,xlwAllowsTacticalTribute:()=>false,xlwSpellActionPending:()=>false});
 const card={id:'unit',name:'needs-tribute',type:'unit',tribute:2};g.hand.push(card);
 g.canSummonCard=()=>true;g.xlwBlueStarRequirement=()=>'';g.clearModes=()=>{};
 g.xlwRequireSpellCompletion=()=>false;g.xlwValkyrieMaterials=()=>[];g.xlwIsBreakfast=()=>false;g.selectedTributeCard=null;g.selectedHandForTribute=null;g.tacticalSummonUsed=false;g.setStatus=value=>{g.status=value;};
 vm.runInContext(section('window.xlwExecuteHandUnitSummon =','// 渲染我方手牌'),g);
 await g.xlwExecuteHandUnitSummon(card,0);assert.match(g.status||'',/祭品|戰術/);
});

test('a targetless spell uses the ordinary counter chain, reaches the grave once, and counts as a cast',async()=>{
 const g=fresh(),card={id:'CND-test',name:'賞味期限',type:'magic'};g.hand.push(card);
 g.spellChainStack=[];g.xlwSanitizeGoatCardTypes=()=>{};g.isDessertUnit=()=>false;g.setStatus=()=>{};g.clearModes=()=>{};g.renderStablePanel=()=>{};
 g.xlwShowSpellActivationOverlay=async()=>{};let casts=0;
 g.castSpellChain=async(c,apply)=>{assert.equal(c,card);casts++;await apply();};
 const start=game.indexOf('async function castSpell(handIndex)');const end=game.indexOf('\nasync function ',start+10);const code=game.slice(start,end);
 for(const match of code.matchAll(/window\.([A-Za-z_$][\w$]*)\s*\(/g)) if(!(match[1] in g))g[match[1]]=()=>false;
 vm.runInContext(code,g);await g.castSpell(0);
 assert.equal(casts,1);assert.equal(g.hand.length,0);assert.equal(g.graveyard[0],card);assert.equal(g.graveyard.length,1);assert.equal(g.XLW_castSpellBusy,false);
});
test('a failed comparison triggers failure reward even when destruction is resisted',async()=>{
 const g=fresh(),loser=unit('C-ORC-0060',1);loser.indestructible=true;
 g.field.player_front[0]=loser;g.field.enemy_front[0]=unit('defender',5);
 await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
 assert.equal(g.field.player_front[0],loser);assert.equal(g.playerBonusScore,3);
});
test('Call Game checks only the declared condition, not whichever condition remains true',async()=>{
 const g=fresh();Object.assign(g,{XLW_callGameDeclared:true,XLW_callGameDeclaringPlayer:'player',XLW_callGameCondition:1,
  xlwIsShenaOnField:()=>false,hasOphiuchusOnField:()=>false,calculateTotalStars:()=>19,calculateUnitCount:side=>side?8:0,
  triggerCallGameEnd:()=>{g.ended=true;}});
 vm.runInContext(section('async function checkCallGameAtTurnStart(','function handleTurnEndCountdownLogic('),g);
 await g.checkCallGameAtTurnStart(true);assert.equal(g.ended,undefined);assert.equal(g.XLW_callGameDeclared,false);
});

test('a successful effect returning the target to hand does not award a combat-destruction reward',async()=>{
 const g=fresh(),a=unit('ORC-0003',5),d=unit('defend',1);
 g.field.player_front[0]=a;g.field.enemy_front[0]=d;
 g.applyCombatSuccessReward=async()=>{g.field.enemy_front[0]=null;g.XLW_ENEMY.hand.push(d.card);};
 await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');assert.equal(g.playerBonusScore,0);assert.equal(g.enemyGraveyard.length,0);
});
