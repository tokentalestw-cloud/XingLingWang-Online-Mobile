const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const root = path.join(__dirname, "..");
const source = fs.readFileSync(path.join(root, "static/game_v8.js"), "utf8");
const duel = fs.readFileSync(path.join(root, "static/duel_consistency.js"), "utf8");
const slice = (start, end) => {
  const a = source.indexOf(start);
  const b = source.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, start);
  return source.slice(a, b);
};
const unit = (id, fields = {}) => ({card: {id, name: id, type: "unit"}, ...fields});

function fixture() {
  const ctx = vm.createContext({
    isMultiplayer: false, isMyTurn: true, turn: 4, phase: "召喚階段", hand: [], graveyard: [], enemyGraveyard: [],
    playerExtraDeck: [], enemyExtraDeck: [], allCards: [],
    field: Object.fromEntries(["player_front", "player_back", "enemy_front", "enemy_back"].map(z => [z, Array(5).fill(null)])),
    window: {XLW_ENEMY: {hand: [], grave: []}, isUnitSilenced: u => Boolean(u?.silenced), isUnitEffectImmune: u => Boolean(u?.immune),
      xlwIsUnitBarbarian: u => Boolean(u?.savage), xlwIsUnitPatron: c => Boolean(c?.patron), isDemonUnit: () => false,
      xlwCardHasKeyword: () => false},
    isUnitMagicImmune: u => Boolean(u?.magicImmune), isUnitConfined: () => false,
    xlwIsUnitUnmovable: u => Boolean(u?.fixed), cleanUnitLeavingField: async () => {},
    showXLWConfirm: async () => true, showXLWChoiceModal: async () => 0, render() {}, logBattle() {},
    castSpellChain: async (_, apply) => apply(), aiCastSpell: async (_, apply) => apply()
  });
  ctx.destroyUnit = async (z, i) => { if (!ctx.field[z][i]?.protected) ctx.field[z][i] = null; };
  vm.runInContext(duel, ctx);
  return ctx;
}

const push = slice("async function xlwPushUnit(", "async function moveOrPushUnitToSlot");
test("01 rejects unsupported pushes without mutating the lane", async () => {
  const c = fixture();
  c.field.player_front[0] = unit("A");
  vm.runInContext(push, c);
  assert.equal(await c.xlwPushUnit("player_front", 0, "up"), false);
  assert.equal(c.field.player_front[0].card.id, "A");
});
test("02 stops a collision from overwriting a protected unit", async () => {
  const c = fixture();
  c.field.player_front.splice(0, 3, unit("A"), unit("B", {protected: true}), unit("C"));
  c.isUnitConfined = (_, idx) => idx === 2;
  vm.runInContext(push, c);
  assert.equal(await c.xlwPushUnit("player_front", 0, "right"), false);
  assert.deepEqual(c.field.player_front.slice(0, 3).map(x => x.card.id), ["A", "B", "C"]);
});
test("03 returns fusion pieces when the carrier is pushed into hand", async () => {
  const c = fixture();
  c.field.player_back[0] = unit("A", {devourCards: [{card: unit("B").card}]});
  vm.runInContext(push, c);
  assert.equal(await c.xlwPushUnit("player_back", 0, "back", {offBoardAction: "hand"}), true);
  assert.deepEqual(c.hand.map(card => card.id), ["A", "B"]);
});
test("04 releases captured cards during push-to-hand cleanup", async () => {
  const c = fixture();
  const captive = unit("B");
  c.field.player_back[0] = unit("A", {kidnappedCards: [captive.card]});
  c.cleanUnitLeavingField = async captured => {
    assert.equal(c.field.player_back[0], null);
    c.window.XLW_ENEMY.hand.push(captured.kidnappedCards[0]);
  };
  vm.runInContext(push, c);
  await c.xlwPushUnit("player_back", 0, "back", {offBoardAction: "hand"});
  assert.deepEqual(c.window.XLW_ENEMY.hand, [captive.card]);
});
test("05 preserves the rival's card if their hand is temporarily unavailable", async () => {
  const c = fixture();
  c.field.enemy_back[0] = unit("A");
  delete c.window.XLW_ENEMY.hand;
  vm.runInContext(push, c);
  assert.equal(await c.xlwPushUnit("enemy_back", 0, "back", {offBoardAction: "hand"}), false);
  assert.equal(c.field.enemy_back[0].card.id, "A");
});

const martial = slice("window.xlwResolveSavageMartial =", "window.xlwResolveSavageAttack =");
function martialFixture(id, ownZone = "player_front") {
  const c = fixture();
  const card = {id, name: id};
  const attacker = unit("ATK", {attacking: true, savage: true}), defender = unit("DEF");
  c.field[ownZone][1] = attacker;
  c.field.enemy_front[1] = defender;
  c.hand.push(card);
  c.events = [];
  c.xlwPushUnit = async (...args) => { c.events.push(args); return true; };
  vm.runInContext(martial, c);
  return {c, card, attacker, defender, play: () => c.window.xlwResolveSavageMartial(id, true, attacker, ownZone, 1, "enemy_front", 1, defender)};
}
test("06 no-shadow kick pushes from the front lane and breaks to hand", async () => {
  const {c, play} = martialFixture("R-EWD-0069");
  assert.equal(await play(), true);
  assert.equal(c.events[0][2], "back");
  assert.equal(c.events[0][3].offBoardAction, "hand");
});
test("07 no-shadow kick cannot be used by a back-row attacker", async () => {
  const {c, card, play} = martialFixture("R-EWD-0069", "player_back");
  assert.equal(await play(), false);
  assert.deepEqual(c.hand, [card]);
});
test("08 left hook asks before spending the actual card", async () => {
  const {c, card, play} = martialFixture("R-EWD-0068");
  c.showXLWConfirm = async () => false;
  assert.equal(await play(), false);
  assert.deepEqual(c.hand, [card]);
  assert.deepEqual(c.events, []);
});
test("09 a resolved left hook disappears to the extra deck once", async () => {
  const {c, card, play} = martialFixture("R-EWD-0068");
  assert.equal(await play(), true);
  assert.equal(await play(), false);
  assert.deepEqual(c.playerExtraDeck, [card]);
  assert.equal(c.events[0][3].offBoardAction, "graveyard");
});
test("10 martial movement respects enemy magic resistance", async () => {
  const {c, defender, play} = martialFixture("R-EWD-0069");
  defender.magicImmune = true;
  assert.equal(await play(), false);
  assert.deepEqual(c.events, []);
});
test("11 a replaced target cannot receive an earlier martial selection", async () => {
  const {c, card, play} = martialFixture("R-EWD-0069");
  c.showXLWConfirm = async () => { c.field.enemy_front[1] = unit("OTHER"); return true; };
  assert.equal(await play(), false);
  assert.deepEqual(c.hand, [card]);
});

const poison = slice("window.xlwUnitHasPoison =", "\n};") + "\n};";
test("12 mushroom poison is granted to both adjacent savages only", () => {
  const c = fixture();
  const source = unit("ASSR-EWD-0060");
  c.field.player_front.splice(0, 5, unit("far", {savage: true}), unit("left", {savage: true}), source, unit("right", {savage: true}), unit("near"));
  vm.runInContext(poison, c);
  for (const index of [1, 3]) assert.equal(c.window.xlwUnitHasPoison(c.field.player_front[index], "player_front", index), true);
  assert.equal(c.window.xlwUnitHasPoison(c.field.player_front[0], "player_front", 0), false);
  c.field.player_front[1].savage = false;
  assert.equal(c.window.xlwUnitHasPoison(c.field.player_front[1], "player_front", 1), false);
});
test("13 a silenced mushroom source does not grant its aura", () => {
  const c = fixture();
  c.field.player_front[0] = unit("ASSR-EWD-0060", {silenced: true});
  c.field.player_front[1] = unit("A", {savage: true});
  vm.runInContext(poison, c);
  assert.equal(c.window.xlwUnitHasPoison(c.field.player_front[1], "player_front", 1), false);
});

const mask = slice("window.xlwCheckGoatMaskSpellCountered =", "// 17. SR-VRT-0077");
function maskFixture() {
  const c = fixture();
  c.field.player_front[0] = unit("SR-GOT-0060");
  vm.runInContext(mask, c);
  const spell = {id: "SR-GOT-0001", name: "山羊術"};
  return {c, spell, recover: () => c.window.xlwCheckGoatMaskSpellCountered(spell, true)};
}
test("14 goat mask cannot duplicate a countered card that never entered the grave", async () => {
  const {c, recover} = maskFixture();
  assert.equal(await recover(), false);
  assert.deepEqual(c.hand, []);
});
test("15 goat mask is optional and does not charge the limit when declined", async () => {
  const {c, spell, recover} = maskFixture();
  c.graveyard.push(spell);
  c.showXLWConfirm = async () => false;
  assert.equal(await recover(), false);
  assert.deepEqual(c.graveyard, [spell]);
  assert.equal(c.field.player_front[0].maskUsedTurn, undefined);
});
test("16 goat mask cannot recover twice in the same turn", async () => {
  const {c, spell, recover} = maskFixture();
  c.graveyard.push(spell);
  assert.equal(await recover(), true);
  c.graveyard.push({...spell});
  assert.equal(await c.window.xlwCheckGoatMaskSpellCountered(c.graveyard[0], true), false);
  assert.deepEqual(c.hand, [spell]);
});

const guest = slice("window.xlwCheckExpelledGuestBeforeDestroy =", "// 14. SR-CND-0069");
test("17 a canceled guest summon leaves the selected patron in hand", async () => {
  const c = fixture(), patron = {...unit("P").card, patron: true};
  vm.runInContext(guest, c);
  c.hand.push(patron);
  c.window.xlwSpecialSummonUnit = async (_, __, options) => { assert.equal(options.sourcePile()[0], patron); return false; };
  await c.window.xlwCheckExpelledGuestBeforeDestroy(unit("R-VRT-0071"), true);
  assert.deepEqual(c.hand, [patron]);
});
test("18 guest destruction invokes the search before the guest leaves", async () => {
  const destruction = slice("async function destroyUnit(", "await window.xlwResolveSavageAfterDestruction");
  assert.match(destruction, /await window\.xlwCheckExpelledGuestBeforeDestroy\?\.\(unit, owner === "player"\);[\s\S]*?await cleanUnitLeavingField\(unit, zone\);\s*field\[zone\]\[idx\] = null/);
});

const fan = slice("window.xlwCheckElectricFanPush =", "// 7. C-VLG-0063");
test("19 electric fan respects a canceled optional combine effect", async () => {
  const c = fixture();
  c.field.enemy_front[0] = unit("target");
  c.showXLWConfirm = async () => false;
  c.xlwPushUnit = async () => assert.fail("optional push was declined");
  vm.runInContext(fan, c);
  assert.equal(await c.window.xlwCheckElectricFanPush(unit("C-RBT-0074"), "player_front", 0, true), false);
});
test("20 mechanical fusion dispatches the electric fan effect", () => {
  const body = slice("window.xlwExecuteMechCombine =", "async function xlwSeparateSingleFusedUnit");
  assert.match(body, /C-RBT-0074[\s\S]{0,200}xlwCheckElectricFanPush/);
});
test("21 ghost samurai lets other units attack during the same tactical turn", () => {
  const c = fixture();
  vm.runInContext(slice("window.xlwCheckGhostSamuraiSacrifice =", "// 8. C-VRT-0073"), c);
  vm.runInContext(slice("function xlwIsFlyingGoat(", "function xlwCanDeclareAfterTactical"), c);
  c.window.xlwCheckGhostSamuraiSacrifice(unit("C-VLG-0063").card, true);
  assert.equal(c.xlwCanAttackAfterTactical(unit("plain"), "player_front", 0), true);
  c.turn++;
  assert.equal(c.xlwCanAttackAfterTactical(unit("plain"), "player_front", 0), false);
});
test("22 fusion rejects itself and stale hosts before moving any material", async () => {
  const c = fixture(), body = slice("window.xlwExecuteMechCombine =", "async function xlwSeparateSingleFusedUnit");
  const sourceUnit = unit("source"), replacedHost = unit("host");
  vm.runInContext(body, c);
  c.field.player_front[0] = sourceUnit;
  c.field.player_front[1] = unit("replacement");
  assert.equal(await c.window.xlwExecuteMechCombine(sourceUnit, sourceUnit, "player_front", 0, "player_front", 0), false);
  assert.equal(await c.window.xlwExecuteMechCombine(sourceUnit, replacedHost, "player_front", 0, "player_front", 1), false);
  assert.equal(c.field.player_front[0], sourceUnit);
});

test("23 left hook remains available when combat has already exhausted the surviving attacker", async () => {
  const {attacker, play} = martialFixture("R-EWD-0068");
  attacker.attacking = false;
  attacker.tapped = true;
  assert.equal(await play(), true);
});

test("24 stale destination cannot be overwritten by a delayed drunken boy selection", async () => {
  const c = fixture();
  const boy = unit("C-VRT-0073", {tapped: true}), blocker = unit("blocker");
  c.field.player_front[0] = boy;
  c.showXLWChoiceModal = async () => { c.field.player_front[1] = blocker; return 0; };
  vm.runInContext(slice("window.xlwCheckDrunkenBoyBeerMove =", "// 9. R-CAT-0066"), c);
  await c.window.xlwCheckDrunkenBoyBeerMove(true);
  assert.equal(c.field.player_front[0], boy);
  assert.equal(c.field.player_front[1], blocker);
  assert.equal(boy.tapped, true);
});

test("25 brewing dispatches the drunken effect by the revised card ID", async () => {
  const c = fixture();
  const calls = [];
  c.window.xlwCheckDrunkenBoyBeerMove = async side => calls.push(side);
  const header = slice("window.xlwOnMagicCardCast =", "// 1. 見習魔法師");
  vm.runInContext(header + "};", c);
  await c.window.xlwOnMagicCardCast(true, {id: "C-VRT-0065", name: "渣釀酒"});
  await c.window.xlwOnMagicCardCast(false, {id: "C-VRT-0065", name: "渣釀酒"});
  assert.deepEqual(calls, [true, false]);
});
