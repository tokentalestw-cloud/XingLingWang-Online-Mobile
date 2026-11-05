const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/game_v8.js'), 'utf8');
const start = source.indexOf('function getUnitAtk(');
const end = source.indexOf('\nfunction ', source.indexOf('function getUnitStars(', start) + 1);
const statSource = source.slice(start, end);
let tests = 0;
function fixture() {
  const g = {
    field: Object.fromEntries(['player_front','player_back','enemy_front','enemy_back'].map(z => [z, Array(5).fill(null)])),
    $: () => null, isDessertUnit: () => false, isDrinkerUnit: () => false,

    turn: 4, phase: '召喚階段', deck: [{}], hand: [], graveyard: [], enemyGraveyard: [],
    playerBonusScore: 0, enemyBonusScore: 0
  };
  g.window = g;
  g.XLW_ENEMY = { deck: [{}], hand: [], grave: [] };
  for (const match of statSource.matchAll(/window\.([A-Za-z_$][\w$]*)\s*\(/g)) g[match[1]] = () => false;
  g.xlwIsLittleTraveler = unit => unit?.card?.id === 'TOKEN_TRAVELER';
  g.isUnitSilenced = () => false;
  vm.createContext(g);
  vm.runInContext(statSource, g);
  return g;
}
function unit(id, name, attack = 1, score = 1) { return { card: { id, name, attack, score }, equipments: [] }; }
module.exports = (async () => {
  for (const side of ['player', 'enemy']) {
    const g = fixture();
    const zone = side + '_front';
    const back = side + '_back';
    let u = unit('TEST', '測試單位', 3);
    u.atkModifier = 2;
    g.field[zone][2] = u;
    assert.equal(g.getUnitAtk(u, zone, 2), 5);
    assert.equal(g.getUnitAtk(u), 5);
    tests += 2;
    u = unit('SR-SPT-0023', '火焰旅人');
    u.attacking = true;
    g.field[zone][2] = u;
    assert.equal(g.getUnitAtk(u, zone, 2), 5);
    tests++;
    u = unit('TOKEN_TRAVELER', '小旅人');
    g.field[zone][2] = u;
    g.field[zone][1] = unit('SPT-0007', '勇氣旅人', 4, 4);
    g.field[back][0] = unit('SPT-0010', '中旅人', 3, 3);
    assert.equal(g.getUnitAtk(u, zone, 2), 5);
    g.field[back][1] = unit('R-SPT-0050', '詩配酒旅人', 6, 6);
    assert.equal(g.getUnitAtk(u, zone, 2), 5);
    assert.equal(g.getUnitStars(u, zone, 2), 4);
    tests += 3;
    u = unit('SPT-0057', '怨念的小旅人', 1, -2);
    g.field[zone][2] = u;
    assert.equal(g.getUnitAtk(u, zone, 2), 1);
    assert.equal(g.getUnitStars(u, zone, 2), -2);
    tests += 2;
    u = unit('CCS-0035', '加油小丑', 'X', 'X');
    u.atkModifier = 2;
    g.field[zone][2] = u;
    g.XLW_playerRouletteWheel = [{}, {}, {}];
    g.XLW_enemyRouletteWheel = [{}, {}];
    assert.equal(g.getUnitAtk(u, zone, 2), (side === 'player' ? 3 : 2) + 2);
    assert.equal(g.getUnitStars(u, zone, 2), side === 'player' ? 3 : 2);
    tests += 2;
  }
  console.log(`${tests} bidirectional attack/score scope, traveler buffs and summon-stat checks: PASS`);
})();
