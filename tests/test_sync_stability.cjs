const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const { randomUUID } = require('node:crypto');
const source = fs.readFileSync(path.join(__dirname, '../static/online_sync.js'), 'utf8');
let now = 10000, tests = 0;
function fixture(process = async () => {}) {
  const errors = [], checkpoints = [], items = new Map();
  const g = { crypto: { randomUUID }, structuredClone, Date: { now: () => now } };
  vm.runInNewContext(source, { window: g, Date: g.Date, Event: class {}, setTimeout, clearTimeout });
  const sync = new g.XLWOnlineSync({ key: 'stability', process,
    storage: { getItem: k => items.get(k), setItem: (k, v) => items.set(k, v) },
    checkpoint: () => checkpoints.push(sync.metadata()), fail: error => errors.push(error) });
  return { sync, errors, checkpoints };
}
function socket(onSend = () => {}) {
  return { readyState: 1, bufferedAmount: 0, sent: [], send(raw) { const m = JSON.parse(raw); this.sent.push(m); onSend(m); } };
}
const incoming = (sock, data) => sock.onmessage({ data: JSON.stringify(data) });
module.exports = (async () => {
  {
    const { sync } = fixture(), sock = socket(); sync.attach(sock);
    sock.sendObject({ action: 'move_unit', message_id: 'queued' });
    assert.equal(sock.sent.length, 0); assert.equal(sync.pending.size, 1); tests++;
    incoming(sock, { type: 'welcome', sync_protocol: 2 });
    assert.equal(sock.sent.length, 1); assert.equal(sock.sent[0].action, 'resume_delivery'); tests++;
    incoming(sock, { type: 'resume_complete', epoch: 'room' });
    assert.equal(sock.sent[1].message_id, 'queued');
    await sync.tail;
    assert.equal(sock.sent.length, 2, 'A handshake must not send pending operations twice'); tests++;
    sync.resend(false); assert.equal(sock.sent.length, 2); tests++;
    now += 3000; sync.resend(false); assert.equal(sock.sent.length, 3); tests++;
    sock.bufferedAmount = 100000; now += 3000; sync.resend(false);
    assert.equal(sock.sent.length, 3); tests++;
    sock.bufferedAmount = 0; sync.resend(false); assert.equal(sock.sent.length, 4); tests++;
    incoming(sock, { type: 'delivery_ack', message_id: 'queued' });
    assert.equal(sync.pending.size, 0); assert.equal(sync.lastAttempt.size, 0); tests++;
  }
  {
    let release; const { sync, errors } = fixture(async data => {
      if (data.action === 'wait_for_peer') await new Promise(resolve => { release = resolve; });
    });
    const old = socket(); sync.attach(old); sync.ready = true; sync.epoch = 'room';
    incoming(old, { action: 'wait_for_peer', epoch: 'room', server_seq: 1 });
    await Promise.resolve(); await Promise.resolve();
    const replacement = socket(m => { if (m.action === 'reply') release(); });
    sync.attach(replacement);
    replacement.sendObject({ action: 'reply', message_id: 'response' });
    assert.equal(replacement.sent.length, 0); tests++;
    incoming(replacement, { type: 'resume_complete', epoch: 'room' });
    assert.equal(replacement.sent[0].action, 'reply', 'Pending replies cannot wait behind the handler they unblock'); tests++;
    await sync.tail;
    assert.equal(sync.ready, true); assert.equal(sync.cursor, 1); assert.deepEqual(errors, []); tests++;
  }
  {
    let release, restored = 0;
    const { sync } = fixture(async data => {
      if (data.action === 'wait') await new Promise(resolve => { release = resolve; });
      if (data.type === 'restore_client_backup') restored++;
    });
    const old = socket(); sync.attach(old); sync.ready = true;
    incoming(old, { action: 'wait', epoch: 'room', server_seq: 1 });
    await Promise.resolve(); await Promise.resolve();
    incoming(old, { type: 'restore_client_backup', state: { sync_metadata: { epoch: 'room', cursor: 0 } } });
    sync.attach(socket()); release(); await sync.tail;
    assert.equal(restored, 0); assert.equal(sync.cursor, 1); tests++;
  }
  {
    const { sync, errors } = fixture(), sock = socket(); sync.epoch = 'old-room'; sync.attach(sock);
    sock.sendObject({ action: 'end_turn', message_id: 'stale-action' });
    incoming(sock, { type: 'resume_complete', epoch: 'different-room' });
    assert.equal(sync.failed, true); assert.equal(sock.sent.length, 0); assert.equal(errors.length, 1); tests++;
    sync.restore({ epoch: 'bad', cursor: -1 });
    assert.equal(sync.epoch, 'old-room'); tests++;
  }
  {
    const { sync, errors } = fixture(); let closed = false;
    const failed = socket(); failed.send = () => { throw Error('network interrupted'); };
    failed.close = () => { closed = true; };
    sync.attach(failed); sync.ready = true;
    assert.doesNotThrow(() => failed.sendObject({ action: 'end_turn', message_id: 'durable' }));
    assert.equal(closed, true); assert.equal(sync.ready, false); assert.equal(sync.failed, false);
    assert.equal(sync.pending.size, 1); tests++;
    const replacement = socket(); sync.attach(replacement);
    incoming(replacement, { type: 'resume_complete', epoch: 'room' }); await sync.tail;
    assert.equal(replacement.sent[0].message_id, 'durable');
    incoming(replacement, { type: 'delivery_ack', message_id: 'durable' });
    assert.equal(sync.pending.size, 0); assert.deepEqual(errors, []); tests++;
  }
  {
    const { sync } = fixture(); sync.lastPong = now - 60000;
    const sock = socket(); sync.attach(sock);
    assert.equal(sync.lastPong, now); tests++;
    sock.sendObject({ action: 'move_unit', message_id: 'resume-fail' });
    sync.originalSend = () => { throw Error('send failed while resuming'); };
    sock.close = () => {};
    incoming(sock, { type: 'resume_complete', epoch: 'room' }); await sync.tail;
    assert.equal(sync.ready, false); assert.equal(sync.wireReady, false); assert.equal(sync.pending.size, 1); tests++;
  }
  console.log(`${tests} reconnect handshake, response deadlock, retry pacing, upload backpressure and stale-backup checks: PASS`);
})();
