const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');
const slice=(a,b)=>{const i=source.indexOf(a),j=source.indexOf(b,i+1);assert.ok(i>=0&&j>i,a);return source.slice(i,j);};
const card=(id,extra={})=>({id,name:id,type:'unit',attack:2,score:1,_xlwInstanceId:id,...extra});
function fixture(){const g={console,structuredClone,WeakSet,field:Object.fromEntries(['player_front','player_back','enemy_front','enemy_back'].map(z=>[z,Array(5).fill(null)])),hand:[],deck:[],graveyard:[],enemyGraveyard:[],playerExtraDeck:[],enemyExtraDeck:[],playerExileZone:[],enemyExileZone:[],turn:4,phase:'召喚階段',isMyTurn:true,isMultiplayer:false,XLW_ENEMY:{deck:[],hand:[],grave:[]},logBattle(){},render(){},shuffle(){},sendFullGameStateToOpponent(){},isUnitSilenced:()=>false,xlwShowSpellActivationOverlay:async()=>{},castSpellChain:async(c,fn)=>fn(),showXLWConfirm:async()=>true,showXLWChoiceModal:async()=>0,xlwBlueStarRequirement:()=>'',performSummonToSlot:async()=>{},triggerAiSummonEffects:async()=>{},xlwRevealCard:async()=>{},xlwChargeEnergy:async()=>{},xlwGetSteamEnergy:()=>3,xlwConsumeEnergy:()=>true,xlwIsGoatCard:c=>c.goat,xlwIsGoatUnit:u=>u?.card?.goat,xlwIsUnitPowerPlant:c=>!!c.power,draw(){},xlwSetFactionFieldCard(){}};
 g.window=g;vm.createContext(g);vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/duel_consistency.js'),'utf8'),g);
 for(const [side,fn]of [['player','xlwGetEmptyPlayerSlots'],['enemy','xlwGetEmptyEnemySlots']])g[fn]=()=>['front','back'].flatMap(row=>g.field[side+'_'+row].flatMap((u,idx)=>u?[]:[{zone:side+'_'+row,idx}]));
 vm.runInContext(slice('window.xlwSpecialSummonUnit =','window.xlwIsImmediateEffectBlocked ='),g);
 vm.runInContext(slice('function xlwIsFieldMagic(','async function xlwResolveAries('),g);
 vm.runInContext(slice('// Transactional Steam searches:','async function xlwResolveExpansionUnitClick('),g);return g;}
for(const kind of ['principal','space'])for(const mode of ['replaced','removed','cancel'])test(`${kind} search never removes an unrelated deck card after a snapshot: ${mode}`,async()=>{
 const g=fixture(),target=card('target',{goat:true,type:'magic',magic_type:'場地',name:'宇宙山羊星空'}),keep=card('keep');g.deck=[target,keep];g.hand=[card('initial')];let shuffled=0;g.shuffle=()=>shuffled++;
 g.showXLWChoiceModal=async()=>{g.deck=mode==='removed'?[keep]:[structuredClone(target),keep];g.hand=[card('new-draw')];return mode==='cancel'?null:0;};
 const starts=kind==='principal'?['// 5. 校長山羊','// 6. 牧山羊犬']:['// 11. 太空羊妹妹','// 12. 宇宙山羊 回溯羊'];vm.runInContext('async function run(card,isPlayer){'+slice(...starts)+'}',g);
 await g.run({id:kind==='principal'?'SR-GOT-0028':'GOT-0043'},true);assert.ok(g.deck.includes(keep));assert.deepEqual(Array.from(g.hand,c=>c.id),mode==='replaced'?['new-draw','target']:['new-draw']);assert.equal(shuffled,mode==='replaced'?1:0);
});
test('Principal Goat accepts real field magic, not a goat unit merely named after a field',async()=>{
 const g=fixture(),field=card('field',{goat:true,type:'magic',magic_type:'場地'});g.deck=[card('unit',{goat:true,name:'宇宙山羊太羊學院'}),field];g.showXLWChoiceModal=async(t,m,options)=>{assert.equal(options.length,1);return 0;};vm.runInContext('async function run(card,isPlayer){'+slice('// 5. 校長山羊','// 6. 牧山羊犬')+'}',g);await g.run({id:'SR-GOT-0028'},true);assert.equal(g.hand[0].id,'field');assert.equal(g.deck[0].id,'unit');
});
for(const mode of ['replaced','removed','cancel','occupied'])test(`Power Ball keeps an unplaced hand unit and draws only on successful placement: ${mode}`,async()=>{
 const g=fixture(),spell=card('C-ELE-0035',{type:'magic'}),target=card('power',{power:true,tribute:0}),keep=card('keep');g.hand=[spell,target,keep];let menus=0,drawn=0;g.draw=n=>drawn+=n;
 g.showXLWChoiceModal=async()=>{menus++;if(menus===1)return 0;if(mode==='replaced')g.hand=structuredClone(g.hand);if(mode==='removed')g.hand=[keep];if(mode==='occupied')for(const z of ['player_front','player_back'])g.field[z]=Array(5).fill({card:keep});return mode==='cancel'?null:0;};
 vm.runInContext('async function run(card,handIndex){if(false){'+slice('  } else if (card.id === "C-ELE-0035"','  // 11. C-CRB-0033 交通事故')+'}}',g);await g.run(spell,0);
 const units=['player_front','player_back'].flatMap(z=>g.field[z]).filter(u=>u?.card?.id==='power');assert.equal(units.length,mode==='replaced'?1:0);assert.equal(g.hand.some(c=>c.id==='power'),!['removed','replaced'].includes(mode));assert.ok(g.hand.some(c=>c.id==='keep'));assert.equal(drawn,0);assert.equal(g.graveyard.filter(c=>c.id===spell.id).length,1);
});
for(const mode of ['replaced','removed'])test(`Rainbow fountain counts only goat units that were actually discarded: ${mode}`,async()=>{
 const g=fixture(),spell=card('GOT-0027',{type:'magic'}),target=card('goat-unit',{goat:true}),magic=card('goat-magic',{goat:true,type:'magic'}),keep=card('keep');g.hand=[spell,target,magic,keep];g.field.player_front[0]={card:card('board-goat',{goat:true}),atkModifier:0};let menus=0;
 g.showXLWChoiceModal=async(t,m,options)=>{menus++;if(menus===1){assert.equal(options.length,1);g.hand=mode==='removed'?[magic,keep]:[keep,structuredClone(target),magic];return 0;}return -1;};
 vm.runInContext('async function run(card,handIndex){if(false){'+slice('  } else if (card.id === "GOT-0027"','  // 6. ',)+'}}',g);await g.run(spell,0);
 assert.ok(g.hand.includes(magic));assert.ok(g.hand.includes(keep));assert.equal(g.graveyard.filter(c=>c.id===target.id).length,mode==='replaced'?1:0);assert.equal(g.field.player_front[0].atkModifier,mode==='replaced'?2:0);
});
for(const phase of ['召喚階段','戰術佈陣','進攻宣言'])test(`Pipi can search once in ${phase}, preserving the selected identity when hand order changes`,async()=>{
 const g=fixture();g.phase=phase;const target=card('tool',{art_subtype:'道具'}),keep=card('return'),untouched=card('deck-keep');g.deck=[target,untouched];g.hand=[keep];const obj={card:card('SR-STP-0026')};g.field.player_front[0]=obj;let menus=0;
 g.showXLWChoiceModal=async()=>{if(++menus===1){g.deck=structuredClone(g.deck);return 0;}g.hand=[structuredClone(target),card('new-draw'),structuredClone(keep)];return 0;};
 assert.equal(await g.xlwActivatePipi(obj,'player_front',0),true);assert.deepEqual(Array.from(g.hand,c=>c.id),['tool','new-draw']);assert.deepEqual(Array.from(g.deck,c=>c.id),['deck-keep','return']);assert.equal(obj.pipiSearchUsedTurn,4);assert.equal(await g.xlwActivatePipi(obj,'player_front',0),false);assert.ok(!JSON.stringify(obj).includes('Busy'));
});
for(const mode of ['decline','removed','source_left','return_left'])test(`Pipi stale selection does not move a replacement card: ${mode}`,async()=>{
 const g=fixture(),target=card('tool',{art_subtype:'道具'}),keep=card('return');g.deck=[target];g.hand=[keep];const obj={card:card('SR-STP-0026')};g.field.player_front[0]=obj;let menus=0;
 g.showXLWChoiceModal=async()=>{if(++menus===1){if(mode==='source_left')g.field.player_front[0]=null;if(mode==='removed')g.deck=[];return mode==='decline'?-1:0;}g.hand=[target,card('new-draw')];return 0;};
 await g.xlwActivatePipi(obj,'player_front',0);if(mode==='return_left'){assert.deepEqual(Array.from(g.hand,c=>c.id),['tool','new-draw']);assert.equal(g.deck.length,0);}else{assert.deepEqual(Array.from(g.hand,c=>c.id),['return']);assert.notEqual(obj.pipiSearchUsedTurn,4);}
});
for(const phase of ['抽牌階段','防守階段','結束階段'])test(`Pipi cannot activate in ${phase}`,async()=>{const g=fixture();g.phase=phase;g.deck=[card('tool',{art_subtype:'道具'})];const obj={card:card('SR-STP-0026')};g.field.player_front[0]=obj;g.showXLWChoiceModal=()=>assert.fail('illegal phase must not open a choice');assert.equal(await g.xlwActivatePipi(obj,'player_front',0),false);});
test('Pipi immediate effect charges two without automatically performing its active search',async()=>{const g=fixture();let charged=0;g.xlwChargeEnergy=async n=>charged+=n;g.showXLWChoiceModal=()=>assert.fail('search is not immediate');vm.runInContext('async function run(card,isPlayer){'+slice('      // 7. 黑暗商人 皮皮','      // 8. 航海商人 佐希')+'}',g);await g.run({id:'SR-STP-0026'},true);assert.equal(charged,2);});
for(const mode of ['replaced','removed'])test(`Zoxi retrieves from the current top-card selection and keeps all unselected cards: ${mode}`,async()=>{
 const g=fixture(),target=card('tool',{art_subtype:'道具'}),keep=card('keep');g.deck=[keep,target];g.showXLWChoiceModal=async(title)=>{if(title.includes('挑選道具')){g.deck=mode==='removed'?[keep]:[keep,structuredClone(target)];g.hand=[card('drawn')];}return 0;};vm.runInContext('async function run(card,isPlayer){'+slice('      // 8. 航海商人 佐希','      // 9. 蒸汽魔盜團')+'}',g);await g.run({id:'SR-STP-0031'},true);assert.equal(g.deck.length,1);assert.equal(g.deck[0].id,'keep');assert.deepEqual(Array.from(g.hand,c=>c.id),mode==='replaced'?['drawn','tool']:['drawn']);
});
test('viewed deck cards can be ordered top-first, without duplicating a card removed during selection',async()=>{
 const g=fixture(),a=card('a'),b=card('b'),c=card('c'),keep=card('outside');g.deck=[keep,a,b,c];let menus=0;g.showXLWChoiceModal=async()=>{if(++menus===1){g.deck=[keep,structuredClone(a),structuredClone(c)];return 2;}return 0;};await g.xlwOrderViewedSteamCards([a,b,c],true);assert.deepEqual(Array.from(g.deck,c=>c.id),['outside','a','c']);
});

test('Pipi pending interaction is cleared before its final snapshot and effects continue after the source leaves',async()=>{
 const g=fixture(),tool=card('tool',{art_subtype:'道具'}),returned=card('returned');g.deck=[tool];g.hand=[returned];g.isMultiplayer=true;const obj={card:card('SR-STP-0026')};g.field.player_front[0]=obj;
 g.xlwRevealCard=async()=>{assert.ok(g.XLW_pipiSearchWaiting);g.field.player_front[0]=null;};g.sendFullGameStateToOpponent=()=>assert.equal(g.XLW_pipiSearchWaiting,false);
 assert.equal(await g.xlwActivatePipi(obj,'player_front',0),true);assert.deepEqual(Array.from(g.hand,c=>c.id),['tool']);assert.deepEqual(Array.from(g.deck,c=>c.id),['returned']);assert.equal(g.XLW_pipiSearchWaiting,false);assert.ok(!JSON.stringify(obj).includes('SearchBusy'));
});
