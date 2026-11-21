/* Correlated faction choices: a single modal per logical decision, including mirrored resolution. */
(function(global){
 'use strict';
 function create(adapter){
  const local=new Map(),waiters=new Map(),answers=new Map();
  const trim=map=>{if(map.size>256)map.delete(map.keys().next().value);};
  const valid=(options,value)=>options.some(o=>o.value===value);
  function own(key,title,message,options,config){
   if(!local.has(key)){
    const task=Promise.resolve().then(()=>adapter.choose(title,message,options,config)).then(value=>{
     const result=valid(options,value)?value:options[0].value;
     adapter.send({action:'faction_choice_result',key,value:result});return result;
    });local.set(key,task);trim(local);
   }
   return local.get(key);
  }
  async function choose(isLocal,key,title,message,options,config={}){
   if(!options?.length)return null;
   if(options.length===1)return options[0].value;
   if(isLocal)return own(key,title,message,options,config);
   if(answers.has(key)){const value=answers.get(key);answers.delete(key);return valid(options,value)?value:options[0].value;}
   if(!waiters.has(key)){
    let resolve;const promise=new Promise(done=>resolve=done);waiters.set(key,{resolve,promise,options});
    adapter.send({action:'faction_choice_request',key,title,message,options,config});
   }
   return waiters.get(key).promise;
  }
  function receive(data){
   if(typeof data.key!=='string'||data.key.length>300)return;
   if(data.action==='faction_choice_result'){
    const pending=waiters.get(data.key);
    if(pending){if(valid(pending.options,data.value)){waiters.delete(data.key);pending.resolve(data.value);}}
    else{answers.set(data.key,data.value);trim(answers);}
   }else if(data.action==='faction_choice_request'&&Array.isArray(data.options)&&data.options.length>0&&data.options.length<=100){
    void own(data.key,data.title,data.message,data.options,data.config);
   }
  }
  return {choose,receive};
 }
 global.XLWFactionChoices={create};
})(typeof window==='undefined'?globalThis:window);
