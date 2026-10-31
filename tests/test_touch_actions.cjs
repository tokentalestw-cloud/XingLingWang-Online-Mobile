const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/touch_actions.js'),'utf8');let tests=0;
function fixture(pointer=true){
 const listeners={},frames=[],timers=[],classes=new Set(),attrs={};let calls=0,clock=0;
 const button={id:'stableActionMulliganConfirm',disabled:false,isConnected:true,classList:{add:x=>classes.add(x),remove:x=>classes.delete(x)},setAttribute:(k,v)=>attrs[k]=v,removeAttribute:k=>delete attrs[k],closest:()=>button,click(){const e=event('click',{isTrusted:false,detail:0});dispatch('click',e);if(!e.stopped)calls++;}};
 const panel={addEventListener(type,fn){(listeners[type]||=[]).push(fn);}};
 const g={Date:{now:()=>clock},setTimeout:fn=>{timers.push(fn);},requestAnimationFrame:fn=>frames.push(fn)};if(pointer)g.PointerEvent=class{};
 vm.runInNewContext(source,g);g.XLWTouchActions.bind(panel);g.XLWTouchActions.bind(panel);
 function event(type,extra={}){return {type,target:button,pointerType:'touch',pointerId:1,isPrimary:true,clientX:10,clientY:10,isTrusted:true,detail:1,preventDefault(){this.prevented=true;},stopPropagation(){this.propagated=true;},stopImmediatePropagation(){this.stopped=true;},...extra};}
 function dispatch(type,e=event(type)){for(const fn of listeners[type]||[])fn(e);return e;}
 const down=extra=>dispatch('pointerdown',event('pointerdown',extra));const up=extra=>dispatch('pointerup',event('pointerup',extra));
 return {g,button,classes,attrs,listeners,event,dispatch,down,up,flush(){for(const f of frames.splice(0))f();for(const f of timers.splice(0))f();},advance(t){clock+=t;},calls:()=>calls};
}
for(const id of ['stableActionMulliganConfirm','stableActionEnd']){
 const f=fixture();f.button.id=id;f.down();assert(f.classes.has('btn-pressed-instant'));assert.equal(f.calls(),0);f.up();assert.equal(f.attrs['aria-busy'],'true');assert.equal(f.calls(),0);f.flush();assert.equal(f.calls(),1);tests++;
 f.advance(10000);assert.equal(f.dispatch('click').stopped,true);assert.equal(f.calls(),1);tests++;
 // A second deliberate touch remains usable even if its native click is suppressed.
 f.down();f.up();f.flush();assert.equal(f.calls(),2);tests++;
 // A real mouse click and keyboard click still follow the original button behavior.
 f.down({pointerType:'mouse'});assert.equal(f.dispatch('click').stopped,undefined);tests++;
 f.down();f.up();f.flush();assert.equal(f.dispatch('click',f.event('click',{detail:0})).stopped,undefined);tests++;
}
{const f=fixture();f.down();f.dispatch('pointermove',f.event('pointermove',{clientX:40}));f.up({clientX:40});f.flush();assert.equal(f.calls(),0);tests++;}
{const f=fixture();f.down();f.dispatch('pointercancel');f.up();f.flush();assert.equal(f.calls(),0);tests++;}
{const f=fixture();f.button.disabled=true;f.down();f.up();f.flush();assert.equal(f.calls(),0);tests++;}
{const f=fixture();f.down();f.button.isConnected=false;f.up();f.flush();assert.equal(f.calls(),0);tests++;}
{const f=fixture();f.down();f.up();f.button.disabled=true;f.flush();assert.equal(f.calls(),0);tests++;}
{const f=fixture();f.down();f.down({isPrimary:false,pointerId:2});f.up();f.flush();assert.equal(f.calls(),0);tests++;}
{const f=fixture(false),t={identifier:3,clientX:10,clientY:10};f.dispatch('touchstart',f.event('touchstart',{touches:[t]}));f.dispatch('touchend',f.event('touchend',{changedTouches:[t]}));f.flush();assert.equal(f.calls(),1);tests++;}
{const f=fixture(false),t={identifier:3,clientX:10,clientY:10};f.dispatch('touchstart',f.event('touchstart',{touches:[t]}));f.dispatch('touchcancel');f.dispatch('touchend',f.event('touchend',{changedTouches:[t]}));f.flush();assert.equal(f.calls(),0);tests++;}
console.log(`${tests} touch release, delayed-click deduplication, cancellation, disabled and desktop scenarios: PASS`);
