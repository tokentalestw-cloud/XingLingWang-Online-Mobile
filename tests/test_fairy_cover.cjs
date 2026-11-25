const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const source = fs.readFileSync(path.join(__dirname, "../static/game_v8.js"), "utf8");
const cards = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/cards.json"), "utf8"));
const code = (a, b) => source.slice(source.indexOf(a), source.indexOf(b, source.indexOf(a)));
const rows = () => Object.fromEntries(["player_front", "player_back", "enemy_front", "enemy_back"].map(row => [row, Array(5).fill(null)]));

test("all printed innate cover cards and each conditional cover source are recognized", () => {
  const field = rows();
  const ctx = vm.createContext({field, window: {
    isUnitSilenced: unit => !!unit.silenced, xlwIsUnitMech: unit => !!unit.mech,
    XLW_isShieldUnit: unit => !!unit.shield
  }});
  vm.runInContext(code("window.xlwCardHasKeyword =", "window.isPowerPlantUnit ="), ctx);
  vm.runInContext(code("function xlwUnitHasCover(", "async function performSummonToSlot("), ctx);
  const byId = id => cards.find(card => card.id === id);
  const innate = cards.filter(card => /(?:^|[。\n])掩護(?:[。\n]|$)/.test(card.effect_text));
  assert.ok(innate.length >= 8);
  for (const card of innate) assert.ok(ctx.xlwUnitHasCover({card}, "player_front", 2), card.name);
  const shield = {card: {id: "TEST"}, shield: true};
  field.player_back[0] = {card: byId("SR-EVL-0062")};
  assert.equal(ctx.xlwUnitHasCover(shield, "player_front", 2), true);
  assert.equal(ctx.xlwUnitHasCover(field.player_back[0], "player_back", 0), false);
  assert.equal(ctx.xlwUnitHasCover(shield, "enemy_front", 2), false);
  field.player_back[0].silenced = true;
  assert.equal(ctx.xlwUnitHasCover(shield, "player_front", 2), false);
  field.player_back[0] = {card: byId("RBT-0010")};
  assert.equal(ctx.xlwUnitHasCover({card: {id: "TEST"}, mech: true}, "player_front", 2), true);
  assert.equal(ctx.xlwUnitHasCover({card: byId("SSSR-NMS-0067"), tapped: true}, "player_front", 2), true);
  assert.equal(ctx.xlwUnitHasCover({card: {id: "TEST"}, equipments: ["金屬盾牌"]}, "player_front", 2), true);
});

test("Fairy Strategist moves and optionally straightens a unit on its own side", async () => {
  const field = rows();
  const unit = {card: {name: "測試單位"}, tapped: true};
  field.enemy_front[2] = unit;
  const ctx = vm.createContext({
    field, window: {}, xlwIsUnitUnmovable: () => false, render() {}, logBattle() {},
    showXLWConfirm: async () => true, showXLWChoiceModal: async (_, __, options) => options[0].value
  });
  vm.runInContext(code("async function xlwResolveFairyStrategist(", "// 立即發動與入場結算 (PG2"), ctx);
  await ctx.xlwResolveFairyStrategist(true);
  assert.equal(field.enemy_front[2], null);
  assert.equal(field.enemy_front[0], unit);
  assert.equal(unit.tapped, false);
});

test("Small Trap prompts after two summons and compares original attack", async () => {
  const field = rows();
  field.enemy_front[0] = {card: {name: "低攻單位", attack: "3"}, summonedTurn: 3};
  field.enemy_front[1] = {card: {name: "高攻單位", attack: "5"}, summonedTurn: 3};
  field.enemy_front[2] = {card: {name: "舊單位", attack: "1"}, summonedTurn: 2};
  const hand = [{id: "R-NMG-0018"}], graveyard = [];
  let prompts = 0;
  const ctx = vm.createContext({
    field, hand, graveyard, turn: 3, window: {XLW_enemySummonCountThisTurn: 1},
    structuredClone, isUnitMagicImmune: () => false, xlwShowSpellActivationOverlay: async () => {},
    showXLWConfirm: async () => { throw new Error("No redundant confirmation"); },
    showXLWChoiceModal: async (_, __, options) => {
      prompts++;
      assert.equal(options.length, 1);
      return options[0].value;
    },
    destroyUnit: async (zone, idx) => { field[zone][idx] = null; },
    logBattle() {}, render() {}
  });
  const counters = code("window.checkForPlayerSummonCounters =", "  // 2. 嚇人彈跳廣告");
  vm.runInContext(counters + "\n};", ctx);
  vm.runInContext(fs.readFileSync(path.join(__dirname, "../static/duel_consistency.js"), "utf8"), ctx);
  await ctx.window.checkForPlayerSummonCounters();
  assert.equal(prompts, 0);
  ctx.window.XLW_enemySummonCountThisTurn = 2;
  await ctx.window.checkForPlayerSummonCounters();
  assert.equal(prompts, 1);
  assert.equal(field.enemy_front[0], null);
  assert.equal(graveyard.length, 1);
});
