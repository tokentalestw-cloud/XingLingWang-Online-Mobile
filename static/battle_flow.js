(function(global){
  'use strict';
  const scopes=new Map(),spent=new Map();
  const replyFields={sneak_recall:['attZone','attIdx'],double_claw_choice:['attZone','attIdx'],foodball_choice:['zone','idx'],foodball_summon:['zone','idx'],handy_meow_move_sync:['fromZone','fromIdx']};
  const key=(zone,idx)=>zone+':'+idx;
  const signature=unit=>unit&&JSON.stringify([unit.card?.id,unit.card?.name,unit.summonedTurn]);
  function exhaust(unit){if(!unit)return;unit.tapped=true;unit.attacking=false;unit.target=null;}
  function openCombat(attZone,attIdx,defZone,defIdx){
    const keys=[...new Set([key(attZone,attIdx),key(defZone,defIdx)])];
    for(const k of keys)scopes.set(k,(scopes.get(k)||0)+1);
    let closed=false;
    return ()=>{if(closed)return;closed=true;for(const k of keys){const n=scopes.get(k)-1;if(n>0)scopes.set(k,n);else{scopes.delete(k);for(const name of ['XLW_opponentSneakRecall','XLW_opponentDoubleClawNegate','XLW_opponentFoodBallChoice','XLW_opponentFoodBallSummon','XLW_handyMeowOpponentChoice'])if(global[name])delete global[name][k];}}};
  }
  function canBypass(action,data){const fields=replyFields[action];return !!(fields&&data&&scopes.has(key(data[fields[0]],data[fields[1]])));}
  function settle(unit,zone,idx,turn){exhaust(unit);spent.set(key(zone,idx),{signature:signature(unit),turn});}
  function finish(unit,current,zone,idx,turn){
    const record=spent.get(key(zone,idx));if(!record||record.turn!==turn)return;
    if(!current||signature(current)!==signature(unit)){spent.delete(key(zone,idx));return;}
    // A real post-combat readying effect is allowed to leave the survivor upright.
    if(!current.tapped&&!current.attacking){spent.delete(key(zone,idx));return;}
    exhaust(current);
  }
  function reconcile(field,turn){for(const [k,record]of spent){const [zone,index]=k.split(':'),unit=field[zone]?.[Number(index)];if(record.turn!==turn||!unit||signature(unit)!==record.signature){spent.delete(k);continue;}if(zone.startsWith('enemy_')&&global.XLW_DEFENSE_RULE?.playerNeedsDefense)continue;if(unit.attacking)exhaust(unit);else if(!unit.tapped)spent.delete(k);}}
  function drawFlags(player,enemy,snapshot){
    // Only a turn-authoritative snapshot may change this client's draw requirement.
    if(snapshot.includeTurnPhase && snapshot.XLW_enemyNeedsToDraw!==undefined)player=Boolean(snapshot.XLW_enemyNeedsToDraw);
    if(snapshot.XLW_playerNeedsToDraw!==undefined)enemy=Boolean(snapshot.XLW_playerNeedsToDraw);
    return {player,enemy};
  }
  function forgetSide(side){for(const k of spent.keys())if(k.startsWith(side+'_'))spent.delete(k);}
  global.XLWBattleFlow={drawFlags,openCombat,canBypass,settle,finish,reconcile,exhaust,forget(zone,idx){spent.delete(key(zone,idx));},forgetSide,reset(){scopes.clear();spent.clear();}};
})(typeof window==='undefined'?globalThis:window);
