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

test("craft search only takes craft spells, cancellation is free, and the limit renews next turn", async () => {
  const unit = {card: {id: "R-EWD-0051", name: "學會工藝的野人"}};
  const club = {id: "R-EWD-0052", name: "野人工藝-木棒", type: "magic"};
  const cloak = {id: "R-EWD-0053", name: "野人工藝-披風", type: "magic"};
  const other = {id: "SR-EWD-0055", type: "unit"};
  const context = vm.createContext({
    turn: 3, isMyTurn: true, isMultiplayer: false, field: {player_front: [unit]},
    playerExtraDeck: [other, club, cloak], hand: [], xlwEwdInMainPhase: () => true,
    showXLWChoiceModal: async (_, __, cards) => {
      assert.equal(cards.some(option => option.card === other), false);
      return context.pick;
    },
    window: {isUnitSilenced: () => false, XLWDuelConsistency: {
      takeKnownCard: (pile, card) => pile.includes(card) && pile.splice(pile.indexOf(card), 1)[0]
    }},
    render() {}, logBattle() {}, async xlwOnPlayerUnitTapped() {}
  });
  vm.runInContext(code("window.xlwActivateSavageCraft =", "async function xlwResolveExpansionUnitClick"), context);
  const activate = context.window.xlwActivateSavageCraft;
  context.pick = -1;
  assert.equal(await activate(unit, "player_front", 0), false);
  assert.equal(unit.tapped, undefined);
  context.pick = 0;
  assert.equal(await activate(unit, "player_front", 0), true);
  unit.tapped = false;
  assert.equal(await activate(unit, "player_front", 0), false);
  context.turn++;
  assert.equal(await activate(unit, "player_front", 0), true);
  assert.deepEqual(context.hand, [club, cloak]);
  assert.deepEqual(context.playerExtraDeck, [other]);
});

test("pendant must target a savage and disappears back to extra with working magic resistance", async () => {
  const card = {id: "R-EWD-0054", name: "野人工藝-吊墜"};
  const unit = {card: {name: "野人"}};
  const context = vm.createContext({
    field: {player_front: [unit, {card: {name: "非目標"}}], player_back: []},
    playerExtraDeck: [], graveyard: [],
    window: {xlwIsUnitBarbarian: target => target === unit, xlwCardHasKeyword: () => true},
    showXLWChoiceModal: async (_, __, choices, config) => {
      assert.equal(choices.length, 1);
      assert.equal(choices[0].boardTarget.idx, 0);
      assert.equal(config.required, true);
      return 0;
    },
    render() {}, logBattle() {}
  });
  vm.runInContext(code("async function xlwResolveSavageCraftSpell", "async function castSpell(handIndex)"), context);
  vm.runInContext(code("function isUnitMagicImmune(", "function isUnitEffectImmune("), context);
  await context.xlwResolveSavageCraftSpell(card);
  assert.equal(context.isUnitMagicImmune(unit, "player_front", 0), true);
  assert.deepEqual(context.playerExtraDeck, [card]);
  assert.equal(context.graveyard.length, 0);
});

test("three printed attack buffs are each consumed exactly once by the stat resolver", () => {
  const statResolver = code("function getUnitAtk(", "function getUnitStars(");
  for (const property of ["woodClubBonus", "fairySwordBonus", "soulShardAtk"]) {
    assert.equal(statResolver.split("baseAtk += unit." + property).length - 1, 1, property);
  }
});

test("a cave releases only its own side's cards and persists placement before summon reactions", async () => {
  const cave = id => ({id: "R-EWD-0062", shelteredCards: [{id}]});
  const playerField = {dataset: {card: JSON.stringify(cave("first"))}};
  const enemyField = {dataset: {card: JSON.stringify(cave("second"))}};
  const node = own => own ? playerField : enemyField;
  let allow = false;
  const context = vm.createContext({
    document: {getElementById: id => node(id === "playerField")},
    window: {
      xlwGetFactionFieldCard: own => JSON.parse(node(own).dataset.card),
      xlwSpecialSummonUnit: async (card, own, opts) => {
        if (!allow) return false;
        assert.ok(opts.payCost());
        assert.equal(card.id, "second");
        opts.sourcePile().pop();
        opts.onSourceTaken();
        assert.equal(JSON.parse(enemyField.dataset.card).shelteredCards.length, 0);
        return true;
      }
    }
  });
  vm.runInContext(code("window.xlwReleaseSavageCave =", "async function xlwShelterInSavageCave"), context);
  await context.window.xlwReleaseSavageCave(true);
  allow = true;
  await context.window.xlwReleaseSavageCave(false);
  assert.equal(JSON.parse(playerField.dataset.card).shelteredCards[0].id, "first");
  assert.equal(JSON.parse(enemyField.dataset.card).shelteredCards.length, 0);
});

test("fighter search can be declined and is allowed again in a later turn", async () => {
  const unit = {card: {id: "SR-EWD-0065", name: "格鬥專家野人"}};
  const cards = [
    {type: "magic", id: "R-EWD-0068"},
    {type: "magic", id: "R-EWD-0069"}
  ];
  const context = vm.createContext({
    turn: 1, field: {player_front: [unit], player_back: []}, hand: [],
    playerExtraDeck: [...cards], showXLWChoiceModal: async () => context.pick,
    window: {xlwIsUnitMartial: () => true, isUnitSilenced: () => false, XLWDuelConsistency: {
      takeKnownCard: (pile, card) => pile.splice(pile.indexOf(card), 1)[0]
    }}, logBattle() {}
  });
  vm.runInContext(code("window.xlwCheckFighterBarbarianAttackPhaseStart =", "// 16. SR-GOT-0060"), context);
  const search = context.window.xlwCheckFighterBarbarianAttackPhaseStart;
  context.pick = -1;
  await search(true);
  assert.equal(context.hand.length, 0);
  context.pick = 0;
  await search(true);
  await search(true);
  assert.equal(context.hand.length, 1);
  context.turn++;
  await search(true);
  assert.deepEqual(context.hand, cards);
});
