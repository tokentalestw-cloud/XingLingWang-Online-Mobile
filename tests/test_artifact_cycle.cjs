const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');
const fixtureCode=fs.readFileSync(path.join(__dirname,'test_unit_destruction.cjs'),'utf8').split('let tests = 0;')[0];
const fixtureScope={require,__dirname,console};vm.runInNewContext(fixtureCode,fixtureScope);
const section=(start,end)=>source.slice(source.indexOf(start),source.indexOf(end,source.indexOf(start)));
function setup(){
  const g=fixtureScope.fixture();g.isMultiplayer=false;g.structuredClone=structuredClone;
  g.xlwResolveHorrorPriestTribute=async()=>false;
  g.showXLWConfirm=async()=>true;
  g.showXLWChoiceModal=async(t,m,options)=>options[0].value;
  vm.runInContext(section('async function xlwChooseArtifactCycle(','async function executeTributeEffects('),g);
  return g;
}
test('pot tribute and Mummy destruction repeat without duplicating or losing cards on either side',async()=>{
  for(const side of ['player','enemy']){
    const g=setup(),pot={id:'R-ART-0071',name:'狗頭陶罐',type:'unit',attack:'0',score:3},mummy={id:'C-ART-0072',name:'木乃伊',type:'unit',attack:'3',score:2,keywords:['消逝']};
    const extra=side==='player'?g.playerExtraDeck:g.enemyExtraDeck;
    const grave=side==='player'?g.graveyard:g.enemyGraveyard;
    extra.push(mummy);g.field[side+'_front'][0]={card:pot,equipments:[]};
    for(let round=0;round<3;round++){
      const unit=g.field[side+'_front'][0];
      await (side==='player'?g.xlwPlayerTributeUnit:g.xlwEnemyTributeUnit)(unit,side+'_front',0);
      assert.equal(g.field[side+'_front'][0]?.card.id,mummy.id);assert.equal(grave.length,1);assert.equal(extra.length,0);
      await g.destroyUnit(side+'_front',0,side,false,false);
      assert.equal(g.field[side+'_front'][0]?.card.id,pot.id);assert.equal(grave.length,0);assert.equal(extra.length,1);
      assert.equal(extra[0].id,mummy.id);
    }
  }
});
test('optional artifact summons can be declined and tribute placement retains a reserved slot',async()=>{
  const g=setup();g.playerExtraDeck.push({id:'C-ART-0072',name:'木乃伊'});
  g.showXLWConfirm=async()=>false;
  await g.xlwResolveArtifactCycle('tribute',true);assert.equal(g.playerExtraDeck.length,1);
  for(const row of ['player_front','player_back'])g.field[row]=Array.from({length:5},()=>({card:{id:'occupied'}}));
  g.field.player_front[0]=null;let asked=false;g.showXLWConfirm=async()=>{asked=true;return true;};
  await g.xlwResolveArtifactCycle('tribute',true,1);assert.equal(asked,false);assert.equal(g.field.player_front[0],null);
});
test('online artifact choices are requested from the owning player',async()=>{
  const g=setup();g.isMultiplayer=true;g.enemyExtraDeck.push({id:'C-ART-0072',name:'木乃伊'});
  const sent=[];g.crypto={randomUUID:()=> 'pick-1'};g.ws={send(raw){const data=JSON.parse(raw);sent.push(data);if(data.action==='artifact_cycle_pick')queueMicrotask(()=>g.XLW_artifactCycleWaiters.get(data.requestId)(data.slots[0]));}};
  await g.xlwResolveArtifactCycle('tribute',false);
  assert.equal(sent[0].action,'artifact_cycle_pick');assert.equal(sent[1].action,'artifact_cycle_summon');
  assert.equal(g.field.enemy_front[0].card.id,'C-ART-0072');assert.equal(g.enemyExtraDeck.length,0);
});
test('Garden Aunt offers a real action menu and summons one extra-zone seed at the chosen slot',async()=>{
  for(const id of ['R-PLT-0008','SSSR-PLT-0008']){
    const g=setup();g.field.player_front[0]={card:{id,name:'花園阿姨'}};
    const seed={id:'seed',name:'魔法種子',type:'unit'};g.playerExtraDeck.push(seed);
    g.xlwIsUnitSeed=c=>c?.id==='seed';g.xlwResolvePG2TurnEnd=async()=>{};
    g.xlwGetEmptyPlayerSlots=()=>['player_front','player_back'].flatMap(zone=>g.field[zone].flatMap((u,idx)=>u?[]:[{zone,idx}]));
    g.showXLWChoiceModal=async(t,m,options,config)=>{if(t.includes('花園阿姨')){assert.equal(config.actionChoices,true);return 'seed';}return options.at(-1).value;};
    vm.runInContext(section('window.xlwSummonPlantFromExtraDeck =','// 單位成長核心'),g);
    vm.runInContext(section('window.xlwResolveExpansionTurnEnd =','window.xlwResolveExpansionPostDestruction ='),g);
    await g.xlwResolveExpansionTurnEnd(true);
    assert.equal(g.playerExtraDeck.length,0);assert.equal(g.field.player_front[4].card.id,'seed');
    await g.xlwResolveExpansionTurnEnd(true);assert.equal(g.field.player_back.filter(Boolean).length,0);
  }
});
test('record merging keeps older history, flips perspective and does not duplicate snapshots',()=>{
  const g={};vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/battle_record.js'),'utf8'),g);
  const local=Array.from({length:100},(_,i)=>'old '+i);
  const merged=g.XLWBattleRecord.merge(local,['T3 | 我方召喚木乃伊']);
  assert.equal(merged.length,101);assert.match(merged[0],/對手召喚木乃伊/);
  assert.equal(g.XLWBattleRecord.merge(merged,['T3 | 我方召喚木乃伊']).length,101);
});
test('destroyed magic seeds with Vanish return to their owners extra zone instead of the grave',async()=>{
  for(const side of ['player','enemy']){
    const g=setup(),seed={id:'C-PLT-0035',name:'魔法種子',keywords:['消逝'],attack:0};
    g.xlwCardHasKeyword=(card,keyword)=>card.keywords?.includes(keyword);
    g.field[side+'_front'][0]={card:seed,equipments:[]};
    await g.destroyUnit(side+'_front',0,side,false);
    assert.equal((side==='player'?g.playerExtraDeck:g.enemyExtraDeck)[0].id,seed.id);
    assert.equal((side==='player'?g.graveyard:g.enemyGraveyard).length,0);
  }
});
