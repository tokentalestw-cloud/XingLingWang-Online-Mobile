/* Presentation only: consumes existing game decisions; never sends or mutates actions. */
(function (global) {
  'use strict';
  const signed = n => (n > 0 ? '+' : '') + n;
  const goalProgress = total => total>=17 && total<20 ? 20-total : null;
  function strongestLanes(score) {
    if(!score || goalProgress(score.total)===null)return [];
    const lanes=score.lanes||[],best=Math.max(0,...lanes);
    return lanes.flatMap((value,index)=>value===best&&best>0?[index]:[]);
  }
  function scoreDifference(before, after) {
    if (!before || before.total === after.total) return null;
    const field = after.field - before.field;
    const bonus = after.bonus - before.bonus;
    const names = [];
    const keys = new Set([...Object.keys(before.units || {}), ...Object.keys(after.units || {})]);
    for (const key of keys) {
      const old = before.units?.[key], next = after.units?.[key];
      if ((old?.stars || 0) !== (next?.stars || 0) || (old?.count || 0) !== (next?.count || 0)) {
        names.push((next || old).name);
      }
    }
    const parts = [];
    if (field) parts.push(`場上星數 ${signed(field)}★${names.length ? '（' + names.slice(0, 2).join('、') + (names.length > 2 ? '等' : '') + '）' : ''}`);
    if (bonus) parts.push(`額外加分 ${signed(bonus)}★`);
    return { delta: after.total - before.total, field, bonus, reason: parts.join('；') };
  }
  function presence(state) {
    if (state.multi) {
      if (state.failed) return {kind:'paused',label:'同步已暫停',detail:'同步檢查未通過，請依畫面提示恢復對局。'};
      if (state.socket !== 1) return {kind:'reconnecting',label:'重新連線中',detail:'暫停新操作，正在重新建立連線。'};
      if (!state.ready) return {kind:'syncing',label:'補齊對局中',detail:'連線已建立，正在補齊尚未完成的對局操作。'};
      if (state.peerOffline) return {kind:'waiting',label:'等待對手重連',detail:'對手暫時離線，等待其恢復連線。'};
      if (!state.peerJoined) return {kind:'waiting',label:'等待對手加入',detail:'連線已就緒，等待對手加入房間。'};
      if (!state.active) return {kind:'waiting',label:'等待雙方準備',detail:'連線已就緒，等待牌組與先後攻確認。'};
      if (state.phase==='起手換牌') return {kind:'waiting',label:'等待雙方換牌',detail:'請確認換牌，等待雙方完成起手準備。'};
      return {kind:'connected',label:state.myTurn?'我方回合':'對手行動中',detail:'連線已建立，已收到的對局操作皆已套用。'};
    }
    if (state.over) return {kind:'finished',label:'對局已結束',detail:'可查看結算與對戰紀錄。'};
    if (!state.active) return {kind:'waiting',label:'準備對戰',detail:'請選擇遊戲模式。'};
    if (state.phase==='起手換牌') return {kind:'waiting',label:'起手換牌中',detail:'請選擇要更換的起手卡牌並確認。'};
    return state.myTurn ? {kind:'player',label:'我方回合',detail:'可以進行本階段允許的操作。'} :
      {kind:'thinking',label:'對手思考中',detail:'對手正在處理本回合的行動。'};
  }
  function unavailableReason(s) {
    if (s.needsDraw) return '請先抽取本回合手牌。';
    if (!s.myTurn && !s.defense) return '對手回合中，請等待可操作階段。';
    if (s.counterOnly) return '反制卡需等對手觸發對應條件，不能主動發動。';
    if (s.magic && s.phase === '進攻宣言') return '進攻宣言階段不能主動發動此魔法。';
    if (s.magic) return '目前無法發動此魔法，請確認可用階段及卡牌效果條件。';
    if (!['召喚階段','戰術佈陣'].includes(s.phase)) return '目前階段無法召喚手牌。';
    if (s.normalUsed && !s.bypass && s.phase === '召喚階段') return '本階段的一般召喚次數已使用。';
    if (s.tacticalUsed && !s.bypass && s.phase === '戰術佈陣') return '本階段的戰術召喚次數已使用。';
    if (s.tribute > s.units) return `祭品不足：需要 ${s.tribute} 個單位，目前只有 ${s.units} 個。`;
    return '目前無法召喚，請確認空位與卡牌的特殊召喚條件。';
  }
  let previous = null;
  let scoreEvents = {};
  let toastTimer = null;
  let scoreTimer = null;
  let peerOffline = false;
  let recovering = false;
  const state = () => global.xlwGetBattleFeedbackState?.() || {};
  function notice(message, tone='info') {
    if (!global.document || !message || !state().active) return;
    let box = document.getElementById('xlwActionFeedback');
    if (!box) {
      box = document.createElement('div'); box.id='xlwActionFeedback';
      box.setAttribute('role','status'); box.setAttribute('aria-live','polite');
      document.body.appendChild(box);
    }
    box.textContent=String(message); box.dataset.tone=tone; box.hidden=false;
    clearTimeout(toastTimer); toastTimer=setTimeout(()=>{box.hidden=true;},4800);
  }
  function updatePresence() {
    if (!global.document) return;
    const current=state();
    const status=presence({...current,peerOffline});
    const label=document.getElementById('phaseTurnOwner');
    if (label) {
      label.textContent=status.label; label.dataset.connection=status.kind;
      label.title=status.detail; label.setAttribute('aria-label',status.label+'。'+status.detail);
    }
    if (current.multi && ['reconnecting','syncing','paused'].includes(status.kind)) recovering=true;
  }
  function applyScoreEvents() {
    if (!global.document) return;
    for (const side of ['player','enemy']) {
      const card=document.querySelector('#scoreBadgeFixed .score-badge-card.'+side);
      const event=scoreEvents[side];
      if(card)card.classList.toggle('xlw-near-goal',goalProgress(previous?.[side].total)!==null);
      if (!card || !event || Date.now()>event.expires) continue;
      const badge=card.querySelector('.score-lead-badge');
      const source=card.querySelector('.score-bonus-badge');
      if (badge) {badge.textContent=signed(event.delta)+'★';badge.classList.add('xlw-score-delta');badge.dataset.direction=event.delta>0?'up':'down';badge.title=event.reason;}
      if (source) {
        source.replaceChildren(); source.classList.add('xlw-score-source');
        const title=document.createElement('span');title.className='bonus-lbl';title.textContent='變動來源';source.appendChild(title);
        for (const [name,value] of [['場上',event.field],['額外',event.bonus]]) if(value){const line=document.createElement('span');line.className='xlw-score-source-line';line.textContent=name+' '+signed(value)+'★';source.appendChild(line);}
        source.title=event.reason;
      }
    }
  }
  function updateScore(next, quiet=false) {
    if (!previous || quiet) {previous=next;scoreEvents={};return;}
    let changed=false;
    for (const side of ['player','enemy']) {
      const delta=scoreDifference(previous[side],next[side]);
      if(delta){scoreEvents[side]={...delta,expires:Date.now()+4000};changed=true;}
    }
    previous=next;applyScoreEvents();
    if(changed){clearTimeout(scoreTimer);scoreTimer=setTimeout(()=>{scoreEvents={};global.xlwRefreshScorePresentation?.();},4100);}
  }
  function scoreDetails() {
    if (!global.document || !previous) return;
    for (const side of ['player','enemy']) {
      const button=document.querySelector('#scoreBadgeFixed .score-badge-card.'+side+' .score-bonus-badge');
      if(!button)continue;
      const value=previous[side];
      const explain=()=>notice((side==='player'?'我方':'對手')+'：'+(scoreEvents[side]&&Date.now()<scoreEvents[side].expires?scoreEvents[side].reason:`場上星數 ${value.field}★ ＋ 額外加分 ${value.bonus}★ ＝ 總分 ${value.total}★`)+(value.total>=17&&value.total<20?`。距離 20★ 門檻還差 ${20-value.total}★，仍須符合 Call Game 其他條件。`:''));
      button.tabIndex=0;button.setAttribute('role','button');button.setAttribute('aria-label',(side==='player'?'我方':'對手')+'分數來源，點擊查看');
      button.onclick=explain;button.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();explain();}};
    }
  }
  function paintTargetsAndRoutes() {
    if(!global.document)return;
    const current=state();
    const board=document.getElementById('boardWrap');if(!board)return;
    board.querySelectorAll('.xlw-action-label').forEach(e=>e.remove());
    board.querySelectorAll('.xlw-route-target').forEach(e=>e.classList.remove('xlw-route-target'));
    board.querySelectorAll('.xlw-goal-contributor').forEach(e=>e.classList.remove('xlw-goal-contributor'));
    board.querySelector('#xlwAttackRoutes')?.remove();
    if(!current.active||current.over)return;
    for(const side of ['player','enemy']){
      strongestLanes(previous?.[side]).forEach(index=>board.querySelectorAll(`.slot[data-zone^="${side}_"][data-index="${index}"]`).forEach(e=>e.classList.add('xlw-goal-contributor')));
    }
    board.querySelectorAll('.slot.xlw-hand-front-legal,.slot.xlw-hand-front-illegal').forEach(slot=>{
      const label=document.createElement('span');label.className='xlw-action-label';
      label.textContent=slot.classList.contains('xlw-hand-front-legal')?'可放置':'不可放置';slot.appendChild(label);
    });
    const routes=[...(current.routes||[])];
    if(current.selectedAttacker){
      board.querySelectorAll(`.slot[data-zone^="enemy_"][data-index="${current.selectedAttacker.idx}"].has-card`).forEach(slot=>{
        slot.classList.add('xlw-route-target');
        const label=document.createElement('span');label.className='xlw-action-label';label.textContent='同戰線目標';slot.appendChild(label);
        routes.push({from:current.selectedAttacker,to:{zone:slot.dataset.zone,idx:Number(slot.dataset.index)},preview:true});
      });
    }
    if(!routes.length)return;
    const rotated=document.documentElement.classList.contains('xlw-force-landscape')&&innerHeight>innerWidth;
    const logical=e=>{const r=e.getBoundingClientRect();return rotated?{left:r.top,top:innerWidth-r.right,width:r.height,height:r.width}:{left:r.left,top:r.top,width:r.width,height:r.height};};
    const origin=logical(board);const matrix=new DOMMatrixReadOnly(getComputedStyle(board).transform);const scale=Math.hypot(matrix.a,matrix.b)||1;
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.id='xlwAttackRoutes';svg.setAttribute('aria-hidden','true');svg.setAttribute('width','1600');svg.setAttribute('height','1100');
    const defs=document.createElementNS(svg.namespaceURI,'defs');svg.appendChild(defs);
    for(const side of ['player','enemy']){const marker=document.createElementNS(svg.namespaceURI,'marker');marker.id='xlw-route-head-'+side;marker.setAttribute('viewBox','0 0 10 10');marker.setAttribute('refX','8');marker.setAttribute('refY','5');marker.setAttribute('markerWidth','7');marker.setAttribute('markerHeight','7');marker.setAttribute('orient','auto');const arrow=document.createElementNS(svg.namespaceURI,'path');arrow.setAttribute('d','M0 0L10 5L0 10z');arrow.setAttribute('fill',side==='player'?'#f1d79b':'#f1a5b7');marker.appendChild(arrow);defs.appendChild(marker);}
    for(const route of routes){
      const a=board.querySelector(`.slot[data-zone="${route.from.zone}"][data-index="${route.from.idx}"]`),b=board.querySelector(`.slot[data-zone="${route.to.zone}"][data-index="${route.to.idx}"]`);if(!a||!b)continue;
      const ar=logical(a),br=logical(b);let x1=(ar.left+ar.width/2-origin.left)/scale,y1=(ar.top+ar.height/2-origin.top)/scale,x2=(br.left+br.width/2-origin.left)/scale,y2=(br.top+br.height/2-origin.top)/scale;
      const length=Math.hypot(x2-x1,y2-y1);if(length<1)continue;const ux=(x2-x1)/length,uy=(y2-y1)/length;const trim=Math.min(ar.height/scale*.43,length*.28);x1+=ux*trim;y1+=uy*trim;x2-=ux*trim;y2-=uy*trim;
      const line=document.createElementNS(svg.namespaceURI,'line');for(const [key,value]of Object.entries({x1,y1,x2,y2}))line.setAttribute(key,String(value));const side=route.from.zone.startsWith('player_')?'player':'enemy';line.setAttribute('stroke',side==='player'?'#f1d79b':'#f1a5b7');line.setAttribute('stroke-width',route.preview?'3':'5');line.setAttribute('marker-end','url(#xlw-route-head-'+side+')');if(route.preview)line.setAttribute('stroke-dasharray','8 8');svg.appendChild(line);
    }
    board.appendChild(svg);
  }
  const api={scoreDifference,presence,unavailableReason,goalProgress,strongestLanes,notice,updateScore,updatePresence,paintTargetsAndRoutes,
    resetScores(){previous=null;scoreEvents={};clearTimeout(scoreTimer);document.getElementById('xlwActionFeedback')?.setAttribute('hidden','');},
    resetConnection(){peerOffline=false;recovering=false;},
    status(text){updatePresence();if(/連線|同步|伺服器/.test(text))return;if(state().active&&(state().myTurn||/無法|不能|不足|只能|請先/.test(text)))notice(text,/無法|不能|不足|只能|請先/.test(text)?'warning':'info');},
    peer(event){const wasOffline=peerOffline;if(event==='offline')peerOffline=true;if(event==='online')peerOffline=false;updatePresence();if(wasOffline&&event==='online')notice('對手已重新連線，對局將依收到的操作繼續。','success');},
    render(){updatePresence();applyScoreEvents();scoreDetails();paintTargetsAndRoutes();}
  };
  global.XLWBFeedback=api;
  global.addEventListener?.('xlw-sync-ready',()=>{const wasRecovering=recovering;recovering=false;updatePresence();const current=state();if(wasRecovering&&current.active&&current.ready&&current.socket===1&&!current.failed)notice('對局操作已補齊，連線恢復完成。','success');});
})(typeof window!=='undefined'?window:globalThis);
