const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/input_diagnostics.js'),'utf8');let tests=0;
{const g={location:{search:''}};vm.runInNewContext(source,{window:g,URLSearchParams});assert.equal(g.XLWInputDiagnostics,undefined);tests++;}
let clock=100;const listeners={},created=[];
const node=tag=>({tagName:tag,style:{},children:[],setAttribute(){},appendChild(n){this.children.push(n);},remove(){}});
const body=node('body'),doc={readyState:'complete',hidden:false,body,createElement:node,getElementById:id=>null,elementFromPoint:()=>({id:'stableActionEnd'})};
const g={location:{search:'?inputcheck=1'},navigator:{maxTouchPoints:5},PointerEvent:class{},addEventListener(type,fn){listeners[type]=fn;},setInterval(fn){this.interval=fn;},xlwGetBattleFeedbackState:()=>({phase:'召喚階段',myTurn:true,ready:true,socket:1,hand:['SECRET_CARD'],player_id:'PRIVATE_ID'})};
vm.runInNewContext(source,{window:g,URLSearchParams,document:doc,navigator:g.navigator,performance:{now:()=>clock,timeOrigin:1000000},innerWidth:844,innerHeight:390});
assert.equal(body.children[0].id,'xlwInputReport');tests++;
g.XLWInputDiagnostics.mark('test');let data=JSON.parse(g.XLWInputDiagnostics.report());assert.equal(data.events[0].name,'test');assert.equal(data.state.phase,'召喚階段');tests++;
assert(!g.XLWInputDiagnostics.report().includes('SECRET_CARD'));assert(!g.XLWInputDiagnostics.report().includes('PRIVATE_ID'));tests++;
const button={id:'stableActionEnd',disabled:false};listeners.pointerdown({target:{id:'stableActionEnd',closest:selector=>selector==='button'?button:null},clientX:10,clientY:10,timeStamp:20,pointerType:'touch'});
data=JSON.parse(g.XLWInputDiagnostics.report());assert.equal(data.events.at(-1).delay,80);assert.equal(data.events.at(-1).button,'stableActionEnd');tests++;
const finish=g.XLWInputDiagnostics.begin('save-storage');clock+=6000;finish();data=JSON.parse(g.XLWInputDiagnostics.report());assert.equal(data.events.at(-1).duration,6000);tests++;
clock+=1000;g.interval();data=JSON.parse(g.XLWInputDiagnostics.report());assert.equal(data.events.at(-1).name,'main-thread-lag');tests++;
for(let i=0;i<250;i++)g.XLWInputDiagnostics.mark('bounded');assert.equal(JSON.parse(g.XLWInputDiagnostics.report()).events.length,180);tests++;
console.log(`${tests} opt-in, timing, privacy and bounded diagnostic scenarios: PASS`);
