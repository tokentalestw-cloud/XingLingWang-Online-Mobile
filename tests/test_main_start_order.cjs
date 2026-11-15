const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const read = name => fs.readFileSync(path.join(__dirname, "../static", name), "utf8");
const game = read("game_v8.js");
const slice = (start, end) => game.slice(game.indexOf(start), game.indexOf(end, game.indexOf(start)));

test("the active player orders Thief and Angel and the final state syncs once", async () => {
  const order = [];
  const thief = {card: {id: "SR-ART-0068", name: "蜘蛛魔盜團偷天"}};
  const angel = {card: {id: "SSR-ART-0070", name: "四季大天使 慕夏"}, irrigation: 4};
  const art = {id: "C-ART-0001", type: "unit", name: "雕像"};
  const field = {player_front: [thief, angel], player_back: [], enemy_front: [], enemy_back: []};
  const context = vm.createContext({
    field, hand: [art], graveyard: [], playerExtraDeck: [], turn: 8, phase: "召喚階段", isMultiplayer: true,
    window: {
      isUnitSilenced: () => false,
      xlwIrrigateUnit: unit => { order.push("angel"); unit.irrigation = 1; },
      xlwGetEmptyPlayerSlots: () => [],
      xlwResolveExpansionTurnStart: async () => {},
      xlwResolveTurnStartEffects: async () => {}
    },
    logBattle() {}, render() {}, getCardTributeCost: () => 0, isNonHumanoidArtworkCard: () => true,
    xlwCheckBananaMarquisMovement: async () => {},
    sendFullGameStateToOpponent: () => order.push("sync"),
    showXLWChoiceModal: async (title, _, choices) => {
      if (title === "主要階段開始") return choices.find(choice => choice.text.includes("偷天")).value;
      if (title.includes("魔盜行動")) { order.push("thief"); return "kidnap"; }
      return 0;
    }
  });
  vm.runInContext(read("duel_consistency.js"), context);
  vm.runInContext(slice("function xlwQueuePG2MainStart(", "// 結束階段效果 (PG2"), context);
  await context.window.xlwRunMainStart(true);
  await context.window.xlwRunMainStart(true);
  assert.deepEqual(order, ["thief", "angel", "sync"]);
  assert.equal(thief.kidnappedCards[0], art);
  assert.equal(art.originalOwner, "player");
  assert.equal(context.hand.length, 0);
  assert.equal(angel.irrigation, 1);
});
