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
