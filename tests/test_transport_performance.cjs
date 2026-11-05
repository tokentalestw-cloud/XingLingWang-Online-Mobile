const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { randomUUID } = require('node:crypto');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/online_sync.js'), 'utf8');
let encodes = 0;
const json = { parse: JSON.parse, stringify(value) { encodes++; return JSON.stringify(value); } };
const writes = [];
const scope = { structuredClone, crypto: { randomUUID } };
vm.runInNewContext(source, { window: scope, JSON: json, setTimeout, clearTimeout });
const sync = new scope.XLWOnlineSync({
  key: 'performance-test',
  storage: { getItem: () => null, setItem: (key, value) => writes.push([key, value]) },
  process: async () => {},
  checkpoint() {},
  fail(message) { throw Error(message); }
});
const wire = [];
const socket = { readyState: 1, send: value => wire.push(JSON.parse(value)) };
sync.attach(socket);
sync.ready = true;
sync.epoch = 'test';
const state = { field: { player_front: [{ card: { id: 'TEST' }, tapped: false }] } };
socket.sendObject({ action: 'sync_game_state', message_id: 'snapshot', state });
state.field.player_front[0].tapped = true;
sync.resend();
assert.equal(wire[0].state.field.player_front[0].tapped, false);
assert.deepEqual(wire[0], wire[1]);
assert.equal(encodes, 1);
for (let i = 0; i < 30; i++) socket.sendObject({ action: 'move_unit', message_id: 'move-' + i, idx: i % 5 });
assert.equal(encodes, 31, 'Queued snapshots must not be re-encoded for every later operation');
sync.resend();
assert.equal(encodes, 31);
for (const message of [...sync.pending.values()]) socket.onmessage({ data: JSON.stringify({ type: 'delivery_ack', message_id: message.message_id }) });
assert.equal(sync.pending.size, 0);
assert.equal(sync.encodedPending.size, 0);
assert.equal(writes.at(-1)[1], '[]');
const count = writes.length;
socket.onmessage({ data: JSON.stringify({ type: 'delivery_ack', message_id: 'snapshot' }) });
assert.equal(writes.length, count);
console.log('8 immutable snapshot, single encoding, retry, ACK cleanup and duplicate ACK performance checks: PASS');
