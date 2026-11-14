/* Merge peer collection edits against their observed base, never a stale whole-array overwrite. */
(function(global){
  'use strict';
  const clone=value=>JSON.parse(JSON.stringify(value));
  const key=card=>card?String(card._xlwInstanceId||('legacy:'+card.id+':'+card.name)):'unknown';
  function mergeCollection(current,base,incoming,ledger=null,channel=""){
    if(!Array.isArray(incoming))return current;
    if(!Array.isArray(base))return clone(incoming);
    if(!ledger&&JSON.stringify(current)===JSON.stringify(base))return clone(incoming);
    let hash=2166136261;for(const ch of base.map(key).join('|'))hash=Math.imul(hash^ch.charCodeAt(0),16777619)>>>0;
    const once=(op,k)=>{if(!ledger)return true;const id=channel+':'+hash+':'+op+':'+k;if(ledger.has(id))return false;ledger.add(id);return true;};
    const counts=list=>{const m=new Map();for(const c of list)m.set(key(c),(m.get(key(c))||0)+1);return m;};
    const before=counts(base),after=counts(incoming),remove=new Map();
    for(const [k,n]of before)if(n>(after.get(k)||0))remove.set(k,n-(after.get(k)||0));
    for(const [k,n]of remove){let allowed=0;for(let i=0;i<n;i++)if(once('remove',k+':'+i))allowed++;remove.set(k,allowed);}
    const result=current.filter(c=>{const k=key(c),n=remove.get(k)||0;if(n){remove.set(k,n-1);return false;}return true;});
    const present=counts(result),added=new Map();
    for(const card of incoming){const k=key(card),delta=(after.get(k)||0)-(before.get(k)||0);if(delta<=0)continue;const n=added.get(k)||0;if(n>=delta)continue;added.set(k,n+1);if(!once('add',k+':'+n))continue;if(card?._xlwInstanceId&&(present.get(k)||0)>0)continue;result.push(clone(card));present.set(k,(present.get(k)||0)+1);}
    return result;
  }
  let serial=0;
  function identify(list){const seen=new Set();for(let i=0;i<list.length;i++){let c=list[i];if(!c||typeof c!=='object')continue;if(!c._xlwInstanceId||seen.has(c._xlwInstanceId)){c={...c,_xlwInstanceId:global.crypto?.randomUUID?.()||('card-'+Date.now().toString(36)+'-'+(++serial)+'-'+Math.random().toString(36).slice(2))};list[i]=c;}seen.add(c._xlwInstanceId);}return list;}
  function removeCard(list,card){if(!Array.isArray(list)||!card||card.id==='VRT-0011-EFFECT')return null;let i=list.indexOf(card);if(i<0&&card._xlwInstanceId)i=list.findIndex(c=>c?._xlwInstanceId===card._xlwInstanceId);if(i<0&&!card._xlwInstanceId)i=list.findIndex(c=>c&&(c.id===card.id||c.name===card.name));if(i<0)i=list.findIndex(c=>c===null);return i<0?null:list.splice(i,1)[0];}
  function takeKnownCard(source, selected) {
    if (!selected || !Array.isArray(source)) return null;
    let index = source.indexOf(selected);
    if (index < 0) {
      index = source.findIndex(card => card && (selected._xlwInstanceId
        ? card._xlwInstanceId === selected._xlwInstanceId
        : card.id === selected.id && card.name === selected.name));
    }
    return index < 0 ? null : source.splice(index, 1)[0];
  }
  function moveKnownCard(source, destination, selected) {
    if (source === destination || !Array.isArray(destination)) return null;
    const card = takeKnownCard(source, selected);
    if (!card) return null;
    const alreadyMoved = destination.includes(card) || (card._xlwInstanceId &&
      destination.some(item => item?._xlwInstanceId === card._xlwInstanceId));
    if (alreadyMoved) return null;
    destination.push(card);
    return card;
  }
  let ledger=new Set();
  function mergeOwned(current,base,incoming,channel){if(ledger.size>4096)ledger=new Set();return mergeCollection(current,base,incoming,ledger,channel);}
  global.XLWDuelConsistency={clone,key,identify,mergeCollection,mergeOwned,removeCard,takeKnownCard,moveKnownCard,reset(){ledger.clear();}};
})(typeof window==='undefined'?globalThis:window);
