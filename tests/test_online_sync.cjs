const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { randomUUID } = require('node:crypto');
const root = path.resolve(__dirname, '..');
const transportSource = fs.readFileSync(path.join(root, 'static/online_sync.js'), 'utf8');
const gameSource = fs.readFileSync(path.join(root, 'static/game_v8.js'), 'utf8');
new vm.Script(transportSource);
new vm.Script(gameSource);
const context = vm.createContext({ crypto: { randomUUID }, console, Date, Promise, Set, Map });
vm.runInContext(transportSource, context);
const Sync = context.XLWOnlineSync;
function socket() {
  return { readyState: 1, sent: [], send(value) { this.sent.push(JSON.parse(value)); } };
}
function storage() {
  const items = new Map();
  return { getItem: k => items.get(k) || null, setItem: (k, v) => items.set(k, v) };
}
function incoming(sock, data) { sock.onmessage({ data: JSON.stringify(data) }); }
function create(process, options = {}) {
  const errors = [], checkpoints = [];
  let sync;
  sync = new Sync({ key: 'room', storage: storage(), process,
    checkpoint: () => checkpoints.push(sync.metadata()), fail: error => errors.push(error), ...options });
  const sock = socket();
  sync.attach(sock);
  sync.epoch = 'e';
  sync.ready = true;
  return { sync, sock, errors, checkpoints };
}
const tick = async () => { for (let i = 0; i < 20; i++) await Promise.resolve(); };

module.exports = (async () => {
  let tests = 0;
  // A slow animation/choice must finish before a following snapshot is applied.
  let release;
  const order = [];
  let client = create(async data => {
    order.push(data.action + ':start');
    if (data.action === 'summon') await new Promise(resolve => { release = resolve; });
    order.push(data.action + ':end');
  });
  incoming(client.sock, { action: 'summon', epoch: 'e', server_seq: 1 });
  incoming(client.sock, { action: 'sync_game_state', epoch: 'e', server_seq: 2 });
  await tick();
  assert.deepEqual(order, ['summon:start']);
  assert.equal(client.sync.processing, 1);
  release(); await client.sync.tail;
  assert.deepEqual(order, ['summon:start', 'summon:end', 'sync_game_state:start', 'sync_game_state:end']);
  assert.equal(client.sync.cursor, 2); tests++;

  // Duplicate replays cannot execute a card effect twice.
  incoming(client.sock, { action: 'summon', epoch: 'e', server_seq: 1 });
  await tick(); assert.equal(order.length, 4); tests++;

  // A true response can release a promise in the active handler without deadlock.
  let done;
  client = create(async data => {
    if (data.action === 'wait') await new Promise(resolve => { done = resolve; });
    if (data.action === 'response') done();
  }, { canBypass: action => action === 'response' });
  incoming(client.sock, { action: 'wait', epoch: 'e', server_seq: 1 });
  await tick();
  incoming(client.sock, { action: 'response', epoch: 'e', server_seq: 2 });
  await client.sync.tail;
  assert.equal(client.sync.cursor, 2); assert.equal(client.sync.processing, 0); tests++;

  // Lost acknowledgements retain the same message ID when retried.
  client = create(async () => {});
  client.sock.send(JSON.stringify({ action: 'end_turn', next_turn: 2 }));
  const id = client.sock.sent[0].message_id;
  client.sync.resend();
  assert.equal(client.sock.sent[1].message_id, id);
  incoming(client.sock, { type: 'delivery_ack', message_id: id });
  assert.equal(client.sync.pending.size, 0); tests++;

  // Old socket messages are ignored; reconnect resumes with the committed cursor.
  incoming(client.sock, { action: 'x', epoch: 'e', server_seq: 1 });
  await client.sync.tail;
  const old = client.sock, next = socket();
  client.sync.attach(next);
  incoming(old, { action: 'stale', epoch: 'e', server_seq: 2 });
  incoming(next, { type: 'welcome', sync_protocol: 2 });
  await tick();
  assert.equal(next.sent[0].cursor, 1);
  assert.equal(client.sync.cursor, 1); tests++;

  // Unknown epochs pause rather than overwriting a live game.
  incoming(next, { action: 'x', epoch: 'other', server_seq: 2 });
  await client.sync.tail;
  assert.equal(client.errors.length, 1); assert.equal(client.sync.ready, false); tests++;

  // Unacknowledged operations survive a page reload.
  const disk = storage();
  client = create(async () => {}, { storage: disk });
  client.sock.send(JSON.stringify({ action: 'attack_declare' }));
  const reloaded = create(async () => {}, { storage: disk });
  assert.equal(reloaded.sync.pending.size, 1); tests++;

  // Exercise the actual game receive handler, not a duplicate implementation.
  const handlerStart = gameSource.indexOf('  ws.onmessage = async (event) => {');
  const handlerEnd = gameSource.indexOf('  const gameMessageHandler = ws.onmessage;', handlerStart);
  const handler = gameSource.slice(handlerStart, handlerEnd);
  const fields = { player_front: Array(5).fill(null), player_back: Array(5).fill(null),
    enemy_front: Array(5).fill(null), enemy_back: Array(5).fill(null) };
  const globals = {
    ws: {}, window: { XLW_ENEMY: {}, XLW_DEFENSE_RULE: {}, xlwEnterActiveOnlineBoardUI() {} },
    document: { getElementById: () => null }, console: { log() {}, error() {} },
    field: structuredClone(fields), hand: [{ id: 'old-hand' }], deck: [{ id: 'old-deck' }],
    graveyard: [], enemyGraveyard: [], playerExileZone: [], enemyExileZone: [],
    playerExtraDeck: [], enemyExtraDeck: [], playerBonusScore: 0, enemyBonusScore: 0,
    turn: 1, phase: '召喚階段', isMyTurn: false, normalSummonUsed: false, tacticalSummonUsed: false,
    opponent_mulligan_done: false, battleLog: [], isGameOverFlag: false,
    xlwExpectedIncomingSeq: null, saveLocalGameState() {}, render() {}, logBattle() {},
    countdownActive: false, countdownRemaining: 0, countdownTriggerTurn: null, countdownTriggerRole: null,
  };
  const game = vm.createContext(globals);
  vm.runInContext(handler, game);
  const remoteField = structuredClone(fields);
  remoteField.enemy_front[0] = { card: { id: 'goat', creator: 'player' },
    summonedZone: 'enemy_front', target: { zone: 'player_back', idx: 2 },
    kidnappedCards: [{ id: 'captive', originalOwner: 'enemy' }] };
  const snapshot = {
    field: remoteField, enemyHand: [], enemyDeck: [], playerHand: [], playerDeck: [],
    playerBonusScore: 3, enemyBonusScore: 7, XLW_coinTossFirstGo: false,
    includeTurnPhase: true, isMyTurn: true, phase: '戰術佈陣', turn: 4, mulliganDone: true,
  };
  await game.ws.onmessage({ data: JSON.stringify({ action: 'sync_game_state', state: snapshot }) });
  assert.equal(game.hand.length, 0); assert.equal(game.deck.length, 0);
  assert.equal(game.field.player_front[0].card.creator, 'enemy');
  assert.equal(game.field.player_front[0].target.zone, 'enemy_back');
  assert.equal(game.field.player_front[0].kidnappedCards[0].originalOwner, 'player');
  assert.equal(game.window.XLW_coinTossFirstGo, true);
  assert.equal(game.playerBonusScore, 7); assert.equal(game.enemyBonusScore, 3);
  assert.equal(game.isMyTurn, false); assert.equal(game.turn, 4);
  assert.equal(game.opponent_mulligan_done, true); tests++;

  // An unknown (placeholder) opponent hand must not erase actual local cards.
  game.hand = [{ id: 'keep' }]; snapshot.enemyHand = [null];
  await game.ws.onmessage({ data: JSON.stringify({ action: 'sync_game_state', state: snapshot }) });
  assert.equal(game.hand[0].id, 'keep'); tests++;

  // Coordinates for temporary equipment have already been flipped by the server.
  game.field.enemy_back[1] = { card: { name: 'target' } };
  await game.ws.onmessage({ data: JSON.stringify({ action: 'temp_equip_spell_resolved', zone: 'enemy_back', idx: 1,
    spellCard: { name: 'test', id: 'test' }, currentTurn: 4 }) });
  assert.equal(game.field.enemy_back[1].equipments[0], 'test'); tests++;
  // A second error/close notification must not cancel the only reconnect timer.
  const reconnectStart = gameSource.indexOf('function reconnectWebSocket(immediate = false) {');
  const reconnectEnd = gameSource.indexOf('// ===== 23.1', reconnectStart);
  let scheduled = 0, cancelled = 0;
  const reconnectContext = vm.createContext({
    isReconnecting: false, reconnectTimer: null, room_id: 'r', player_id: 'p', player_role: 'player1',
    window: {}, ws: null, console: { log() {} }, setStatus() {},
    setTimeout() { scheduled++; return scheduled; }, clearTimeout() { cancelled++; },
  });
  vm.runInContext(gameSource.slice(reconnectStart, reconnectEnd), reconnectContext);
  vm.runInContext('reconnectWebSocket(); reconnectWebSocket();', reconnectContext);
  assert.equal(scheduled, 1); assert.equal(cancelled, 0); tests++;

  // Twelve seconds of latency must not invent a "no counter" decision.
  const promiseStart = gameSource.indexOf('  const response = await new Promise(resolve => {', gameSource.indexOf('async function castSpellChain('));
  const promiseEnd = gameSource.indexOf('\n  });', promiseStart) + 6;
  let timer;
  const waiting = vm.createContext({ window: {}, isMultiplayer: true, console: { log() {} },
    setStatus() {}, setTimeout(callback) { timer = callback; } });
  vm.runInContext(gameSource.slice(promiseStart, promiseEnd).replace('const response = await', 'result ='), waiting);
  const resolver = waiting.window.XLW_pendingSpellResolve;
  timer();
  assert.equal(waiting.window.XLW_pendingSpellResolve, resolver);
  resolver({ countered: true });
  assert.equal((await waiting.result).countered, true); tests++;

  // Failure still allows a clean exit, instead of trapping both players in the room.
  client = create(async () => {});
  client.sync.stop(new Error('test'));
  client.sock.send(JSON.stringify({ action: 'leave_room' }));
  assert.equal(client.sock.sent.at(-1).action, 'leave_room'); tests++;

  // The receiving player applies turn-start effects once, then sends the result back.
  let untaps = 0, broadcasts = 0;
  Object.assign(game, { xlwCleanExpiredTempEquips() {}, playerUntap() { untaps++; }, checkCallGameAtTurnStart() {},
    sendFullGameStateToOpponent() { broadcasts++; }, setStatus() {} });
  game.window.xlwShowPhaseBanner = () => {};
  game.window.XLW_DEFENSE_RULE.playerNeedsDefense = false;
  await game.ws.onmessage({ data: JSON.stringify({ action: 'end_turn', next_turn: 5 }) });
  assert.equal(untaps, 1); assert.equal(broadcasts, 1); assert.equal(game.isMyTurn, true); tests++;
  // Local state is committed before an operation can reach the peer.
  client = create(async () => {});
  let committed = 0;
  client.sync.checkpoint = () => { assert.equal(client.sock.sent.length, 0); committed++; };
  client.sock.send(JSON.stringify({ action: 'move_unit' }));
  assert.equal(committed, 1); assert.equal(client.sock.sent.length, 1); tests++;

  // Failed persistence must prevent an uncheckpointed operation from being sent.
  client = create(async () => {});
  client.sync.checkpoint = () => { throw new Error('storage full'); };
  assert.throws(() => client.sock.send(JSON.stringify({ action: 'summon' })), /storage full/);
  assert.equal(client.sock.sent.length, 0); assert.equal(client.sync.failed, true); tests++;
  // Exercise the actual setup function and transport together through a complete handshake.
  const setupStart = gameSource.indexOf('function setupWebSocketEvents() {');
  const setupEnd = gameSource.indexOf('// Stop new local operations', setupStart);
  const setupSocket = socket();
  const setupContext = vm.createContext({ ws: setupSocket, room_id: 'room', player_id: 'a', player_role: 'player1',
    xlwOutgoingSeq: 0, xlwExpectedIncomingSeq: null, XLW_gameInProgress: false,
    document: { getElementById: () => null }, sessionStorage: storage(), console: { log() {}, error() {} },
    setStatus() {}, logBattle() {}, saveLocalGameState() {}, xlwSaveOnlineSession() {}, reconnectWebSocket() {},
    setInterval() { return 1; }, clearInterval() {}, WebSocket: { OPEN: 1 }, crypto: { randomUUID },
    dispatchEvent() {}, Event: class {},
  });
  vm.runInContext('window = globalThis;', setupContext);
  vm.runInContext(transportSource, setupContext);
  vm.runInContext(gameSource.slice(setupStart, setupEnd), setupContext);
  setupContext.setupWebSocketEvents();
  setupSocket.onopen();
  incoming(setupSocket, { type: 'welcome', sync_protocol: 2, role: 'player1', message: 'welcome' });
  incoming(setupSocket, { type: 'resume_complete', epoch: 'room-epoch' });
  await setupContext.XLW_sync.tail;
  assert.equal(setupContext.XLW_sync.ready, true);
  assert.equal(setupSocket.sent[0].action, 'resume_delivery');
  incoming(setupSocket, { action: 'battle_log', message: 'ok', epoch: 'room-epoch', server_seq: 1 });
  await setupContext.XLW_sync.tail;
  assert.equal(setupContext.XLW_sync.cursor, 1);
  setupSocket.send(JSON.stringify({ action: 'attack_declare' }));
  assert.equal(typeof setupSocket.sent.at(-1).message_id, 'string'); tests++;
  console.log(`${tests} JavaScript synchronization regression tests: PASS`);
})();
