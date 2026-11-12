const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../static/game_v8.js'), 'utf8');
const start = source.indexOf('function xlwFitBoardRect(');
const end = source.indexOf('\nlet xlwBoardFitFrame', start);
assert(start >= 0 && end > start);
const context = vm.createContext({});
vm.runInContext(source.slice(start, end), context);
const bounds = {left: -102, top: 128, right: 792, bottom: 934};
const cases = [
  [1920, 1080, 308, 1624, 74, 934],
  [1366, 768, 252, 1118, 74, 662],
  [1280, 720, 252, 1032, 74, 614],
  [1024, 768, 174, 850, 54, 662],
  [844, 390, 174, 670, 54, 288],
  [667, 375, 174, 493, 54, 273],
  [568, 320, 174, 394, 54, 218],
  [360, 280, 174, 186, 54, 178]
];
for (const [w, h, left, right, top, bottom] of cases) {
  const space = {left, right, top, bottom};
  const {scale, x, y} = context.xlwFitBoardRect(bounds, space);
  const fitted = {left:x+bounds.left*scale, right:x+bounds.right*scale,
    top:y+bounds.top*scale, bottom:y+bounds.bottom*scale};
  const epsilon = 1e-7;
  assert(scale > 0);
  assert(fitted.left >= left-epsilon && fitted.right <= right+epsilon);
  assert(fitted.top >= top-epsilon && fitted.bottom <= bottom+epsilon);
  assert(fitted.left >= 0 && fitted.right <= w && fitted.top >= 0 && fitted.bottom <= h);
  // At least one available dimension is completely used: any larger uniform
  // scale would overlap a rail or hand. This also guards against old scale caps.
  assert(Math.abs((right-left)-(bounds.right-bounds.left)*scale) < epsilon ||
    Math.abs((bottom-top)-(bounds.bottom-bounds.top)*scale) < epsilon);
  assert(Math.abs((fitted.left+fitted.right)-(left+right)) < epsilon);
  assert(Math.abs((fitted.top+fitted.bottom)-(top+bottom)) < epsilon);
}
console.log('PASS: 8 battlefield fitting cases, bounds, uniform scale and maximum size');

const raw = {left: 0, right: 600, top: 0, bottom: 400};
const initial = {x: 300, y: 110, scale: 1};
const magnify = (obstacles, width = 1280, height = 590) =>
  context.xlwEnlargeBoardFit(initial, raw, [raw], obstacles, width, height);
const near = (a, b) => assert(Math.abs(a-b) < 0.01);
const enlarged = magnify([]);
near(enlarged.scale, 1.1);
near(enlarged.x + 300 * enlarged.scale, initial.x + 300);
near(enlarged.y + 400 * enlarged.scale, initial.y + 400);

const leftRail = {left: 0, top: 0, right: 289, bottom: 540};
const limited = magnify([leftRail]);
assert(limited.scale > 1 && limited.scale < 1.1);
assert(limited.x >= leftRail.right + 4);
near(limited.y + 400 * limited.scale, initial.y + 400);

const topHand = {left: 400, right: 800, top: 10, bottom: 96};
const topLimited = magnify([topHand]);
assert(topLimited.scale > 1 && topLimited.scale < 1.1);
assert(topLimited.y >= topHand.bottom + 4);
near(topLimited.x + 300 * topLimited.scale, initial.x + 300);
assert.equal(magnify([{left: 0, top: 0, right: 298, bottom: 540}]), initial);
console.log('PASS: 1.1x full scale, pinned center and bottom, HUD-safe fallback');
