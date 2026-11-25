/* One authoritative clock per active player; peers display remaining durations, not device timestamps. */
(function(global){
  'use strict';
  function create({read,expire,draw=()=>{},publish=()=>{},now=()=>performance.now(),totalMs=120000,summonMs=60000}){
    let state=null,last=now(),lastSent=-Infinity,running=false,locked=false,generation=0,runKey=null;
    const main=p=>['抽牌階段','防守階段','召喚階段','戰術佈陣','進攻宣言','主要階段'].includes(p);
    function snapshot(){return state?{...state}:null;}
    function receive(s,{restore=false}={}){const r=read(),ownRestore=restore&&r.ours&&s?.owner===r.role;if(!s||(!ownRestore&&(r.ours||s.owner===r.role))||s.turn!==r.turn||!Number.isFinite(s.remaining)||!Number.isFinite(s.stageRemaining))return false;
      state={turn:s.turn,owner:s.owner,phase:String(s.phase),remaining:Math.max(0,Math.min(totalMs,s.remaining)),stageRemaining:Math.max(0,Math.min(totalMs,s.stageRemaining)),paused:!!s.paused};last=now();return true;}
    function reset(){generation++;state=null;last=now();lastSent=-Infinity;locked=false;running=false;runKey=null;}
    async function tick(){const at=now(),r=read(),dt=Math.max(0,at-last);last=at;
      if(!r.enabled||r.over){reset();draw(null,r);return;}
      if(!r.ours){if(state&&state.turn===r.turn&&!state.paused){state.remaining=Math.max(0,state.remaining-dt);state.stageRemaining=Math.max(0,state.stageRemaining-dt);}draw(snapshot(),r);return;}
      if(!main(r.phase)||r.ending){draw(null,r);return;}
      if(!state||state.turn!==r.turn||state.owner!==r.role){generation++;running=false;runKey=null;state={turn:r.turn,owner:r.role,phase:r.phase,remaining:totalMs,stageRemaining:r.phase==='召喚階段'?summonMs:totalMs,paused:false};lastSent=-Infinity;locked=false;}
      else if(state.phase!==r.phase){if(!state.paused)state.remaining=Math.max(0,state.remaining-dt);state.phase=r.phase;state.stageRemaining=r.phase==='召喚階段'?Math.min(summonMs,state.remaining):state.remaining;locked=running;lastSent=-Infinity;}
      else if(!state.paused&&!running){state.remaining=Math.max(0,state.remaining-dt);state.stageRemaining=Math.max(0,state.stageRemaining-dt);}
      const changed=state.paused!==!!r.waiting;state.paused=!!r.waiting;
      draw(snapshot(),r);
      if(changed||at-lastSent>=2000){lastSent=at;publish(snapshot());}
      if(!running&&!state.paused&&(state.remaining<=0||state.stageRemaining<=0)){
        const key=state.turn,serial=generation,reason=state.remaining<=0?'turn':'summon';running=true;locked=true;runKey={turn:key,owner:state.owner,generation:serial};
        try{await expire(reason,key);}finally{if(serial===generation){running=false;const current=read();if(current.turn!==key||!current.ours||current.phase!==state?.phase||(reason==='summon'&&current.phase!=='召喚階段'&&state?.remaining>0))locked=false;if(state&&current.turn===key&&current.ours&&current.phase!==state.phase){state.phase=current.phase;state.stageRemaining=current.phase==='召喚階段'?Math.min(summonMs,state.remaining):state.remaining;state.paused=!!current.waiting;lastSent=-Infinity;}last=now();}}
      }
    }
    return {tick,receive,snapshot,reset,get generation(){return generation;},get locked(){const r=read();return locked&&r.ours&&r.turn===state?.turn;},get autoResolving(){const r=read();return running&&r.ours&&r.turn===runKey?.turn&&r.role===runKey?.owner&&generation===runKey?.generation;}};
  }
  global.XLWTurnClock={create};
})(window);
