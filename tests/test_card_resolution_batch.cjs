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
  assert.match(destruction, /await window\.xlwCheckExpelledGuestBeforeDestroy\?\.\(unit, owner === "player"\);[\s\S]*?await cleanUnitLeavingField\(unit, zone\);\s*if \(field\[zone\]\[idx\] === unit\) field\[zone\]\[idx\] = null/);
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

test("kidnapping commits both locations before cleanup and cannot target itself", async () => {
  const c = fixture();
  const carrier = unit("carrier");
  const captive = unit("captive");
  c.field.player_front[0] = carrier;
  c.field.enemy_front[0] = captive;
  vm.runInContext(slice("async function kidnapCard(", "async function checkPopulationCap"), c);
  c.cleanUnitLeavingField = async () => {
    assert.equal(c.field.enemy_front[0], null);
    assert.equal(carrier.kidnappedCards[0].originalOwner, "enemy");
    c.field.enemy_front[0] = unit("replacement");
  };
  c.structuredClone = structuredClone;
  assert.equal(await c.kidnapCard("player_front", 0, "player_front", 0), false);
  assert.equal(await c.kidnapCard("enemy_front", 0, "player_front", 0), true);
  assert.equal(c.field.enemy_front[0].card.id, "replacement");
});

test("a silenced officer does not divert a captive to the grave", async () => {
  const c = fixture();
  const held = {...unit("held").card, originalOwner: "enemy"};
  const carrier = unit("carrier", {kidnappedCards: [held]});
  c.field.player_front[0] = unit("SSSR-NMS-0050", {silenced: true});
  vm.runInContext(slice("async function cleanUnitLeavingField(", "async function kidnapCard"), c);
  await c.cleanUnitLeavingField(carrier, "player_front");
  assert.equal(c.field.enemy_front[0].card, held);
  assert.equal(c.enemyGraveyard.length, 0);
  await c.cleanUnitLeavingField(carrier, "player_front");
  assert.equal(c.field.enemy_front[1], null);
});

test("Molan awards the captor but sends the captive to its owner's exile", async () => {
  const c = fixture();
  const held = {...unit("held").card, originalOwner: "enemy", tribute: 2};
  const carrier = unit("SSR-ART-0043", {kidnappedCards: [held]});
  c.playerBonusScore = 0;
  c.exileCard = (card, owner) => { assert.equal(owner, "enemy"); assert.equal(card, held); };
  vm.runInContext(slice("async function cleanUnitLeavingField(", "async function kidnapCard"), c);
  await c.cleanUnitLeavingField(carrier, "player_front");
  assert.equal(c.playerBonusScore, 2);
  assert.equal(carrier.kidnappedCards.length, 0);
});

const resolveChain = slice("function resolveLocalSpellChain()", "function renderExtraDecks()");
function chainFixture(deckTop, bombId = "R-NMS-0025") {
  const c = fixture();
  const spell = {id: "target", name: "測試魔法", type: "magic"};
  const bomb = {id: bombId, name: "魔法炸彈客", type: "unit"};
  c.deck = [];
  c.window.XLW_ENEMY.deck = deckTop ? [deckTop] : [];
  c.spellChainStack = [{card: spell, owner: "me"}, {card: bomb, owner: "opponent"}];
  c.hideSpellChainUI = () => {};
  c.exiled = {player: [], enemy: []};
  c.exileCard = (card, owner) => c.exiled[owner].push(card);
  c.window.XLW_pendingSpellResolve = result => { c.result = result; };
  vm.runInContext(resolveChain, c);
  return {c, spell, bomb};
}

test("bomber cannot negate without paying its deck top", () => {
  const {c, bomb} = chainFixture(null);
  c.resolveLocalSpellChain();
  assert.equal(c.result.countered, false);
  assert.deepEqual(c.window.XLW_ENEMY.hand, [bomb]);
  assert.deepEqual(c.exiled, {player: [], enemy: []});
});

test("bomber pays and exiles each physical card exactly once", () => {
  const top = {id: "top", name: "牌庫頂"};
  const {c, spell, bomb} = chainFixture(top, "SSR-NMG-0025-特殊");
  c.resolveLocalSpellChain();
  c.resolveLocalSpellChain();
  assert.equal(c.result.countered, true);
  assert.deepEqual(c.exiled.player, [spell]);
  assert.deepEqual(c.exiled.enemy, [top, bomb]);
  assert.equal(c.window.XLW_ENEMY.deck.length, 0);
});

test("a failed bomber cannot target a unit effect", () => {
  const top = {id: "top", name: "牌庫頂"};
  const {c, spell, bomb} = chainFixture(top);
  spell.type = "unit";
  c.resolveLocalSpellChain();
  assert.equal(c.result.countered, false);
  assert.deepEqual(c.window.XLW_ENEMY.deck, [top]);
  assert.deepEqual(c.window.XLW_ENEMY.hand, [bomb]);
});

test("virtual wheel and mushroom counters never become graveyard cards", () => {
  for (const id of ["VRT-0011-EFFECT", "SSR-CCS-0037-EFFECT"]) {
    const {c} = chainFixture(null);
    c.spellChainStack[1].card = {id, name: id, type: "magic"};
    c.resolveLocalSpellChain();
    assert.equal(c.result.countered, true);
    assert.equal(c.enemyGraveyard.length, 0);
  }
});

test("a middle counter negated by roar returns to its owner's hand", () => {
  const {c} = chainFixture(null);
  const counter = {id: "counter", name: "魔法反制", type: "magic", mana: 1};
  c.spellChainStack[1].card = counter;
  c.spellChainStack.push({card: {id: "R-ORC-0036", name: "怒吼", type: "magic"}, owner: "me"});
  c.resolveLocalSpellChain();
  assert.equal(c.result.countered, false);
  assert.deepEqual(c.window.XLW_ENEMY.hand, [counter]);
  assert.equal(c.window.XLW_enemyCannotUseCardIdThisTurn, counter.id);
});

function counterPromptFixture() {
  const c = fixture();
  const actions = {
    children: [],
    set innerHTML(_value) { this.children = []; },
    appendChild(item) { this.children.push(item); }
  };
  const status = {};
  const item = {card: {id: "spell", name: "測試魔法", type: "magic", mana: 1}, owner: "opponent"};
  c.deck = [];
  c.spellChainStack = [item];
  c.document = {getElementById: id => id === "xlw-chain-status" ? status : actions, createElement: () => ({})};
  c.getOrCreateSpellChainOverlay = () => null;
  c.clearTimeout = () => {};
  c.setTimeout = () => 1;
  c.requestAnimationFrame = callback => callback();
  c.showSpellChainUI = () => {};
  c.xlwShowSpellActivationOverlay = async () => {};
  c.hideSpellChainUI = () => {};
  vm.runInContext(slice("function promptNextChainAction()", "function resolveLocalSpellChain()"), c);
  const button = name => actions.children.find(entry => entry.textContent?.includes(name));
  return {c, item, button};
}

test("bomber is unavailable with no deck cost and offered once the deck has a real card", () => {
  const {c, button} = counterPromptFixture();
  c.hand.push({id: "SSR-NMG-0025-特殊", name: "魔法炸彈客", type: "unit"});
  c.promptNextChainAction();
  assert.equal(button("炸彈客"), undefined);
  c.deck.push({id: "top", name: "牌庫頂"});
  c.promptNextChainAction();
  assert.ok(button("炸彈客"));
});

test("a stale button cannot cast an already-removed counter or spend a different copy", async () => {
  const {c, button} = counterPromptFixture();
  c.hand.push({id: "NMG-0020", name: "魔法反制", _xlwInstanceId: "removed"});
  c.promptNextChainAction();
  const old = button("魔法反制");
  c.hand[0] = {...c.hand[0], _xlwInstanceId: "remaining"};
  await old.onclick();
  assert.equal(c.spellChainStack.length, 1);
  assert.equal(c.hand[0]._xlwInstanceId, "remaining");
});

test("a delayed bomber click cannot cast after its deck is depleted", async () => {
  const {c, button} = counterPromptFixture();
  c.hand.push({id: "R-NMS-0025", name: "魔法炸彈客"});
  c.deck.push({id: "top", name: "牌庫頂"});
  c.promptNextChainAction();
  const old = button("炸彈客");
  c.deck.pop();
  await old.onclick();
  assert.equal(c.spellChainStack.length, 1);
  assert.equal(c.hand.length, 1);
});

test("a tapped mushroom can counter and is destroyed after its owner chooses the effect", async () => {
  const {c, button} = counterPromptFixture();
  const mushroom = unit("VRT-0011", {tapped: true});
  c.field.player_front[1] = mushroom;
  c.promptNextChainAction();
  await button("魔法魔菇").onclick();
  assert.equal(c.field.player_front[1], null);
  assert.equal(c.spellChainStack.at(-1).card.type, "unit");
});

test("a stale mushroom button never destroys the unit that took its slot", async () => {
  const {c, button} = counterPromptFixture();
  c.field.player_front[1] = unit("VRT-0011");
  c.promptNextChainAction();
  const old = button("魔法魔菇");
  c.field.player_front[1] = unit("replacement");
  await old.onclick();
  assert.equal(c.field.player_front[1].card.id, "replacement");
  assert.equal(c.spellChainStack.length, 1);
});

test("wheel reaction is shown without any ordinary counters only during the rival's turn", () => {
  const {c, button} = counterPromptFixture();
  c.window.XLW_playerRouletteWheel = [1, 2, 3];
  c.field.player_back[0] = unit("SSR-CCS-0037");
  c.promptNextChainAction();
  assert.equal(button("輪轉反制"), undefined);
  c.isMyTurn = false;
  c.promptNextChainAction();
  assert.ok(button("輪轉反制"));
});

test("wheel reaction rechecks the minimum wheel size before spending the once-per-turn use", async () => {
  const {c, button} = counterPromptFixture();
  c.isMyTurn = false;
  c.window.XLW_playerRouletteWheel = [1, 2, 3];
  c.field.player_back[0] = unit("SSR-CCS-0037");
  c.window.xlwSpinWheel = async () => assert.fail("wheel is no longer large enough");
  c.promptNextChainAction();
  const old = button("輪轉反制");
  c.window.XLW_playerRouletteWheel.pop();
  await old.onclick();
  assert.equal(c.window.XLW_xiaoyuanUsedThisTurn, undefined);
});

test("wheel animation cannot add a counter to a chain already closed by the peer", async () => {
  const {c, button} = counterPromptFixture();
  c.isMyTurn = false;
  c.window.XLW_playerRouletteWheel = [1, 2, 3];
  c.field.player_back[0] = unit("SSR-CCS-0037");
  c.window.xlwSpinWheel = async () => { c.spellChainStack = []; };
  c.promptNextChainAction();
  await button("輪轉反制").onclick();
  assert.equal(c.spellChainStack.length, 0);
});

test("a silenced merchant cannot make black orb playable at reduced cost", () => {
  const {c, button} = counterPromptFixture();
  c.hand.push({id: "R-STP-0030", name: "黑球"});
  c.window.xlwGetSteamEnergy = () => 2;
  c.field.player_front[0] = unit("STP-0016", {silenced: true});
  c.promptNextChainAction();
  assert.equal(button("黑球"), undefined);
  c.field.player_front[0].silenced = false;
  c.promptNextChainAction();
  assert.ok(button("黑球"));
});

test("a magic-only counter cannot counter the mushroom's unit effect", () => {
  const {c} = chainFixture(null);
  c.spellChainStack[1].card = {id: "VRT-0011-EFFECT", name: "酒醉的魔法魔菇", type: "unit"};
  const handCounter = {id: "NMG-0020", name: "魔法反制", type: "magic"};
  c.spellChainStack.push({card: handCounter, owner: "me"});
  c.resolveLocalSpellChain();
  assert.equal(c.result.countered, true);
  assert.deepEqual(c.graveyard.slice(0, 1), [handCounter]);
});

test("virtual wheel effects do not remove hidden cards in collection fallback", () => {
  const c = fixture();
  const obscured = [null];
  assert.equal(c.window.XLWDuelConsistency.removeCard(obscured, {id: "SSR-CCS-0037-EFFECT", name: "輪轉反制"}), null);
  assert.deepEqual(obscured, [null]);
});

test("a delayed roar cannot negate a zero-mana spell", () => {
  const {c, spell} = chainFixture(null);
  spell.mana = 0;
  c.spellChainStack[1].card = {id: "R-ORC-0036", name: "怒吼", type: "magic"};
  c.resolveLocalSpellChain();
  assert.equal(c.result.countered, false);
  assert.deepEqual(c.hand, []);
  assert.equal(c.window.XLW_playerCannotUseCardIdThisTurn, undefined);
});

test("a delayed roar cannot return a unit effect to hand", () => {
  const {c, spell} = chainFixture(null);
  spell.type = "unit";
  spell.mana = 2;
  c.spellChainStack[1].card = {id: "R-ORC-0036", name: "怒吼", type: "magic"};
  c.resolveLocalSpellChain();
  assert.equal(c.result.countered, false);
  assert.deepEqual(c.hand, []);
});

test("Spell Analysis is offered only if its immediate target was cast in defense", () => {
  const {c, item, button} = counterPromptFixture();
  c.hand.push({id: "SSSR-NMG-0039", name: "法術解析", type: "magic"});
  for (const castInDefense of [undefined, false, true]) {
    item.casterDefensePhase = castInDefense;
    c.promptNextChainAction();
    assert.equal(Boolean(button("法術解析")), castInDefense === true);
  }
});

test("Spell Analysis adjudicates the preceding link, not the root spell's phase", () => {
  for (const defensePhase of [false, true]) {
    const {c} = chainFixture(null);
    const original = c.spellChainStack[0];
    original.casterDefensePhase = !defensePhase;
    const counter = {id: "NMG-0020", name: "魔法反制", type: "magic", mana: 1};
    c.spellChainStack[1].card = counter;
    c.spellChainStack[1].casterDefensePhase = defensePhase;
    c.spellChainStack.push({card: {id: "SSSR-NMG-0039", name: "法術解析", type: "magic"}, owner: "me"});
    c.resolveLocalSpellChain();
    assert.equal(c.result.countered, !defensePhase);
  }
});

test("Spell Analysis cannot negate a unit effect even with the defense timestamp", () => {
  const {c, spell} = chainFixture(null);
  spell.type = "unit";
  c.spellChainStack[0].casterDefensePhase = true;
  c.spellChainStack[1].card = {id: "SSSR-NMG-0039", name: "法術解析", type: "magic"};
  c.resolveLocalSpellChain();
  assert.equal(c.result.countered, false);
});

test("sleep counterpunch is never offered as a bomber counter", () => {
  const {c, button} = counterPromptFixture();
  c.hand.push({id: "R-NMG-0025", name: "睡眠反擊拳", type: "magic"});
  c.deck.push({id: "top", name: "牌庫頂"});
  c.promptNextChainAction();
  assert.equal(button("睡眠反擊拳"), undefined);
});

test("a special bomber variant applies costs even if the display name changes", () => {
  const top = {id: "top", name: "牌庫頂"};
  const {c, spell, bomb} = chainFixture(top, "SSR-NMG-0025-特殊");
  bomb.name = "本地化顯示名稱";
  c.resolveLocalSpellChain();
  assert.equal(c.result.countered, true);
  assert.deepEqual(c.exiled.player, [spell]);
  assert.deepEqual(c.exiled.enemy, [top, bomb]);
});

function aiDefenseFixture(cardId, cardName) {
  const c = fixture();
  const attacker = unit("attacker", {attacking: true, tapped: true, attack: 6, target: {zone: "enemy_front", idx: 0}});
  const defender = unit("defender", {attack: 4});
  const spell = {id: cardId, name: cardName, type: "magic"};
  c.window.XLW_ENEMY.hand.push(spell);
  c.window.XLW_isShieldUnit = () => false;
  c.getUnitAtk = u => u.attack;
  c.xlwShowSpellActivationOverlay = async () => {};
  c.sleep = async () => {};
  c.field.player_front[0] = attacker;
  c.field.enemy_front[0] = defender;
  vm.runInContext(slice("async function aiPlayMagicCardsDefensePhase(", "// 4. AI 戰術佈陣"), c);
  return {c, attacker, defender, run: () => c.aiPlayMagicCardsDefensePhase(0, defender, "enemy_front", 0, attacker, "player_front")};
}

test("AI sleep counterpunch adds one temporary bonus and no permanent attack modifier", async () => {
  const {c, defender, run} = aiDefenseFixture("R-NMG-0025", "睡眠反擊拳");
  await run();
  assert.deepEqual([...defender.equipments], ["睡眠反擊拳(+3)"]);
  assert.equal(defender.atkModifier, undefined);
  assert.equal(defender.tempEquips["睡眠反擊拳(+3)"], c.turn);
});

test("AI Fair Power cannot ready an attacker after the defender leaves", async () => {
  const {c, attacker, run} = aiDefenseFixture("BRV-0011", "公平之力");
  c.aiCastSpell = async (_, apply, defense) => {
    assert.equal(defense, true);
    c.field.enemy_front[0] = null;
    await apply();
  };
  await run();
  assert.equal(attacker.attacking, true);
  assert.equal(attacker.tapped, true);
});

test("AI protection and buff spells do not mutate a defender whose slot was replaced", async () => {
  for (const [id, name, property] of [
    ["BRV-0037", "護甲藥水", "hasArmorPotionBlocker"],
    ["BRV-0038", "增幅藥水", "tempAmpPotionBuff"],
    ["R-NMG-0025", "睡眠反擊拳", "tempEquips"]
  ]) {
    const {c, defender, run} = aiDefenseFixture(id, name);
    c.aiCastSpell = async (_, apply) => {
      c.field.enemy_front[0] = unit("replacement");
      await apply();
    };
    await run();
    assert.equal(defender[property], undefined, name);
    assert.equal(c.field.enemy_front[0][property], undefined, name);
  }
});

test("AI scapegoat leaves the imp in extra when the destination becomes full", async () => {
  const {c, attacker, run} = aiDefenseFixture("BRV-0032", "替罪小魔");
  const imp = {id: "BRV-0002", name: "金幣小魔"};
  c.enemyExtraDeck.push(imp);
  c.window.xlwGetEmptyEnemySlots = () => [{zone: "enemy_front", idx: 1}];
  c.aiCastSpell = async (_, apply) => {
    c.field.enemy_front[1] = unit("blocker");
    c.window.xlwGetEmptyEnemySlots = () => [];
    await apply();
  };
  await run();
  assert.deepEqual(c.enemyExtraDeck, [imp]);
  assert.equal(attacker.target.idx, 0);
  assert.equal(c.field.enemy_front[1].card.id, "blocker");
});

test("sleep counterpunch targets the defending unit, not another tapped ally", () => {
  const c = fixture();
  c.field.player_front[0] = unit("defender");
  c.field.player_front[1] = unit("other", {tapped: true});
  c.field.enemy_front[0] = unit("attacker", {attacking: true, target: {zone: "player_front", idx: 0}});
  vm.runInContext(slice("window.xlwCanTargetDefenseBuff =", "async function castSpell(handIndex)"), c);
  const spell = {name: "睡眠反擊拳"};
  assert.equal(c.window.xlwCanTargetDefenseBuff(spell, "player_front", 0), true);
  assert.equal(c.window.xlwCanTargetDefenseBuff(spell, "player_front", 1), false);
  assert.equal(c.window.xlwCanTargetDefenseBuff(spell, "enemy_front", 0), false);
});

test("immune units do not count as eligible enemy targets for a potion", () => {
  const c = fixture();
  c.isUnitEffectImmune = unit => Boolean(unit.immune);
  c.field.enemy_front[0] = unit("magic-immune", {magicImmune: true});
  c.field.enemy_front[1] = unit("effect-immune", {immune: true});
  c.field.player_front[0] = unit("friendly", {magicImmune: true});
  vm.runInContext(slice("window.xlwCanTargetDefenseBuff =", "async function castSpell(handIndex)"), c);
  const spell = {name: "削弱藥水"};
  assert.equal(c.window.xlwCanTargetDefenseBuff(spell, "enemy_front", 0), false);
  assert.equal(c.window.xlwCanTargetDefenseBuff(spell, "enemy_front", 1), false);
  assert.equal(c.window.xlwCanTargetDefenseBuff(spell, "player_front", 0), true);
});

test("AI weakening potion leaves the attacker alone if it gains magic resistance during the chain", async () => {
  const {c, attacker, run} = aiDefenseFixture("NMG-0003", "削弱藥水");
  c.aiCastSpell = async (_, apply) => { attacker.magicImmune = true; await apply(); };
  await run();
  assert.equal(attacker.equipments, undefined);
});

test("AI goat magic does not overwrite an attacker replaced during a chain", async () => {
  const {c, run} = aiDefenseFixture("SSR-NMG-0012", "山羊術");
  const replacement = unit("replacement");
  c.window.xlwIsGoatBlocked = () => false;
  c.aiCastSpell = async (_, apply) => { c.field.player_front[0] = replacement; await apply(); };
  await run();
  assert.equal(c.field.player_front[0], replacement);
  assert.equal(c.graveyard.length, 0);
});

test("AI attacking-power reward uses the resolved difference after a chain response", async () => {
  const {c, attacker, defender, run} = aiDefenseFixture("R-BRV-0049", "以小欺大");
  defender.card.art_subtype = "魔族";
  c.enemyBonusScore = 0;
  c.renderScore = () => {};
  c.aiCastSpell = async (_, apply) => { attacker.attack = 5; await apply(); };
  await run();
  assert.equal(c.enemyBonusScore, 1);
});

test("goat transformation disposes the original unit, fused pieces, and true equipment once", async () => {
  const c = fixture(), original = unit("old");
  const piece = unit("piece").card;
  const sword = {id: "R-ORC-0054", name: "破甲劍", type: "magic"};
  const coat = {id: "coat", name: "外衣", type: "magic"};
  Object.assign(original, {
    devourCards: [{card: piece}, null], equipments: [sword, coat, "削弱藥水"],
    xlwArmorBreakSwords: [sword], hasSpellShield: true, hasPoison: true,
    woodClubBonus: 4, tempEquips: {削弱藥水: c.turn},
    attacking: true, tapped: true, target: {zone: "enemy_front", idx: 0}
  });
  c.field.player_front[0] = original;
  c.structuredClone = structuredClone;
  c.window.xlwTriggerGoatPolymorphReactions = async () => {};
  vm.runInContext(slice("async function cleanUnitLeavingField(", "async function kidnapCard("), c);
  vm.runInContext(slice("window.xlwTransformUnitToGoat =", "// 觸發山羊變形被動"), c);
  const goat = {id: "GOT-0014", name: "盾牌山羊", _xlwInstanceId: "from-hand"};
  assert.equal(await c.window.xlwTransformUnitToGoat(original, "player_front", 0, goat, true), true);
  assert.deepEqual(c.graveyard.map(card => card.id).sort(), ["R-ORC-0054", "coat", "old", "piece"]);
  assert.equal(c.field.player_front[0], original);
  assert.equal(original.card._xlwInstanceId, "from-hand");
  assert.equal(original.tapped, true);
  assert.equal(original.attacking, true);
  assert.equal(original.target.idx, 0);
  for (const modifier of ["devourCards", "hasSpellShield", "hasPoison", "woodClubBonus", "tempEquips", "xlwArmorBreakSwords"]) {
    assert.equal(original[modifier], undefined, modifier);
  }
});

test("a stale target does not receive a goat transformation and an on-board goat is not cloned with its ID", async () => {
  const c = fixture(), original = unit("old"), source = unit("goat");
  source.card._xlwInstanceId = "board-goat";
  c.field.player_back[1] = source;
  c.structuredClone = structuredClone;
  c.window.xlwTriggerGoatPolymorphReactions = async () => {};
  vm.runInContext(slice("window.xlwTransformUnitToGoat =", "// 觸發山羊變形被動"), c);
  const transform = () => c.window.xlwTransformUnitToGoat(original, "player_front", 0, source.card, true);
  assert.equal(await transform(), false);
  assert.equal(c.graveyard.length, 0);
  c.field.player_front[0] = original;
  assert.equal(await transform(), true);
  assert.equal(source.card._xlwInstanceId, "board-goat");
  assert.equal(original.card._xlwInstanceId, undefined);
});

test("canceling the transformation target preserves the chosen tribute and hand card", async () => {
  const c = fixture(), tribute = unit("tribute");
  const spell = {id: "GOT-0014", name: "盾牌山羊"};
  c.field.player_front[0] = tribute;
  c.field.enemy_front[1] = unit("target");
  c.hand.push(spell);
  c.getCardTributeCost = () => 1;
  c.window.isUnitMagicImmune = () => false;
  c.window.xlwPlayerTributeUnit = async () => assert.fail("cost on canceled target");
  const choices = [0, null];
  c.showXLWChoiceModal = async (_, __, options) => {
    if (choices.length === 1) assert.equal(options.some(option => option.boardTarget.zone === "player_front"), false);
    return choices.shift();
  };
  vm.runInContext(slice("window.xlwInitiateGoatPolymorphFromHand =", "window.xlwFinishBlackHoleVictory"), c);
  await c.window.xlwInitiateGoatPolymorphFromHand(spell, 0);
  assert.deepEqual(c.hand, [spell]);
  assert.equal(c.field.player_front[0], tribute);
});

test("splitting rechecks the slot after an interactive choice and skips missing materials", async () => {
  const c = fixture(), host = unit("host", {isCombined: true, devourCards: [null, {card: unit("piece").card}]});
  c.field.player_front[0] = host;
  const newOccupant = unit("replacement");
  c.structuredClone = structuredClone;
  let prompts = 0;
  c.showXLWChoiceModal = async (_, __, choices) => {
    if (prompts++ === 0) {
      assert.equal(choices[0].boardTarget.idx, 0);
      c.field.player_front[0] = newOccupant;
    }
    return 0;
  };
  vm.runInContext(slice("async function xlwSeparateSingleFusedUnit(", "// 單位真實攻擊力"), c);
  assert.equal(await c.xlwSeparateSingleFusedUnit("player_front", 0), 2);
  assert.equal(host.isCombined, false);
  assert.equal(c.field.player_front[0], newOccupant);
  assert.deepEqual(c.field.player_front.slice(1, 3).map(u => u.card.id), ["host", "piece"]);
});

test("armor sword does not attach to a unit transformed while the choice is open", async () => {
  const c = fixture();
  const host = unit("ORC-0010");
  c.field.player_front[0] = host;
  c.showXLWChoiceModal = async () => { host.card = unit("GOT-0014").card; return 0; };
  const sword = {id: "R-ORC-0054", name: "破甲劍"};
  vm.runInContext(slice("function xlwArmorSwordTargets()", "async function xlwResolveSoftClocks()"), c);
  await c.xlwEquipArmorSword(sword);
  assert.equal(host.xlwArmorBreakSwords, undefined);
  assert.deepEqual(c.graveyard, [sword]);
});

test("legacy peer transformation settles ownership without repeating active goat reactions", async () => {
  const c = fixture();
  const target = unit("former");
  c.field.enemy_front[0] = target;
  c.structuredClone = structuredClone;
  c.window.xlwTriggerGoatPolymorphReactions = async () => assert.fail("peer reaction already settled");
  const goat = {id: "SSR-NMG-0012", name: "山羊術", _xlwInstanceId: "spell"};
  vm.runInContext(slice("window.xlwTransformUnitToGoat =", "// 觸發山羊變形被動"), c);
  await c.window.xlwTransformUnitToGoat(target, "enemy_front", 0, goat, false, false, {replay: true});
  assert.equal(c.graveyard.length, 0);
  assert.equal(c.window.XLW_ENEMY.grave[0].id, "former");
  assert.equal(target.card.creator, "enemy");
});

test("AI successful transformations and disappearing potions do not duplicate the spell in grave", async () => {
  const c = fixture();
  c.window.xlwStarLineTrophies = [];
  c.window.xlwOnMagicCardCast = async () => {};
  c.window.xlwCardHasKeyword = (_, kw) => kw === "消逝";
  c.enemyExileZone = [];
  c.showSpellChainUI = () => {};
  c.promptNextChainAction = () => queueMicrotask(() => c.window.XLW_pendingSpellResolve({countered: false}));
  c.setTimeout = () => 1;
  vm.runInContext(slice("async function aiCastSpell(", "async function aiPlayMagicCardsSummonPhase"), c);
  const goat = {id: "SSR-NMG-0012", name: "山羊術"};
  await c.aiCastSpell(goat, async () => "transformed", true);
  for (const id of ["BRV-0037", "BRV-0038"]) {
    const potion = {id, name: id};
    await c.aiCastSpell(potion, async () => {}, true);
  }
  assert.deepEqual(c.window.XLW_ENEMY.grave, []);
  assert.deepEqual(c.enemyExtraDeck.map(card => card.id), ["BRV-0037", "BRV-0038"]);
});

test("root fairy counts only unsilenced adjacent friendly sources", () => {
  const c = fixture(), ally = unit("fairy", {savage: false});
  c.window.xlwIsUnitFairy = candidate => candidate === ally;
  c.field.player_front[2] = ally;
  c.field.player_front[1] = unit("C-EVL-0058");
  c.field.player_front[3] = unit("C-EVL-0058", {silenced: true});
  c.field.player_back[2] = unit("C-EVL-0058");
  c.field.enemy_front[2] = unit("C-EVL-0058");
  vm.runInContext(slice("window.xlwCountAdjacentRootFairies =", "function getUnitAtk("), c);
  assert.equal(c.window.xlwCountAdjacentRootFairies(ally, "player_front", 2), 2);
  assert.equal(c.window.xlwCountAdjacentRootFairies(unit("nonfairy"), "player_front", 2), 0);
});

test("fairy lawyer pays its tap only after transfer and may recover again next turn", async () => {
  const c = fixture(), lawyer = unit("C-EVL-0061");
  c.field.player_front[0] = lawyer;
  c.graveyard.push({id: "first", type: "magic"}, {id: "second", type: "magic"});
  c.xlwOnPlayerUnitTapped = async () => {};
  vm.runInContext(slice("window.xlwResolveFairyLawyer =", "window.xlwResolveExpansionTurnStart ="), c);
  c.showXLWChoiceModal = async () => -1;
  await c.window.xlwResolveFairyLawyer(true);
  assert.equal(lawyer.tapped, undefined);
  c.showXLWChoiceModal = async () => 0;
  await c.window.xlwResolveFairyLawyer(true);
  assert.equal(lawyer.tapped, true);
  lawyer.tapped = false;
  await c.window.xlwResolveFairyLawyer(true);
  assert.equal(c.hand.length, 1);
  c.turn++;
  await c.window.xlwResolveFairyLawyer(true);
  assert.equal(c.hand.length, 2);
});

test("soul crystal is preserved on cancel and spends itself only at a valid revival placement", async () => {
  const c = fixture(), crystal = unit("C-EVL-0063"), fairy = unit("fairy").card;
  c.window.xlwIsUnitFairy = card => card === fairy;
  c.field.player_front[0] = crystal;
  c.graveyard = [fairy];
  vm.runInContext(slice("window.xlwResolveFairySoulCrystal =", "window.xlwResolveExpansionPostDestruction ="), c);
  c.window.xlwSpecialSummonUnit = async () => false;
  await c.window.xlwResolveFairySoulCrystal(fairy, true);
  assert.equal(c.field.player_front[0], crystal);
  assert.deepEqual(c.graveyard, [fairy]);
  c.window.xlwSpecialSummonUnit = async (selected, _, opts) => {
    assert.equal(selected, fairy);
    assert.equal(await opts.beforePlacement(), true);
    return Boolean(c.window.XLWDuelConsistency.takeKnownCard(opts.sourcePile(), selected));
  };
  assert.equal(await c.window.xlwResolveFairySoulCrystal(fairy, true), true);
  assert.equal(c.field.player_front[0], null);
  assert.deepEqual(c.graveyard, [crystal.card]);
});

test("Luna does not spend its once-per-turn reaction on cancellation or a stale destination", async () => {
  const c = fixture(), luna = unit("ASSR-EVL-0065", {tapped: true, attacking: true});
  c.field.player_front[0] = luna;
  vm.runInContext(slice("window.xlwCheckLunaDefenseReaction =", "// 2. C-CCS-0044"), c);
  c.showXLWChoiceModal = async () => { c.field.player_front[1] = unit("blocker"); return 0; };
  await c.window.xlwCheckLunaDefenseReaction();
  assert.equal(luna.lunaUsedTurn, undefined);
  assert.equal(c.field.player_front[0], luna);
  c.showXLWChoiceModal = async () => 0;
  await c.window.xlwCheckLunaDefenseReaction();
  assert.equal(c.field.player_front[2], luna);
  assert.equal(luna.lunaUsedTurn, c.turn);
  assert.equal(luna.tapped, false);
  assert.equal(luna.attacking, false);
});

test("weapon master must still be active for the actual Crystal Arrow to move from extra", async () => {
  const c = fixture(), master = unit("R-EVL-0032"), winner = unit("fairy");
  const arrow = {id: "EVL-0055", name: "水晶箭矢"};
  c.window.xlwIsUnitFairy = candidate => candidate === winner;
  c.field.player_front[1] = master;
  c.playerExtraDeck.push(arrow);
  vm.runInContext(slice("window.xlwRetrieveCrystalArrow =", "window.xlwResolvePG2CombatSuccess ="), c);
  c.showXLWConfirm = async () => { master.silenced = true; return true; };
  assert.equal(await c.window.xlwRetrieveCrystalArrow(winner, true), false);
  assert.deepEqual(c.playerExtraDeck, [arrow]);
  master.silenced = false;
  c.showXLWConfirm = async () => true;
  assert.equal(await c.window.xlwRetrieveCrystalArrow(winner, true), true);
  assert.deepEqual(c.hand, [arrow]);
  assert.equal(c.playerExtraDeck.length, 0);
});

test("Crystal Arrow target choices exclude tributes and all applicable protections", () => {
  const c = fixture();
  c.getCardTributeCost = card => card.tribute || 0;
  c.isUnitIndestructible = candidate => Boolean(candidate.indestructible);
  c.window.isUnitMagicImmune = candidate => Boolean(candidate.magicImmune);
  const paid = unit("paid");
  paid.card.tribute = 1;
  c.field.enemy_front.splice(0, 5, paid, unit("magic", {magicImmune: true}), unit("effect", {immune: true}),
    unit("indestructible", {indestructible: true}), unit("legal"));
  vm.runInContext(slice("window.xlwCrystalArrowTargets =", "async function castSpell(handIndex)"), c);
  assert.deepEqual(Array.from(c.window.xlwCrystalArrowTargets({id: "EVL-0055"}), entry => entry.idx), [4]);
});

test("fairy crossbow cannot attack on entry and only reaches other lanes with a unit directly behind it", () => {
  const c = fixture();
  const crossbow = unit("EVL-0056", {summonedTurn: c.turn});
  c.field.player_front[0] = crossbow;
  c.field.enemy_back[4] = unit("opponent");
  c.window.XLW_isShieldUnit = candidate => Boolean(candidate.shield);
  c.isUnitAttackProtected = () => false;
  c.xlwFairHeroBlocksAttack = () => false;
  c.hasArmorBreak = () => false;
  c.window.hasFlying = () => false;
  vm.runInContext(slice("function xlwAttackTargetBlock(", "async function xlwTogglePlayerAttack("), c);
  vm.runInContext(slice("window.xlwFairyCrossbowCanAttack =", "function validPlayerAttackLine("), c);
  assert.equal(c.window.xlwFairyCrossbowCanAttack(crossbow), false);
  c.turn++;
  assert.equal(c.window.xlwFairyCrossbowCanAttack(crossbow), true);
  assert.equal(c.window.xlwFairyCrossbowTargets(crossbow, "player_front", 0).length, 0);
  c.field.player_back[0] = unit("support");
  assert.equal(c.window.xlwFairyCrossbowTargets(crossbow, "player_front", 0)[0].idx, 4);
  crossbow.silenced = true;
  assert.equal(c.window.xlwFairyCrossbowTargets(crossbow, "player_front", 0).length, 0);
});

test("AI Kasaren takes only fairy tributes", () => {
  const c = fixture();
  const hero = {id: "EVL-0057", type: "unit", name: "妖精英雄凱薩倫", attack: 7, tribute: 1};
  c.window.XLW_ENEMY.hand.push(hero);
  c.enemyExileZone = [];
  c.xlwIsUnitUnsacrificable = () => false;
  c.xlwBlueStarRequirement = () => "";
  c.getCardTributeCost = card => card.tribute;
  c.field.enemy_front[0] = unit("non-fairy");
  vm.runInContext(slice("window.aiFindBestSummonableCard =", "async function runEnemyTurn"), c);
  assert.equal(c.window.aiFindBestSummonableCard(), null);
  c.field.enemy_back[0] = unit("fairy", {fairy: true});
  c.window.xlwIsUnitFairy = candidate => Boolean(candidate?.fairy);
  const result = c.window.aiFindBestSummonableCard();
  assert.equal(result.card, hero);
  assert.equal(result.tributeUnits[0].unit.card.id, "fairy");
});

test("fairy reduction count uses base stats without calling the queen award recursively", () => {
  const c = fixture();
  c.field.player_front[0] = unit("SR-EVL-0064");
  c.field.player_front[1] = unit("reduced");
  c.field.player_front[1].card.score = 5;
  c.getUnitStars = (unit, _, __, skipAwards, record) => {
    assert.equal(skipAwards, true);
    if (unit.card.id === "reduced") record(3, "player");
    return 0;
  };
  vm.runInContext(slice("window.xlwReadStarReductions = function", "const TROPHY_ATTACK"), c);
  assert.equal(c.window.xlwGetTotalStarsReducedByEffects(true), 3);
});

test("soul refiner does not discard the first choice if the second selection is canceled", async () => {
  const c = fixture(), offered = unit("offered").card, old = unit("old").card;
  c.deck = [{id: "existing"}];
  c.hand = [offered];
  c.graveyard = [old];
  c.window.xlwIsUnitFairy = () => true;
  vm.runInContext(slice("window.xlwResolveFairySoulRefiner =", "window.xlwResolvePG2Summon ="), c);
  const picks = [0, null];
  c.showXLWChoiceModal = async () => picks.shift();
  assert.equal(await c.window.xlwResolveFairySoulRefiner(true), false);
  assert.deepEqual(c.hand, [offered]);
  assert.deepEqual(c.graveyard, [old]);
  c.showXLWChoiceModal = async () => 0;
  assert.equal(await c.window.xlwResolveFairySoulRefiner(true), true);
  assert.deepEqual(c.graveyard, [offered]);
  assert.equal(c.deck.at(-1), old);
  assert.equal(c.hand.length, 0);
});

test("Balloon Fairy gives the AI its actual top card once, while a silenced copy gives no draw", async () => {
  const c = fixture();
  const source = unit("R-EVL-0043", {fairy: true});
  const top = {id: "top"};
  c.window.XLW_ENEMY.deck = [{id: "next"}, top];
  c.field.enemy_front[0] = source;
  c.field.enemy_front[1] = unit("R-EVL-0043", {silenced: true, fairy: true});
  c.field.enemy_front[2] = unit("high", {fairy: true, stars: 4});
  c.window.xlwIsUnitFairy = target => Boolean(target?.fairy);
  c.getUnitStars = target => target.stars || 0;
  vm.runInContext(slice("window.xlwResolveBalloonFairy =", "window.xlwResolveExpansionTurnStart ="), c);
  await c.window.xlwResolveBalloonFairy(false);
  await c.window.xlwResolveBalloonFairy(false);
  assert.deepEqual(c.window.XLW_ENEMY.hand, [top]);
  assert.equal(c.window.XLW_ENEMY.deck.length, 1);
});

test("Morlana counts reductions caused by her side across both fields without netting other bonuses", () => {
  const c = fixture(), friendly = unit("friendly"), opposing = unit("opposing");
  c.field.player_front[0] = friendly;
  c.field.enemy_front[0] = opposing;
  c.getUnitStars = (target, _, __, skipAward, record) => {
    assert.equal(skipAward, true);
    if (target === friendly) { record(2, "enemy"); record(1, null); }
    if (target === opposing) { record(4, "player"); record(1, "enemy"); }
    return 20;
  };
  vm.runInContext(slice("window.xlwReadStarReductions = function", "const TROPHY_ATTACK"), c);
  assert.equal(c.window.xlwGetTotalStarsReducedByEffects(true, true), 4);
  assert.equal(c.window.xlwGetTotalStarsReducedByEffects(false, true), 3);
  assert.equal(c.window.xlwGetTotalStarsReducedByEffects(true), 3);
});

test("Fairy Forest's reductions are bound to the current field, side, unit type and main phase", () => {
  const c = fixture(), fairy = unit("fairy");
  c.window.xlwIsUnitFairy = candidate => candidate === fairy;
  c.window.xlwGetFactionFieldCard = own => own ? {id: "C-EVL-0067"} : null;
  c.getUnitStars = (_, __, ___, ____, reduce) => { reduce(2, "player"); reduce(3, "enemy"); return 8; };
  vm.runInContext(slice("window.xlwReadStarReductions = function", "const TROPHY_ATTACK"), c);
  assert.equal(c.window.xlwFairyForestLevel(fairy, "player_front", 0), 5);
  assert.equal(c.window.xlwFairyForestLevel(fairy, "enemy_front", 0), 0);
  assert.equal(c.window.xlwFairyForestLevel(unit("other"), "player_front", 0), 0);
  c.phase = "防守階段";
  assert.equal(c.window.xlwFairyForestLevel(fairy, "player_front", 0), 0);
});

function springFairyFixture() {
  const c = fixture(), old = unit("R-EVL-0052");
  const target = {id: "revived", name: "回收單位", type: "unit"};
  c.field.player_front[0] = old;
  c.deck = [];
  c.graveyard = [{id: "magic", type: "magic"}, target];
  c.mulliganActive = false;
  c.setStatus = () => {};
  c.draw = count => { for (let i = 0; i < count; i++) c.hand.push(c.deck.pop()); };
  vm.runInContext(slice("window.xlwSpringFairyRefill =", "// 智慧的般若"), c);
  return {c, old, target};
}

test("Spring Fairy cannot refill during normal draws or while silenced", async () => {
  const {c, old} = springFairyFixture();
  c.phase = "抽牌階段";
  assert.equal(await c.window.xlwDrawFairyAware(1), 0);
  c.phase = "召喚階段";
  old.silenced = true;
  assert.equal(await c.window.xlwDrawFairyAware(1), 0);
  assert.equal(c.graveyard.length, 2);
});

test("Spring Fairy offers only unit cards and cancellation preserves the once-per-turn use", async () => {
  const {c, old, target} = springFairyFixture();
  c.showXLWChoiceModal = async (_, __, choices) => {
    assert.equal(choices[0].card, target);
    assert.equal(choices.length, 2);
    return -1;
  };
  assert.equal(await c.window.xlwDrawFairyAware(1), 0);
  assert.equal(old.springFairyTurn, undefined);
  assert.equal(c.graveyard.length, 2);
  c.showXLWChoiceModal = async () => 0;
  assert.equal(await c.window.xlwDrawFairyAware(2), 1);
  assert.equal(old.springFairyTurn, c.turn);
  assert.deepEqual(c.hand, [target]);
});

test("Spring Fairy cannot remove a stale graveyard card or replace a freshly refilled deck top", async () => {
  const {c, target, old} = springFairyFixture();
  const lateTop = {id: "late", name: "剛放入牌庫頂"};
  c.showXLWChoiceModal = async () => { c.deck.push(lateTop); return 0; };
  assert.equal(await c.window.xlwDrawFairyAware(1), 1);
  assert.deepEqual(c.hand, [lateTop]);
  assert.ok(c.graveyard.includes(target));
  assert.equal(old.springFairyTurn, undefined);
  c.showXLWChoiceModal = async () => { c.graveyard.splice(1, 1); return 0; };
  assert.equal(await c.window.xlwDrawFairyAware(1), 0);
  assert.equal(c.graveyard[0].id, "magic");
});

test("dark fairy target selection keeps its original target and checks resistance after selection", async () => {
  const c = fixture(), target = unit("target", {attack: -2});
  c.field.enemy_back[2] = target;
  vm.runInContext(slice("window.xlwPickDarkFairyTarget =", "window.xlwResolvePG2Summon ="), c);
  const pick = () => c.window.xlwPickDarkFairyTarget("夜行黑妖精", true, candidate => candidate.attack <= -2, "目標");
  c.showXLWChoiceModal = async (_, __, options) => {
    assert.equal(options[0].boardTarget.idx, 2);
    target.immune = true;
    return 0;
  };
  assert.equal(await pick(), null);
  target.immune = false;
  c.showXLWChoiceModal = async () => { c.field.enemy_back[2] = unit("replacement"); return 0; };
  assert.equal(await pick(), null);
  c.field.enemy_back[2] = target;
  c.showXLWChoiceModal = async () => 0;
  assert.equal((await pick()).unit, target);
});

test("warden cancellation preserves the turn limit and a successful choice stores a two-turn capture", async () => {
  const c = fixture(), warden = unit("R-EVL-0036"), captive = unit("target", {attack: -1});
  c.field.player_front[0] = warden;
  c.field.enemy_back[0] = captive;
  c.structuredClone = structuredClone;
  c.xlwEwdInMainPhase = () => true;
  c.getUnitAtk = target => target.attack;
  vm.runInContext(slice("window.xlwPickDarkFairyTarget =", "window.xlwResolvePG2Summon ="), c);
  vm.runInContext(slice("async function kidnapCard(", "async function checkPopulationCap"), c);
  vm.runInContext(slice("window.xlwActivateFairyWarden =", "async function xlwResolveExpansionUnitClick"), c);
  c.showXLWChoiceModal = async () => null;
  assert.equal(await c.window.xlwActivateFairyWarden(warden, "player_front", 0), false);
  assert.equal(warden.fairyWardenTurn, undefined);
  c.showXLWChoiceModal = async () => 0;
  assert.equal(await c.window.xlwActivateFairyWarden(warden, "player_front", 0), true);
  assert.equal(warden.kidnappedCards[0].fairyReleaseTurn, c.turn + 2);
  assert.equal(warden.kidnappedCards[0].originalOwner, "enemy");
  assert.equal(await c.window.xlwActivateFairyWarden(warden, "player_front", 0), false);
});

test("timed fairy captives return to their owner without diverting to the officer's grave", async () => {
  const c = fixture();
  const timed = {id: "timed", originalOwner: "enemy", fairyReleaseTurn: c.turn + 2};
  const permanent = {id: "permanent", originalOwner: "enemy"};
  const captor = unit("R-EVL-0036", {kidnappedCards: [timed, permanent]});
  c.field.player_front[0] = captor;
  c.field.player_front[1] = unit("SSSR-NMS-0050");
  vm.runInContext(slice("async function cleanUnitLeavingField(", "async function kidnapCard"), c);
  vm.runInContext(slice("window.xlwReleaseTimedFairyCaptives =", "window.xlwResolveExpansionTurnStart ="), c);
  await c.window.xlwReleaseTimedFairyCaptives(true);
  assert.equal(c.field.enemy_front[0], null);
  c.turn += 2;
  await c.window.xlwReleaseTimedFairyCaptives(false);
  assert.equal(c.field.enemy_front[0], null);
  await c.window.xlwReleaseTimedFairyCaptives(true);
  assert.equal(c.field.enemy_front[0].card, timed);
  assert.equal(timed.fairyReleaseTurn, undefined);
  assert.deepEqual([...captor.kidnappedCards], [permanent]);
  assert.deepEqual(c.enemyGraveyard, []);
});

test("Black Castle Prison counts its side's captive cards for fairies and kidnapping units only", () => {
  const c = fixture(), ownFairy = unit("fairy"), captor = unit("captor", {kidnappedCards: [{id: "A"}, null, {id: "B"}]});
  c.field.player_front.splice(0, 2, ownFairy, captor);
  c.field.enemy_front[0] = unit("enemy", {kidnappedCards: [{id: "C"}]});
  c.window.xlwGetFactionFieldCard = own => own ? {id: "R-EVL-0040"} : null;
  c.window.xlwIsUnitFairy = candidate => candidate === ownFairy;
  vm.runInContext(slice("window.xlwFairyPrisonLevel =", "const TROPHY_ATTACK"), c);
  assert.equal(c.window.xlwFairyPrisonLevel(ownFairy, "player_front"), 2);
  assert.equal(c.window.xlwFairyPrisonLevel(captor, "player_front"), 2);
  assert.equal(c.window.xlwFairyPrisonLevel(unit("unrelated"), "player_front"), 0);
  captor.kidnappedCards.pop();
  assert.equal(c.window.xlwFairyPrisonLevel(ownFairy, "player_front"), 1);
});

test("alchemy spends one eligible fairy only after a valid target and only once per turn", async () => {
  const c = fixture(), alchemist = unit("R-EVL-0038"), enemy = unit("target");
  const material = {id: "material", name: "妖精", type: "unit", score: 3};
  c.field.player_front[0] = alchemist;
  c.hand.push(material, {...material, score: 4});
  c.window.xlwIsUnitFairy = () => true;
  c.xlwEwdInMainPhase = () => true;
  c.showXLWChoiceModal = async (_, __, choices) => {
    assert.equal(choices.length, 2);
    return 0;
  };
  c.window.XLWDuelConsistency = {moveKnownCard(from, to, card) {
    to.push(...from.splice(from.indexOf(card), 1));
    return true;
  }};
  vm.runInContext(slice("window.xlwPickDarkFairyTarget =", "window.xlwResolvePG2Summon ="), c);
  vm.runInContext(slice("window.xlwActivateDarkFairyAlchemist =", "window.xlwActivateFairyWarden ="), c);
  const activate = () => c.window.xlwActivateDarkFairyAlchemist(alchemist, "player_front", 0);
  c.window.xlwPickDarkFairyTarget = async () => null;
  assert.equal(await activate(), false);
  assert.equal(c.hand[0], material);
  assert.deepEqual(c.graveyard, []);
  c.window.xlwPickDarkFairyTarget = async () => ({unit: enemy});
  assert.equal(await activate(), true);
  assert.deepEqual(c.graveyard, [material]);
  assert.equal(enemy.darkFairyAttackPenalties[0].amount, 2);
  assert.equal(enemy.darkFairyAttackPenalties[0].expiresTurn, c.turn + 1);
  assert.equal(await activate(), false);
});

test("Black Castle Recycler captures only a live Fairy grave unit and keeps its copied aura until leaving the field", async () => {
  const c = fixture(), robot = unit("SR-EVL-0041");
  const fairy = {id: "R-EVL-0025", type: "unit", name: "妖精", fairy: true};
  const other = {id: "other", type: "unit"};
  c.field.player_front[0] = robot;
  c.graveyard.push(other, fairy);
  c.window.xlwIsUnitFairy = card => Boolean(card.fairy);
  vm.runInContext(slice("window.xlwActivateFairyRecycler =", "window.xlwResolvePG2Summon ="), c);
  vm.runInContext(slice("window.xlwFairyEffectCard =", "window.xlwReadStarReductions ="), c);
  const activate = () => c.window.xlwActivateFairyRecycler(robot, "player_front", 0, true);
  c.showXLWChoiceModal = async (_, __, options) => {
    assert.equal(options.length, 2);
    assert.equal(options[0].card, fairy);
    return -1;
  };
  assert.equal(await activate(), false);
  assert.deepEqual(c.graveyard, [other, fairy]);
  c.showXLWChoiceModal = async () => 0;
  assert.equal(await activate(), true);
  assert.deepEqual(c.graveyard, [other]);
  assert.equal(robot.kidnappedCards[0], fairy);
  assert.equal(c.window.xlwActiveFairySources("player_", "EVL-0025")[0], robot);
  robot.silenced = true;
  assert.equal(c.window.xlwActiveFairySources("player_", "EVL-0025").length, 0);
  robot.silenced = false;
  robot.kidnappedCards.pop();
  assert.equal(c.window.xlwActiveFairySources("player_", "EVL-0025").length, 1);
  c.field.player_front[0] = null;
  assert.equal(c.window.xlwActiveFairySources("player_", "EVL-0025").length, 0);
  assert.equal(robot.card.id, "SR-EVL-0041");
});

test("Black Castle Recycler returns its captives to each owner's grave without ownership metadata", async () => {
  const c = fixture(), own = {id: "own", originalOwner: "player"};
  const enemy = {id: "enemy", originalOwner: "enemy"};
  const robot = unit("SR-EVL-0041", {kidnappedCards: [own, enemy]});
  vm.runInContext(slice("async function cleanUnitLeavingField(", "async function kidnapCard"), c);
  await c.cleanUnitLeavingField(robot, "player_front");
  assert.deepEqual(c.graveyard, [{id: "own"}]);
  assert.deepEqual(c.enemyGraveyard, [{id: "enemy"}]);
  assert.equal(robot.kidnappedCards.length, 0);
  assert.equal(c.field.player_front[0], null);
  assert.equal(c.field.enemy_front[0], null);
});

test("timed release keeps the captor's equipped armor break sword", async () => {
  const c = fixture(), sword = {id: "sword"};
  const captor = unit("R-EVL-0036", {xlwArmorBreakSwords: [sword], equipments: ["破甲劍"], kidnappedCards: [{id: "enemy", originalOwner: "enemy"}]});
  vm.runInContext(slice("async function cleanUnitLeavingField(", "async function kidnapCard"), c);
  await c.cleanUnitLeavingField(captor, "player_front", {releaseOnly: true});
  assert.deepEqual(captor.xlwArmorBreakSwords, [sword]);
  assert.deepEqual(c.graveyard, []);
  assert.equal(c.field.enemy_front[0].card.id, "enemy");
});

test("Freya can decline a local defense and cannot push a stale or resistant summon", async () => {
  const c = fixture(), freya = unit("R-EVL-0047"), target = unit("target");
  c.field.player_back[0] = freya;
  c.field.enemy_front[0] = target;
  vm.runInContext(slice("window.xlwFairyEffectCard =", "window.xlwReadStarReductions ="), c);
  vm.runInContext(slice("window.xlwResolveFairyFreyaPush =", "window.xlwResolvePG2Summon ="), c);
  vm.runInContext(push, c);
  const react = () => c.window.xlwResolveFairyFreyaPush("enemy_front", 0, false);
  c.showXLWConfirm = async () => false;
  assert.equal(await react(), false);
  assert.equal(c.field.enemy_front[0], target);
  c.showXLWConfirm = async () => { target.immune = true; return true; };
  assert.equal(await react(), false);
  target.immune = false;
  c.showXLWConfirm = async () => { c.field.enemy_front[0] = unit("replacement"); return true; };
  assert.equal(await react(), false);
  c.field.enemy_front[0] = target;
  c.showXLWConfirm = async () => true;
  assert.equal(await react(), true);
  assert.equal(c.field.enemy_back[0], target);
});

test("Dark Fairy Executioner exiles the exact captive to its original owner only after a valid selection", async () => {
  const c = fixture(), captive = {id: "duplicate", originalOwner: "enemy", fairyReleaseTurn: 6};
  const other = {id: "duplicate", originalOwner: "player"};
  const captor = unit("captor", {kidnappedCards: [other, captive]});
  const opposingCaptor = unit("opposing", {kidnappedCards: [{id: "opposing-captive"}]});
  const exiled = [];
  c.field.player_front[0] = captor;
  c.field.enemy_front[0] = opposingCaptor;
  c.exileCard = (card, owner) => exiled.push({card, owner});
  vm.runInContext(slice("window.xlwResolveFairyExecutioner =", "window.xlwResolveFairyFreyaPush ="), c);
  const activate = () => c.window.xlwResolveFairyExecutioner(true);
  c.showXLWChoiceModal = async (_, __, choices) => {
    assert.equal(choices.length, 3);
    assert.equal(choices[1].card, captive);
    return -1;
  };
  assert.equal(await activate(), false);
  c.showXLWChoiceModal = async () => { c.field.player_front[0] = null; return 1; };
  assert.equal(await activate(), false);
  c.field.player_front[0] = captor;
  c.showXLWChoiceModal = async () => 1;
  assert.equal(await activate(), true);
  assert.equal(exiled[0].card, captive);
  assert.equal(exiled[0].owner, "enemy");
  assert.deepEqual(captive, {id: "duplicate"});
  assert.deepEqual(captor.kidnappedCards, [other]);
  assert.equal(opposingCaptor.kidnappedCards.length, 1);
});

test("Klia can move only an enemy whose stars were reduced by its summoner and leaves it tapped", async () => {
  const c = fixture(), affected = unit("affected", {tapped: true});
  c.field.enemy_front[0] = affected;
  c.field.enemy_front[1] = unit("unattributed");
  c.field.player_front[0] = unit("friendly");
  c.window.xlwReadStarReductions = candidate => candidate === affected ? {player: 1} : {unattributed: 1};
  c.showXLWConfirm = async () => assert.fail("Klia cannot turn a card upright");
  let picks = 0;
  c.showXLWChoiceModal = async (_, __, options) => {
    if (++picks === 1) {
      assert.equal(options.length, 2);
      assert.equal(options[0].boardTarget.zone, "enemy_front");
      return 0;
    }
    return options.findIndex(choice => choice.boardTarget?.zone === "enemy_back" && choice.boardTarget.idx === 2);
  };
  vm.runInContext(slice("async function xlwResolveFairyStrategist(", "window.xlwResolveFairySoulRefiner ="), c);
  await c.xlwResolveFairyStrategist(true, true);
  assert.equal(c.field.enemy_front[0], null);
  assert.equal(c.field.enemy_back[2], affected);
  assert.equal(affected.tapped, true);
});

test("Fairy draw rewards distinguish empty draw attempts and post-phase checks for each side", () => {
  const c = fixture(), elder = unit("R-EVL-0009"), mayor = unit("R-EVL-0028");
  const opposingMayor = unit("R-EVL-0028");
  c.deck = [{id: "last"}];
  c.window.XLW_ENEMY.deck = [{id: "opponent"}];
  c.playerBonusScore = 0;
  c.enemyBonusScore = 0;
  c.mulliganActive = false;
  c.$ = () => null;
  c.setStatus = () => {};
  c.field.player_front[0] = elder;
  c.field.player_back[0] = mayor;
  c.field.enemy_front[0] = opposingMayor;
  vm.runInContext(slice("window.xlwFairyEffectCard =", "window.xlwReadStarReductions ="), c);
  vm.runInContext(slice("window.xlwResolveFairyDrawReward =", "window.xlwSpringFairyRefill ="), c);
  const reward = c.window.xlwResolveFairyDrawReward;
  c.draw(1);
  assert.equal(c.playerBonusScore, 0);
  assert.equal(reward(true, false), 2);
  assert.equal(reward(true, false), 0);
  c.draw(2);
  assert.equal(c.playerBonusScore, 3);
  c.window.XLW_ENEMY.deck.pop();
  c.turn++;
  assert.equal(reward(true, false), 0);
  assert.equal(reward(false, true), 1);
  assert.equal(c.enemyBonusScore, 1);
  c.isMultiplayer = true;
  assert.equal(reward(false, true), 0);
  c.mulliganActive = true;
  assert.equal(reward(true, true), 0);
});

test("Fairy Shooting Instructor rechecks its rear slot and moves only eligible Fairy units upright", async () => {
  const c = fixture(), instructor = unit("R-EVL-0029");
  const ally = unit("ally", {fairy: true, tapped: true, attacking: true, target: {idx: 1}});
  c.field.player_front[0] = instructor;
  c.field.player_front[1] = unit("unmovable", {fairy: true, fixed: true});
  c.field.player_back[2] = ally;
  c.field.enemy_front[2] = unit("enemy", {fairy: true});
  c.window.xlwIsUnitFairy = candidate => Boolean(candidate?.fairy);
  vm.runInContext(slice("window.xlwResolveFairyShootingInstructor =", "window.xlwResolveFairyExecutioner ="), c);
  const activate = () => c.window.xlwResolveFairyShootingInstructor(instructor, "player_front", 0, true);
  c.showXLWChoiceModal = async (_, __, options) => {
    assert.equal(options.length, 2);
    assert.equal(options[0].boardTarget.idx, 2);
    c.field.player_back[0] = unit("new occupant");
    return 0;
  };
  assert.equal(await activate(), false);
  assert.equal(c.field.player_back[2], ally);
  c.field.player_back[0] = null;
  c.showXLWChoiceModal = async () => 0;
  assert.equal(await activate(), true);
  assert.equal(c.field.player_back[2], null);
  assert.equal(c.field.player_back[0], ally);
  assert.equal(ally.tapped, false);
  assert.equal(ally.attacking, false);
  assert.equal(ally.target, null);
});

test("Fairy ranged targets respect sniper rows and destination protections across both perspectives", () => {
  const c = fixture();
  c.window.hasFlying = () => false;
  c.window.XLW_isShieldUnit = candidate => Boolean(candidate.shield);
  c.isUnitAttackProtected = (zone, idx) => zone === "enemy_back" && idx === 3;
  c.xlwFairHeroBlocksAttack = () => false;
  c.hasArmorBreak = () => false;
  c.field.enemy_front[0] = unit("same lane");
  c.field.enemy_front[2] = unit("other front");
  c.field.enemy_back[3] = unit("protected");
  c.field.enemy_back[4] = unit("other back");
  c.field.player_back[3] = unit("opposite");
  vm.runInContext(slice("function xlwAttackTargetBlock(", "async function xlwTogglePlayerAttack("), c);
  vm.runInContext(slice("window.xlwFairyCrossbowCanAttack =", "function validPlayerAttackLine("), c);
  const targets = (id, zone) => Array.from(c.window.xlwFairyCrossbowTargets(unit(id), zone, 0),
    target => target.unit.card.id);
  assert.deepEqual(targets("SR-EVL-0030", "player_front"), ["same lane", "other back"]);
  assert.deepEqual(targets("EVL-0001", "player_front"), ["same lane", "other front", "other back"]);
  assert.deepEqual(targets("SR-EVL-0030", "enemy_front"), ["opposite"]);
});

test("Valkyrie bonuses stay on their side and grant cards only for attacking wins", async () => {
  const c = fixture();
  const valkyrie = unit("SR-EVL-0026", {fairy: true});
  const recruit = unit("EVL-0008", {fairy: true, hasFairySwordDraw: true});
  const enemyValkyrie = unit("SR-EVL-0026", {fairy: true});
  const nonFairy = unit("nonfairy");
  c.field.player_front.splice(0, 2, recruit, nonFairy);
  c.field.player_back[0] = valkyrie;
  c.field.enemy_back[0] = enemyValkyrie;
  c.window.xlwIsUnitFairy = candidate => Boolean(candidate?.fairy);
  const draws = [];
  c.window.xlwDrawFairyAware = async (amount, player) => { draws.push(player); return amount; };
  vm.runInContext(slice("window.xlwFairyEffectCard =", "window.xlwReadStarReductions ="), c);
  vm.runInContext(slice("window.xlwFairyValkyrieBonus =", "window.xlwResolvePG2CombatSuccess ="), c);
  assert.equal(c.window.xlwFairyValkyrieBonus(recruit, "player_front"), 1);
  assert.equal(c.window.xlwFairyValkyrieBonus(nonFairy, "player_front"), 0);
  assert.equal(await c.window.xlwResolveFairyCombatDraw(recruit, true, false), 1);
  assert.equal(await c.window.xlwResolveFairyCombatDraw(recruit, true, true), 3);
  valkyrie.silenced = true;
  assert.equal(c.window.xlwFairyValkyrieBonus(recruit, "player_front"), 0);
  assert.equal(await c.window.xlwResolveFairyCombatDraw(recruit, true, true), 2);
  assert.equal(await c.window.xlwResolveFairyCombatDraw(enemyValkyrie, false, true), 1);
  c.isMultiplayer = true;
  assert.equal(await c.window.xlwResolveFairyCombatDraw(enemyValkyrie, false, true), 0);
  assert.deepEqual(draws, [true, true, true, true, true, true, false]);
});

test("Valkyrie reuses a selected material slot on a full board and only pays after placement", async () => {
  const c = fixture(), val = {id: "SR-EVL-0026", name: "瓦蓮娜", type: "unit"};
  c.hand.push(val);
  c.normalSummonUsed = false;
  c.calculateTotalStars = () => 14;
  c.getUnitStars = candidate => candidate.stars;
  c.xlwIsUnitUnsacrificable = candidate => Boolean(candidate.fixed);
  c.clearModes = () => {};
  c.structuredClone = structuredClone;
  c.performSummonToSlot = async () => {};
  c.field.player_front.fill(unit("fixed", {fixed: true}));
  c.field.player_back.fill(unit("fixed back", {fixed: true}));
  const a = unit("A", {stars: 2}), b = unit("B", {stars: 3});
  c.field.player_front.splice(0, 2, a, b);
  vm.runInContext(slice("function xlwValkyrieMaterials(", "window.xlwExecuteHandUnitSummon ="), c);
  const activate = () => c.window.xlwSummonFairyValkyrie(val);
  for (const placement of ["cancel", 0]) {
    const answers = [0, 0, "confirm", placement];
    c.showXLWChoiceModal = async (_, __, options) => {
      const answer = answers.shift();
      assert.ok(options.some(choice => choice.value === answer));
      return answer;
    };
    assert.equal(await activate(), placement !== "cancel");
    if (placement === "cancel") {
      assert.equal(c.hand[0], val);
      assert.equal(c.field.player_front[0], a);
      assert.deepEqual(c.graveyard, []);
      assert.equal(c.normalSummonUsed, false);
    }
  }
  assert.deepEqual(c.hand, []);
  assert.deepEqual(c.graveyard, [a.card, b.card]);
  assert.equal(c.field.player_front[0].card.id, val.id);
  assert.equal(c.field.player_front[1], null);
  assert.equal(c.normalSummonUsed, true);
});

test("Saade and Shini use the actual grave entry and distinguish Fairy units from Fairy spells", async () => {
  const c = fixture();
  const saade = {id: "NY-EVL-0016", type: "unit", fairy: true};
  const shini = {id: "SR-EVL-0024", type: "unit", fairy: true};
  const spell = {id: "spell", type: "magic", fairy: true};
  const nonfairy = {id: "other", type: "unit"};
  c.window.xlwIsUnitFairy = card => Boolean(card.fairy);
  c.graveyard.push(saade, shini, spell, nonfairy);
  vm.runInContext(slice("window.xlwRecoverFairyFromGrave =", "window.xlwOnCardEntersGraveyard ="), c);
  c.showXLWChoiceModal = async (_, __, options) => {
    assert.equal(options.length, 2);
    assert.equal(options[0].card, spell);
    return -1;
  };
  assert.equal(await c.window.xlwRecoverFairyFromGrave(shini, true), false);
  c.showXLWChoiceModal = async (_, __, options) => {
    assert.equal(options[0].card, shini);
    return 0;
  };
  assert.equal(await c.window.xlwRecoverFairyFromGrave(saade, true), true);
  assert.deepEqual(c.hand, [shini]);
  assert.deepEqual(c.graveyard, [saade, spell, nonfairy]);
  assert.equal(await c.window.xlwRecoverFairyFromGrave(shini, true), false);
});

test("Fairy Reinforcement reveals only selected Fairy units and keeps unchosen cards at the deck bottom", async () => {
  const c = fixture();
  const old = {id: "old"}, spell = {id: "spell", type: "magic", fairy: true};
  const fairy = {id: "fairy", type: "unit", fairy: true};
  const revealed = [];
  c.window.xlwIsUnitFairy = card => Boolean(card.fairy);
  c.window.xlwRevealCard = async card => { revealed.push(card); };
  vm.runInContext(slice("window.xlwResolveFairyReinforcement =", "window.xlwResolveFairyExecutioner ="), c);
  c.deck = [old, spell, fairy];
  assert.equal(await c.window.xlwResolveFairyReinforcement(c.deck, c.hand), 1);
  assert.deepEqual(c.deck, [spell, old]);
  assert.deepEqual(c.hand, [fairy]);
  assert.deepEqual(revealed, [fairy]);
  c.deck = [old, spell, fairy];
  const picks = [-1, 1];
  c.showXLWChoiceModal = async () => picks.shift();
  assert.equal(await c.window.xlwResolveFairyReinforcement(c.deck, c.hand), 0);
  assert.deepEqual(c.deck, [spell, fairy, old]);
});

test("Fairy mass relocation can swap occupied slots atomically and cannot displace fixed units", async () => {
  const c = fixture();
  const a = unit("a"), b = unit("b"), fixed = unit("fixed", {fixed: true});
  c.field.player_front.splice(0, 3, a, b, fixed);
  vm.runInContext(slice("window.xlwResolveFairyMassRelocation =", "window.xlwResolveFairyReinforcement ="), c);
  const activate = () => c.window.xlwResolveFairyMassRelocation();
  for (const cancel of [true, false]) {
    let pickCount = 0;
    c.showXLWChoiceModal = async (_, __, options) => {
      pickCount++;
      if (pickCount === 1) return "player";
      const boardOptions = options.filter(choice => choice.boardTarget);
      assert.ok(boardOptions.every(choice => choice.boardTarget.idx !== 2 || choice.boardTarget.zone !== "player_front"));
      assert.equal(c.field.player_front[0], a);
      assert.equal(c.field.player_front[1], b);
      if (cancel && pickCount === 3) return "cancel";
      return boardOptions.find(choice => choice.boardTarget.zone === "player_front" &&
        choice.boardTarget.idx === (pickCount === 2 ? 1 : 0)).value;
    };
    assert.equal(await activate(), !cancel);
  }
  assert.deepEqual(c.field.player_front.slice(0, 3), [b, a, fixed]);
});

test("Relocation upgrade requires two distinct enemy retreats in the ending turn and replaces a known card", async () => {
  const c = fixture(), first = unit("first"), second = unit("second");
  const source = {id: "EVL-0017"}, upgrade = {id: "R-EVL-0050", name: "挪移大魔法"};
  c.hand.push(source);
  c.playerExtraDeck.push(upgrade);
  c.field.enemy_back[0] = first;
  c.field.enemy_back[1] = second;
  vm.runInContext(slice("window.xlwRecordFairyRetreat =", "window.xlwResolveFairyMassRelocation ="), c);
  const mark = c.window.xlwRecordFairyRetreat;
  const activate = () => c.window.xlwTryFairyRelocationUpgrade(c.turn);
  mark(first, "enemy_front", "enemy_back");
  mark(first, "enemy_front", "enemy_back");
  assert.equal(await activate(), false);
  mark(second, "enemy_back", "enemy_front");
  assert.equal(await activate(), false);
  mark(second, "enemy_front", "enemy_back");
  c.field.enemy_back[0] = null;
  c.showXLWChoiceModal = async () => -1;
  assert.equal(await activate(), false);
  assert.deepEqual(c.hand, [source]);
  c.showXLWChoiceModal = async () => 0;
  assert.equal(await activate(), true);
  assert.deepEqual(c.hand, [upgrade]);
  assert.deepEqual(c.playerExtraDeck, []);
});

test("Wolf Mace uses one authoritative transfer and does not move another extra card on a stale choice", async () => {
  const c = fixture(), orc = unit("R-ORC-0001", {equipments: ["破甲劍"]});
  c.allCards=[{id:'R-ORC-0072',name:'破甲劍',type:'magic',faction:'獸人',art_subtype:'永久，裝備'}];
  const mace = {id: "R-ORC-0054"}, other = {id: "other"};
  c.field.player_front[0] = orc;
  c.playerExtraDeck.push(mace, other);
  c.isMultiplayer = true;
  c.renderExtraDecks = () => {};
  const snapshots = [];
  c.xlwSendExtraToHand = () => snapshots.push({hand: [...c.hand], extra: [...c.playerExtraDeck]});
  vm.runInContext(slice("async function xlwHandleWolfMaceCombatSuccess(", "async function resolveUnitCombat("), c);
  const activate = () => c.xlwHandleWolfMaceCombatSuccess(orc, "player_front", 0, "player");
  c.showXLWConfirm = async () => false;
  await activate();
  assert.deepEqual(c.playerExtraDeck, [mace, other]);
  c.showXLWConfirm = async () => { c.playerExtraDeck.shift(); return true; };
  await activate();
  assert.deepEqual(c.playerExtraDeck, [other]);
  assert.deepEqual(c.hand, []);
  c.playerExtraDeck.unshift(mace);
  c.showXLWConfirm = async () => true;
  await activate();
  assert.deepEqual(snapshots, [{hand: [mace], extra: [other]}]);
  c.showXLWConfirm = async () => assert.fail("remote combat should never block on a local choice");
  await c.xlwHandleWolfMaceCombatSuccess(orc, "enemy_front", 0, "enemy");
});

test("Extra-zone peer summons consume only the identified copy and cannot overwrite an occupied slot", async () => {
  const c = fixture();
  const a = {id: "C-GOT-0060", _xlwInstanceId: "a"};
  const b = {id: a.id, _xlwInstanceId: "b"};
  const other = {id: "other"};
  c.enemyExtraDeck.push(a, b, other);
  vm.runInContext(slice("function xlwRemoveMirroredExtraCard(", "function renderExtraDecks("), c);
  c.receiveToken = vm.runInContext("(async data => { if (false) {} " +
    slice('} else if (data.action === "xlw_extra_summon_token") {', '} else if (data.action === "add_to_hand_sync") {')
      .replace(/^}/, "") + "} })", c);
  const summon = card => c.receiveToken({action: "xlw_extra_summon_token", zone: "enemy_front", idx: 0, card});
  await summon(b);
  assert.equal(c.field.enemy_front[0].card, b);
  assert.deepEqual(c.enemyExtraDeck, [a, other]);
  await summon(a);
  assert.equal(c.field.enemy_front[0].card, b);
  assert.deepEqual(c.enemyExtraDeck, [a, other]);
  assert.equal(c.xlwRemoveMirroredExtraCard(c.enemyExtraDeck, b), null);
});

test("Meow upgrades consume one exact extra card and ignore repeated or stale peer upgrades", async () => {
  const c = fixture(), source = unit("R-CAT-0028");
  source.card._xlwInstanceId = "break";
  const upgraded = {id: "SR-CAT-0047", _xlwInstanceId: "first"};
  const duplicate = {id: upgraded.id, _xlwInstanceId: "second"};
  c.structuredClone = structuredClone;
  c.field.enemy_front[0] = source;
  c.enemyExtraDeck.push(upgraded, duplicate);
  let leaveCount = 0;
  c.cleanUnitLeavingField = async () => { leaveCount++; };
  vm.runInContext(slice("function xlwRemoveMirroredExtraCard(", "function renderExtraDecks("), c);
  vm.runInContext(slice("async function xlwApplyMeowUpgrade(", "async function xlwCheckNegativeEnergyMeowUpgrade("), c);
  c.receiveUpgrade = vm.runInContext("(async data => { if (false) {} " +
    slice('} else if (data.action === "extra_upgrade_sync"', '} else if (data.action === "double_claw_choice") {')
      .replace(/^}/, "") + "} })", c);
  const message = {action: "extra_upgrade_to_hand_sync", zone: "enemy_front", idx: 0, sourceCard: source.card, newCard: upgraded};
  await c.receiveUpgrade(message);
  assert.deepEqual(c.enemyExtraDeck, [duplicate]);
  assert.deepEqual(c.window.XLW_ENEMY.hand, [upgraded]);
  assert.equal(c.field.enemy_front[0], null);
  c.field.enemy_front[0] = unit("R-CAT-0028");
  c.field.enemy_front[0].card._xlwInstanceId = "replacement";
  await c.receiveUpgrade(message);
  assert.deepEqual(c.enemyExtraDeck, [duplicate]);
  assert.equal(c.field.enemy_front[0].card._xlwInstanceId, "replacement");
  assert.equal(leaveCount, 1);
});

test("An extra retrieval updates the active side's mirror without overwriting its board or taking another copy", () => {
  const c = fixture();
  const card = {id: "EVL-0055", _xlwInstanceId: "arrow-a"};
  const other = {id: card.id, _xlwInstanceId: "arrow-b"};
  const own = unit("unrelated");
  c.enemyExtraDeck.push(other, card);
  c.field.player_back[0] = own;
  vm.runInContext(slice("function xlwSendExtraToHand(", "function renderExtraDecks("), c);
  assert.equal(c.isMyTurn, true);
  assert.equal(c.xlwApplyPeerExtraToHand({...card}), true);
  assert.equal(c.xlwApplyPeerExtraToHand({...card}), false);
  assert.deepEqual(c.enemyExtraDeck, [other]);
  assert.deepEqual(c.window.XLW_ENEMY.hand, [card]);
  assert.equal(c.field.player_back[0], own);
});

test("The extra thief can use an enemy rear slot and keeps its extra card if that slot becomes occupied", async () => {
  const c = fixture(), thief = {id: "SSSR-NMS-0064", name: "大耳賊"};
  const existing = unit("new occupant");
  c.playerExtraDeck.push(thief);
  c.structuredClone = structuredClone;
  c.xlwBlueStarRequirement = () => false;
  c.window.xlwGetEmptyEnemySlots = () => [{zone: "enemy_front", idx: 0}, {zone: "enemy_back", idx: 2}];
  c.window.xlwResolvePG2Summon = async () => {};
  vm.runInContext(slice("window.xlwSpecialSummonUnit =", "window.xlwIsImmediateEffectBlocked ="), c);
  const summon = () => c.window.xlwSpecialSummonUnit(thief, true, {
    destinationIsPlayer: false, frontPriority: false, sourcePile: () => c.playerExtraDeck
  });
  c.showXLWChoiceModal = async (_, __, options) => {
    assert.equal(options.length, 2);
    c.field.enemy_back[2] = existing;
    return 1;
  };
  assert.equal(await summon(), false);
  assert.equal(c.field.enemy_back[2], existing);
  assert.deepEqual(c.playerExtraDeck, [thief]);
  c.field.enemy_back[2] = null;
  c.showXLWChoiceModal = async () => 1;
  assert.equal(await summon(), true);
  assert.equal(c.field.enemy_back[2].card.id, thief.id);
  assert.deepEqual(c.playerExtraDeck, []);
});

test("A relayed Prajna evolution affects only the opponent and ignores a repeat", async () => {
  const c = fixture();
  const own = unit("own");
  const old = unit("old");
  old.card.name = "智慧的般若";
  old.card._xlwInstanceId = "old-prajna";
  const upgrade = {id: "SR-VLG-0049", _xlwInstanceId: "first"};
  const other = {...upgrade, _xlwInstanceId: "second"};
  c.structuredClone = structuredClone;
  c.field.player_front[1] = own;
  c.field.enemy_front[1] = old;
  c.enemyExtraDeck.push(other, upgrade);
  const exiled = [];
  c.exileCard = card => exiled.push(card);
  c.triggerUpgradeBonus = () => {};
  vm.runInContext(slice("function xlwRemoveMirroredExtraCard(", "function renderExtraDecks("), c);
  c.receivePrajna = vm.runInContext("(async data => { if (false) {} " +
    slice('} else if (data.action === "hannya_evolve_sync") {', '} else if (data.action === "extra_summon_resolved") {')
      .replace(/^}/, "") + "} })", c);
  const message = {action: "hannya_evolve_sync", zone: "enemy_front", idx: 1, angryHannya: upgrade, sourceCard: old.card};
  await c.receivePrajna(message);
  await c.receivePrajna(message);
  assert.equal(c.field.player_front[1], own);
  assert.deepEqual(c.field.enemy_front[1].card, upgrade);
  assert.deepEqual(c.enemyExtraDeck, [other]);
  assert.deepEqual(exiled, [old.card]);
});

test("Peer tactical swaps use relay coordinates once and reject a replay against the changed source slots", async () => {
  const c = fixture();
  const a = unit("a"), b = unit("b"), own = unit("own");
  c.field.enemy_front[0] = a;
  c.field.enemy_back[0] = b;
  c.field.player_front[0] = own;
  c.unitName = candidate => candidate.card.id;
  vm.runInContext(slice("function xlwMatchesPeerCard(", "function renderExtraDecks("), c);
  const receive = vm.runInContext("(async data => { if (false) {} " +
    slice('} else if (data.action === "swap_units") {', '} else if (data.action === "scarecrow_move_sync") {')
      .replace(/^}/, "") + "} })", c);
  const msg = {action: "swap_units", zoneA: "enemy_front", idxA: 0, zoneB: "enemy_back", idxB: 0, first: a.card, second: b.card};
  await receive(msg);
  await receive(msg);
  assert.equal(c.field.enemy_front[0], b);
  assert.equal(c.field.enemy_back[0], a);
  assert.equal(c.field.player_front[0], own);
});

test("A mirrored pile summon rejects a stale destination and preserves other copies", () => {
  const c = fixture();
  const card = {id: "SSSR-NMS-0060", _xlwInstanceId: "hirako-a"};
  const other = {...card, _xlwInstanceId: "hirako-b"};
  c.enemyGraveyard.push(other, card);
  c.field.enemy_front[0] = unit("occupied");
  vm.runInContext(slice("function xlwMatchesPeerCard(", "function renderExtraDecks("), c);
  const summon = idx => c.xlwApplyPeerPileSummon({zone: "enemy_front", idx, card}, c.enemyGraveyard, false);
  assert.equal(summon(0), false);
  assert.deepEqual(c.enemyGraveyard, [other, card]);
  assert.equal(summon(1), true);
  assert.equal(summon(2), false);
  assert.deepEqual(c.enemyGraveyard, [other]);
  assert.equal(c.field.enemy_front[1].card, card);
});

test("Thief asks its attacking owner only when current attack is exactly twice current stars", async () => {
  const c = fixture(), attacker = unit("piercer", {attacking: true, attack: 8, stars: 4, piercing: true});
  attacker.card.attack = 3;
  c.phase = "進攻宣言";
  c.field.player_front[0] = attacker;
  const thief = {id: "SSSR-NMS-0064"};
  c.playerExtraDeck.push(thief);
  c.getUnitAtk = unit => unit.attack;
  c.getUnitStars = unit => unit.stars;
  c.checkUnitHasPiercing = unit => unit.piercing;
  let prompts = 0, placements = 0;
  c.showXLWConfirm = async () => { prompts++; return true; };
  c.window.xlwSpecialSummonUnit = async (card, own, options) => {
    assert.equal(card, thief);
    assert.equal(own, true);
    assert.equal(options.destinationIsPlayer, false);
    assert.equal(options.frontPriority, false);
    assert.equal(options.beforePlacement(), true);
    attacker.stars = 3;
    assert.equal(options.beforePlacement(), false);
    attacker.stars = 4;
    placements++;
    return true;
  };
  vm.runInContext(slice("window.xlwTryThiefSummon =", "window.xlwResolveSavageMartial ="), c);
  const trigger = () => c.window.xlwTryThiefSummon(attacker, "player_front", 0);
  assert.equal(await trigger(), true);
  assert.equal(placements, 1);
  attacker.attack = 6; // Twice printed attack, but not twice current stars.
  assert.equal(await trigger(), false);
  attacker.attack = 8;
  attacker.attacking = false;
  assert.equal(await trigger(), false);
  attacker.attacking = true;
  c.isMyTurn = false;
  assert.equal(await trigger(), false);
  c.isMyTurn = true;
  c.showXLWConfirm = async () => { prompts++; attacker.stars = 5; return true; };
  assert.equal(await trigger(), false);
  assert.equal(prompts, 2);
  assert.equal(placements, 1);
});

test("Main-phase equipment remains playable while its owner is declaring attacks", () => {
  const c = fixture();
  c.xlwIsBreakfast = () => false;
  c.phase = "進攻宣言";
  c.isMultiplayer = true;
  const attacker = unit("R-ORC-0001", {attacking: true, tapped: true, target: {zone: "enemy_front", idx: 0}});
  c.field.player_front[0] = attacker;
  const hat = {id: "R-0RC-0044", name: "符咒獸人的符咒帽", type: "magic", usable_phases: ["Main Phase"]};
  vm.runInContext(slice("window.xlwCanPlayHandCard =", "window.xlwShowHandCardQuickMenu ="), c);
  assert.equal(c.window.xlwCanPlayHandCard(hat, 0), true);
  assert.equal(attacker.attacking, true);
  assert.equal(attacker.target.idx, 0);
  assert.equal(c.window.xlwCanPlayHandCard({...hat, usable_phases: ["Defense Phase"]}, 0), false);
  c.isMyTurn = false;
  assert.equal(c.window.xlwCanPlayHandCard(hat, 0), false);
  c.isMyTurn = true;
  assert.equal(c.window.xlwCanPlayHandCard({id: "ART-0020", name: "星空", type: "magic"}, 0), false);
});
