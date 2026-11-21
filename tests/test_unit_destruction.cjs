const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const {test} = require('node:test');
const source = fs.readFileSync(path.join(__dirname, '../static/game_v8.js'), 'utf8');
function section(name) {
  const start = source.search(new RegExp('(?:async )?function ' + name + '\\('));
  const next = source.slice(start + 1).search(/\n(?:async )?function /);
  return source.slice(start, next < 0 ? undefined : start + 1 + next);
}
const code = ['destroyUnit', 'isUnitIndestructible', 'isUnitAttackProtected', 'xlwHandleWolfMaceCombatSuccess', 'resolveUnitCombat'].map(section).join('\n');
function unit(id, attack, properties = {}) {
  return { card: { id, name: id, attack, score: 1 }, equipments: [], ...properties };
}
function fixture(withRewards = false) {
  const g = {
    console, document: { querySelector: () => null, getElementById: () => null },
    field: Object.fromEntries(['player_front','player_back','enemy_front','enemy_back'].map(z => [z, Array(5).fill(null)])),
    graveyard: [], enemyGraveyard: [], hand: [], deck: [], playerExtraDeck: [], enemyExtraDeck: [],
    playerExileZone: [], enemyExileZone: [], turn: 4, isMyTurn: true, isMultiplayer: true,
    ws: null, countdownActive: false, playerBonusScore: 0, enemyBonusScore: 0,
    logBattle() {}, logDebug() {}, render() {}, renderScore() {}, sleep: async () => {},
    cleanUnitLeavingField: async () => {}, unitName: u => u.card.name,
    showXLWConfirm: async () => false, showXLWChoiceModal: async () => null,
    getCardTributeCost: card => Number(card.tribute || 0), setTimeout: () => 0,
    getUnitAtk: u => Number(u.card.attack), getUnitStars: u => Number(u.card.score),
    hasArmorBreak: () => false, checkUnitHasPiercing: () => false,
    showCombatNumberAnimation: async () => {}, applyCombatSuccessReward() {}, sendFullGameStateToOpponent() {}
  };
  g.window = g;
  g.XLW_ENEMY = { hand: [], deck: [], grave: g.enemyGraveyard };
  for (const match of code.matchAll(/window\.([A-Za-z_$][\w$]*)\s*\(/g)) {
    if (!(match[1] in g)) g[match[1]] = () => false;
  }
  g.xlwUnitHasPoison = u => Boolean(u.poison);
  g.XLW_isShieldUnit = u => u?.card?.attack === '盾';
  vm.createContext(g);
  vm.runInContext(code, g);
  if (withRewards) vm.runInContext(section('applyCombatSuccessReward'), g);
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../static/battle_flow.js'), 'utf8'), g);
  return g;
}
let tests = 0;
module.exports = (async () => {
  for (const zone of ['player_front','player_back','enemy_front','enemy_back']) {
    const owner = zone.startsWith('player_') ? 'player' : 'enemy';
    for (const combat of [false, true]) {
      const g = fixture();
      const u = unit('ordinary', 3);
      g.field[zone][2] = u;
      await Promise.all([g.destroyUnit(zone, 2, owner, false, combat), g.destroyUnit(zone, 2, owner, false, combat)]);
      assert.equal(g.field[zone][2], null);
      assert.equal((owner === 'player' ? g.graveyard : g.enemyGraveyard).length, 1);
      assert.equal(g.XLW_activeDestructions.has(u), false);
      tests++;
    }
    const protectedGame = fixture();
    const protectedUnit = unit('C-ART-0061', 3);
    protectedGame.field[zone][2] = protectedUnit;
    await protectedGame.destroyUnit(zone, 2, owner, false, true);
    assert.equal(protectedGame.field[zone][2], protectedUnit);
    assert.equal(protectedGame.graveyard.length + protectedGame.enemyGraveyard.length, 0);
    tests++;
  }
  for (const side of ['player', 'enemy']) {
    const other = side === 'player' ? 'enemy' : 'player';
    for (const [atk, def, attackPoison, defendPoison, attackDies, defendDies] of [
      [5, 2, false, false, false, true],
      [2, 5, false, false, true, false],
      [3, 3, false, false, false, true],
      [2, 5, true, false, true, true],
      [5, 2, true, true, true, true]
    ]) {
      const g = fixture();
      const attacker = unit('attacker', atk, { poison: attackPoison, attacking: true, target: { zone: other + '_front', idx: 0 } });
      const defender = unit('defender', def, { poison: defendPoison });
      g.field[side + '_front'][0] = attacker;
      g.field[other + '_front'][0] = defender;
      await g.resolveUnitCombat(side + '_front', 0, other + '_front', 0, other);
      assert.equal(g.field[side + '_front'][0] === null, attackDies);
      assert.equal(g.field[other + '_front'][0] === null, defendDies);
      assert.equal(g.graveyard.length + g.enemyGraveyard.length, Number(attackDies) + Number(defendDies));
      assert.equal(attacker.attacking, false);
      tests++;
    }
  }
  const immune = fixture();
  immune.field.player_front[0] = unit('BRV-0002', 2, { indestructible: true, poison: true });
  const survivor = unit('survivor', 3, { attacking: true });
  immune.field.enemy_front[0] = survivor;
  await immune.destroyUnit('player_front', 0, 'player', false, true);
  assert.equal(immune.field.enemy_front[0], survivor);
  assert.equal(immune.enemyBonusScore, 0);
  tests++;
  const retry = fixture();
  const u = unit('ordinary', 3);
  retry.field.player_front[0] = u;
  retry.document.querySelector = () => { throw Error('simulated presentation failure'); };
  await assert.rejects(retry.destroyUnit('player_front', 0, 'player', false), /presentation failure/);
  assert.equal(retry.XLW_activeDestructions.has(u), false);
  retry.document.querySelector = () => null;
  await retry.destroyUnit('player_front', 0, 'player', false);
  assert.equal(retry.field.player_front[0], null);
  tests++;
  console.log(`${tests} complete combat/destruction, poison recursion, immunity and duplicate-grave checks: PASS`);
})();

test('combat-success rewards follow attack comparison despite front-row destruction resistance, from either seat', async()=>{
  for(const side of ['player','enemy'])for(const attack of [3,5]) {
    const other=side==='player'?'enemy':'player',g=fixture(true);
    const attacker=unit('R-ORC-0040',attack,{attacking:true});
    const urn=unit('C-ART-0061',3);
    g.field[side+'_front'][0]=attacker;g.field[other+'_front'][0]=urn;
    await g.resolveUnitCombat(side+'_front',0,other+'_front',0,other);
    assert.equal(g.field[other+'_front'][0],urn);
    assert.equal(side==='player'?g.playerBonusScore:g.enemyBonusScore,3);
    assert.equal(attacker.attacking,false);
  }
});
test('surviving a failed comparison does not award combat success',async()=>{
  const g=fixture(true),attacker=unit('R-ORC-0040',2,{indestructible:true});
  g.field.player_front[0]=attacker;g.field.enemy_front[0]=unit('target',5);
  await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
  assert.equal(g.field.player_front[0],attacker);assert.equal(g.playerBonusScore,0);
});
test('defender rewards follow comparison even when the weaker attacker resists destruction',async()=>{
  const g=fixture(true);
  g.field.player_front[0]=unit('R-ORC-0040',2,{indestructible:true});
  g.field.enemy_front[0]=unit('R-ORC-0007',5);
  await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
  assert.equal(g.enemyBonusScore,1);assert.equal(g.playerBonusScore,0);
});
test('poison destruction cannot turn a lower attack into combat success or erase the higher comparison',async()=>{
  const g=fixture(true);
  g.field.player_front[0]=unit('R-ORC-0040',5);
  g.field.enemy_front[0]=unit('poison',2,{poison:true});
  await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
  assert.equal(g.playerBonusScore,3);assert.equal(g.field.player_front[0],null);
});
test('piercing resolves the rear independently instead of unconditionally destroying it',async()=>{
  for(const side of ['player','enemy'])for(const backAttack of [2,5,8]) {
    const other=side==='player'?'enemy':'player',g=fixture(true),animations=[];
    const attacker=unit('R-ORC-0040',5,{piercing:true,attacking:true});
    const back=unit('rear',backAttack);
    g.checkUnitHasPiercing=u=>!!u.piercing;
    g.showCombatNumberAnimation=async(a,ai,d)=>animations.push(d);
    g.field[side+'_front'][0]=attacker;g.field[other+'_front'][0]=unit('C-ART-0061',3);g.field[other+'_back'][0]=back;
    const result=await g.resolveUnitCombat(side+'_front',0,other+'_front',0,other);
    assert.deepEqual(animations,[other+'_front',other+'_back']);
    assert.equal(g.field[other+'_back'][0]===null,backAttack<=5);
    assert.equal(g.field[side+'_front'][0]===null,backAttack>5);
    assert.equal(side==='player'?g.playerBonusScore:g.enemyBonusScore,backAttack<=5?6:3);
    assert.match(result,/貫穿後排/);
  }
});
test('piercing honors rear shields, resistance and poison and stops if the attacker leaves',async()=>{
  for(const kind of ['shield','resistance','poison','dead-attacker']) {
    const g=fixture(),attacker=unit('attacker',5,{piercing:true});
    const front=unit('front',kind==='dead-attacker'?9:1);
    const back=unit(kind==='resistance'?'C-ART-0061':'rear',kind==='shield'?'盾':1,{poison:kind==='poison'});
    g.checkUnitHasPiercing=u=>!!u.piercing;
    g.field.player_front[0]=attacker;g.field.enemy_front[0]=front;g.field.enemy_back[0]=back;
    await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
    if(kind==='poison')assert.equal(g.field.player_front[0],null);
    else assert.equal(g.field.enemy_back[0],back);
    if(kind==='dead-attacker')assert.equal(g.field.player_front[0],null);
  }
});
test('Cleaver rewards only actual destroyed units across both piercing battles',async()=>{
  for(const frontProtected of [false,true]) {
    const g=fixture(true),attacker=unit('ORC-0003',5,{piercing:true});
    g.checkUnitHasPiercing=u=>!!u.piercing;
    g.field.player_front[0]=attacker;
    g.field.enemy_front[0]=unit(frontProtected?'C-ART-0061':'front',2);
    g.field.enemy_back[0]=unit('rear',2);
    await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
    assert.equal(g.playerBonusScore,frontProtected?1:2);
  }
});
test('sneak recall waits until piercing finishes and can follow a rear-only success',async()=>{
  const g=fixture();let decisions=0;
  g.isMultiplayer=false;
  g.checkUnitHasPiercing=u=>!!u.piercing;
  g.xlwUnitHasSneak=u=>!!u.sneak;
  g.showXLWConfirm=async()=>{decisions++;return false;};
  const attacker=unit('attacker',5,{piercing:true,sneak:true,indestructible:true});
  g.field.player_front[0]=attacker;g.field.enemy_front[0]=unit('strong-front',9);g.field.enemy_back[0]=unit('weak-rear',1);
  await g.resolveUnitCombat('player_front',0,'enemy_front',0,'enemy');
  assert.equal(g.field.enemy_back[0],null);assert.equal(decisions,1);assert.equal(attacker.tapped,true);
});
