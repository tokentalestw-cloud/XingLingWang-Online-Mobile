const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..');const global={};vm.runInNewContext(fs.readFileSync(path.join(root,'static/turn_order.js'),'utf8'),{window:global,Uint8Array});
const create=global.XLWTurnOrder.createController;let tests=0;
for(const swap of [0,1])for(const selected of [0,1])for(const choice of ['first','second']){
 const started=[];const c=create({random:()=>swap,onStart:first=>started.push(first)});assert.equal(c.pick(selected),false);c.ready();assert.equal(c.pick(selected),true);assert.equal(c.pick(1-selected),false);const winner=selected===swap?'player1':'player2';assert.equal(c.snapshot().winner,winner);if(winner==='player1')c.choose(choice);else{assert.equal(c.choose(choice),false);c.chooseAI(choice);}assert.deepEqual(started,[(winner==='player1')===(choice==='first')]);assert.equal(c.confirm({draw_id:'single',first_role:'player1'}),false);tests++;
}
for(const winner of ['player1','player2'])for(const first of ['player1','player2']){
 const clients=[];
 for(const role of ['player1','player2']){const sent=[],started=[];const c=create({role,multi:true,send:m=>sent.push(m),onStart:value=>started.push(value)});c.ready();if(role==='player1'){c.pick(0);assert.equal(sent[0].action,'turn_order_pick');}else assert.equal(c.pick(0),false);c.reveal({selected:0,winner_role:winner,draw_id:'draw'});assert.equal(c.choose('first'),role===winner);assert.equal(c.confirm({draw_id:'wrong',first_role:first}),false);c.confirm({draw_id:'draw',first_role:first});assert.deepEqual(started,[role===first]);c.confirm({draw_id:'draw',first_role:first});assert.equal(started.length,1);clients.push(c);}assert.notEqual(clients[0].snapshot().firstRole===clients[0].snapshot().role,clients[1].snapshot().firstRole===clients[1].snapshot().role);tests++;
}
for(const stage of ['pending','choice','confirming','done']){let started=0;const c=create({role:'player1',multi:true,onStart:()=>started++});assert.equal(c.restore({role:'player1',multi:true,stage,drawId:'saved',winner:'player1',selected:1}),true);assert.equal(c.snapshot().stage,stage);assert.equal(started,0);assert.equal(c.pick(0),false);tests++;}
assert.equal(create({multi:true}).restore({role:'player2',multi:true,stage:'choice'}),false);tests++;
new vm.Script(fs.readFileSync(path.join(root,'static/game_v8.js'),'utf8'));
console.log(`${tests} turn-order selection, authority, perspective and recovery scenarios: PASS`);
