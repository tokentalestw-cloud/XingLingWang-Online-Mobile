const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "../static/game_v8.js"), "utf8");
function section(start, end) {
  const a = source.indexOf(start);
  const b = source.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, `Missing source section: ${start}`);
  return source.slice(a, b);
}

module.exports = (async () => {
  const eligible = { id: "CCS-0006", name: "表演人偶", type: "unit" };
  const first = { id: "NEUTRAL-1", type: "unit" };
  const second = { id: "NEUTRAL-2", type: "unit" };
  const deck = [eligible, first, second];
  const wheel = [];
  const math = Object.create(Math);
  math.random = () => 0;
  const context = {
    deck, Math: math, getCardTributeCost: () => 0,
    showXLWChoiceModal: async () => 0,
    window: {
      xlwIsCircusCard: card => card.id.startsWith("CCS-"),
      xlwPutCardOnWheel: async (card, isPlayer) => { assert.equal(isPlayer, true); wheel.push(card); }
    }
  };
  vm.createContext(context);
  vm.runInContext(section("function shuffle(arr)", "function draw(n)"), context);
  vm.runInContext("async function summon(card, zone) {" +
    section("// 🎪 馬戲團好夥伴 (R-CCS-0026", "// 🦀 討拍旅人 火野貝") + "}", context);
  await context.summon({ id: "R-CCS-0026" }, "player_front");
  assert.deepEqual(deck, [second, first]);
  assert.deepEqual(wheel, [eligible]);

  const field = {
    player_front: [{ card: { id: "CCS-0032" } }, { card: { id: "CCS-0032" } }],
    player_back: [], enemy_front: [], enemy_back: []
  };
  const graveyard = [];
  let drawn = 0;
  const spin = {
    field, deck: [{}, {}], hand: [], graveyard, Math: math,
    getUnitAtk: () => 4, draw: n => { drawn += n; }, render() {}, logBattle() {}
  };
  spin.window = spin;
  spin.isUnitSilenced = () => false;
  spin.XLW_playerRouletteWheel = [{ id: "OTHER", name: "測試", attack: 5 }, { id: "OTHER", name: "測試", attack: 5 }];
  vm.runInNewContext(section("window.xlwSpinWheel =", "window.xlwIsLittleTraveler ="), spin);
  await spin.xlwSpinWheel(true, 2);
  assert.equal(drawn, 1);
  assert.equal(graveyard.length, 2);
  console.log("2 circus summon, shuffle and once-per-turn reveal draw regressions: PASS");
})();
