const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');
const section=(start,end)=>source.slice(source.indexOf(start),source.indexOf(end,source.indexOf(start)));
function setup(){
  const timers=[];
  const context=vm.createContext({window:{XLW_ENEMY:{grave:[],hand:[]}},document:{getElementById:()=>null},$:()=>null,
    structuredClone,selectedMulliganIndexes:new Set(),clearModes(){},render(){},setStatus(){},logBattle(){},
    setTimeout(fn){timers.push(fn);return timers.length;},clearTimeout(){},turn:1,phase:'召喚階段',
    normalSummonUsed:false,tacticalSummonUsed:false});
  vm.runInContext(section('window.XLW_Tutorial = {','window.xlwStartTutorial ='),context);
  return {context,tutorial:context.window.XLW_Tutorial,timers};
}
test('tutorial setup uses regular summon accounting and clears stale selection/draw state',()=>{
  const {context,tutorial}=setup();
  context.window.XLW_bypassNormalSummonLimit=true;
  context.window.XLW_playerNeedsToDraw=true;
  tutorial.setupDemoBattle(true);
  assert.equal(context.window.XLW_bypassNormalSummonLimit,false);
  assert.equal(context.window.XLW_bypassTurnCheck,false);
  assert.equal(context.window.XLW_playerNeedsToDraw,false);
  assert.equal(context.normalSummonUsed,false);
  assert.equal(context.hand.length,4);
  assert.equal(context.graveyard.length,0);
});
test('tutorial phase click delegates once and never falls into normal forced summoning',async()=>{
  let calls=0;
  const context=vm.createContext({window:{XLW_Tutorial:{active:true,async handleInteraction(type,payload){calls++;assert.equal(type,'click_phase_btn');assert.equal(payload.phase,'進攻宣言');return true;}}},
    xlwRequireSpellCompletion:()=>false,selectedHandForTribute:null,tributeWaitingPosition:false,
    xlwEnforceForcedSummonRule(){throw Error('must not run both tutorial and normal handlers');}});
  vm.runInContext(section('async function changeActionPhase(','// 戰術移動單位'),context);
  assert.equal(await context.changeActionPhase('進攻宣言'),true);assert.equal(calls,1);
});
test('guided phase transition does not recurse, double execute or advance twice on rapid clicks',async()=>{
  const {context,tutorial,timers}=setup();let calls=0,advances=0;
  tutorial.active=true;tutorial.steps=[{interactive:{type:'click_phase_btn',phase:'進攻宣言'}}];
  tutorial.nextStep=()=>advances++;
  context.changeActionPhase=async(phase,options)=>{calls++;assert.equal(phase,'進攻宣言');assert.equal(options.tutorialAction,true);};
  assert.equal(await tutorial.handleInteraction('click_phase_btn',{phase:'進攻宣言'}),true);
  assert.equal(await tutorial.handleInteraction('click_phase_btn',{phase:'進攻宣言'}),false);
  assert.equal(calls,1);assert.equal(timers.length,1);
  timers[0]();assert.equal(advances,1);
});
test('draw lesson waits for draw completion before entering its next phase',async()=>{
  const {context,tutorial}=setup();let release;
  tutorial.active=true;tutorial.steps=[{interactive:{type:'click_deck',afterDrawPhase:'防守階段'}}];
  context.phase='抽牌階段';context.window.XLW_playerNeedsToDraw=true;
  context.performPlayerTurnStartDraw=()=>new Promise(resolve=>{release=resolve;});
  context.window.xlwShowPhaseBanner=()=>{};
  const pending=tutorial.handleInteraction('click_deck',{});
  assert.equal(context.phase,'抽牌階段');assert.equal(context.window.XLW_playerNeedsToDraw,false);
  release();assert.equal(await pending,true);
  assert.equal(context.phase,'防守階段');assert.equal(context.window.XLW_defenseCounterActive,true);
});
