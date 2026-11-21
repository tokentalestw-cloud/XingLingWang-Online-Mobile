/* Explicit battle priority, with durable ordered replies and no auto-pass timeout. */
(function(global) {
  'use strict';
  function create(adapter) {
    const early = new Map(), choices = new Map(), pendingChoices = new Map(), counts = new Map();
    let active = null;
    const bound = map => { if (map.size > 256) map.delete(map.keys().next().value); };
    const id = c => [c.turn,c.attackerRole,c.attRow,c.attIdx,c.defRow,c.defIdx,c.stage].join(':');
    function receive(message) {
      if (!message || typeof message.key !== 'string' || message.key.length > 200) return;
      if (message.action === 'battle_rule_choice') {
        if (pendingChoices.has(message.key)) { pendingChoices.get(message.key)(message.value); pendingChoices.delete(message.key); }
        else { choices.set(message.key,message.value); bound(choices); }
      } else if (message.action === 'battle_rule_pass' && Number.isInteger(message.revision)) {
        early.set(message.key,message.revision); bound(early);
        if (active?.key === message.key && active.revision === message.revision) {
          active.peerPassed = true; active.finish(); adapter.render();
        }
      }
    }
    async function open(context) {
      const base=id(context), n=(counts.get(base)||0)+1; counts.set(base,n); bound(counts);
      const key=base+':'+n;
      const previous=adapter.getDefense();
      let resolve;
      const complete=new Promise(done=>resolve=done);
      const state={key,revision:0,label:context.label,localPassed:false,peerPassed:!context.multi || early.get(key)===0,
        pass() {
          if(state.localPassed || adapter.busy()) return;
          state.localPassed=true;
          if(context.multi) {adapter.sync();adapter.send({action:'battle_rule_pass',key,revision:state.revision});}
          state.finish();adapter.render();
        },
        resetPasses() {state.revision++;state.localPassed=false;state.peerPassed=!context.multi;adapter.render();},
        finish() {if(state.localPassed && state.peerPassed && !adapter.busy())resolve();}
      };
      active=state; adapter.activate(state); adapter.setDefense(true); adapter.render();
      try {await complete;} finally {
        early.delete(key); if(active===state)active=null;
        adapter.activate(null);adapter.setDefense(previous);adapter.render();
      }
    }
    async function choose(context,title,message,options) {
      const base=id(context)+':choice', n=(counts.get(base)||0)+1;counts.set(base,n);bound(counts);
      const key=base+':'+n;
      if (!context.multi || context.localAttacker) {
        const result=await adapter.choose(title,message,options);
        const value=options.some(o=>o.value===result)?result:options[0].value;
        if(context.multi)adapter.send({action:'battle_rule_choice',key,value});
        return value;
      }
      if(choices.has(key)) {const value=choices.get(key);choices.delete(key);return value;}
      return new Promise(done=>pendingChoices.set(key,done));
    }
    return {receive,open,choose,get active(){return active;}};
  }
  function mergeRow(current,incoming) {
    return (incoming||[]).map((next,i)=>{
      const old=current?.[i];
      const same=old?.card && next?.card && (old.card._xlwInstanceId
        ? old.card._xlwInstanceId===next.card._xlwInstanceId
        : old.card.id===next.card.id && old.summonedTurn===next.summonedTurn);
      if(!same)return next;
      for(const key of Object.keys(old))delete old[key];
      Object.assign(old,next);return old;
    });
  }
  global.XLWOfficialBattle={create,mergeRow};
})(typeof window==='undefined'?globalThis:window);
