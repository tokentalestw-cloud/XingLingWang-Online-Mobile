/* XingLingWang audio: local synthesis, bounded voices, no game-state mutations. */
(function(global){
  'use strict';
  const BANK = {
    click: {group:'ui',gap:.065,notes:[[640,.045,.12,0,'sine',520]]},
    select: {group:'ui',gap:.08,notes:[[587,.09,.07],[880,.09,.035,.025]]},
    draw: {gap:.12,noise:[.13,.055,1600],notes:[[360,.12,.045,0,'triangle',590]]},
    summon: {gap:.18,noise:[.09,.06,700],notes:[[145,.22,.16,0,'sine',82],[440,.22,.065,.025],[587,.3,.045,.06]]},
    tribute: {gap:.45,notes:[[147,.48,.14],[294,.4,.075,.03,'triangle'],[440,.42,.065,.09],[587,.5,.05,.15],[880,.5,.035,.22]]},
    spell: {gap:.26,noise:[.28,.035,2600],notes:[[587,.3,.07],[740,.3,.055,.065],[880,.36,.045,.13],[1175,.4,.025,.2]]},
    field: {gap:.5,notes:[[147,.65,.10,0,'sine',220],[294,.6,.06,.08],[440,.65,.04,.15],[587,.6,.025,.23]]},
    coin: {gap:.2,notes:[[880,.1,.075],[1175,.17,.045,.075],[1480,.2,.02,.14]]},
    attack: {gap:.14,noise:[.16,.09,1100],notes:[[220,.21,.13,0,'triangle',85],[96,.24,.13,0,'sine',52]]},
    destroy: {gap:.18,noise:[.24,.10,1500],notes:[[330,.23,.08,0,'triangle',92],[110,.25,.08]]},
    shield: {gap:.18,noise:[.1,.045,2100],notes:[[880,.19,.07,0,'triangle',660],[587,.3,.055]]},
    phase: {gap:.4,notes:[[440,.19,.07],[587,.25,.055,.07]]},
    turn: {gap:.65,notes:[[294,.24,.07],[440,.26,.065,.07],[587,.4,.055,.15]]},
    enemyTurn: {gap:.65,notes:[[440,.2,.055],[294,.32,.06,.1]]},
    score: {gap:.8,notes:[[740,.17,.04],[880,.22,.035,.06]]},
    victory: {gap:2.5,result:true,notes:[[294,.5,.085],[440,.5,.075,.12],[587,.65,.07,.25],[740,.7,.055,.4],[880,1,.05,.56],[1175,.9,.025,.75]]},
    defeat: {gap:2.5,result:true,notes:[[294,.5,.08],[262,.5,.065,.18],[220,.65,.055,.36],[147,.9,.07,.56]]}
  };
  const clamp=(value,fallback=.65)=>Number.isFinite(Number(value))?Math.max(0,Math.min(1,Number(value))):fallback;
  function createEngine(ctx,settings,{offline=false}={}){
    const master=ctx.createGain(), tone=ctx.createBiquadFilter(), compressor=ctx.createDynamicsCompressor();
    tone.type='lowpass'; tone.frequency.value=6200; tone.Q.value=.45;
    compressor.threshold.value=-12; compressor.knee.value=18; compressor.ratio.value=8;
    compressor.attack.value=.004; compressor.release.value=.16;
    tone.connect(compressor); compressor.connect(master); master.connect(ctx.destination);
    master.gain.value=settings.enabled?settings.volume*2:0;
    const active=new Set(), last=new Map(); let resultUntil=0;
    const noise=ctx.createBuffer(1,Math.ceil(ctx.sampleRate*.35),ctx.sampleRate);
    let seed=7301; const samples=noise.getChannelData(0);
    for(let i=0;i<samples.length;i++){seed=(seed*16807)%2147483647;samples[i]=(seed/2147483647*2-1);}
    function setVolume(){const now=ctx.currentTime;master.gain.cancelScheduledValues(now);master.gain.setTargetAtTime(settings.enabled?settings.volume*2:0,now,.012);}
    function stop(){for(const entry of [...active]){try{entry.source.stop();}catch(_){}entry.cleanup();}last.clear();resultUntil=0;}
    function voice(source,level,start,duration,filter){
      const envelope=ctx.createGain(), nodes=[source,envelope];
      if(filter){nodes.push(filter);source.connect(filter);filter.connect(envelope);}else source.connect(envelope);
      envelope.connect(tone);
      envelope.gain.setValueAtTime(0,start);
      envelope.gain.linearRampToValueAtTime(level,start+.004);
      envelope.gain.exponentialRampToValueAtTime(.0001,start+Math.max(.012,duration-.012));
      envelope.gain.linearRampToValueAtTime(0,start+duration);
      const entry={source,cleanup(){active.delete(entry);for(const node of nodes)try{node.disconnect();}catch(_){}}};
      active.add(entry);source.onended=entry.cleanup;source.start(start);source.stop(start+duration+.005);
    }
    function play(type){
      const item=BANK[type],now=ctx.currentTime;
      if(!item||!settings.enabled||settings.volume===0||(!offline&&ctx.state!=='running'))return false;
      if(now-(last.get(type)??-100)<item.gap||(!item.result&&now<resultUntil))return false;
      if(type==='summon'&&now-(last.get('tribute')??-100)<.65)return false;
      const count=item.notes.length+(item.noise?1:0);
      if(item.result){stop();resultUntil=now+1.8;}else if(active.size+count>24)return false;
      last.set(type,now);
      const gain=(item.group==='ui'?settings.ui:settings.battle);
      if(gain===0)return false;
      for(const [frequency,duration,level,delay=0,wave='sine',end] of item.notes){
        const source=ctx.createOscillator();source.type=wave;
        source.frequency.setValueAtTime(frequency,now+delay);
        if(end)source.frequency.exponentialRampToValueAtTime(end,now+delay+duration*.8);
        voice(source,level*gain,now+delay,duration);
      }
      if(item.noise){const [duration,level,freq]=item.noise,source=ctx.createBufferSource(),filter=ctx.createBiquadFilter();
        source.buffer=noise;filter.type='bandpass';filter.frequency.value=freq;filter.Q.value=.6;
        voice(source,level*gain,now,duration,filter);
      }
      return true;
    }
    return {play,stop,setVolume,get activeVoices(){return active.size;}};
  }
  function read(key,fallback){try{return global.localStorage.getItem(key)??fallback;}catch(_){return fallback;}}
  const settings={enabled:read('xlw_sfx_enabled','true')!=='false',volume:clamp(read('xlw_sfx_volume',.65)),battle:clamp(read('xlw_sfx_battle',.85),.85),ui:clamp(read('xlw_sfx_ui',.55),.55)};
  let ctx,engine,previousBattle=null;
  function save(){try{for(const [name,value]of Object.entries(settings))global.localStorage.setItem('xlw_sfx_'+(name==='enabled'?'enabled':name),String(value));}catch(_){}updateButton();}
  function updateButton(){const b=global.document?.getElementById('xlwSfxToggleBtn');if(b){b.textContent=settings.enabled&&settings.volume>0?'音效：開 ▾':'音效：關 ▾';b.setAttribute('aria-label','音效設定');b.setAttribute('aria-haspopup','dialog');}}
  function unlock(){
    if(!settings.enabled||global.document?.hidden)return;
    try{if(!ctx||ctx.state==='closed'){const Context=global.AudioContext||global.webkitAudioContext;if(!Context)return;ctx=new Context({latencyHint:'interactive'});engine=createEngine(ctx,settings);}
      if(ctx.state==='suspended'||ctx.state==='interrupted')Promise.resolve(ctx.resume()).catch(()=>{});
    }catch(_){}
  }
  function play(type){
    if(global.document?.hidden||!engine)return false;
    const state=global.xlwGetBattleFeedbackState?.();
    if(state?.multi&&state.active&&(!state.ready||state.failed))return false;
    try{return engine.play(type);}catch(_){return false;}
  }
  function observeBattle(next,quiet){
    const previous=previousBattle;previousBattle=next;
    if(!previous||quiet||!global.XLW_gameInProgress)return;
    const units=score=>Object.values(score?.units||{}).reduce((sum,unit)=>sum+unit.count,0);
    if(units(next.player)+units(next.enemy)>units(previous.player)+units(previous.enemy))play('summon');
  }
  function toggle(){settings.enabled=!settings.enabled;save();if(!settings.enabled)engine?.stop();else unlock();engine?.setVolume();if(settings.enabled)play('select');}
  function openSettings(){
    unlock();const existing=document.getElementById('xlwAudioSettings');if(existing){existing.remove();return;}
    const panel=document.createElement('div');panel.id='xlwAudioSettings';panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-labelledby','xlwAudioTitle');
    panel.innerHTML=`<div class="xlw-audio-card"><div class="xlw-audio-heading"><strong id="xlwAudioTitle">星靈音效</strong><button type="button" data-close aria-label="關閉音效設定">✕</button></div><label class="xlw-audio-enable"><span>啟用音效</span><input type="checkbox" data-enabled></label><label>總音量 <output data-output="volume"></output><input aria-label="總音量" type="range" min="0" max="100" data-volume="volume"></label><label>戰鬥與卡牌 <output data-output="battle"></output><input aria-label="戰鬥與卡牌音量" type="range" min="0" max="100" data-volume="battle"></label><label>操作提示 <output data-output="ui"></output><input aria-label="操作提示音量" type="range" min="0" max="100" data-volume="ui"></label><div class="xlw-audio-footer"><span>設定會自動保存</span><button type="button" data-preview>試聽召喚</button></div></div>`;
    const close=()=>{panel.remove();document.getElementById('xlwSfxToggleBtn')?.focus();};
    panel.querySelector('[data-close]').onclick=close;
    panel.onclick=e=>{if(e.target===panel)close();};
    const enabled=panel.querySelector('[data-enabled]');enabled.checked=settings.enabled;enabled.onchange=()=>{if(enabled.checked!==settings.enabled)toggle();};
    for(const input of panel.querySelectorAll('[data-volume]')){const name=input.dataset.volume,output=panel.querySelector(`[data-output="${name}"]`);input.value=Math.round(settings[name]*100);output.textContent=input.value+'%';
      input.oninput=()=>{settings[name]=clamp(Number(input.value)/100);output.textContent=input.value+'%';save();engine?.setVolume();};
      input.onchange=()=>{unlock();play(name==='ui'?'select':'summon');};
    }
    panel.querySelector('[data-preview]').onclick=()=>{unlock();play('summon');};
    panel.onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();close();}if(e.key==='Tab'){const nodes=[...panel.querySelectorAll('button,input')],first=nodes[0],last=nodes[nodes.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}};
    document.body.appendChild(panel);panel.querySelector('[data-close]').focus();
  }
  global.XLWAudio={createEngine,bank:BANK,settings,observeBattle,resetBattle(){previousBattle=null;engine?.stop();},stop(){engine?.stop();},get diagnostics(){return {state:ctx?.state||'locked',activeVoices:engine?.activeVoices||0};}};
  global.xlwPlaySFX=play;global.xlwToggleSFX=toggle;global.xlwOpenAudioSettings=openSettings;
  if(global.document){
    for(const event of ['pointerdown','touchend','keydown'])document.addEventListener(event,unlock,{passive:true,capture:true});
    document.addEventListener('click',e=>{if(e.target.closest?.('#hand .card'))play('select');const button=e.target.closest?.('button');if(button&&!button.disabled&&button.id!=='xlwSfxToggleBtn'&&!button.closest('#xlwAudioSettings'))play('click');},true);
    document.addEventListener('visibilitychange',()=>{if(document.hidden){engine?.stop();if(ctx?.state==='running')Promise.resolve(ctx.suspend()).catch(()=>{});}});
    global.addEventListener('pagehide',()=>engine?.stop());
    document.addEventListener('DOMContentLoaded',updateButton);updateButton();
  }
})(typeof window==='undefined'?globalThis:window);
