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
  const identity = fs.readFileSync(path.join(__dirname, "../static/duel_consistency.js"), "utf8");
  vm.runInContext(identity, context);
  vm.runInContext(section("async function xlwMovePileCardToWheel(", "async function xlwResolveWheelEntryEffect("), context);
  await context.summon({ id: "R-CCS-0026" }, "player_front");
  assert.deepEqual(deck, [second, first]);
  assert.deepEqual(wheel, [eligible]);
  const selected = {id: "CCS-0006", _xlwInstanceId: "chosen"};
  const other = {id: "CCS-0006", _xlwInstanceId: "other"};
  const live = [{...selected}, other];
  assert.equal(await context.xlwMovePileCardToWheel(live, selected, true), undefined);
  assert.deepEqual(live, [other]);
  assert.equal(wheel.at(-1)._xlwInstanceId, "chosen");
  assert.equal(await context.xlwMovePileCardToWheel(live, selected, true), false);
  assert.deepEqual(live, [other]);
  assert.equal(wheel.length, 2);

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
  spin.isMultiplayer = false;
  spin.setTimeout = setTimeout;
  spin.XLW_enemyRouletteWheel = [];
  vm.runInNewContext(section("function xlwHasInnateWheelEntry(", "function renderCircusWheel("), spin);
  spin.xlwGravePile(graveyard, true);
  const innate = { id: "CCS-0031", name: "壯膽觀眾", type: "unit", effect_text: "上靶。開盤：增加攻擊力。" };
  const incidental = { id: "CCS-0015", name: "上靶自願者", type: "unit", effect_text: "立即：使你場上單位上靶。" };
  assert.equal(spin.xlwHasInnateWheelEntry(innate), true);
  assert.equal(spin.xlwHasInnateWheelEntry(incidental), false);
  spin.isUnitSilenced = () => false;
  spin.XLW_playerRouletteWheel = [{ id: "OTHER", name: "測試", attack: 5 }, { id: "OTHER", name: "測試", attack: 5 }];
  vm.runInNewContext(section("window.xlwSpinWheel =", "window.xlwIsLittleTraveler ="), spin);
  await spin.xlwSpinWheel(true, 2);
  assert.equal(drawn, 1);
  assert.equal(graveyard.length, 2);
  spin.xlwResolveWheelEntryEffect = async () => {};
  graveyard.push(innate, incidental);
  assert.equal(spin.XLW_playerRouletteWheel[0], innate);
  assert.equal(graveyard.at(-1), incidental);
  assert.equal(graveyard.includes(innate), false);
  await spin.XLW_wheelEntryQueue;
  await spin.xlwSpinWheel(true);
  assert.equal(spin.XLW_playerRouletteWheel.length, 0);
  assert.equal(graveyard.at(-1), innate);
  spin.renderScore = () => {};
  spin.playerBonusScore = 0;
  for (const [id, name] of [["R-CCS-0041", "幸運觀眾"], ["CCS-0003", "喵草"]]) {
    for (const success of [true, false]) {
      const revealed = {id, name, attack: 1};
      spin.XLW_playerRouletteWheel = [revealed];
      spin.xlwSpecialSummonUnit = async card => {
        assert.equal(card, revealed);
        return success;
      };
      const graveCount = graveyard.length;
      const reward = spin.playerBonusScore;
      await spin.xlwSpinWheel(true);
      assert.equal(graveyard.length, graveCount + Number(!success));
      if (!success) assert.equal(graveyard.at(-1), revealed);
      assert.equal(spin.playerBonusScore, reward + Number(id === "R-CCS-0041"));
    }
  }
  console.log("Circus regressions: transfers, once-per-turn draw and exclusive summon or grave after reveal");
})();
