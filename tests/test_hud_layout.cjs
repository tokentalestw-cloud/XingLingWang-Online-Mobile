const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../static/game_v8.js'), 'utf8');
const start = source.indexOf('window.xlwShowPhaseBanner = async function');
const end = source.indexOf('// 節奏校準', start);
assert(start >= 0 && end > start, 'Locate the production banner function');
const attributes = {};
const banner = { style: {}, dataset: {}, offsetWidth: 10,
  setAttribute: (key, value) => { attributes[key] = value; } };
const context = vm.createContext({ window: {}, isMyTurn: true,
  document: { getElementById: () => banner }, setTimeout: callback => callback() });
vm.runInContext(source.slice(start, end), context);
module.exports = (async () => {
  const cases = [
    [true, '召喚階段', 'player', '我方召喚階段'],
    [false, '召喚階段', 'enemy', '對手召喚階段'],
    [true, '對手召喚階段', 'enemy', '對手召喚階段'],
    [false, '我方回合', 'player', '我方回合'],
    [true, '請點選牌組抽牌', 'player', '請點選牌組抽牌'],
    [false, '對方防守階段', 'enemy', '對手防守階段'],
  ];
  for (const [isMyTurn, text, side, expected] of cases) {
    context.isMyTurn = isMyTurn;
    // The historical stage colour is deliberately wrong: ownership must still win.
    await context.window.xlwShowPhaseBanner(text, '#ff0000');
    assert.equal(banner.dataset.side, side);
    assert.equal(banner.textContent, expected);
  }
  assert.equal(attributes.role, 'status');
  assert.equal(attributes['aria-live'], 'polite');
  console.log('6 turn-owner banner cases and accessible announcements: PASS');
})();
