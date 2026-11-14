const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const read = name => fs.readFileSync(path.join(__dirname, "../static", name), "utf8");
const source = read("game_v8.js");
const section = (start, end) => source.slice(source.indexOf(start), source.indexOf(end, source.indexOf(start)));

test("tactical tribute recognizes queen variants, excludes other factions, and respects silence", () => {
  const queen = { card: { id: "SSR-CND-0057-泳裝" } };
  let silenced = false;
  const context = vm.createContext({window: {isUnitSilenced: () => silenced}, field: {player_front: [queen]}});
  vm.runInContext(section("function isDessertCard(", "window.isDessertCard"), context);
  vm.runInContext(section("function isDessertQueen(", "async function xlwSeparateAllFusedUnits"), context);
  const dessert = { id: "CND-0099", type: "unit" };
  assert.ok(context.xlwAllowsTacticalTribute(dessert));
  assert.ok(!context.xlwAllowsTacticalTribute({ id: "ART-0001" }));
  silenced = true;
  assert.ok(!context.xlwAllowsTacticalTribute(dessert));
});

test("gummy retrieval transfers one actual extra-deck card with a notice for each player", () => {
  const target = { id: "C-CND-0060", name: "軟糖幻影" };
  const hand = [], extra = [target], notices = [], sent = [];
  const context = vm.createContext({
    window: {XLWBFeedback: {notice: message => notices.push(message)}},
    hand, playerExtraDeck: extra, isMultiplayer: true,
    ws: {readyState: 1, send: message => sent.push(JSON.parse(message))},
    logBattle() {}, render() {}, renderExtraDecks() {}, sendFullGameStateToOpponent() {}
  });
  vm.runInContext(read("duel_consistency.js"), context);
  vm.runInContext(section("function xlwRecoverGummyPhantom(", "async function xlwSeparateAllFusedUnits"), context);
  const card = { name: "幻影軟糖" };
  context.xlwRecoverGummyPhantom(card, true);
  context.xlwRecoverGummyPhantom(card, true);
  assert.deepEqual(hand, [target]);
  assert.equal(extra.length, 0);
  assert.equal(notices.length, 1);
  assert.match(notices[0], /加入我方手牌/);
  assert.equal(sent.length, 1);
  assert.match(sent[0].message, /加入對手手牌/);
  assert.equal(sent[0].showNotice, true);
});
