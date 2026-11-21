const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const game = fs.readFileSync(path.join(__dirname, "../static/game_v8.js"), "utf8");
const consistency = fs.readFileSync(path.join(__dirname, "../static/duel_consistency.js"), "utf8");
const effect = game.slice(game.indexOf("window.xlwTriggerSktImmediateEffects ="), game.indexOf("window.xlwUnitHasPoison ="));

function setup(id) {
  const card = { id };
  const undead = { id: "SKT-1234", name: "Undead", type: "unit", _xlwInstanceId: "instance-1" };
  const graveyard = [undead];
  const unit = { card };
  const row = [unit];
  const logs = [];
  const context = vm.createContext({
    window: { xlwIsUndeadCard: () => true },
    field: { player_front: row },
    graveyard,
    enemyGraveyard: [],
    deck: [],
    hand: [],
    logBattle: message => logs.push(message),
    render() {},
    shuffle() {},
  });
  vm.runInContext(consistency, context);
  context.xlwFactionDecisionKey = () => 'coffin-test';
  context.window.xlwChooseFactionAction = (local, key, title, message, options) => context.showXLWChoiceModal(title, message, options);
  vm.runInContext(game.slice(game.indexOf('// Coffin Ship loads physical'), game.indexOf('// End Coffin Ship loading.')), context);
  vm.runInContext(effect, context);
  return { context, undead, graveyard, unit, row, logs,
    run: () => context.window.xlwTriggerSktImmediateEffects(card, "player_front", 0, true) };
}

test("Coffin Ship leaves the selected card in the grave if the ship leaves", async () => {
  const { context, graveyard, undead, row, unit, logs, run } = setup("SKT-0050");
  context.showXLWChoiceModal = async () => {
    row[0] = null;
    return 0;
  };
  await run();
  assert.deepEqual(graveyard, [undead]);
  assert.equal(unit.kidnappedCards.length, 0);
  assert.deepEqual(logs, []);
});

test("Coffin Ship takes the current instance after the grave entry is cloned", async () => {
  const { context, graveyard, undead, unit, run } = setup("SKT-0050");
  const refreshed = { ...undead };
  context.showXLWChoiceModal = async () => {
    graveyard[0] = refreshed;
    return 0;
  };
  await run();
  assert.equal(graveyard.length, 0);
  assert.equal(unit.kidnappedCards[0], refreshed);
  assert.equal(refreshed.originalOwner, "player");
});

test("Gus keeps the card in the grave when special summon is canceled", async () => {
  const { context, graveyard, undead, logs, run } = setup("SKT-0003");
  context.showXLWChoiceModal = async () => 0;
  let attempted = false;
  context.window.xlwSpecialSummonUnit = async (card, isPlayer, options) => {
    attempted = true;
    assert.equal(card, undead);
    assert.equal(isPlayer, true);
    assert.equal(options.sourcePile(), graveyard);
    assert.deepEqual(graveyard, [undead]);
    return false;
  };
  await run();
  assert.equal(attempted, true);
  assert.deepEqual(graveyard, [undead]);
  assert.deepEqual(logs, []);
});
