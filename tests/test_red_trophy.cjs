const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const {test} = require("node:test");
const source = fs.readFileSync(require("node:path").join(__dirname, "../static/game_v8.js"), "utf8");

test("a trophy uses attack 6, loses irrigation, and pays only the finishing side", async () => {
  const g = {
    structuredClone, turn: 4, graveyard: [], enemyGraveyard: [], playerBonusScore: 0, enemyBonusScore: 0,
    getUnitAtk: unit => unit.power,
    xlwUnitHasRanged: unit => unit.ranged,
    showCombatNumberAnimation: async (_zone, _lane, target, idx, _attack, defense) => {
      assert.deepEqual([target, idx, defense], ["star_trophy", 2, 6]);
    },
    destroyed: [],
    destroyUnit: async (_zone, _lane, owner) => { g.destroyed.push(owner); },
    xlwHandleUnitTappedTriggers: async () => {},
    XLWBattleFlow: {settle: unit => { unit.attacking = false; unit.tapped = true; }},
    logBattle() {}, render() {}
  };
  g.window = g;
  const start = source.indexOf("const TROPHY_ATTACK");
  vm.runInNewContext(source.slice(start, source.indexOf("// 主要階段開始時效果 (PG2", start)), g);
  const trophy = {id:"alpha", owner:"player", irrigation:15, placedTurn:3, card:{id:"SR-NMG-0042"}};
  g.xlwStarLineTrophies[2] = trophy;
  const strike = (power, owner, ranged = false) => g.xlwResolveTrophyAttack({power, ranged, trophyTargetId:"alpha"}, owner + "_front", 2);
  await strike(5, "enemy");
  assert.equal(trophy.irrigation, 10);
  assert.deepEqual(g.destroyed, ["enemy"]);
  await strike(4, "player", true);
  assert.equal(trophy.irrigation, 6);
  assert.deepEqual(g.destroyed, ["enemy"]);
  await strike(6, "enemy");
  assert.equal(g.xlwTrophyAt(2), null);
  assert.equal(g.enemyBonusScore, 15);
  assert.equal(g.playerBonusScore, 0);
  assert.equal(g.graveyard.length, 1);
  await strike(15, "enemy");
  assert.equal(g.enemyBonusScore, 15);
  const stale = Array(5).fill(null);
  stale[2] = {...trophy, irrigation:15, owner:"enemy"};
  g.xlwRestoreTrophies(stale, true);
  assert.equal(g.xlwTrophyAt(2), null);
  stale[2] = {...stale[2], id:"beta", placedTurn:4};
  g.xlwRestoreTrophies(stale, true);
  assert.equal(g.xlwTrophyAt(2).owner, "player");
});
