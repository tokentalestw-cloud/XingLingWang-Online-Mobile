/* Native touch activation for the two primary battle actions. */
(function(global){
  'use strict';
  const bound=new WeakSet();
  const now=()=>Date.now();
  const action=target=>target?.closest?.('#stableActionMulliganConfirm,#stableActionEnd');
  function bind(panel){
    if(!panel||bound.has(panel))return;bound.add(panel);
    let press=null,compatibilityUntil=0;
    const begin=(event,x,y,id)=>{
      const button=action(event.target);if(!button||button.disabled)return;
      press={button,x,y,id,moved:false};button.classList.add('btn-pressed-instant');
    };
    const cancel=()=>{press?.button.classList.remove('btn-pressed-instant');press=null;};
    const move=(x,y)=>{if(press&&Math.hypot(x-press.x,y-press.y)>12){press.moved=true;press.button.classList.remove('btn-pressed-instant');}};
    const finish=event=>{
      const p=press;press=null;if(!p)return;
      const button=p.button;
      if(p.moved||!button.isConnected||button.disabled||action(event.target)!==button){button.classList.remove('btn-pressed-instant');return;}
      // Safari's subsequent compatibility click must not run the same action twice.
      event.preventDefault();event.stopPropagation();compatibilityUntil=now()+15000;
      button.setAttribute('aria-busy','true');
      let dispatched=false;
      const run=()=>{if(dispatched)return;dispatched=true;
        try{if(button.isConnected&&!button.disabled)button.click();}
        finally{button.removeAttribute('aria-busy');button.classList.remove('btn-pressed-instant');}
      };
      // Allow the pressed state to paint before storage/network/game work starts.
      if(global.requestAnimationFrame)global.requestAnimationFrame(()=>global.setTimeout(run,0));
      global.setTimeout(run,80);
    };
    panel.addEventListener('click',event=>{
      const button=action(event.target);
      if(button&&event.isTrusted&&event.detail!==0&&now()<compatibilityUntil){event.preventDefault();event.stopImmediatePropagation();}
    },true);
    panel.addEventListener('keydown',()=>{compatibilityUntil=0;},true);
    if(global.PointerEvent){
      panel.addEventListener('pointerdown',event=>{if(event.pointerType==='mouse')compatibilityUntil=0;if(event.pointerType==='touch'||event.pointerType==='pen'){if(event.isPrimary===false){cancel();return;}begin(event,event.clientX,event.clientY,event.pointerId);}},true);
      panel.addEventListener('pointermove',event=>{if(press?.id===event.pointerId)move(event.clientX,event.clientY);},true);
      panel.addEventListener('pointerup',event=>{if(press?.id===event.pointerId){move(event.clientX,event.clientY);finish(event);}},true);
      panel.addEventListener('pointercancel',cancel,true);
    }else{
      panel.addEventListener('touchstart',event=>{if(event.touches.length!==1){cancel();return;}const t=event.touches[0];begin(event,t.clientX,t.clientY,t.identifier);},{capture:true,passive:true});
      panel.addEventListener('touchmove',event=>{const t=Array.from(event.touches).find(t=>t.identifier===press?.id);if(t)move(t.clientX,t.clientY);},{capture:true,passive:true});
      panel.addEventListener('touchend',event=>{const t=Array.from(event.changedTouches).find(t=>t.identifier===press?.id);if(t){move(t.clientX,t.clientY);finish(event);}},{capture:true,passive:false});
      panel.addEventListener('touchcancel',cancel,true);
    }
  }
  global.XLWTouchActions={bind};
})(typeof window==='undefined'?globalThis:window);
