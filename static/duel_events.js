/* Read-only public action journal. Animation never holds the transport or ACK queue. */
(function (global) {
  'use strict';
  const titles = {summon:'召喚',move:'移動',grave:'送入墓地',exile:'除外',leave:'離開場上',
    draw:'抽牌',hand:'手牌變動',deck:'牌庫變動',extra:'額外區變動',recover:'回收卡牌',
    attack:'進攻宣言',cancel:'取消進攻',tap:'橫放',stand:'轉正',stats:'能力變化',equip:'裝備變化',
    field:'場地變更',phase:'階段推進',spell:'魔法／反制發動',effect:'效果發動'};
  const cardView = card => card ? {id:card.id, instance:card._xlwInstanceId,
    name:String(card.name || card.id || '卡牌').slice(0,80),
    image:typeof card.image === 'string' && /^\/static\//.test(card.image) ? card.image : ''} : null;
  const same = (a,b) => a && b && (a.instance && b.instance ? a.instance === b.instance : a.id === b.id);
  const location = item => `${item.zone.endsWith('front')?'前排':'後排'}第 ${item.idx+1} 欄`;
  const count = list => (list || []).filter(Boolean).length;
  function capture(raw) {
    const result = {active:raw.active,quiet:raw.quiet,turn:raw.turn,phase:raw.phase,myTurn:raw.myTurn,
      next:raw.next || '',sides:{}};
    for (const side of ['player','enemy']) {
      const data=raw.sides?.[side] || {};
      result.sides[side]={board:[],grave:(data.grave||[]).filter(Boolean).map(cardView),
        exile:(data.exile||[]).filter(Boolean).map(cardView),extra:count(data.extra),
        hand:Number(data.hand)||0,deck:Number(data.deck)||0,field:cardView(data.field)};
      for(const row of ['front','back']) (data[row]||[]).forEach((unit,idx)=>{
        if(!unit?.card)return;
        result.sides[side].board.push({card:cardView(unit.card),zone:side+'_'+row,idx,
          tapped:!!unit.tapped,attacking:!!unit.attacking,
          target:unit.target?`${unit.target.zone}:${unit.target.idx}`:'',
          stats:JSON.stringify([unit.card.attack,unit.card.score,unit.atkModifier,unit.bonusScore,
            unit.irrigation,unit.decay,unit.hasDecay,unit.permanentAtkBonus]),
          equip:JSON.stringify(unit.equipments||[])});
      });
    }
    return result;
  }
  function additions(before,after) {
    const pool=[...before];
    return after.filter(card=>{
      const idx=pool.findIndex(old=>same(old,card));
      if(idx<0)return true;
      pool.splice(idx,1);return false;
    });
  }
  function diff(before,after) {
    if(!before || !after.active || after.quiet || !before.active || before.quiet || after.turn<before.turn)return [];
    const events=[];
    const add=(kind,side,card,detail)=>events.push({kind,side,card,detail});
    for(const side of ['player','enemy']) {
      const old=before.sides[side],next=after.sides[side],pool=[...old.board];
      const graves=additions(old.grave,next.grave),exiles=additions(old.exile,next.exile);
      for(const item of next.board) {
        let idx=pool.findIndex(previous=>same(previous.card,item.card)&&previous.zone===item.zone&&previous.idx===item.idx);
        if(idx<0)idx=pool.findIndex(previous=>same(previous.card,item.card));
        if(idx<0){add('summon',side,item.card,location(item));continue;}
        const previous=pool.splice(idx,1)[0];
        if(previous.zone!==item.zone||previous.idx!==item.idx)add('move',side,item.card,`${location(previous)} → ${location(item)}`);
        if(item.attacking&&(!previous.attacking||item.target!==previous.target))add('attack',side,item.card,location(item));
        else if(previous.attacking&&!item.attacking)add(item.tapped?'tap':'stand',side,item.card,'進攻姿態已結束');
        else if(item.tapped!==previous.tapped)add(item.tapped?'tap':'stand',side,item.card,location(item));
        if(item.stats!==previous.stats)add('stats',side,item.card,`${location(item)}・請查看卡牌目前數值`);
        if(item.equip!==previous.equip)add('equip',side,item.card,location(item));
      }
      for(const item of pool)if(!graves.some(c=>same(c,item.card))&&!exiles.some(c=>same(c,item.card)))
        add('leave',side,item.card,location(item));
      for(const card of graves)add('grave',side,card,'卡牌已進入墓地');
      for(const card of exiles)add('exile',side,card,'卡牌已進入除外區');
      if(!same(old.field,next.field)&&(old.field||next.field))add('field',side,next.field||old.field,next.field?'場地卡已放置':'場地卡已離場');
      const hand=next.hand-old.hand,deck=next.deck-old.deck;
      if(hand>0&&deck<0)add('draw',side,null,`抽取 ${Math.min(hand,-deck)} 張牌（不公開內容）`);
      else if(hand)add('hand',side,null,`手牌 ${hand>0?'+':''}${hand} 張，目前 ${next.hand} 張`);
      if(deck&&!(hand>0&&deck<0))add('deck',side,null,`牌庫 ${deck>0?'+':''}${deck} 張，剩餘 ${next.deck} 張`);
      if(next.extra!==old.extra)add('extra',side,null,`額外區 ${next.extra-old.extra>0?'+':''}${next.extra-old.extra} 張`);
    }
    if(before.phase!==after.phase||before.myTurn!==after.myTurn||before.turn!==after.turn)
      add('phase',after.myTurn?'player':'enemy',null,`第 ${after.turn} 回合・${after.phase}`);
    return events;
  }
  function group(events) {
    const result=[];
    for(const event of events) {
      const previous=result.find(e=>e.kind===event.kind&&e.side===event.side&&e.kind!=='phase');
      if(previous) {
        previous.count=(previous.count||1)+1;
        if(event.card?.name && previous.names.length<3)previous.names.push(event.card.name);
        previous.detail=`${previous.names.join('、')}${previous.count>previous.names.length?'等':''}（共 ${previous.count} 項）`;
      } else result.push({...event,names:event.card?[event.card.name]:[]});
    }
    return result;
  }
  let previous=null,timer=null,box=null,panel=null,nextText='',serial=0,remoteLogs=[];
  const queue=[],history=[],seen=new Map();
  function ensureUI() {
    if(box?.isConnected)return;
    box=global.document.createElement('aside');box.id='xlwDuelEvents';
    box.setAttribute('aria-label','對戰操作提示');
    const status=global.document.createElement('div');status.className='duel-event-current';
    status.setAttribute('role','status');status.setAttribute('aria-live','polite');
    const image=global.document.createElement('img');image.alt='';
    const text=global.document.createElement('div');
    for(const tag of ['strong','b','span'])text.appendChild(global.document.createElement(tag));
    status.append(image,text);
    const next=global.document.createElement('p');next.className='duel-event-next';
    const button=global.document.createElement('button');button.type='button';button.textContent='最近操作';button.setAttribute('aria-expanded','false');
    panel=global.document.createElement('ol');panel.id='xlwDuelEventHistory';panel.hidden=true;
    button.setAttribute('aria-controls',panel.id);
    button.onclick=()=>{panel.hidden=!panel.hidden;button.setAttribute('aria-expanded',String(!panel.hidden));};
    box.append(status,next,button,panel);global.document.body.appendChild(box);
  }
  function paint(event) {
    if(!global.document)return;
    ensureUI();box.hidden=false;
    const status=box.querySelector('.duel-event-current');status.dataset.side=event.side;
    const image=status.querySelector('img');image.hidden=!event.card?.image;
    if(event.card?.image)image.src=event.card.image;
    const text=status.lastElementChild;
    text.children[0].textContent=`${event.side==='player'?'我方':'對手'}・${titles[event.kind]||'操作'}${event.count>1?' ×'+event.count:''}`;
    text.children[1].textContent=event.card?.name||'';
    text.children[2].textContent=event.detail||'';
    box.querySelector('.duel-event-next').textContent=nextText;
    paintHistory();
  }
  function paintHistory() {
    if(!panel)return;
    panel.replaceChildren();
    for(const item of history.slice(0,12)) {
      const line=global.document.createElement('li');
      line.textContent=`${item.side==='player'?'我方':'對手'} ${titles[item.kind]||'操作'}｜${item.card?.name||item.detail}${item.card?'・'+item.detail:''}`;
      panel.appendChild(line);
    }
  }
  function play() {
    timer=null;
    const event=queue.shift();
    if(!event)return;
    paint(event);
    timer=global.setTimeout(play,queue.length>3?650:1200);
  }
  function push(event,key) {
    if(!event||!titles[event.kind])return;
    const now=Date.now();
    for(const [id,time]of seen)if(now-time>2500)seen.delete(id);
    if(key&&seen.has(key))return;
    if(key)seen.set(key,now);
    if(seen.size>128)seen.delete(seen.keys().next().value);
    history.unshift({...event,serial:++serial});if(history.length>24)history.length=24;
    paintHistory();
    if(queue.length>=6)queue.shift();queue.push(event);
    if(timer===null)play();
  }
  function observe(raw) {
    if(!raw)return;
    if(!raw.active){reset();return;}
    const next=capture(raw);nextText=next.next;
    for(const event of group(diff(previous,next)))push(event);
    previous=next;
    if(box)box.querySelector('.duel-event-next').textContent=nextText;
  }
  function activation(card,side) {
    if(!previous?.active||previous.quiet)return;
    side=/^(player(?:_|$)|me$)/.test(side)?'player':'enemy';
    push({kind:'spell',side,card:cardView(card),detail:'請留意目標選擇與反制時窗'},`spell:${side}:${card?._xlwInstanceId||card?.id}`);
  }
  function effect(text) {
    if(!previous?.active||previous.quiet)return;
    const parsed=global.XLWBFeedback?.effectMessage(text) ||
      (/效果發動|效果觸發|無效化|發動了|發動【/.test(text)?{title:'',detail:String(text)}:null);
    if(!parsed)return;
    const side=/對手|敵方/.test(parsed.title)?'enemy':'player';
    const card=previous.sides[side].board.find(item=>parsed.title.includes(item.card.name))?.card;
    push({kind:'effect',side,card,detail:`${parsed.title}${parsed.title?'：':''}${parsed.detail}`.slice(0,220)},`effect:${text}`);
  }
  function syncLogs(lines,quiet=false) {
    if(!Array.isArray(lines))return;
    const pool=[...remoteLogs],fresh=lines.slice(0,30).filter(line=>{
      const idx=pool.indexOf(line);
      if(idx<0)return true;
      pool.splice(idx,1);return false;
    });
    remoteLogs=lines.slice(0,30);
    if(quiet)return;
    for(const line of fresh.slice(0,6).reverse()) {
      // The sender's own effects only; already mirrored opponent logs must not echo.
      const text=String(line).replace(/^T\d+\s*\|\s*/, '');
      if(/對手|敵方/.test(text.split(/[：:]/)[0]))continue;
      effect(text.replace(/我方|對手|敵方/g,word=>word==='我方'?'對手':'我方'));
    }
  }
  function reset() {
    previous=null;queue.length=0;history.length=0;seen.clear();
    global.clearTimeout(timer);timer=null;nextText='';remoteLogs=[];
    if(box){box.remove();box=null;panel=null;}
  }
  // A fixed, short beat; never wait for the visual queue or a peer acknowledgement.
  const beat=()=>global.document?.hidden?Promise.resolve():new Promise(resolve=>global.setTimeout(resolve,450));
  global.XLWDuelEvents={capture,diff,group,observe,activation,effect,syncLogs,reset,beat,
    diagnostics:()=>({queued:queue.length,history:history.length,seen:seen.size})};
})(typeof window!=='undefined'?window:globalThis);
