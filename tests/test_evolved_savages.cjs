const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const source = fs.readFileSync(path.join(__dirname, "../static/game_v8.js"), "utf8");
const code = (start, end) => source.slice(source.indexOf(start), source.indexOf(end, source.indexOf(start)));

test("guerrilla offers the owner's hand or grave once per main phase and ignores peer replay", async () => {
  const destroyed = { card: { id: "EWD-0001" }, savage: true };
  const hand = [{ id: "C-EWD-0057" }], graveyard = [{ id: "C-EWD-0057" }];
  const choices = [];
  const context = vm.createContext({
    isMyTurn: true, isMultiplayer: true, phase: "召喚階段", turn: 2, hand, graveyard,
    playerExtraDeck: [], enemyExtraDeck: [],
    showXLWChoiceModal: async (_, __, options) => { choices.push(options.map(choice => choice.text).join(",")); return 1; },
    window: {
      xlwIsUnitBarbarian: unit => unit.savage,
      xlwSpecialSummonUnit: async (card, own, opts) => {
        assert.equal(own, true);
        const pile = opts.sourcePile();
        pile.splice(pile.indexOf(card), 1);
        return true;
      }
    }
  });
  vm.runInContext(code("window.xlwResolveSavageAfterDestruction =", "window.xlwResolvePG2Destruction ="), context);
  const resolve = context.window.xlwResolveSavageAfterDestruction;
  await resolve(destroyed, "enemy_front");
  await resolve(destroyed, "player_front");
  await resolve(destroyed, "player_front");
  assert.equal(hand.length, 0);
  assert.equal(graveyard.length, 1);
  assert.deepEqual(choices, ["墓地,手牌,不發動"]);
});

test("an outfielder uses the owner's extra deck and the rival's field during tactical play", async () => {
  const card = { id: "SR-EWD-0055", name: "緊張的外野人" };
  const received = [];
  const context = vm.createContext({
    isMyTurn: true, isMultiplayer: true, phase: "戰術佈陣", turn: 2,
    hand: [], graveyard: [], playerExtraDeck: [card], enemyExtraDeck: [],
    showXLWConfirm: async () => true,
    window: {
      xlwIsUnitBarbarian: () => true,
      xlwSpecialSummonUnit: async (summoned, own, opts) => {
        received.push([summoned, own, opts.destinationIsPlayer, opts.sourcePile()[0]]);
        opts.sourcePile().pop();
        return true;
      }
    }
  });
  vm.runInContext(code("window.xlwResolveSavageAfterDestruction =", "window.xlwResolvePG2Destruction ="), context);
  const unit = { card: { id: "EWD-0001" } };
  await context.window.xlwResolveSavageAfterDestruction(unit, "player_front");
  await context.window.xlwResolveSavageAfterDestruction(unit, "player_front");
  assert.deepEqual(received, [[card, true, false, card]]);
});
