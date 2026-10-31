const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),{randomUUID}=require('node:crypto');
const root=path.join(__dirname,'..'),flow=fs.readFileSync(path.join(root,'static/battle_flow.js'),'utf8'),transport=fs.readFileSync(path.join(root,'static/online_sync.js'),'utf8');
const g={};vm.runInNewContext(flow,{window:g});const f=g.XLWBattleFlow;let tests=0;
for(const [action,payload]of [['sneak_recall',{attZone:'enemy_front',attIdx:1}],['double_claw_choice',{attZone:'enemy_front',attIdx:1}],['foodball_choice',{zone:'player_front',idx:2}],['foodball_summon',{zone:'player_front',idx:2}],['handy_meow_move_sync',{fromZone:'player_front',fromIdx:2}]]){
 assert.equal(f.canBypass(action,payload),false);const close=f.openCombat('enemy_front',1,'player_front',2);assert.equal(f.canBypass(action,payload),true);assert.equal(f.canBypass('sync_game_state',payload),false);close();assert.equal(f.canBypass(action,payload),false);tests++;
}
const unit=()=>({card:{id:'A',name:'attacker'},summonedTurn:1,tapped:true,attacking:true,target:{zone:'enemy_front',idx:0}});
{const u=unit();f.settle(u,'player_front',0,4);assert.equal(u.tapped,true);assert.equal(u.attacking,false);assert.equal(u.target,null);const stale=unit();f.reconcile({player_front:[stale]},4);assert.equal(stale.tapped,true);assert.equal(stale.attacking,false);tests++;}
{const u=unit();f.settle(u,'player_front',0,4);const fresh={...unit(),summonedTurn:5};f.reconcile({player_front:[fresh]},4);assert.equal(fresh.attacking,true);tests++;}
{const u=unit();f.settle(u,'player_front',0,4);u.tapped=false;f.finish(u,u,'player_front',0,4);assert.equal(u.tapped,false);tests++;}
{const u=unit();f.settle(u,'player_front',0,4);const clone=unit();f.finish(u,clone,'player_front',0,4);assert.equal(clone.attacking,false);assert.equal(clone.tapped,true);tests++;}
{const u=unit();f.settle(u,'player_front',0,4);f.forgetSide('player');const next=unit();f.reconcile({player_front:[next]},5);assert.equal(next.attacking,true);tests++;}
{g.XLW_opponentSneakRecall={'enemy_front:1':false};const a=f.openCombat('enemy_front',1,'player_front',0),b=f.openCombat('enemy_front',1,'player_front',2);a();assert.equal(g.XLW_opponentSneakRecall['enemy_front:1'],false);b();assert.equal(g.XLW_opponentSneakRecall['enemy_front:1'],undefined);tests++;}
for(const [player,enemy,snapshot,expected]of [
 [false,true,{includeTurnPhase:false,XLW_enemyNeedsToDraw:true,XLW_playerNeedsToDraw:false},[false,false]],
 [false,false,{includeTurnPhase:true,XLW_enemyNeedsToDraw:true,XLW_playerNeedsToDraw:false},[true,false]],
 [true,true,{includeTurnPhase:true,XLW_enemyNeedsToDraw:false},[false,true]],
 [true,false,{},[true,false]]
]){const result=f.drawFlags(player,enemy,snapshot);assert.deepEqual([result.player,result.enemy],expected);tests++;}
module.exports=(async()=>{
 for(const reply of ['sneak_recall','double_claw_choice','foodball_choice','foodball_summon','handy_meow_move_sync']){
  const ctx={crypto:{randomUUID},console,Promise,Date,Map,Set};vm.runInNewContext(flow,ctx);vm.runInNewContext(transport,ctx);const order=[];let release,client;
  const waiting=new Promise(r=>release=r),storage={getItem:()=>null,setItem(){}};
  const sync=new ctx.XLWOnlineSync({key:'test',storage,canBypass:(action,data)=>ctx.XLWBattleFlow.canBypass(action,data),process:async data=>{if(data.action==='resolve_lane'){const close=ctx.XLWBattleFlow.openCombat('enemy_front',1,'player_front',2);order.push('waiting');await waiting;order.push('settled');close();}else if(data.action===reply){order.push('reply');release();}else order.push('snapshot');},checkpoint(){},fail:e=>{throw Error(e);}});
  const socket={readyState:1,send(){}};sync.attach(socket);sync.ready=true;sync.epoch='e';const incoming=data=>socket.onmessage({data:JSON.stringify(data)});const tick=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
  incoming({action:'resolve_lane',server_seq:1,epoch:'e'});await tick();incoming({action:'sync_game_state',server_seq:2,epoch:'e'});
  incoming({action:reply,server_seq:3,epoch:'e',attZone:'enemy_front',attIdx:1,zone:'player_front',idx:2,fromZone:'player_front',fromIdx:2});await tick();await sync.tail;
  assert.deepEqual(order,['waiting','reply','settled','snapshot']);assert.equal(sync.cursor,3);assert.equal(sync.processing,0);tests++;
 }
 new vm.Script(fs.readFileSync(path.join(root,'static/game_v8.js'),'utf8'));
 console.log(`${tests} battle-reply deadlock, exhaustion, stale snapshot and readying scenarios: PASS`);
})();
