const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../static/mobile_viewport.js'),'utf8');
const game=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');
assert(!game.includes('xlw-orientation-mask'),'No orientation blackout code remains');
assert(!game.includes('xlwScheduleOrientCheck'),'No delayed duplicate orientation coordinator remains');
const html=fs.readFileSync(path.join(__dirname,'../static/index.html'),'utf8');
assert(html.indexOf('/static/mobile_viewport.js')<html.indexOf('<body'),'Viewport is initialized before first body paint');
function environment({ios=true,active=false,standalone=false,body=true,width=390,height=844}={}) {
  function element(){const classes=new Set(),styles={};return{classes,styles,
    classList:{toggle(n,on){if(on)classes.add(n);else classes.delete(n);}},
    style:{setProperty(n,v){styles[n]=v;}}};}
  const handlers=new Map();
  const add=(name,fn)=>{if(!handlers.has(name))handlers.set(name,[]);handlers.get(name).push(fn);};
  const fire=name=>{for(const fn of handlers.get(name)||[])fn({isTrusted:true});};
  const root=element();
  const document={documentElement:root,body:body?element():null,hidden:false,
    addEventListener:add,createElement(){throw Error('Viewport must not create a blackout overlay');}};
  const window={innerWidth:width,innerHeight:height,screen:{},addEventListener:add,
    matchMedia:q=>({matches:q==='(pointer: coarse)' || (q==='(display-mode: standalone)'&&standalone)}),
    visualViewport:{addEventListener:add},adjustBoardScale(){}};
  const navigator={userAgent:ios?'iPhone':'Android',platform:ios?'iPhone':'Linux',maxTouchPoints:5,
    userActivation:{isActive:active},standalone};
  const context=vm.createContext({window,document,navigator,Promise,
    setTimeout(){throw Error('No delayed viewport refits');}});
  vm.runInContext(source,context);
  return{root,document,window,navigator,fire,element};
}
module.exports=(async()=>{
  let tests=0;
  const iphone=environment({body:false});
  assert(iphone.root.classes.has('xlw-force-landscape'));
  assert.equal(iphone.root.styles['--xlw-ui-width'],'844px');
  assert.equal(iphone.root.styles['--xlw-ui-height'],'390px'); tests++;
  iphone.document.body=iphone.element(); iphone.fire('DOMContentLoaded');
  assert(iphone.document.body.classes.has('xlw-force-landscape')); tests++;
  iphone.fire('orientationchange');
  iphone.window.innerWidth=844; iphone.window.innerHeight=390; iphone.fire('resize');
  assert(!iphone.root.classes.has('xlw-force-landscape'));
  assert(!iphone.document.body.classes.has('xlw-force-landscape'));
  assert.equal(iphone.root.styles['--xlw-ui-width'],'844px');
  assert.equal(iphone.root.styles['--xlw-ui-height'],'390px'); tests++;
  iphone.window.innerWidth=390; iphone.window.innerHeight=844; iphone.fire('resize');
  assert(iphone.root.classes.has('xlw-force-landscape')); tests++;
  assert.equal(await iphone.window.xlwAutoLandscapeFullscreen(),false); tests++;

  const inactive=environment(); let deniedRequests=0;
  inactive.root.requestFullscreen=()=>{deniedRequests++;return Promise.resolve();};
  assert.equal(await inactive.window.xlwAutoLandscapeFullscreen(),false);
  assert.equal(deniedRequests,0); tests++;

  const android=environment({ios:false,active:true}); let requests=0,locks=0,complete;
  android.root.requestFullscreen=()=>{requests++;return new Promise(resolve=>{complete=()=>{android.document.fullscreenElement=android.root;android.fire('fullscreenchange');resolve();};});};
  android.window.screen.orientation={lock:()=>{locks++;return Promise.resolve();}};
  const first=android.window.xlwAutoLandscapeFullscreen();
  assert.equal(first,android.window.xlwAutoLandscapeFullscreen());
  assert.equal(requests,1); complete(); await first;
  android.fire('webkitfullscreenchange'); android.fire('resize'); android.fire('orientationchange');
  assert.equal(locks,1); assert.equal(requests,1); tests++;
  android.document.fullscreenElement=null; android.fire('fullscreenchange');
  assert.equal(requests,1,'Exiting native fullscreen must not cause automatic re-entry'); tests++;

  const rejected=environment({ios:false,active:true}); let rejectedLocks=0;
  rejected.root.requestFullscreen=()=>Promise.reject(Error('NotAllowedError'));
  rejected.window.screen.orientation={lock:()=>{rejectedLocks++;return Promise.resolve();}};
  assert.equal(await rejected.window.xlwAutoLandscapeFullscreen(),false);
  assert.equal(rejectedLocks,0); assert(rejected.root.classes.has('xlw-force-landscape')); tests++;

  const installed=environment({standalone:true,active:false}); let installedRequests=0;
  installed.root.requestFullscreen=()=>{installedRequests++;return Promise.resolve();};
  installed.fire('DOMContentLoaded'); await installed.window.xlwAutoLandscapeFullscreen();
  assert.equal(installedRequests,0); assert(installed.root.classes.has('xlw-force-landscape')); tests++;
  console.log(`${tests} mobile viewport/fullscreen scenarios: PASS`);
})();
