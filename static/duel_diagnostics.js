/* Passive, bounded diagnostics. Never repair state or send private card contents. */
(function(global){
 'use strict';
 const VERSION='duel-diagnostics-v1',LIMIT=180;
 const hash=value=>{const text=JSON.stringify(value);let h=2166136261;for(let i=0;i<text.length;i++)h=Math.imul(h^text.charCodeAt(i),16777619)>>>0;return h.toString(16).padStart(8,'0');};
 const card=c=>c?{id:String(c.id||''),attack:c.attack??null,score:c.score??null}:null;
 const list=v=>Array.isArray(v)?v:[];
 function publicSections(s,role){
  const own=role==='player2'?'player2':'player1',opp=own==='player1'?'player2':'player1';
  const rows={};
  const unit=u=>u?{card:card(u.card),tapped:!!u.tapped&&!u.attacking,attacking:!!u.attacking,atkModifier:u.atkModifier||0,
   irrigation:u.irrigation??u.irrigationValue??0,passengers:u.passengers??u.rideCount??0,
   combined:list(u.devourCards).map(p=>({card:card(p.card),expose:p.expose,value:p.value})),captured:list(u.kidnappedCards).map(card)}:null;
  for(const [side,r]of [['player',own],['enemy',opp]])for(const row of ['front','back'])rows[r+'_'+row]=list(s.field?.[side+'_'+row]).map(unit);
  const faction=s.factionState||{},scores={},zones={},energy={};
  scores[own]=Number(s.playerBonusScore)||0;scores[opp]=Number(s.enemyBonusScore)||0;
  for(const [side,r]of [['player',own],['enemy',opp]]){
   zones[r]={grave:list(side==='player'?s.graveyard:s.enemyGraveyard).map(card),exile:list(side==='player'?s.playerExileZone:s.enemyExileZone).map(card),field:card(s[side+'FieldCard']),wheel:list(faction[side+'Wheel']).map(card)};
   energy[r]=Number(faction[side+'Energy'])||0;
  }
  const counts={};for(const [side,r]of [['player',own],['enemy',opp]])counts[r]={hand:list(s[side+'Hand']).length,deck:list(s[side+'Deck']).length,extra:list(s[side+'ExtraDeck']).length};
  const ordered=obj=>Object.fromEntries(Object.keys(obj).sort().map(k=>[k,obj[k]]));
  return {board:hash(ordered(rows)),scores:hash(ordered(scores)),zones:hash(ordered(zones)),energy:hash(ordered(energy)),counts:hash(ordered(counts))};
 }
 function inventory(s){
  const entries=[];
  function add(c,where){if(!c?._xlwInstanceId||/^TOKEN|^TRAVELER/.test(c.id||'')||c.name==='小旅人')return;entries.push({id:String(c._xlwInstanceId),where});}
  for(const key of ['hand','deck','graveyard','playerExtraDeck','playerExileZone','enemyHand','enemyDeck','enemyGraveyard','enemyExtraDeck','enemyExileZone'])for(const c of list(s[key]))add(c,key);
  for(const [zone,row]of Object.entries(s.field||{}))list(row).forEach((u,i)=>{
   if(!u)return;const at=zone+':'+i;add(u.card,at);
   for(const key of ['devourCards','kidnappedCards','xlwArmorBreakSwords','grantedMagicCards','attachedSpells'])for(const p of list(u[key]))add(p.card||p,at+':'+key);
  });
  add(s.playerFieldCard,'playerField');add(s.enemyFieldCard,'enemyField');
  for(const side of ['player','enemy'])for(const c of list(s.factionState?.[side+'Wheel']))add(c,side+'Wheel');
  for(const item of list(s.factionState?.banishedTimeGoats))add(item.card,'temporaryExile');
  for(const item of list(s.spellChainStack))add(item.card,'spellChain');
  return entries;
 }
 function create(adapter={}){
  let events=[],issues=[],known=new Map(),missing=new Map(),reported=new Set(),proofs=new Map(),serial=0,timer=null,epoch=Math.random().toString(36).slice(2),busyAt=null;
  const now=()=>adapter.now?.()??Date.now();
  function record(kind,data={}){events.push({at:now(),kind,...data});if(events.length>LIMIT)events.shift();}
  function issue(code,detail){const key=code+JSON.stringify(detail);if(reported.has(key))return;reported.add(key);if(reported.size>512)reported.delete(reported.values().next().value);issues.push({at:now(),code,...detail});if(issues.length>80)issues.shift();}
  function scan(s){
   if(!s||s.busy||!s.active)return;
   const present=new Map();for(const e of inventory(s)){if(!present.has(e.id))present.set(e.id,[]);present.get(e.id).push(e.where);}
   for(const [id,locations]of present){if(locations.length>1)issue('duplicate_instance',{instance:id,locations});known.set(id,locations[0]);missing.delete(id);}
   for(const [id,where]of known)if(!present.has(id)){const count=(missing.get(id)||0)+1;missing.set(id,count);if(count>=2)issue('unaccounted_instance',{instance:id,lastLocation:where,certainty:'needs_review'});}
   record('checkpoint',{turn:s.turn,phase:s.phase,tracked:present.size});
  }
  function schedule(){if(timer!==null)return;timer=global.setTimeout(()=>{timer=null;try{const s=adapter.read?.();if(s?.busy){busyAt??=now();if(now()-busyAt>30000)record('long_wait',{turn:s.turn,phase:s.phase,seconds:Math.round((now()-busyAt)/1000)});schedule();return;}busyAt=null;scan(s);}catch(e){record('diagnostic_error',{message:String(e.message).slice(0,160)});}},800);}
  function proof(state,role){if(!['player1','player2'].includes(role))return undefined;const id=epoch+':'+(++serial),sections=publicSections(state,role);proofs.set(id,{sections,at:now()});if(proofs.size>48)proofs.delete(proofs.keys().next().value);return {version:VERSION,id,role,sections};}
  function receipt(proofData,state,role,busy){
   if(proofData?.version!==VERSION||typeof proofData.id!=='string'||proofData.id.length>180||!['player1','player2'].includes(proofData.role)||proofData.role===role)return null;
   return {action:'duel_diagnostic_receipt',version:VERSION,id:proofData.id,sections:busy?null:publicSections(state,role),skipped:busy?'interaction_in_progress':null};
  }
  function receive(data){const pending=proofs.get(data.id);if(!pending||data.version!==VERSION)return;proofs.delete(data.id);
   if(data.skipped){record('comparison_skipped',{reason:String(data.skipped).slice(0,60)});return;}
   if(!data.sections||Object.keys(pending.sections).some(k=>typeof data.sections[k]!=='string'||data.sections[k].length!==8))return;
   const different=Object.keys(pending.sections).filter(k=>pending.sections[k]!==data.sections[k]);
   record('peer_comparison',{id:data.id,matched:!different.length,sections:different});
   if(different.length)issue('public_state_mismatch',{proof:data.id,sections:different,expected:pending.sections,actual:Object.fromEntries(Object.keys(pending.sections).map(k=>[k,data.sections[k]]))});
  }
  function exportReport(){let s={};try{s=adapter.read?.()||{};}catch(_){}return {version:VERSION,createdAt:new Date(now()).toISOString(),build:adapter.build||'',state:{turn:s.turn,phase:s.phase,role:s.role,active:!!s.active,busy:!!s.busy},coverage:{inventory:'Identified physical cards only; tokens and unknown legacy cards excluded.',missing:'Suspected after two settled checkpoints; not automatically repaired.',sync:'Public snapshot boundaries only; skipped during overlapping interactions.'},events:[...events],issues:[...issues],logs:list(adapter.logs?.()).slice(0,100).map(v=>String(v).slice(0,700))};}
  function reset(){events=[];issues=[];known.clear();missing.clear();reported.clear();proofs.clear();serial=0;epoch=Math.random().toString(36).slice(2);busyAt=null;if(timer!==null)global.clearTimeout(timer);timer=null;record('new_match');}
  return {record,scan,schedule,proof,receipt,receive,exportReport,reset,identityCollision:(id)=>issue('duplicate_identity_reassigned',{instance:String(id)})};
 }
 let controller=null;
 const api={create,publicSections,inventory,init(adapter){controller=create(adapter);return controller;},
  identityCollision:(...a)=>controller?.identityCollision(...a),record:(...a)=>controller?.record(...a),schedule:()=>controller?.schedule(),reset:()=>controller?.reset(),
  proof:(...a)=>controller?.proof(...a),receipt:(...a)=>controller?.receipt(...a),receive:(...a)=>controller?.receive(...a),
  exportReport:()=>controller?.exportReport(),download(){const report=controller?.exportReport();if(!report)return;const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='星靈王-對戰診斷-'+Date.now()+'.json';document.body.appendChild(a);a.click();a.remove();global.setTimeout(()=>URL.revokeObjectURL(url),1000);}};
 global.addEventListener?.('error',event=>api.record('runtime_error',{message:String(event.message||'Error').replace(/https?:\/\/[^\s)]+/g,'[url]').slice(0,180),line:event.lineno}));
 global.addEventListener?.('unhandledrejection',event=>api.record('unhandled_rejection',{message:String(event.reason?.message||event.reason||'Error').replace(/https?:\/\/[^\s)]+/g,'[url]').slice(0,180)}));
 global.XLWDuelDiagnostics=api;
})(typeof window==='undefined'?globalThis:window);
