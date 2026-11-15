const {test} = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");
const source = fs.readFileSync(require("node:path").join(__dirname, "../static/game_v8.js"), "utf8");

function load(start, end, globals) {
  vm.runInNewContext(source.slice(source.indexOf(start), source.indexOf(end, source.indexOf(start))), globals);
}
function game() {
  const g = {
    field: Object.fromEntries(["player_front", "player_back", "enemy_front", "enemy_back"].map(z => [z, Array(5).fill(null)])),
    room_id: "test", turn: 3, phase: "進攻宣言", isMultiplayer: true,
    tacticalSummonUsed: false, XLW_DEFENSE_RULE: {resolving: true},
    LITTLE_TRAVELER: {id: "TOKEN_TRAVELER"}, structuredClone, setTimeout, clearTimeout,
    ws: {send(s) { g.messages.push(JSON.parse(s)); }}, messages: [],
    isUnitSilenced: () => false, hasFlying: unit => !!unit?.flying,
    XLW_isShieldUnit: unit => !!unit?.shield, hasArmorBreak: () => false,
    isUnitAttackProtected: () => false, xlwUnitHasRanged: unit => !!unit?.ranged,
    xlwIsAttackBlockedByClea: () => false, xlwOnPlayerUnitTapped: async () => {},
    checkUnitHasPiercing: () => false, playerExtraDeck: [],
    xlwCaptureSummonCover: () => null, playTravelerSummonAnimation() {},
    unitName: unit => unit.card.name, setStatus() {}, logBattle() {}, render() {}
  };
  g.window = g;
  g.getUnitAtk = unit => unit.attack;
  load("function xlwFairHeroBlocksAttack(", "function isUnitAttackProtected(", g);
  load("function xlwIsFlyingGoat(", "async function changeActionPhase(", g);
  load("async function xlwAutoDeclarePlayerAttacks(", "window.xlwTogglePlayerAttack =", g);
  load("async function xlwSummonGoatTravelers(", "async function resolveUnitCombat(", g);
  return g;
}

test("Fair Hero blocks unequal attack values from either side and permits equal values", () => {
  const g = game();
  for (const [from, to] of [["player_front", "enemy_front"], ["enemy_front", "player_front"]]) {
    const attacker = {attack: 7};
    g.field[to][0] = {card: {id: "R-BRV-0001"}, attack: 8};
    assert.equal(g.xlwFairHeroBlocksAttack(attacker, from, 0, to, 0), true);
    attacker.attack = 8;
    assert.equal(g.xlwFairHeroBlocksAttack(attacker, from, 0, to, 0), false);
  }
});

test("conditional summons require the summoning side's specific prerequisites", () => {
  const g = game();
  g.playerExileZone = [];
  g.enemyExileZone = [];
  load("function xlwBlueStarRequirement(", "function canSummonCard(", g);
  const bear = {id: "ELE-0019"}, mazu = {id: "SR-FMS-0036"}, engineer = {id: "SSR-RBT-0026"};
  for (const card of [bear, mazu, engineer]) assert.ok(g.xlwBlueStarRequirement(card, true));
  g.field.player_back[0] = {card: {id: "ELE-0025"}};
  g.playerExileZone.push({id: "R-FMS-0017"});
  g.field.player_front[0] = {devourCards: [{}]};
  g.field.player_front[1] = {isCombined: true};
  for (const card of [bear, mazu, engineer]) {
    assert.equal(g.xlwBlueStarRequirement(card, true), "");
    assert.ok(g.xlwBlueStarRequirement(card, false));
  }
});

test("only two chosen traveler placements are mirrored from either owner", async () => {
  const g = game();
  const peer = game();
  g.field.player_front[0] = peer.field.enemy_front[0] = {card: {id: "R-GOT-0008-PG"}};
  const picks = [4, 2];
  g.showXLWChoiceModal = async (_title, _message, choices, config) => {
    assert.equal(config.required, true);
    const index = picks.shift();
    return choices.find(option => option.value.idx === index).value;
  };
  const mirror = peer.xlwSummonGoatTravelers("enemy_front", 0);
  await g.xlwSummonGoatTravelers("player_front", 0);
  assert.equal(g.messages.length, 1);
  const positions = g.messages[0].positions.map(slot => ({...slot, zone: "enemy_front"}));
  assert.deepEqual(positions.map(slot => slot.idx), [4, 2]);
  peer.XLW_goatTravelerPlacements.get("test:3:enemy_front:0")(positions);
  await mirror;
  for (const row of [g.field.player_front, peer.field.enemy_front]) {
    assert.deepEqual(row.map(unit => unit?.card.id), ["R-GOT-0008-PG", undefined, "TOKEN_TRAVELER", undefined, "TOKEN_TRAVELER"]);
  }
});

test("ranged target is a board choice and the selected row is sent", async () => {
  for (const chosenRow of ["enemy_front", "enemy_back", null]) {
    const g = game();
    const unit = {card: {id: "bow", name: "弓兵"}, ranged: true};
    g.field.player_front[1] = unit;
    g.field.enemy_front[1] = {card: {id: "bird"}, flying: true};
    g.field.enemy_back[1] = {card: {id: "enemy"}};
    await g.xlwAutoDeclarePlayerAttacks();
    assert.equal(unit.attacking, undefined);
    g.showXLWChoiceModal = async (_title, _message, choices) => {
      assert.deepEqual(Array.from(choices, c => c.boardTarget.zone), ["enemy_front", "enemy_back"]);
      return chosenRow;
    };
    await g.xlwTogglePlayerAttack("player_front", 1);
    assert.equal(!!unit.attacking, !!chosenRow);
    assert.equal(g.messages[0]?.targetZone, chosenRow ?? undefined);
  }
});

test("Flying Goat can choose to attack after tactical movement, ordinary units cannot", async () => {
  const g = game();
  g.XLW_tacticalMoveUsed = true;
  const ordinary = {card: {id: "normal", name: "普通單位"}};
  const goat = {card: {id: "R-GOT-0025", name: "飛天山羊"}};
  g.field.player_front[2] = ordinary;
  g.field.player_back[2] = goat;
  g.field.enemy_front[2] = {card: {id: "enemy"}};
  assert.equal(g.xlwCanDeclareAfterTactical(), true);
  await g.xlwTogglePlayerAttack("player_front", 2);
  await g.xlwTogglePlayerAttack("player_back", 2);
  assert.equal(ordinary.attacking, undefined);
  assert.equal(goat.attacking, true);
  assert.equal(g.messages[0].attZone, "player_back");
});

