const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/game_v8.js'), 'utf8');
const start = source.indexOf('// Faction state uses');
const core = source.slice(start, source.indexOf('// ===== 6. 召喚與獻祭召喚系統 =====', start));
let tests = 0;
function fixture() {
  const elements = { playerField: { dataset: {} }, enemyField: { dataset: {} } };
  const g = {
    document: { getElementById: id => elements[id] || null },
    field: Object.fromEntries(['player_front', 'player_back', 'enemy_front', 'enemy_back'].map(z => [z, Array(5).fill(null)])),
    turn: 3, hand: [], deck: [], graveyard: [], enemyGraveyard: [], allCards: [], playerExtraDeck: [], enemyExtraDeck: [],
    playerBonusScore: 0, enemyBonusScore: 0,
    isUnitSilenced: u => Boolean(u.silenced), render() {}, renderScore() {}, logBattle() {},
    showXLWConfirm: async () => false, structuredClone,
    setTimeout() { throw Error('Detached effect timer is forbidden'); }
  };
  g.window = g; g.XLW_ENEMY = { grave: [], hand: [], deck: [] };
  vm.createContext(g); vm.runInContext(core, g);
  return { g, elements };
}
module.exports = (async () => {
  for (const isPlayer of [true, false]) {
    const { g, elements } = fixture();
    const key = isPlayer ? 'XLW_playerSteamEnergy' : 'XLW_enemySteamEnergy';
    assert.equal(g.xlwGetMaxSteamEnergy(isPlayer), 5); tests++;
    assert.equal(await g.xlwChargeEnergy(2, isPlayer), 2);
    assert.equal(g[key], 2); tests++;
    assert.equal(g.xlwConsumeEnergy(1, isPlayer), true);
    assert.equal(g[key], 1); tests++;
    assert.equal(g.xlwConsumeEnergy('player', 4), false);
    assert.equal(g[key], 1); tests++;
    assert.equal(g.xlwConsumeEnergy(2, isPlayer), false); tests++;
    assert.equal(await g.xlwChargeEnergy(NaN, isPlayer), 0); tests++;
    g.xlwSetFactionFieldCard({ id: 'R-STP-0025', name: '超載能源場' }, isPlayer);
    assert.equal(g.xlwGetMaxSteamEnergy(isPlayer), 6);
    assert.equal(g.xlwGetMaxSteamEnergy(!isPlayer), 5); tests++;
    g.xlwSetFactionFieldCard({ id: 'R-STP-0054', name: '解放能源廠' }, isPlayer);
    assert.equal(g.xlwGetMaxSteamEnergy(isPlayer), 4);
    assert.equal((isPlayer ? g.graveyard : g.XLW_ENEMY.grave)[0].id, 'R-STP-0025'); tests++;
    assert.equal(g.xlwConsumeEnergy(3, isPlayer), true);
    assert.equal(g[key], 0); tests++;
    delete elements[isPlayer ? 'playerField' : 'enemyField'].dataset.card;
    assert.equal(g.xlwGetMaxSteamEnergy(isPlayer), 5); tests++;
    // Two charging sources must terminate, finish before return, and re-arm for a new event.
    const zone = isPlayer ? 'player_front' : 'enemy_front';
    g.field[zone][0] = { card: { id: 'R-STP-0052', name: '蒸汽充能塔' } };
    g.field[zone][1] = { card: { id: 'OTHER', name: '裝備單位' }, equipments: ['通電道具 通電裝'] };
    await g.xlwChargeEnergy(1, isPlayer);
    assert.equal(g[key], 5); assert.equal(g.XLW_electrifyChargeSources, null); tests++;
    g.field[zone][1] = null; g[key] = 0;
    await g.xlwChargeEnergy(1, isPlayer);
    assert.equal(g[key], 3); tests++;
    g[key] = 0;
    await g.xlwChargeEnergy(1, isPlayer);
    assert.equal(g[key], 3); tests++;
    g.xlwTriggerElectrify = async () => { throw Error('presentation error'); };
    await assert.rejects(g.xlwChargeEnergy(1, isPlayer), /presentation error/);
    assert.equal(g.XLW_electrifyChargeSources, null); tests++;
  }
  {
    const { g } = fixture(), { g: peer } = fixture();
    g.XLW_playerSteamEnergy = 4; g.XLW_enemySteamEnergy = 2;
    g.XLW_playerBlackHoleLane = 3; g.XLW_enemyBlackHoleLane = 1;
    g.XLW_banishedTimeGoats = [{ card: { id: 'GOT-0051' }, isPlayer: true }];
    const state = g.xlwCaptureFactionState();
    peer.xlwRestoreFactionState(state, true);
    assert.equal(peer.XLW_playerSteamEnergy, 2); assert.equal(peer.XLW_enemySteamEnergy, 4);
    assert.equal(peer.XLW_playerBlackHoleLane, 1); assert.equal(peer.XLW_enemyBlackHoleLane, 3);
    assert.equal(peer.XLW_banishedTimeGoats[0].isPlayer, false); tests++;
    peer.XLW_banishedTimeGoats[0].card.id = 'CHANGED';
    assert.equal(state.banishedTimeGoats[0].card.id, 'GOT-0051'); tests++;
    g.xlwResetFactionState();
    assert.equal(g.XLW_playerSteamEnergy + g.XLW_enemySteamEnergy + g.XLW_playerBlackHoleLane + g.XLW_enemyBlackHoleLane, 0);
    assert.equal(g.XLW_banishedTimeGoats.length, 0); tests++;
    g.xlwRestoreFactionState(state);
    assert.equal(g.XLW_playerSteamEnergy, 4); assert.equal(g.XLW_playerBlackHoleLane, 3); tests++;
    g.xlwRestoreFactionState({ playerEnergy: NaN, enemyEnergy: -1 });
    assert.equal(g.XLW_playerSteamEnergy, 4); assert.equal(g.XLW_enemySteamEnergy, 2); tests++;
  }
  {
    const { g } = fixture();
    g.XLW_playerBlackHoleLane = 2;
    g.field.player_front[0] = { card: { id: 'GOT-0001' } };
    for (let i = 0; i < 3; i++) g.field.enemy_front[i] = { card: { id: 'GOT-0002' } };
    await g.xlwCheckBlackHoleGoatProgress(true);
    assert.equal(g.XLW_playerBlackHoleLane, 3); tests++;
  }
  for (const isPlayer of [true, false]) {
    const { g } = fixture(); const sent = [], results = [];
    g.isGameOverFlag = false; g.isMultiplayer = true;
    g.WebSocket = { OPEN: 1 }; g.ws = { readyState: 1, send: raw => sent.push(JSON.parse(raw)) };
    g.triggerCallGameEnd = (winner, reason) => { results.push({ winner, reason }); g.isGameOverFlag = true; };
    const laneKey = isPlayer ? 'XLW_playerBlackHoleLane' : 'XLW_enemyBlackHoleLane';
    g[laneKey] = 4;
    for (let i = 0; i < 4; i++) { g.field.player_front[i] = { card: { id: 'GOT-0001' } }; g.field.enemy_front[i] = { card: { id: 'GOT-0002' } }; }
    await g.xlwCheckBlackHoleGoatProgress(isPlayer);
    g.xlwFinishBlackHoleVictory(isPlayer);
    assert.equal(g[laneKey], 5); assert.equal(results.length, 1); assert.equal(sent.length, 1);
    assert.equal(sent[0].specialWinner, isPlayer ? 'player' : 'enemy'); tests++;
  }
  {
    const { g } = fixture();
    const goat = { id: 'GOT-0011', name: '藍山羊' }; g.deck = [goat];
    g.showXLWChoiceModal = async (a, b, options) => options[0].value;
    g.shuffle = () => {};
    const a = source.indexOf('  // 🐱🐐 喵山羊 (GOT-0015): 偷竊。');
    const b = source.indexOf('  // (a-彩虹)', a);
    vm.runInContext('async function searchGoat(card) {' + source.slice(a, b) + '}', g);
    await g.searchGoat({ id: 'GOT-0015', name: '喵山羊' });
    assert.equal(g.hand[0], goat); assert.equal(g.deck.length, 0); tests++;
  }
  for (const isPlayer of [true, false]) {
    const { g } = fixture(); const zone = isPlayer ? 'player_front' : 'enemy_front';
    g.unit = { card: { id: 'GOT-0040', name: '火圈山羊', attack: '3', score: 2 } }; g.t = { zone, idx: 0 };
    g.field[zone][0] = g.unit; g.field[zone][1] = { card: { id: 'OTHER', name: '原單位' } };
    g.isUnitMagicImmune = () => false; g.xlwCheckGoatResearcherTrigger = async () => {};
    g.showXLWConfirm = async () => true; g.showXLWChoiceModal = async () => 0;
    const a = source.indexOf('        // 🐐 GOT-0040 火圈山羊:');
    const b = source.indexOf('        // 🍬 CND-0003', a);
    vm.runInContext('async function tributeHook() {' + source.slice(a, b) + '}', g);
    await g.tributeHook();
    assert.equal(g.field[zone][1].card.id, 'GOT-0040');
    assert.equal((isPlayer ? g.graveyard : g.XLW_ENEMY.grave)[0].id, 'OTHER'); tests++;
  }
  // Validate every shipped deck reference against the actual catalogue.
  const cards = JSON.parse(fs.readFileSync(path.join(root, 'data/cards.json'), 'utf8'));
  const ids = new Set(cards.map(c => c.id));
  for (const file of ['data/decks.json', 'static/decks.json']) {
    const decks = JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
    for (const [name, list] of Object.entries(decks)) {
      for (const id of list) assert.ok(ids.has(id), `${name}: missing ${id}`);
    }
    tests++;
  }
  console.log(`${tests} faction field, energy, bounded charge chains, reset, mirrored snapshot and catalogue checks: PASS`);
})();
