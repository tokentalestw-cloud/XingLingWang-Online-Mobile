/* One explicit, dismissible record window; no permanent text over the battlefield. */
(function(global){
  'use strict';
  let overlay=null,content=null,summary=null,previousFocus=null,pending=false;
  function close(){if(!overlay)return;overlay.remove();overlay=null;previousFocus?.focus?.();}
  function render(){
    if(!overlay)return;
    const data=global.xlwReadBattleRecord?.() || {logs:[]};
    summary.textContent=`第 ${data.turn || 0} 回合・${data.phase || '尚未開始'}　我方 ${data.player ?? 0}★ / 對手 ${data.enemy ?? 0}★`;
    const position=content.scrollTop;
    content.replaceChildren();
    const recent=global.XLWDuelEvents?.recent() || [];
    if(recent.length){
      const heading=document.createElement('h3');heading.textContent='最近操作';content.appendChild(heading);
      for(const event of recent.slice(0,12)){
        const line=document.createElement('p');line.textContent=`${event.side==='player'?'我方':'對手'}・${global.XLWDuelEvents.titles[event.kind] || '操作'}｜${event.card?.name || ''} ${event.detail || ''}`;
        content.appendChild(line);
      }
    }
    const heading=document.createElement('h3');heading.textContent='對戰記錄';content.appendChild(heading);
    for(const text of data.logs.length?data.logs:['尚無對戰記錄']){
      const line=document.createElement('p');line.textContent=String(text);content.appendChild(line);
    }
    content.scrollTop=position;
  }
  function refresh(){
    if(!overlay || pending)return;
    pending=true;
    global.requestAnimationFrame(()=>{pending=false;render();});
  }
  function open(){
    if(overlay){refresh();return;}
    previousFocus=document.activeElement;
    overlay=document.createElement('div');overlay.id='xlwBattleRecord';
    const panel=document.createElement('section');panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-labelledby','xlwBattleRecordTitle');
    const header=document.createElement('header'),title=document.createElement('h2'),button=document.createElement('button');
    title.id='xlwBattleRecordTitle';title.textContent='對戰記錄';button.type='button';button.textContent='關閉';button.onclick=close;
    header.append(title,button);summary=document.createElement('p');summary.className='battle-record-summary';
    content=document.createElement('div');content.className='battle-record-content';content.tabIndex=0;
    panel.append(header,summary,content);overlay.appendChild(panel);
    overlay.onclick=event=>{if(event.target===overlay)close();};
    overlay.onkeydown=event=>{
      if(event.key==='Escape'){event.stopPropagation();close();}
      if(event.key==='Tab'){event.preventDefault();(document.activeElement===button?content:button).focus();}
    };
    document.body.appendChild(overlay);render();button.focus();
  }
  function merge(local,incoming){
    const counts=new Map();
    for(const line of local)counts.set(line,(counts.get(line)||0)+1);
    const fresh=[];
    for(const raw of incoming.slice(0,80)){
      const line=String(raw).replace(/我方|對手|敵方/g,word=>word==='我方'?'對手':'我方');
      if(counts.get(line))counts.set(line,counts.get(line)-1);else fresh.push(line);
    }
    return [...fresh,...local].slice(0,500);
  }
  global.XLWBattleRecord={open,close,refresh,merge};
})(typeof window==='undefined'?globalThis:window);
