const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/game_v8.js'), 'utf8');
function section(name) {
  let start = source.indexOf('async function ' + name + '(');
  if (start < 0) start = source.indexOf('function ' + name + '(');
  const next = source.slice(start + 1).search(/\n(?:async )?function /);
  return source.slice(start, next < 0 ? undefined : start + 1 + next);
}
const effectStart = source.indexOf('window.xlwResolveEndPhaseEffects =');
const effects = source.slice(effectStart, source.indexOf('// Functionally implemented keyword-only', effectStart));
const code = section('endPlayerTurnAndRunEnemy') + '\n' + section('runNeutralEndPhaseEffects') + '\n' + effects;
let tests = 0;
function fixture(role = 'player1') {
  const errors = [], sent = [], paused = [];
  const g = {
    console: { log() {}, warn() {}, error(...args) { errors.push(args.map(String).join(' ')); } },
    navigator: {}, document: { getElementById: () => null }, $: () => null, structuredClone,
    field: Object.fromEntries(['player_front','player_back','enemy_front','enemy_back'].map(z => [z, Array(5).fill(null)])),
    hand: [], deck: [{}, {}], graveyard: [], enemyGraveyard: [], playerExtraDeck: [], enemyExtraDeck: [],
    isMyTurn: true, isMultiplayer: true, player_role: role, mulliganActive: false,
    phase: '進攻宣言', turn: 1, playerBonusScore: 0, enemyBonusScore: 0,
    countdownActive: false, isGameOverFlag: false,
    render() {}, renderScore() {}, renderStablePanel() {}, clearModes() {},
    setStatus(value) { g.status = value; }, logBattle() {}, sleep: async () => {},
    xlwRequireSpellCompletion: () => false, xlwEnforceForcedSummonRule: async () => false,
    checkPopulationCap: async () => {}, xlwCleanExpiredTempEquips() {},
    calculateTotalStars: side => side ? 3 : 0, calculateUnitCount: side => side ? 1 : 0,
    resolveDecayStatus: async () => {}, handleTurnEndCountdownLogic() {}, checkCallGameAtTurnStart() {},
    saveLocalGameState() {}, isPigmentCard: () => false, getUnitAtk: () => 0,
    sendFullGameStateToOpponent: (includePhase, action) => sent.push({ action, turn: g.turn }),
    destroyUnit: async (zone, idx, owner) => {
      assert.equal(owner, zone.startsWith('player_') ? 'player' : 'enemy');
      const unit = g.field[zone][idx];
      if (unit) (owner === 'player' ? g.graveyard : g.XLW_ENEMY.grave).push(unit.card);
      g.field[zone][idx] = null;
    }
  };
  g.window = g;
  g.XLW_ENEMY = { deck: [{}, {}], hand: [], grave: [] };
  g.XLW_sync = { stop(error) { paused.push(error.message); } };
  for (const match of code.matchAll(/window\.([A-Za-z_$][\w$]*)\s*\(/g)) {
    if (!(match[1] in g)) g[match[1]] = () => false;
  }
  g.field.player_front[3] = { card: { id: 'R-ART-0011', name: '拿波崙', attack: 3, score: 3 }, equipments: [] };
  vm.createContext(g);
  vm.runInContext(code, g);
  return { g, errors, sent, paused };
}
module.exports = (async () => {
  for (const role of ['player1', 'player2']) {
    const { g, errors, sent } = fixture(role);
    for (let cycle = 0; cycle < 20; cycle++) {
      const previous = g.turn;
      g.isMyTurn = true;
      g.phase = '進攻宣言';
      await g.endPlayerTurnAndRunEnemy();
      assert.equal(g.turn, previous + 1);
      assert.equal(g.phase, '抽牌階段');
      assert.equal(g.isMyTurn, false);
      assert.equal(g.XLW_isPlayerTurnEnding, false);
      assert.equal(sent.filter(message => message.action === 'end_turn').length, cycle + 1);
    }
    assert.deepEqual(errors, []);
    tests += 20;
    const failed = fixture(role);
    failed.g.phase = '召喚階段';
    failed.g.xlwEnforceForcedSummonRule = async () => { throw Error('preflight failure'); };
    await failed.g.endPlayerTurnAndRunEnemy();
    assert.equal(failed.g.XLW_isPlayerTurnEnding, false);
    assert.deepEqual(failed.paused, ['preflight failure']);
    assert.equal(failed.sent.length, 0);
    tests++;
    const pending = fixture(role);
    let release;
    pending.g.XLW_playerNeedsToDraw = true;
    pending.g.xlwHandlePlayerDeckClick = () => new Promise(resolve => { release = resolve; });
    const first = pending.g.endPlayerTurnAndRunEnemy();
    await pending.g.endPlayerTurnAndRunEnemy();
    release();
    await first;
    assert.equal(pending.sent.filter(message => message.action === 'end_turn').length, 1);
    tests++;
  }
  for (const side of [true, false]) {
    for (const candy of ['R-CND-0039', 'R-CND-0052']) {
      const { g } = fixture();
      for (const row of Object.values(g.field)) row.fill(null);
      const zone = side ? 'player_front' : 'enemy_front';
      const host = { card: { id: 'HOST', name: '合體單位' }, devourCards: [{ card: { id: candy } }] };
      g.field[zone][0] = host;
      await g.runNeutralEndPhaseEffects(side);
      assert.equal(g.field[zone][0], null);
      assert.equal((side ? g.graveyard : g.XLW_ENEMY.grave)[0], host.card);
      tests++;
    }
  }
  const circus = fixture();
  circus.g.xlwGetFactionFieldCard = side => side ? { id: 'CCS-0029' } : null;
  circus.g.XLW_playerWheelSpinsThisTurn = 1;
  await circus.g.endPlayerTurnAndRunEnemy();
  assert.equal(circus.g.playerBonusScore, 1);
  assert.equal(circus.g.XLW_playerWheelSpinsThisTurn, 0);
  tests++;
  const sendStart = source.indexOf('  if (isMultiplayer) {', source.indexOf('    } // end of if (!immediateEffectNegated)'));
  const sendEnd = source.indexOf('  if (window.XLW_summonPlacementResolve)', sendStart);
  for (const special of [true, false]) {
    const messages = [];
    const c = {
      isMultiplayer: true, isSpecialSummon: special, summonMessageSent: false, selectedHandForSummon: 0,
      zone: 'player_front', idx: 0, card: { id: 'SUMMONED' }, field: { player_front: [{ card: { id: 'SUMMONED' } }] },
      ws: { send: raw => messages.push(JSON.parse(raw)) }, sendFullGameStateToOpponent() {}
    };
    c.window = c;
    vm.runInNewContext(source.slice(sendStart, sendEnd), c);
    assert.equal(messages[0].fromHand, !special);
    tests++;
  }
  console.log(`${tests} full end-turn, role symmetry, repeated-input, failure recovery and effect-source checks: PASS`);
})();
