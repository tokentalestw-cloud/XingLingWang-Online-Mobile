const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../static/game_v8.js'), 'utf8');
const start = source.indexOf('function xlwFitBoardRect(');
const end = source.indexOf('\nlet xlwBoardFitFrame', start);
const context = vm.createContext({});
vm.runInContext(source.slice(start, end), context);
const bounds = {left:-102, right:1094, top:128, bottom:934};
const space = {left:174, right:670, top:30, bottom:320};
const scenarios = [
  null,
  {left:680,right:836,top:8,bottom:37},
  {left:536,right:836,top:8,bottom:37},
  {left:536,right:836,top:8,bottom:65},
  {left:580,right:836,top:8,bottom:37},
  {left:710,right:836,top:8,bottom:120}
];
for (const toolbar of scenarios) {
  const f = context.xlwFitBoardAroundToolbar(bounds, space, toolbar, 8);
  const r = {left:f.x+bounds.left*f.scale,right:f.x+bounds.right*f.scale,
    top:f.y+bounds.top*f.scale,bottom:f.y+bounds.bottom*f.scale};
  assert(r.left>=space.left-1e-6 && r.right<=space.right+1e-6);
  assert(r.top>=space.top-1e-6 && r.bottom<=space.bottom+1e-6);
  if(toolbar) assert(r.right<=toolbar.left-8+1e-6 || r.top>=toolbar.bottom+8-1e-6 || r.left>=toolbar.right+8-1e-6);
  if(!toolbar || toolbar.left>=680) {
    assert(Math.abs((r.bottom-r.top)/390 - 290/390)<1e-6,
      'Reference battlefield occupies about 74% of the landscape height');
  }
}
console.log('PASS: 6 reference layout cases, full height beside toolbar and safe button clearance');
