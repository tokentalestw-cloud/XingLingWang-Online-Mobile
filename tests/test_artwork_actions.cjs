const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const game = fs.readFileSync(path.join(__dirname, "../static/game_v8.js"), "utf8");
const section = (start, end) => game.slice(game.indexOf(start), game.indexOf(end, game.indexOf(start)));

test("Soft Clocks taps selected units only and its branch exits after one grave entry", async () => {
  const units = ["甲", "乙", "丙"].map(name => ({card: {name}, tapped: false}));
  const spell = {id: "C-ART-0073"};
  const selected = [1, "cancel"];
  const context = vm.createContext({
    window: {}, field: {player_front: units, player_back: []}, hand: [spell], handIndex: 0, card: spell,
    graveyard: [], logBattle() {}, render() {}, xlwOnPlayerUnitTapped: async () => {},
    showXLWChoiceModal: async () => selected.shift(),
    xlwShowSpellActivationOverlay: async () => {},
    castSpellChain: async (_, callback) => callback()
  });
  vm.runInContext(section("async function xlwResolveSoftClocks()", "// 魔法卡點擊發動"), context);
  const branch = section('  } else if (card.id === "C-ART-0073"', "  // 14. R-VRT-0070");
  await vm.runInContext("(async () => { if (false) {" + branch + "} graveyard.push(card); })()", context);
  assert.deepEqual(units.map(unit => unit.tapped), [false, true, false]);
  assert.deepEqual(context.graveyard, [spell]);
});

test("Breakfast may return from the field in each part of the main phase", async () => {
  for (const phase of ["召喚階段", "戰術佈陣", "進攻宣言"]) {
    const card = {id: "R-ART-0030"};
    const unit = {card};
    const field = {player_front: [unit]};
    const drawn = {id: "top"};
    const deck = [drawn], hand = [];
    const context = vm.createContext({
      window: {isUnitSilenced: () => false}, field, deck, hand, phase, isMyTurn: true, isMultiplayer: false,
      xlwSpellActionPending: () => false, cleanUnitLeavingField: async () => {},
      draw() { hand.push(deck.pop()); }, shuffle() {}, render() {}, logBattle() {}
    });
    vm.runInContext(section("function xlwIsBreakfast(", "window.xlwExecuteHandUnitSummon"), context);
    await context.xlwResolveBreakfast(card, {zone: "player_front", idx: 0, unit});
    assert.equal(field.player_front[0], null);
    assert.deepEqual(hand, [drawn]);
    assert.deepEqual(deck, [card]);
  }
});
