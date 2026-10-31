(function(global){
 'use strict';
 if(!new URLSearchParams(global.location.search).has('inputcheck'))return;
 const entries=[],start=performance.now();let sequence=0;
 function mark(name,data={}){entries.push({ms:Math.round(performance.now()-start),name,...data});if(entries.length>180)entries.shift();}
 const state=()=>global.xlwGetBattleFeedbackState?.()||{};
 const snapshot=()=>{const s=state();return {phase:s.phase,myTurn:s.myTurn,ready:s.ready,socket:s.socket,processing:global.XLW_sync?.processing,pending:global.XLW_sync?.pending?.size};};
 const label=node=>node?.id||node?.closest?.('[id]')?.id||node?.tagName||'none';
 for(const type of ['pointerdown','pointerup','pointercancel','touchstart','touchend','touchcancel','click'])global.addEventListener(type,event=>{
  if(event.target?.closest?.('#xlwInputReportDialog,#xlwInputReport'))return;
  const button=event.target?.closest?.('button'),point=event.changedTouches?.[0]||event;
  const hit=Number.isFinite(point.clientX)?document.elementFromPoint(point.clientX,point.clientY):null;
  const stamp=event.timeStamp>1e12?event.timeStamp-performance.timeOrigin:event.timeStamp;
  mark(type,{target:label(event.target),button:label(button),hit:label(hit),disabled:button?.disabled,pointer:event.pointerType,delay:Math.max(0,Math.round(performance.now()-stamp)),...snapshot()});
 },{capture:true,passive:true});
 let previous=performance.now();global.setInterval(()=>{const t=performance.now(),lag=t-previous-250;previous=t;if(!document.hidden&&lag>150)mark('main-thread-lag',{duration:Math.round(lag)});},250);
 function report(){return JSON.stringify({version:'inputcheck-v10',pointerEvents:!!global.PointerEvent,touchPoints:global.navigator.maxTouchPoints,viewport:[innerWidth,innerHeight],state:snapshot(),events:entries},null,1);}
 function open(){document.getElementById('xlwInputReportDialog')?.remove();const d=document.createElement('div');d.id='xlwInputReportDialog';d.setAttribute('role','dialog');d.style.cssText='position:fixed;inset:4%;z-index:2147483647;background:#0b1729;color:#fff;padding:12px;display:flex;flex-direction:column;gap:8px;border:1px solid #b8a574;border-radius:12px';
 const title=document.createElement('strong');title.textContent='操作延遲紀錄（不含手牌或個人資料）';d.appendChild(title);
 const text=document.createElement('textarea');text.id='xlwInputReportText';text.readOnly=true;text.value=report();text.style.cssText='flex:1;min-height:0;width:100%;font:11px monospace;color:#eee;background:#07101f';d.appendChild(text);
 const copy=document.createElement('button');copy.textContent='複製紀錄';copy.onclick=async()=>{try{await navigator.clipboard.writeText(text.value);copy.textContent='已複製，請貼回對話';}catch(_){text.focus();text.select();copy.textContent='請長按文字並複製';}};d.appendChild(copy);
 const close=document.createElement('button');close.textContent='關閉';close.onclick=()=>d.remove();d.appendChild(close);document.body.appendChild(d);}
 function init(){const b=document.createElement('button');b.id='xlwInputReport';b.textContent='操作診斷';b.style.cssText='position:fixed;left:5px;bottom:5px;z-index:2147483646;padding:6px 10px;color:#eadba8;background:#101d30;border:1px solid #a69c72;border-radius:6px;font-size:11px';b.onclick=open;document.body.appendChild(b);}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
 global.XLWInputDiagnostics={mark,begin(name){const id=++sequence,t=performance.now();mark(name+':start',{id});return()=>mark(name+':end',{id,duration:Math.round(performance.now()-t)});},report};
})(window);
