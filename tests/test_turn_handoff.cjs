const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),{randomUUID}=require('node:crypto');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'static/game_v8.js'),'utf8');
const start=source.indexOf('  ws.onmessage = async (event) => {'),end=source.indexOf('  const gameMessageHandler = ws.onmessage;',start);
const drawStart=source.indexOf('window.xlwHandlePlayerDeckClick = async function(event) {'),drawEnd=source.indexOf('\n};',drawStart)+3;
const empty=()=>({player_front:Array(5).fill(null),player_back:Array(5).fill(null),enemy_front:Array(5).fill(null),enemy_back:Array(5).fill(null)});
let tests=0;
module.exports=(async()=>{
for(const role of ['player1','player2']){
 let defenses=0,summons=0,initializations=0;const frames=[];
 const c=vm.createContext({ws:{},console:{log(){},error(){}},document:{getElementById:()=>null},
 field:empty(),hand:[],deck:[{}],graveyard:[],enemyGraveyard:[],playerExileZone:[],enemyExileZone:[],playerExtraDeck:[],enemyExtraDeck:[],playerBonusScore:0,enemyBonusScore:0,
 turn:10,phase:'召喚階段',isMyTurn:false,isMultiplayer:true,player_role:role,normalSummonUsed:false,tacticalSummonUsed:false,opponent_mulligan_done:true,battleLog:[],isGameOverFlag:false,
 countdownActive:false,countdownRemaining:0,countdownTriggerTurn:null,countdownTriggerRole:null,xlwExpectedIncomingSeq:null,
 setStatus(){},logBattle(){},saveLocalGameState(){},render(){frames.push({phase:c.phase,initialized:initializations});},
 xlwCleanExpiredTempEquips(){},playerUntap(){initializations++;},checkCallGameAtTurnStart(){},sendFullGameStateToOpponent(){},
 performPlayerTurnStartDraw:async()=>{},sleep:async()=>{},xlwResolvePlayerDefensePhase:async()=>{defenses++;},checkCrazyFanSummon:async()=>{summons++;}
 });
 vm.runInContext('window=globalThis; XLW_ENEMY={}; XLW_DEFENSE_RULE={playerNeedsDefense:false,enemyNeedsDefense:false}; xlwEnterActiveOnlineBoardUI=()=>{}; xlwShowPhaseBanner=()=>{};',c);
 vm.runInContext(fs.readFileSync(path.join(root,'static/battle_flow.js'),'utf8'),c);
 vm.runInContext(source.slice(start,end)+'\nconst gameMessageHandler=ws.onmessage;',c);vm.runInContext(source.slice(drawStart,drawEnd),c);
 const board=empty();board.player_front[1]={card:{id:'attack',name:'attack'},attacking:true,tapped:true,target:{zone:'enemy_front',idx:1}};
 board.enemy_front[1]={card:{id:'defend',name:'defend'}};
 const state={field:board,turn:11,phase:'抽牌階段',isMyTurn:false,includeTurnPhase:true,XLW_enemyNeedsToDraw:true,enemyNeedsDefense:false,playerNeedsDefense:false};
 await c.ws.onmessage({data:JSON.stringify({action:'end_turn',next_turn:11,state})});
 assert.equal(c.isMyTurn,true);assert.equal(c.turn,11);assert.equal(c.XLW_DEFENSE_RULE.playerNeedsDefense,true);assert.equal(c.field.enemy_front[1].attacking,true);
 assert.equal(frames.length,1);assert.equal(frames[0].initialized,1);tests++;
 await c.xlwHandlePlayerDeckClick();assert.equal(defenses,1);assert.equal(summons,0);assert.equal(c.phase,'防守階段');tests++;
 await c.ws.onmessage({data:JSON.stringify({action:'sync_game_state',state:{...state,turn:10,field:empty()}})});
 assert.equal(c.field.enemy_front[1].attacking,true);assert.equal(c.phase,'防守階段');tests++;
 await c.ws.onmessage({data:JSON.stringify({action:'end_turn',next_turn:11,state})});assert.equal(initializations,1);assert.equal(c.XLW_playerNeedsToDraw,false);tests++;
 // No declared attack means the regular summon phase remains available.
 c.XLW_DEFENSE_RULE.playerNeedsDefense=false;c.field=empty();c.XLW_playerNeedsToDraw=true;
 await c.xlwHandlePlayerDeckClick();assert.equal(defenses,1);assert.equal(summons,1);assert.equal(c.phase,'召喚階段');tests++;
}
// Deterministic scheduler checks bulk backups never precede actions or multiply.
const timers=new Map();let timerId=0;const g={crypto:{randomUUID},setTimeout(fn){timers.set(++timerId,fn);return timerId;},clearTimeout(id){timers.delete(id);}};
vm.runInNewContext(fs.readFileSync(path.join(root,'static/online_sync.js'),'utf8'),g);
const sent=[],socket={readyState:1,bufferedAmount:0,send(raw){sent.push(JSON.parse(raw));}},storage={getItem:()=>null,setItem(){}};
let sync;sync=new g.XLWOnlineSync({key:'test',storage,process:async()=>{},checkpoint:()=>sync.send({action:'backup_client_state',state:{cursor:2}}),fail:e=>{throw Error(e);}});sync.attach(socket);sync.ready=true;
for(let i=0;i<50;i++)sync.send({action:'backup_client_state',state:{cursor:i}});
assert.equal(sent.length,0);assert.equal(timers.size,1);tests++;
sync.send({action:'mulligan_confirm'});assert.equal(sent[0].action,'mulligan_confirm');tests++;
const runTimer=()=>{const [id,fn]=timers.entries().next().value;timers.delete(id);fn();};
runTimer();assert.equal(sent.length,1);assert.equal(timers.size,1);tests++;
sync.pending.clear();sync.send({action:'backup_client_state',state:{cursor:99}});runTimer();assert.equal(sent.at(-1).state.cursor,99);assert.equal(timers.size,0);tests++;
socket.bufferedAmount=100;sync.send({action:'backup_client_state',state:{cursor:100}});runTimer();assert.equal(sent.at(-1).state.cursor,99);tests++;
sync.send({action:'end_turn',next_turn:3});assert.equal(sent.at(-1).action,'end_turn');sync.fail=()=>{};sync.stop(Error('test done'));assert.equal(timers.size,0);tests++;
console.log(`${tests} bidirectional atomic handoff, defense, stale snapshot and backup priority scenarios: PASS`);
})();
