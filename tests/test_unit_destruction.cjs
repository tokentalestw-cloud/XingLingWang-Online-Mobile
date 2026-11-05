const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/game_v8.js'), 'utf8');
function section(name) {
  const start = source.search(new RegExp('(?:async )?function ' + name + '\\('));
  const next = source.slice(start + 1).search(/\n(?:async )?function /);
  return source.slice(start, next < 0 ? undefined : start + 1 + next);
}
const code = ['destroyUnit', 'isUnitIndestructible', 'isUnitAttackProtected', 'resolveUnitCombat'].map(section).join('\n');
function unit(id, attack, properties = {}) {
  return { card: { id, name: id, attack, score: 1 }, equipments: [], ...properties };
}
function fixture() {
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
    showCombatNumberAnimation: async () => {}, applyCombatSuccessReward() {}
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
