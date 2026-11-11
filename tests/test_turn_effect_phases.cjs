const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/game_v8.js'), 'utf8');
const start = source.indexOf('window.xlwResolveTurnStartEffects =');
const end = source.indexOf('// Functionally implemented keyword-only', start);
const effectSource = source.slice(start, end);
let tests = 0;
function fixture() {
  const field = Object.fromEntries(['player_front','player_back','enemy_front','enemy_back'].map(z => [z, Array(5).fill(null)]));
  const g = {
    field, hand: [], deck: [], graveyard: [], enemyGraveyard: [], playerExtraDeck: [], enemyExtraDeck: [],
    $: () => null,
    allCards: [], turn: 4, isMultiplayer: true, playerBonusScore: 0, enemyBonusScore: 0,
    structuredClone, logBattle() {}, render() {}, renderScore() {}, renderExtraDecks() {},
    setStatus() {}, xlwCheckBananaMarquisMovement: async () => {},
    shuffle() {}, showXLWConfirm: async () => true, showXLWChoiceModal: async () => 0,
    isUnitSilenced: () => false, isDemonUnit: () => false, isTreasureUnit: () => false,
    xlwGetEmptyPlayerSlots: () => [], xlwGetEmptyEnemySlots: () => [],
    xlwTriggerMaskTaunt: async () => {}, xlwTriggerSageEffect: async () => {},
    xlwCardHasKeyword: (card, word) => (card.keywords || []).includes(word),
    xlwSpecialSummonUnit: async () => {},
    destroyUnit: async (z, i) => { field[z][i] = null; }
  };
  g.window = g;
  g.XLW_ENEMY = { hand: [], deck: [], grave: [] };
  g.document ||= { getElementById: () => null }; vm.createContext(g);vm.runInContext(source.slice(source.indexOf("// Faction state uses"), source.indexOf("// ===== 6. 召喚與獻祭召喚系統 =====", source.indexOf("// Faction state uses"))),g);
  vm.runInContext(effectSource, g);
  return g;
}
module.exports = (async () => {
  for (const side of [true, false]) {
    let g = fixture();
    await g.xlwResolveTurnStartEffects(side);
    tests++;
    const prefix = side ? 'player_' : 'enemy_';
    g = fixture();
    const portal = { card: { id: 'BRV-0046', name: '傳送門' } };
    const npc = { card: { id: 'BRV-0045', name: '傳送門NPC' } };
    const monster = { card: { id: 'BRV-0020', name: '這個怪物' } };
    g.field[prefix + 'front'][0] = portal;
    g.field[prefix + 'front'][1] = npc;
    g.field[prefix + 'back'][0] = monster;
    await g.xlwResolveTurnStartEffects(side);
    assert.equal(g.field[prefix + 'front'][0], portal);
    assert.equal(g.field[prefix + 'back'][0], monster);
    assert.equal(g.playerExtraDeck.length + g.enemyExtraDeck.length, 0);
    tests++;
    await g.xlwResolveEndPhaseEffects(side);
    assert.equal(g.field[prefix + 'front'][0], null);
    assert.equal(g.field[prefix + 'front'][1], npc);
    assert.equal(g.field[prefix + 'back'][0], null);
    assert.equal((side ? g.playerExtraDeck : g.enemyExtraDeck)[0], portal.card);
    tests++;
  }
  for (const side of [true, false]) {
    const g = fixture();
    const theater = { id: 'CCS-0029' };
    const wheelKey = side ? 'XLW_playerRouletteWheel' : 'XLW_enemyRouletteWheel';
    g[wheelKey] = [{}, {}];
    g.xlwGetFactionFieldCard = player => player === side ? theater : null;
    let calls = 0;
    g.xlwSpinWheel = async (player, times, card) => {
      assert.equal(player, side);
      assert.equal(times, 1);
      assert.equal(card, theater);
      calls++;
    };
    await g.xlwResolveTurnStartEffects(side);
    assert.equal(calls, 0);
    g[wheelKey].push({});
    await g.xlwResolveTurnStartEffects(side);
    await g.xlwResolveTurnStartEffects(side);
    assert.equal(calls, 1);
    g.turn += 2;
    await g.xlwResolveTurnStartEffects(side);
    assert.equal(calls, 2);
    tests++;
  }
  const drawStart = source.indexOf('async function performPlayerTurnStartDraw()');
  const drawEnd = source.indexOf('// 全局玩家點選牌組抽牌處理函式', drawStart);
  for (const online of [false, true]) {
    const g = fixture();
    g.isMultiplayer = online;
    g.deck.push({ id: 'TEST-1', name: '測試一' }, { id: 'TEST-2', name: '測試二' });
    vm.runInContext(source.slice(drawStart, drawEnd), g);
    await g.performPlayerTurnStartDraw();
    assert.equal(g.hand.length, 2);
    assert.equal(g.deck.length, 0);
    if (online) {
      await g.performPlayerTurnStartDraw();
      assert.equal(g.hand.length, 2);
    }
    tests++;
  }
  // The God Eye replacement uses the normal draw list without a second draw.
  for (const accept of [false, true]) {
    const g = fixture();
    g.isMultiplayer = false;
    g.showXLWConfirm = async () => accept;
    g.field.player_front[0] = { card: { id: 'R-RBT-0060' }, devourCards: [{}] };
    g.deck.push(...['search', 'spare', 'normal', 'top'].map(id => ({ id, name: id })));
    vm.runInContext(source.slice(drawStart, drawEnd), g);
    await g.performPlayerTurnStartDraw();
    assert.equal(g.deck.length, 2);
    assert.deepEqual(g.hand.map(card => card.id).sort(), accept ? ['search', 'top'] : ['normal', 'top']);
    tests++;
  }
  for (const commander of ['absent', 'active', 'silenced']) {
    const g = fixture(); g.isMultiplayer = false;
    g.field.player_front[0] = { card: { id: 'SLIDER', name: '滑行單位', keywords: ['滑行'] }, tapped: true };
    if (commander !== 'absent') g.field.player_back[0] = { card: { id: 'R-STP-0039', name: '奧麗' }, silenced: commander === 'silenced' };
    g.isUnitSilenced = u => Boolean(u.silenced);
    vm.runInContext(source.slice(drawStart, drawEnd), g); await g.performPlayerTurnStartDraw();
    assert.equal(g.field.player_front[0].tapped, commander !== 'active');
    assert.equal(g.XLW_playerSteamEnergy, commander === 'active' ? 1 : 0); tests++;
  }
  console.log(`${tests} bidirectional turn-start crash and end-phase timing checks: PASS`);
})();
