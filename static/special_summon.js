/* Card-specific presentation only. Never changes a card, rule, turn or network message. */
(function(global){
  'use strict';
  const ASSET='/static/summon_fx/';
  const YUKI={name:'雪女',sound:'yuki',size:960,key:'yuki',video:ASSET+'yuki_summon_packed_v2.mp4',poster:ASSET+'yuki_summon_poster_v2.webp',duration:4000};
  const EMPEROR={name:'始皇帝',sound:'emperor',size:1152,key:'emperor',video:ASSET+'emperor_summon_packed_v2.mp4',poster:ASSET+'emperor_summon_poster_v2.webp',army:ASSET+'terracotta_army_v2.webp',duration:4100};
  const CANDY={name:'糖果女孩',sound:'candy',size:960,key:'candy',video:ASSET+'candy_summon_packed_v1.mp4',poster:ASSET+'candy_summon_poster_v1.webp',duration:4100};
  const ANNIE={name:'火把骷髏 小哀妮',sound:'annie',size:960,key:'annie',video:ASSET+'annie_summon_packed_v3.mp4',poster:ASSET+'annie_summon_poster_v3.webp',duration:4200};
  function match(card){
    if(!card)return null;
    if(/^(?:ASSR|R|SR|SSR|SSSR|VR|PR)-SKT-0010(?:-.+)?$/.test(card.id||'')||(/^火把骷髏\s*小哀妮$/.test(card.name||'')&&[card.deck,card.faction,card.race].includes('骷髏人')))return ANNIE;
    if(/^(?:ASSR|R|SR|SSR|SSSR)-CND-0064$/.test(card.id||'')||(card.name==='糖果女孩'&&[card.deck,card.faction,card.race].includes('甜點王國')))return CANDY;
    if(/^(?:ASSR|R|SR|SSR|SSSR)-ART-0059$/.test(card.id||'')||(card.name==='始皇帝'&&[card.deck,card.faction,card.race].includes('藝術品')))return EMPEROR;
    return /^(?:ASSR|R|SR|SSR|SSSR)-VLG-0012$/.test(card.id||'')||
      (card.name==='雪女'&&[card.deck,card.faction,card.race].includes('妖怪村莊'))?YUKI:null;
  }
  function snowParticles(width,height,count=64,random=Math.random){
    return Array.from({length:count},()=>{const depth=.12+random()*.88;return {x:random()*width,y:random()*height,depth,size:1.5+depth*12,speed:22+depth*85,phase:random()*6.283,spin:(random()-.5)*.6};});
  }
  function createVideo(effect=YUKI){const video=document.createElement('video');video.muted=true;video.defaultMuted=true;video.playsInline=true;video.setAttribute('playsinline','');video.setAttribute('webkit-playsinline','');video.preload='auto';video.disablePictureInPicture=true;video.src=effect.video;return video;}
  const warmedVideos=new Map();let active=null;
  function preload(cards){if(!global.document)return;for(const card of cards||[]){const effect=match(card);if(!effect||warmedVideos.has(effect.key))continue;try{const video=createVideo(effect);video.load();warmedVideos.set(effect.key,video);const image=new Image();image.src=effect.poster;if(effect.army){const army=new Image();army.src=effect.army;}}catch(_){}}}
  function compositor(canvas){
    const gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:true,antialias:false,powerPreference:'low-power',preserveDrawingBuffer:false});
    if(!gl)return null;
    const resources=[];
    const shader=(type,source)=>{const item=gl.createShader(type);gl.shaderSource(item,source);gl.compileShader(item);if(!gl.getShaderParameter(item,gl.COMPILE_STATUS)){gl.deleteShader(item);throw Error('Shader compilation failed');}resources.push(['shader',item]);return item;};
    try{
      const program=gl.createProgram();resources.push(['program',program]);
      gl.attachShader(program,shader(gl.VERTEX_SHADER,'attribute vec2 p; varying vec2 uv; void main(){uv=(p+1.0)*0.5;gl_Position=vec4(p,0.0,1.0);}'));
      gl.attachShader(program,shader(gl.FRAGMENT_SHADER,'precision mediump float; varying vec2 uv; uniform sampler2D frame; void main(){vec3 rgb=texture2D(frame,vec2(uv.x*0.5,uv.y)).rgb;float a=texture2D(frame,vec2(0.5+uv.x*0.5,uv.y)).r; a=smoothstep(0.025,0.975,a);gl_FragColor=vec4(rgb*a,a);}'));
      gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error('Shader linking failed');gl.useProgram(program);
      const buffer=gl.createBuffer();resources.push(['buffer',buffer]);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
      const position=gl.getAttribLocation(program,'p');gl.enableVertexAttribArray(position);gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0);
      const texture=gl.createTexture();resources.push(['texture',texture]);gl.bindTexture(gl.TEXTURE_2D,texture);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.uniform1i(gl.getUniformLocation(program,'frame'),0);gl.clearColor(0,0,0,0);gl.viewport(0,0,canvas.width,canvas.height);
      return {draw(video){gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,video);gl.clear(gl.COLOR_BUFFER_BIT);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);},dispose(){for(const [kind,item]of resources)gl['delete'+kind[0].toUpperCase()+kind.slice(1)](item);gl.getExtension('WEBGL_lose_context')?.loseContext();}};
    }catch(_){for(const [kind,item]of resources)gl['delete'+kind[0].toUpperCase()+kind.slice(1)](item);return null;}
  }
  function flakeSprite(near,gold=false){
    const image=document.createElement('canvas');image.width=image.height=48;const ctx=image.getContext('2d');ctx.translate(24,24);if(gold){ctx.fillStyle=near?'#fff1b4':'#dfaa52';ctx.shadowColor='#f8c367';ctx.shadowBlur=near?10:4;ctx.rotate(Math.PI/4);ctx.fillRect(-3,-3,6,6);return image;}ctx.strokeStyle='#e6faff';ctx.lineWidth=near?1.6:1.2;ctx.shadowColor='#8edfff';ctx.shadowBlur=near?4:1;
    for(let i=0;i<6;i++){ctx.rotate(Math.PI/3);ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(0,-16);ctx.moveTo(0,-9);ctx.lineTo(-4,-12);ctx.moveTo(0,-9);ctx.lineTo(4,-12);ctx.stroke();}return image;
  }
  function emberSprite(near){
    const image=document.createElement('canvas');image.width=image.height=48;const ctx=image.getContext('2d');ctx.translate(24,24);ctx.shadowColor='#ff5c1e';ctx.shadowBlur=near?12:6;
    const gradient=ctx.createLinearGradient(0,-16,0,14);gradient.addColorStop(0,'#fff3b5');gradient.addColorStop(.5,'#ffb542');gradient.addColorStop(1,'#e84a18');ctx.fillStyle=gradient;
    ctx.beginPath();ctx.moveTo(0,-17);ctx.bezierCurveTo(2,-6,12,0,8,9);ctx.bezierCurveTo(4,18,-9,12,-7,4);ctx.bezierCurveTo(-5,-4,-2,-6,0,-17);ctx.fill();return image;
  }
  function candySprite(near,tone){
    const image=document.createElement('canvas');image.width=image.height=96;const ctx=image.getContext('2d');ctx.translate(48,48);
    const colors=[['#ff76ad','#a92d66','#ffe1ee'],['#61e0d4','#177e99','#ddfff7'],['#ffd06b','#c36b2b','#fff7db']][tone];
    ctx.shadowColor=colors[0];ctx.shadowBlur=near?8:3;ctx.strokeStyle=colors[1];ctx.lineWidth=2;
    if(tone===2){ctx.fillStyle='#fff4da';ctx.fillRect(-2,8,4,25);}
    else{ctx.fillStyle=colors[0];for(const direction of [-1,1]){ctx.beginPath();ctx.moveTo(direction*16,0);ctx.lineTo(direction*31,-13);ctx.lineTo(direction*27,0);ctx.lineTo(direction*31,13);ctx.closePath();ctx.fill();ctx.stroke();ctx.beginPath();ctx.moveTo(direction*20,-2);ctx.lineTo(direction*28,-8);ctx.moveTo(direction*20,2);ctx.lineTo(direction*28,8);ctx.stroke();}}
    const gradient=ctx.createLinearGradient(-12,-18,13,18);gradient.addColorStop(0,colors[2]);gradient.addColorStop(.35,colors[0]);gradient.addColorStop(1,colors[1]);ctx.fillStyle=gradient;
    ctx.beginPath();ctx.ellipse(0,0,tone===2?18:20,tone===2?18:14,0,0,Math.PI*2);ctx.fill();ctx.stroke();
    ctx.shadowBlur=0;ctx.strokeStyle=colors[2];ctx.lineWidth=3;ctx.beginPath();if(tone===2){ctx.arc(0,0,11,.2,5.5);ctx.arc(0,0,5,5.5,1,false);}else{ctx.moveTo(-7,-10);ctx.lineTo(4,10);ctx.moveTo(1,-11);ctx.lineTo(12,7);}ctx.stroke();ctx.fillStyle='#ffffffb8';ctx.beginPath();ctx.ellipse(-7,-7,6,2,-.35,0,Math.PI*2);ctx.fill();return image;
  }
  function play(card,{zone='',idx=0}={}){
    const effect=match(card);if(!effect||!global.document)return Promise.resolve(false);
    if(active?.key===zone+':'+idx)return active.promise;
    active?.cancel();
    let resolve;const promise=new Promise(done=>resolve=done),overlay=document.createElement('div');overlay.className='xlw-yuki-summon'+(effect.key==='yuki'?'':' xlw-'+effect.key+'-summon');overlay.dataset.effect=effect.key;overlay.dataset.cardId=card.id||'';overlay.dataset.renderMode='poster';
    overlay.innerHTML='<canvas class="xlw-yuki-snow far" aria-hidden="true"></canvas><div class="xlw-yuki-halo" aria-hidden="true"></div><div class="xlw-yuki-performer"><img class="xlw-yuki-poster" alt="雪女登場"><canvas class="xlw-yuki-video" aria-hidden="true"></canvas></div><canvas class="xlw-yuki-snow near" aria-hidden="true"></canvas><div class="xlw-yuki-caption"><strong>雪女</strong></div><button type="button" class="xlw-yuki-skip" aria-label="略過動畫"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button>';
    if(effect.army)overlay.insertAdjacentHTML('afterbegin','<div class="xlw-emperor-army" aria-hidden="true"><img src="'+effect.army+'" alt=""></div>');
    overlay.querySelector('.xlw-yuki-caption strong').textContent=effect.name;
    const owner=zone.startsWith('enemy_')?'對手星靈':'我方星靈';overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');overlay.setAttribute('aria-label',owner+effect.name+'登場動畫');
    document.body.appendChild(overlay);
    const performer=overlay.querySelector('.xlw-yuki-performer'),poster=overlay.querySelector('.xlw-yuki-poster'),canvas=overlay.querySelector('.xlw-yuki-video');poster.src=effect.poster;poster.alt=effect.name+'登場';canvas.width=canvas.height=effect.size;
    let allowMovie=true,renderer=null,video=null,raf=0,loadTimer=0,hardTimer=0,fadeTimer=0,finished=false,disposed=false,lastFrameIndex=-1,lastSnow=0,elapsed=0;
    const oldFocus=document.activeElement;const reduced=global.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    let snow=[];const snowCanvases=[...overlay.querySelectorAll('.xlw-yuki-snow')],sprites=effect.key==='candy'?[0,1,2,3,4,5].map(i=>candySprite(i>=3,i%3)):effect.key==='annie'?[emberSprite(false),emberSprite(true)]:[flakeSprite(false,effect.key==='emperor'),flakeSprite(true,effect.key==='emperor')];
    function size(){const width=overlay.clientWidth,height=overlay.clientHeight,dpr=Math.min(global.devicePixelRatio||1,1.5);for(const c of snowCanvases){c.width=Math.round(width*dpr);c.height=Math.round(height*dpr);c.getContext('2d').setTransform(dpr,0,0,dpr,0,0);}snow=snowParticles(width,height,reduced?20:(width<1000?64:90));if(effect.key==='candy')for(const sweet of snow){sweet.size=8+sweet.depth*22;sweet.speed*=.8;sweet.spin*=2;}if(effect.key==='annie')for(const ember of snow){ember.size=2+ember.depth*8;ember.speed*=1.2;ember.spin*=.3;}if(effect.key==='emperor')for(const mote of snow){mote.size*=.45;mote.speed*=.45;}}
    function finish(){if(finished)return;finished=true;overlay.classList.add('is-leaving');if(video)video.pause();fadeTimer=setTimeout(dispose,reduced?80:240);}
    function dispose(){if(disposed)return;disposed=true;cancelAnimationFrame(raf);clearTimeout(loadTimer);clearTimeout(hardTimer);clearTimeout(fadeTimer);document.removeEventListener('visibilitychange',hidden);global.removeEventListener('pagehide',finish);global.removeEventListener('resize',size);if(video){video.onended=video.onerror=null;video.pause();video.removeAttribute('src');video.load();}renderer?.dispose();overlay.remove();if(active?.promise===promise)active=null;if(oldFocus?.isConnected)oldFocus.focus?.({preventScroll:true});resolve(true);}
    function hidden(){if(document.hidden){finished=true;dispose();}}
    overlay.addEventListener('click',event=>event.stopPropagation());
    const skip=overlay.querySelector('button');skip.onclick=finish;skip.focus({preventScroll:true});overlay.onkeydown=event=>{event.stopPropagation();if(event.key==='Escape'){event.preventDefault();finish();}if(event.key==='Tab'){event.preventDefault();skip.focus();}};
    size();global.addEventListener('resize',size);global.addEventListener('pagehide',finish);document.addEventListener('visibilitychange',hidden);
    active={key:zone+':'+idx,promise,cancel(){finished=true;dispose();}};
    global.xlwPlaySFX?.(effect.sound);
    if(!reduced){try{renderer=compositor(canvas);}catch(_){renderer=null;}}
    if(renderer){
      video=warmedVideos.get(effect.key)||createVideo(effect);warmedVideos.delete(effect.key);video.className='xlw-yuki-source';overlay.appendChild(video);video.currentTime=0;video.onended=finish;
      const fallback=()=>{allowMovie=false;overlay.dataset.renderMode='poster';video?.pause();video.onended=null;};video.onerror=fallback;
      // A failed or slow movie never blocks the duel. Keep the transparent poster and snow.
      loadTimer=setTimeout(()=>{if(lastFrameIndex<0)fallback();},950);
      try{Promise.resolve(video.play()).catch(fallback);}catch(_){fallback();}
    }
    function frame(time){
      if(disposed)return;
      if(!lastSnow)lastSnow=time;
      const dt=Math.min((time-lastSnow)/1000,.05);
      if(time-lastSnow>=15){elapsed+=dt;lastSnow=time;
        const w=overlay.clientWidth,h=overlay.clientHeight;for(const c of snowCanvases)c.getContext('2d').clearRect(0,0,w,h);
        for(const flake of snow){flake.y+=flake.speed*dt*(['emperor','annie'].includes(effect.key)?-1:1);if(['emperor','annie'].includes(effect.key)&&flake.y<-20){flake.y=h+20;flake.x=Math.random()*w;}flake.x+=Math.sin(elapsed*.7+flake.phase)*10*flake.depth*dt;if(flake.y>h+20){flake.y=-20;flake.x=Math.random()*w;}const ctx=snowCanvases[flake.depth>.66?1:0].getContext('2d');ctx.save();ctx.globalAlpha=.18+flake.depth*.65;ctx.translate(flake.x,flake.y);ctx.rotate(flake.phase+elapsed*flake.spin);const s=flake.size;ctx.drawImage(sprites[effect.key==='candy'?(flake.depth>.66?3:0)+Math.min(2,Math.floor(flake.phase/6.283*3)):(flake.depth>.66?1:0)],-s,-s,s*2,s*2);ctx.restore();}

      }
      if(allowMovie&&video&&renderer&&!finished&&video.readyState>=2&&Math.floor(video.currentTime*60)!==lastFrameIndex){try{renderer.draw(video);lastFrameIndex=Math.floor(video.currentTime*60);overlay.dataset.renderMode='video';}catch(_){video.pause();video.onended=null;overlay.dataset.renderMode='poster';}}
      raf=requestAnimationFrame(frame);
    }
    raf=requestAnimationFrame(frame);hardTimer=setTimeout(finish,reduced?1700:effect.duration+500);
    return promise;
  }
  global.XLWSpecialSummon={match,snowParticles,preload,play,cancel(){active?.cancel();}};
})(typeof window==='undefined'?globalThis:window);
