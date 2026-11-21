const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const {randomUUID} = require("node:crypto");
const root = path.resolve(__dirname, "..");
const game = fs.readFileSync(path.join(root, "static/game_v8.js"), "utf8");
function ui() {
  let now = 0, serial = 0;
  const timers = new Map();
  class Node {
    constructor(tag) { this.tag = tag; this.children = []; this.textContent = ""; this.attrs = {}; }
    setAttribute(k, v) { this.attrs[k] = v; }
    append(...nodes) { for (const n of nodes) { n.parent = this; this.children.push(n); } }
    remove() { this.parent.children = this.parent.children.filter(n => n !== this); }
    focus() { document.activeElement = this; }
    querySelectorAll(tag) { return this.children.flatMap(n => [...(n.tag === tag ? [n] : []), ...n.querySelectorAll(tag)]); }
  }
  const document = {body: new Node("body"), createElement: tag => new Node(tag), addEventListener() {}, removeEventListener() {}};
  const scope = {window: {}, document, Date: {now: () => now},
    setInterval: fn => {timers.set(++serial, {fn, due: 0}); return serial;},
    setTimeout: (fn, ms) => {timers.set(++serial, {fn, due: now + ms}); return serial;},
    clearTimeout: id => timers.delete(id), clearInterval: id => timers.delete(id)};
  vm.runInNewContext(fs.readFileSync(path.join(root, "static/summon_reaction.js"), "utf8"), scope);
  return {reaction: scope.window.XLWSummonReaction, document, timers, advance(ms) { now += ms; for (const timer of [...timers.values()]) if (timer.due <= now) timer.fn(); }};
}
test("Summon reaction shares a 15-second deadline across confirmation and target selection", async () => {
  const c = ui(), card = {id: "summon", name: "雪女", attack: 6, score: 5, tribute: 2, effect_text: "完整效果", image: "/card.jpg"};
  c.reaction.begin(card);
  const confirm = c.reaction.confirm("星空", "是否反制");
  const overlay = c.document.body.children[0];
  assert.ok(overlay.querySelectorAll("img").some(n => n.src === "/card.jpg"));
  assert.ok(overlay.querySelectorAll("p").some(n => n.textContent === "完整效果"));
  c.advance(14000);
  overlay.querySelectorAll("button")[0].onclick();
  assert.equal(await confirm, true);
  const choose = c.reaction.choose("小陷阱目標", "選擇目標", [{text: "目標", card, value: 0}]);
  c.advance(1001);
  assert.equal(await choose, null);
  assert.equal(c.document.body.children.length, 0);
  assert.equal(c.timers.size, 0);
  assert.equal(await c.reaction.confirm("後續反制", "期限已過"), false);
});
test("Closing a reaction cleans its timer and a late tap cannot activate it", async () => {
  const c = ui();
  c.reaction.begin({id: "a"});
  const waiting = c.reaction.confirm("反制", "說明");
  const button = c.document.body.children[0].querySelectorAll("button")[0];
  c.advance(15000);
  button.onclick();
  assert.equal(await waiting, false);
  assert.equal(c.timers.size, 0);
  c.reaction.begin({id: "b"});
  const next = c.reaction.confirm("第二張", "說明");
  c.reaction.end();
  assert.equal(await next, false);
  assert.equal(c.document.body.children.length, 0);
});
test("A delayed counter answer cannot settle another summon request", () => {
  const start = game.indexOf('    } else if (data.action === "counter_summon_response") {');
  const end = game.indexOf('    } else if (data.action === "samurai_recover_request") {', start);
  const scope = {window: {XLW_pendingSummonRequestId: "second"}};
  const replies = [];
  scope.window.XLW_pendingSummonCounterResolve = data => replies.push(data);
  vm.createContext(scope);
  vm.runInContext("function receive(data) { if(false) {} " + game.slice(start, end).replace(/^\s*}/, "") + "}}", scope);
  scope.receive({action: "counter_summon_response", summonRequestId: "first", countered: true});
  assert.equal(replies.length, 0);
  scope.receive({action: "counter_summon_response", summonRequestId: "second", countered: false});
  assert.equal(replies.length, 1);
  assert.equal(scope.window.XLW_pendingSummonCounterResolve, null);
});
test("A 500-message late-game burst checkpoints once and acknowledges only durable applied state", async () => {
  const scope = {crypto: {randomUUID}, console, Date, Promise, Set, Map};
  vm.runInNewContext(fs.readFileSync(path.join(root, "static/online_sync.js"), "utf8"), scope);
  let applied = 0, checkpoints = 0, saved = 0;
  const messages = [];
  const sync = new scope.XLWOnlineSync({key: "burst", storage: {getItem() {return null;}, setItem() {}},
    process: async () => {applied++;}, checkpoint: () => {checkpoints++; saved = applied;},
    fail: message => {throw new Error(message);}});
  const socket = {readyState: 1, send(raw) { const data = JSON.parse(raw); messages.push(data);
    if (data.action === "delivery_applied") assert.equal(saved, applied); }};
  sync.attach(socket);
  sync.epoch = "e"; sync.ready = true;
  for (let i = 1; i <= 500; i++) socket.onmessage({data: JSON.stringify({action: "update", server_seq: i, epoch: "e"})});
  await sync.tail;
  assert.equal(applied, 500);
  assert.equal(checkpoints, 1);
  assert.equal(sync.cursor, 500);
  assert.equal(messages.filter(m => m.action === "delivery_applied").length, 1);
});

test("A counter boundary preserves the summoned unit continuation but applies destruction", () => {
  const start = game.indexOf("function xlwMergeSummonBoundaryRow(");
  const end = game.indexOf("function setupWebSocketEvents(", start);
  const scope = vm.createContext({});
  vm.runInContext(game.slice(start, end), scope);
  const summoned = {card: {id: "snow", _xlwInstanceId: "live"}, summonedTurn: 4};
  const incoming = structuredClone(summoned);
  incoming.bonusAtk = 2;
  assert.equal(scope.xlwMergeSummonBoundaryRow([summoned], [incoming])[0], summoned);
  assert.equal(summoned.bonusAtk, 2);
  assert.equal(scope.xlwMergeSummonBoundaryRow([summoned], [null])[0], null);
  const replacement = {card: {id: "snow", _xlwInstanceId: "other"}};
  assert.equal(scope.xlwMergeSummonBoundaryRow([summoned], [replacement])[0], replacement);
});
