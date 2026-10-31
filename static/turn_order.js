(function(global){
  'use strict';
  const other=role=>role==='player1'?'player2':'player1';
  const bit=()=>global.crypto?.getRandomValues?global.crypto.getRandomValues(new Uint8Array(1))[0]&1:(Math.random()<.5?0:1);
  function createController({role='player1',multi=false,send=()=>{},onStart=()=>{},onChange=()=>{},random=bit}={}){
    let state={role,multi,stage:'shuffling',selected:null,winner:null,drawId:null,firstRole:null};
    const cards=random()?[other(role),role]:[role,other(role)];
    const update=()=>onChange({...state});
    return {
      snapshot:()=>({...state}),
      ready(){if(state.stage==='shuffling'){state.stage='pick';update();}},
      pick(selected){
        if(state.stage!=='pick'||![0,1].includes(selected)||(multi&&role!=='player1'))return false;
        state.selected=selected;state.stage='pending';update();
        if(multi)send({action:'turn_order_pick',selected});
        else{state.winner=cards[selected];state.drawId='single';state.stage='choice';update();}
        return true;
      },
      choose(choice){
        if(state.stage!=='choice'||state.winner!==role||!['first','second'].includes(choice))return false;
        if(multi){state.stage='confirming';update();send({action:'turn_order_choice',draw_id:state.drawId,choice});}
        else this.confirm({draw_id:state.drawId,first_role:choice==='first'?role:other(role)});
        return true;
      },
      chooseAI(choice){if(!multi&&state.stage==='choice'&&state.winner!==role&&['first','second'].includes(choice))this.confirm({draw_id:state.drawId,first_role:choice==='first'?other(role):role});},
      reveal(event){
        if(!multi||state.stage==='done'||!['player1','player2'].includes(event.winner_role)||![0,1].includes(event.selected)||!event.draw_id)return false;
        if(state.drawId&&state.drawId!==event.draw_id)return false;
        state={...state,stage:'choice',selected:event.selected,winner:event.winner_role,drawId:event.draw_id};update();return true;
      },
      confirm(event){
        if(state.stage==='done'||!state.drawId||event.draw_id!==state.drawId||!['player1','player2'].includes(event.first_role))return false;
        state.firstRole=event.first_role;state.stage='done';update();onStart(event.first_role===role);return true;
      },
      restore(saved){
        if(!saved||saved.role!==role||saved.multi!==multi||!['shuffling','pick','pending','choice','confirming','done'].includes(saved.stage))return false;
        state={...state,...saved};if(state.stage==='shuffling')state.stage='pick';update();return true;
      }
    };
  }
  let controller,config,timer,aiTimer;
  function getOverlay(){
    let overlay=document.getElementById('xlw-coin-toss-overlay');
    if(!overlay){overlay=document.createElement('div');overlay.id='xlw-coin-toss-overlay';overlay.className='xlw-order-overlay';overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');overlay.setAttribute('aria-labelledby','xlwOrderTitle');
      overlay.innerHTML='<section class="xlw-order-panel"><div class="xlw-order-eyebrow">星靈契約</div><h2 id="xlwOrderTitle">先後攻決定權</h2><p id="xlwOrderStatus" role="status" aria-live="polite"></p><div id="xlwOrderCards" class="xlw-order-cards"></div><div id="xlwOrderActions" class="xlw-order-actions"></div></section>';overlay.addEventListener('keydown',event=>{if(event.key==='Tab'){const buttons=[...overlay.querySelectorAll('button:not(:disabled)')];if(!buttons.length){event.preventDefault();return;}const first=buttons[0],last=buttons[buttons.length-1];if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}}});document.body.appendChild(overlay);}
    return overlay;
  }
  function render(state){
    if(!global.document)return;
    const overlay=getOverlay();overlay.style.display=state.stage==='done'?'none':'flex';
    const row=document.getElementById('xlwOrderCards'),status=document.getElementById('xlwOrderStatus'),actions=document.getElementById('xlwOrderActions');
    row.classList.toggle('is-shuffling',state.stage==='shuffling');row.innerHTML='';actions.innerHTML='';
    const revealed=!!state.winner,isOwn=state.winner===state.role;
    status.textContent=state.stage==='shuffling'?'正在洗混兩張決定卡…':state.stage==='pending'?'翻開決定卡，等待同步結果…':state.stage==='confirming'?'正在確認先後攻順序…':revealed?(isOwn?'抽中「由你決定」，請選擇先攻或後攻。':(state.multi?'由對手取得決定權，等待對手選擇先攻或後攻。':'抽中「敵方決定」，對手 AI 正在選擇先攻或後攻。')):(state.multi&&state.role!=='player1'?'等待房主從兩張卡中選一張。':'兩張卡背相同，請選一張翻開。');
    for(let i=0;i<2;i++){
      const card=document.createElement('button');card.type='button';card.className='xlw-order-card';card.dataset.index=i;
      card.disabled=state.stage!=='pick'||(state.multi&&state.role!=='player1');card.setAttribute('aria-label',`選擇${i===0?'左':'右'}邊的決定卡`);
      const face=!!state.winner&&state.selected===i;
      card.classList.toggle('is-revealed',face);card.classList.toggle('is-unselected',revealed&&!face);
      const art=document.createElement('img');art.src=face?'/static/card_images/turn_order_front_v1.webp':'/static/card_images/turn_order_back_v1.webp';art.alt=face?'決定卡正面':'先後攻決定權卡背';art.draggable=false;card.appendChild(art);
      if(face){const label=document.createElement('span');label.className='xlw-order-face '+(isOwn?'own':'enemy');label.textContent=isOwn?'由你決定':'敵方決定';card.appendChild(label);card.setAttribute('aria-label',label.textContent);}
      card.onclick=()=>{global.xlwPlaySFX?.('draw');controller.pick(i);};row.appendChild(card);
    }
    if(state.stage==='choice'&&isOwn){for(const [choice,label] of [['first','我要先攻'],['second','我要後攻']]){const button=document.createElement('button');button.type='button';button.className='xlw-order-choice';button.textContent=label;button.onclick=()=>controller.choose(choice);actions.appendChild(button);}}
    if(state.stage==='choice'&&!isOwn&&!state.multi&&!aiTimer){aiTimer=setTimeout(()=>{aiTimer=null;controller?.chooseAI(bit()?'first':'second');},1300);}
    if(state.stage==='choice')global.xlwPlaySFX?.('select');
    const focusTarget=actions.querySelector('button')||row.querySelector('button:not(:disabled)');
    if(focusTarget)focusTarget.focus({preventScroll:true});
  }
  const api={createController,
    start(options){if(global.Image){const front=new Image();front.src='/static/card_images/turn_order_front_v1.webp';}clearTimeout(timer);clearTimeout(aiTimer);aiTimer=null;config=options;controller=createController({...options,onChange:render});render(controller.snapshot());global.xlwPlaySFX?.('draw');timer=setTimeout(()=>controller.ready(),900);},
    snapshot(){return controller?.snapshot()||null;},
    restore(saved,options){if(!saved)return;clearTimeout(timer);clearTimeout(aiTimer);aiTimer=null;config=options;controller=createController({...options,onChange:render});controller.restore(saved);},
    receive(event){if(!controller&&config)controller=createController({...config,onChange:render});if(event.action==='turn_order_reveal')controller?.reveal(event);if(event.action==='turn_order_confirmed')controller?.confirm(event);},
    hide(){clearTimeout(timer);clearTimeout(aiTimer);aiTimer=null;const overlay=global.document?.getElementById('xlw-coin-toss-overlay');if(overlay)overlay.style.display='none';},
    error(message){const status=global.document?.getElementById('xlwOrderStatus');if(status)status.textContent=message;}
  };
  global.XLWTurnOrder=api;
})(typeof window==='undefined'?globalThis:window);
