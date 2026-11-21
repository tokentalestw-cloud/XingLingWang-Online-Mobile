const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');
const slice=(a,b)=>source.slice(source.indexOf(a),source.indexOf(b,source.indexOf(a)));
const base={require,__dirname,console};vm.runInNewContext(fs.readFileSync(path.join(__dirname,'test_unit_destruction.cjs'),'utf8').split('let tests = 0;')[0],base);
const mechanical=slice('// Official mechanical fusion:','async function xlwSeparateSingleFusedUnit(');
const transport=slice('// Official transport lifecycle:','// 盾牌單位判斷');
const core=slice('// Faction state uses','// ===== 6. 召喚與獻祭召喚系統 =====');
const card=(id,extra={})=>({id,name:id,type:'unit',attack:3,score:2,art_subtype:'機械',keywords:['機械合體'],...extra});
const unit=(id,extra={})=>({card:card(id),summonedTurn:2,summonedZone:'player_front',equipments:[],...extra});
function fixture(){
 const g=base.fixture();Object.assign(g,{isMultiplayer:false,isMyTurn:true,phase:'召喚階段',turn:4,structuredClone,allCards:[],LITTLE_TRAVELER:{id:'TOKEN_TRAVELER',name:'小旅人',type:'unit'},setStatus(){},xlwQueueWheelEntryEffect(){}});
 const nodes={playerField:{dataset:{}},enemyField:{dataset:{}}};g.document.getElementById=id=>nodes[id]||null;
 for(const m of (mechanical+core).matchAll(/window\.([A-Za-z_$][\w$]*)\s*\(/g))if(!(m[1] in g))g[m[1]]=()=>false;
 g.xlwChooseFactionAction=async(local,key,title,message,options)=>options[0]?.value;
 g.showXLWChoiceModal=async(title,message,options)=>options[0]?.value;
 g.xlwIsUnitMech=u=>u?.card?.art_subtype?.includes('機械')||u?.card?.art_subtype?.includes('機甲');
 g.xlwIsUnitUnmovable=u=>!!u.fixed;g.xlwHasMechCombine=c=>c?.keywords?.includes('機械合體');
 g.xlwFactionDecisionKey=(u,z,reason,n)=>[u.card?.id,z,reason,n].join(':');
 vm.runInContext(transport+core+mechanical+slice('async function cleanUnitLeavingField(','async function kidnapCard('),g);
 return {g,nodes};
}
test('normal mechanical fusion discards both equipments, preserves two physical cards and uses one exposed side',async()=>{
 for(const side of ['player','enemy']){
  const {g}=fixture(),z=side+'_front',a=unit('a'),b=unit('b');a.card.originalOwner=side;b.card.originalOwner=side;
  const eqA={id:'eqA',name:'eqA',type:'magic'},eqB={id:'eqB',name:'eqB',type:'magic'};g.allCards.push(eqA,eqB);a.equipments=['eqA'];b.equipments=['eqB'];
  g.field[z][0]=a;g.field[z][1]=b;
  assert.equal(await g.xlwExecuteMechCombine(a,b,z,0,z,1,side==='player'),true);
  const result=g.field[z][1];assert.equal(result.devourCards[0].expose,'atk');assert.equal(result.devourCards[0].value,3);assert.equal(result.devourCards.length,1);
  assert.equal(g.field[z][0],null);assert.equal(result.card.id,'b');assert.equal(result.equipments.length,0);
  assert.deepEqual(Array.from((side==='player'?g.graveyard:g.XLW_ENEMY.grave),c=>c.id),['eqA','eqB']);
 }
});
test('a real Armor Sword object and its name are discarded only once',async()=>{
 const {g}=fixture(),u=unit('carrier'),sword={id:'sword',name:'破甲劍',type:'magic'};
 u.xlwArmorBreakSwords=[{...sword}];u.equipments=['破甲劍'];g.allCards.push(sword);
 await g.xlwDiscardFusionMagic(u,'player_front');assert.equal(g.graveyard.length,1);
});
test('a combined target or combined source is rejected before any choice or zone mutation',async()=>{
 for(const sourceCombined of [false,true]){
  const {g}=fixture(),a=unit('a'),b=unit('b');(sourceCombined?a:b).devourCards=[{card:card('bottom'),expose:'atk',value:3}];
  g.field.player_front[0]=a;g.field.player_front[1]=b;
  assert.equal(await g.xlwExecuteMechCombine(a,b,'player_front',0,'player_front',1),false);assert.equal(g.field.player_front[0],a);assert.equal(g.field.player_front[1],b);
 }
});
test('same-name participants are allowed together once, but cannot participate again in that phase',async()=>{
 const {g}=fixture(),state={names:new Set(),slots:new Set()},a=unit('same'),b=unit('same');g.field.player_front[0]=a;g.field.player_front[1]=b;
 assert.equal(await g.xlwExecuteMechCombine(a,b,'player_front',0,'player_front',1,true,{state}),true);
 const c=unit('same'),d=unit('different');g.field.player_front[2]=c;g.field.player_front[3]=d;
 assert.equal(await g.xlwExecuteMechCombine(c,d,'player_front',2,'player_front',3,true,{state}),false);
});
test('manual mechanical phase visits lanes/front-back in order and can end without visiting later lanes',async()=>{
 const {g}=fixture(),a=unit('a'),b=unit('b'),c=unit('c');g.field.player_back[0]=a;g.field.player_front[1]=b;g.field.player_front[4]=c;
 const seen=[];g.showXLWChoiceModal=async(title,message,options)=>{seen.push(message);return 'end';};
 assert.equal(await g.xlwBeginMechanicalPhase(),true);assert.equal(seen.length,1);assert.match(seen[0],/1號戰線後排/);
 assert.equal(await g.xlwBeginMechanicalPhase(),false);assert.equal(g.XLW_mechPhase,null);
});
test('mecha fusion requires a third movable unit and captures it without granting its combine effect',async()=>{
 const {g}=fixture(),a=unit('a'),b=unit('b'),third=unit('RBT-0001');a.card.keywords.push('機甲合體');b.card.art_subtype='機甲';
 g.field.player_front[0]=a;g.field.player_front[1]=b;
 assert.equal(await g.xlwExecuteMechCombine(a,b,'player_front',0,'player_front',1,true,{mecha:true}),false);
 third.fixed=true;g.field.player_front[2]=third;
 assert.equal(await g.xlwExecuteMechCombine(a,b,'player_front',0,'player_front',1,true,{mecha:true}),false);
 third.fixed=false;const target=unit('enemy');g.field.enemy_front[0]=target;
 assert.equal(await g.xlwExecuteMechCombine(a,b,'player_front',0,'player_front',1,true,{mecha:true}),true);
 const result=g.field.player_front[1];assert.equal(result.kidnappedCards[0].id,'RBT-0001');assert.equal(result.devourCards.length,1);assert.equal(g.field.enemy_front[0],target);assert.equal(g.field.player_front[2],null);
});
test('ordinary fusion of mecha cards does not receive mecha-only buffs',async()=>{
 const {g}=fixture(),a=unit('C-RBT-0068'),b=unit('b');a.card.keywords.push('機甲合體');b.card.keywords.push('機甲合體');g.field.player_front[0]=a;g.field.player_front[1]=b;
 await g.xlwExecuteMechCombine(a,b,'player_front',0,'player_front',1,true,{mecha:false});const result=g.field.player_front[1];
 assert.equal(result.atkModifier,2);assert.equal(result.flying,undefined);assert.equal(result.armorBreak,undefined);
});
test('the same owner chooses the order of both printed combine effects',async()=>{
 const {g}=fixture(),a=unit('a'),b=unit('b'),order=[];g.field.player_front[0]=a;g.field.player_front[1]=b;
 g.xlwChooseFactionAction=async(local,key,title,text,options)=>key.endsWith(':order')?1:options[0].value;
 g.xlwResolveMechanicalEffects=async(ctx,local,cards,react)=>{if(!react)order.push(cards[0].id);};
 await g.xlwExecuteMechCombine(a,b,'player_front',0,'player_front',1,true);assert.deepEqual(order,['b','a']);
});
test('mecha aborts before discarding the other materials if the third unit leaves during effects',async()=>{
 const {g}=fixture(),a=unit('a'),b=unit('b'),c=unit('c');a.card.keywords.push('機甲合體');b.card.keywords.push('機甲合體');
 a.equipments=['retain'];g.field.player_front[0]=a;g.field.player_front[1]=b;g.field.player_front[2]=c;
 g.xlwResolveMechanicalEffects=async()=>{g.field.player_front[2]=null;};
 assert.equal(await g.xlwExecuteMechCombine(a,b,'player_front',0,'player_front',1,true,{mecha:true}),false);
 assert.equal(g.field.player_front[0],a);assert.equal(g.field.player_front[1],b);assert.equal(a.equipments[0],'retain');
});
test('inherited combat traits require the exposed attack side',()=>{
 const {g}=fixture(),u=unit('top');u.devourCards=[{card:card('bottom',{keywords:['貫穿','劇毒','遠程','阻擋']}),expose:'stars'}];
 for(const word of ['貫穿','劇毒','遠程','阻擋'])assert.equal(g.xlwFusedKeyword(u,word),false);
 u.devourCards[0].expose='atk';for(const word of ['貫穿','劇毒','遠程','阻擋'])assert.equal(g.xlwFusedKeyword(u,word),true);
});
test('boarding respects printed capacity and prevents disembark until a later turn',async()=>{
 const {g}=fixture(),u=unit('transport',{card:card('transport',{effect_text:'搭乘1(3)'}),summonedTurn:4});
 assert.equal(g.xlwPassengerCount(u),1);assert.equal(await g.xlwDismountTravelers(u,1,true),false);
 assert.equal(await g.xlwBoardTravelerIntoTransport(null,u,2),true);assert.equal(u.passengers,3);assert.equal(u.rideCount,3);
 assert.equal(await g.xlwBoardTravelerIntoTransport(null,u,1),false);g.turn++;
 let summoned=0;g.xlwSpecialSummonUnit=async()=>{summoned++;};assert.equal(await g.xlwDismountTravelers(u,2,true),true);assert.equal(u.passengers,1);assert.equal(summoned,0);
});
test('disembark bells trigger once per card, not by summoning the departing passengers',async()=>{
 const {g}=fixture(),u=unit('transport',{card:card('transport',{effect_text:'搭乘3'}),summonedTurn:2});g.field.player_front[0]=unit('R-CRB-0025');g.field.player_back[0]=unit('R-CRB-0025');
 let count=0;g.xlwSpecialSummonUnit=async()=>count++;
 await g.xlwDismountTravelers(u,1,true);await g.xlwDismountTravelers(u,1,true);assert.equal(count,2);assert.equal(u.passengers,1);
});
test('losing the passenger trait returns passengers and cannot refill them when regained',()=>{
 const {g}=fixture(),u=unit('transport',{card:card('transport',{effect_text:'搭乘3'})});assert.equal(g.xlwPassengerCount(u),3);
 u.card=card('ordinary',{effect_text:''});assert.equal(g.xlwPassengerCount(u),0);u.card=card('transport',{effect_text:'搭乘3'});assert.equal(g.xlwPassengerCount(u),0);
});
test('energy cap loss changes stored state, and zero consumption needs an explicit card exception',()=>{
 for(const local of [true,false]){const {g,nodes}=fixture(),key=local?'XLW_playerSteamEnergy':'XLW_enemySteamEnergy';g[key]=6;assert.equal(g.xlwGetSteamEnergy(local),5);assert.equal(g[key],5);assert.equal(g.xlwConsumeEnergy(0,local),false);
 nodes[local?'playerField':'enemyField'].dataset.card=JSON.stringify({id:'R-STP-0054'});assert.equal(g.xlwGetSteamEnergy(local),4);assert.equal(g.xlwConsumeEnergy(1,local),true);assert.equal(g[key],4);}
});
test('charging alone never triggers electricity; sliding follows ordered lanes and excludes the slider',async()=>{
 const {g}=fixture(),order=[];g.field.player_front[3]=unit('R-STP-0046');g.field.player_front[1]=unit('R-STP-0052');g.field.enemy_front[0]=unit('R-STP-0046');const slider=g.field.player_back[0]=unit('R-STP-0046');
 g.logBattle=text=>{if(text.startsWith('【通電】'))order.push(text);};await g.xlwChargeEnergy(1,true);assert.equal(g.playerBonusScore,0);
 await g.xlwTriggerElectrify(true,slider,[3,2,1,0]);assert.equal(order.length,3);assert.match(order[0],/4號/);assert.match(order[1],/2號/);assert.match(order[2],/1號/);assert.equal(g.XLW_playerSteamEnergy,3);assert.equal(g.playerBonusScore,2);assert.equal(g.enemyBonusScore,2);
});
test('multiple electrification effects on one unit follow its controllers choice',async()=>{
 const {g}=fixture(),order=[],u=unit('R-STP-0046');u.equipments=['通電道具 通電裝'];g.field.player_front[1]=u;
 g.xlwChooseFactionAction=async(local,key,title,message,options)=>options.find(o=>o.value==='suit')?.value||options[0].value;
 g.logBattle=text=>{if(text.startsWith('【通電】'))order.push(text);};await g.xlwTriggerElectrify(true,null,[1]);
 assert.match(order[0],/通電裝/);assert.match(order[1],/電能方塊/);assert.equal(g.XLW_playerSteamEnergy,2);assert.equal(g.playerBonusScore,2);
});
test('the active player selects one captive, its holder places it, and remaining captives go to their holders graves',async()=>{
 const {g}=fixture(),a={id:'a',name:'a',originalOwner:'enemy'},b={id:'b',name:'b',originalOwner:'player'},captor=unit('captor',{kidnappedCards:[a,b]});g.field.player_front[0]=captor;
 const decisions=[];g.xlwChooseFactionAction=async(local,key,title,text,options)=>{decisions.push(local);return title==='綁架者離場'?1:options[0].value;};
 await g.cleanUnitLeavingField(captor,'player_front');assert.equal(g.field.player_front[0].card,b);assert.equal(g.field.player_front[0].tapped,true);assert.equal(g.XLW_ENEMY.grave[0],a);assert.deepEqual(decisions,[true,true]);
});
test('a captive with a full owners board goes to grave, never to hand',async()=>{
 const {g}=fixture(),c={id:'held',originalOwner:'enemy'},captor=unit('captor',{kidnappedCards:[c]});for(const z of ['enemy_front','enemy_back'])g.field[z].fill(unit('occupied'));
 await g.cleanUnitLeavingField(captor,'player_front');assert.equal(g.XLW_ENEMY.grave[0],c);assert.equal(g.XLW_ENEMY.hand.length,0);
});
test('a summoned captive in the vacated slot is not erased by the outer destruction routine',async()=>{
 const {g}=fixture(),held={id:'held',name:'held',originalOwner:'player'},captor=unit('captor',{kidnappedCards:[held]});g.field.player_front[0]=captor;
 await g.destroyUnit('player_front',0,'player',false);assert.equal(g.field.player_front[0].card.id,'held');assert.equal(g.field.player_front[0].tapped,true);
});
test('a negated open card completes without TDZ errors and goes to its holder, from either seat',async()=>{
 for(const local of [true,false]){const {g}=fixture(),card={id:'open-test',name:'open-test',attack:2,originalOwner:local?'enemy':'player'};
 g.XLW_playerRouletteWheel=[];g.XLW_enemyRouletteWheel=[];(local?g.XLW_playerRouletteWheel:g.XLW_enemyRouletteWheel).push(card);
 const start=source.indexOf('window.xlwSpinWheel =');vm.runInContext(source.slice(start,source.indexOf('\n};',start)+3),g);
 await g.xlwSpinWheel(local,1,null,{suppressOpenEffect:true});assert.equal((local?g.XLW_ENEMY.grave:g.graveyard)[0],card);assert.equal((local?g.graveyard:g.XLW_ENEMY.grave).length,0);
 }
});

const brokerScope={};vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/faction_choices.js'),'utf8'),brokerScope);
test('mirrored faction decisions open one owner prompt and deliver the same result to both sides',async()=>{
 let resolve,calls=0,brokers;
 const options=[{text:'first',value:0},{text:'second',value:1}];
 brokers=[0,1].map(i=>brokerScope.XLWFactionChoices.create({choose:async()=>{calls++;return new Promise(done=>resolve=done);},send:data=>brokers[1-i].receive(data)}));
 const own=brokers[0].choose(true,'shared','x','x',options);
 const peer=brokers[1].choose(false,'shared','x','x',options);
 await Promise.resolve();assert.equal(calls,1);resolve(1);assert.deepEqual(await Promise.all([own,peer]),[1,1]);
});
test('a faction result arriving before its mirrored trigger is retained',async()=>{
 const broker=brokerScope.XLWFactionChoices.create({choose:()=>assert.fail('remote result already exists'),send:()=>assert.fail('no duplicate request')});
 broker.receive({action:'faction_choice_result',key:'early',value:1});
 assert.equal(await broker.choose(false,'early','x','x',[{value:0},{value:1}]),1);
});
test('wheel and fused-card holder markers mirror without changing the sender data',()=>{
 const {g}=fixture();const source=[{originalOwner:'player',devourCards:[{card:{originalOwner:'enemy'}}]}];
 const next=g.xlwFlipHolderMarkers(source);assert.equal(next[0].originalOwner,'enemy');assert.equal(next[0].devourCards[0].card.originalOwner,'player');assert.equal(source[0].originalOwner,'player');
});
test('manual mechanical phase usage is restored with the appropriate peer ownership',()=>{
 const {g}=fixture();g.XLW_mechanicalManualTurn=4;g.XLW_enemyMechanicalManualTurn=3;g.XLW_playerRouletteWheel=[];g.XLW_enemyRouletteWheel=[];
 const snapshot=g.xlwCaptureFactionState();const {g:peer}=fixture();peer.xlwRestoreFactionState(snapshot,true);
 assert.equal(peer.XLW_mechanicalManualTurn,3);assert.equal(peer.XLW_enemyMechanicalManualTurn,4);
});

test('effect-created extra mechanical phase has its own name and slot restrictions',async()=>{
 const {g}=fixture(),a=unit('a'),b=unit('b');g.field.player_front[0]=a;g.field.player_front[1]=b;
 g.XLW_mechPhase={turn:g.turn,names:new Set(['a']),slots:new Set(['player_front:0']),manual:true};
 assert.equal(await g.xlwExecuteMechCombine(a,b,'player_front',0,'player_front',1,true,{effect:true}),true);
 assert.equal(g.XLW_mechPhase.names.size,1);
});
test('a foreign fusion effect asks its controller rather than auto-selecting the first target',async()=>{
 const {g}=fixture();g.isMultiplayer=true;
 g.field.player_front[0]=unit('victim0');g.field.player_front[1]=unit('victim1');let requested=false,removed;
 g.xlwChooseFactionAction=async(local,key,title,message,options)=>{assert.equal(local,false);requested=true;return 1;};g.destroyUnit=async(z,i)=>removed=[z,i];
 const c=card('RBT-0001');await g.xlwResolveMechanicalEffects({key:'foreign',sourceCard:c,targetCard:card('b'),targetUnit:unit('result'),targetZone:'enemy_front',targetIdx:0,combinedCards:[c,card('b')]},false,[c],false);
 assert.equal(requested,true);assert.deepEqual(removed,['player_front',1]);
});
test('active-player board authority still accepts peer collection baselines',()=>{
 const handler=slice('} else if (data.action === "sync_game_state") {','const quietEventRecovery');
 assert.match(handler,/xlwAcceptSpellOwnerCollections\(\{hand:s\.playerHand,deck:s\.playerDeck/);
});
