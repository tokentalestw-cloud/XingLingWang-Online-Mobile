const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const game = fs.readFileSync(path.join(__dirname, "../static/game_v8.js"), "utf8");
const section = (start, end) => game.slice(game.indexOf(start), game.indexOf(end, game.indexOf(start)));

test("Soft Clocks real choice routing allows board targets plus Finish", async () => {
  const attached = [];
  const slots = new Map();
  const element = () => ({
    classList: {add() {}, remove() {}},
    appendChild(child) { child.parentNode = this; },
    remove() {}, querySelectorAll() { return []; },
    addEventListener(type, handler) { this[type] = handler; },
    removeEventListener(type) { delete this[type]; }
  });
  const context = vm.createContext({window: {}, TROPHY_ZONE: "trophy", document: {
    createElement: element, body: {appendChild(node) { attached.push(node); }},
    querySelector(selector) { if (!slots.has(selector)) slots.set(selector, element()); return slots.get(selector); }
  }});
  vm.runInContext(section("function showXLWChoiceModal(", "// ===== 新增：墓地渲染"), context);
  let settled = false;
  const pending = context.showXLWChoiceModal("軟爛的時鐘們", "選擇我方單位", [
    {text: "甲", value: 0, boardTarget: {zone: "player_front", idx: 0}},
    {text: "結束選擇", value: "cancel"}
  ], {boardOnly: true}).then(value => { settled = true; return value; });
  await Promise.resolve();
  assert.equal(settled, false, "must wait for a board click instead of silently returning null");
  assert.equal(attached.length, 1);
  assert.match(attached[0].innerHTML, /結束選擇/);
  const slot = [...slots.values()][0];
  slot.click({stopPropagation() {}, preventDefault() {}});
  assert.equal(await pending, 0);
  assert.equal(slot.click, undefined, "selection handlers must be removed after choosing");
});

test("Puppeteer uses its printed two stars and needs no tribute", () => {
  const cards = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/cards.json"), "utf8"));
  const card = cards.find(card => card.id === "C-ART-0066");
  const context = vm.createContext({window: {}, field: {player_front: [], player_back: []}, phase: "戰術佈陣", isMyTurn: true, turn: 1});
  vm.runInContext(section("function getCardTributeCost(", "function countSelectedTributesValue("), context);
  assert.equal(card.score, 2);
  assert.equal(context.getCardTributeCost(card), 0);
  context.phase = "召喚階段";
  assert.equal(context.getCardTributeCost(card), 0);
});

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

test("Armor Sword stays on its bearer and enters the grave once when it leaves", async () => {
  const sword = {id: "R-ORC-0072", name: "破甲劍"};
  const unit = {card: {id: "ORC-0001", name: "獸人"}};
  const context = vm.createContext({
    window: {}, field: {player_front: [unit], player_back: []}, graveyard: [],
    showXLWChoiceModal: async () => 0, xlwLogSharedCardEffect() {}, render() {}
  });
  vm.runInContext(section("function xlwArmorSwordTargets()", "async function xlwResolveSoftClocks()"), context);
  vm.runInContext(section("async function cleanUnitLeavingField(", "async function kidnapCard("), context);
  await context.xlwEquipArmorSword(sword);
  assert.deepEqual(Array.from(unit.equipments), ["破甲劍"]);
  assert.equal(context.graveyard.length, 0);
  await context.cleanUnitLeavingField(unit, "player_front");
  await context.cleanUnitLeavingField(unit, "player_front");
  assert.deepEqual(context.graveyard, [sword]);
});

test("Mercenary Camp pays bonus for an Orc-only discount in the current summon phase", async () => {
  const camp = {id: "SR-ORC-0065", name: "獸人傭兵營"};
  const node = {dataset: {card: JSON.stringify(camp)}};
  const context = vm.createContext({
    window: {isUnitSilenced: () => false}, playerBonusScore: 5, phase: "召喚階段", turn: 3,
    field: {player_front: [], player_back: []}, hand: [], isMyTurn: true, isMultiplayer: false,
    $: () => node, xlwRequireSpellCompletion: () => false, showXLWChoiceModal: async () => 2,
    xlwLogSharedCardEffect() {}, render() {}
  });
  vm.runInContext(section("function xlwIsOrcCamp(", "function xlwArmorSwordTargets("), context);
  vm.runInContext(section("function getCardTributeCost(", "function countSelectedTributesValue("), context);
  await context.xlwActivateOrcCamp(camp);
  assert.equal(context.playerBonusScore, 3);
  const orc = {id: "ORC-0001", tribute: 3};
  assert.equal(context.getCardTributeCost(orc), 1);
  assert.equal(context.getCardTributeCost({id: "VLG-0001", tribute: 3}), 3);
  context.phase = "戰術佈陣";
  assert.equal(context.getCardTributeCost(orc), 3);
});
