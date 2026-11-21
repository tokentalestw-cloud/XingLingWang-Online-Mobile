const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/game_v8.js'),'utf8');
const slice=(a,b)=>{const i=source.indexOf(a),j=source.indexOf(b,i+1);assert.ok(i>=0&&j>i);return source.slice(i,j);};
const base={require,__dirname,console};vm.runInNewContext(fs.readFileSync(path.join(__dirname,'test_unit_destruction.cjs'),'utf8').split('let tests = 0;')[0],base);
const card=(id,extra={})=>({id,name:id,type:'unit',attack:2,score:1,_xlwInstanceId:id,...extra});
function fixture(){const g=base.fixture();Object.assign(g,{structuredClone,isMultiplayer:false,allCards:[],phase:'召喚階段',xlwBlueStarRequirement:()=>'',performSummonToSlot:async()=>{},triggerAiSummonEffects:async()=>{},xlwIsUnitFairy:c=>!!c.fairy,xlwIsUndeadCard:()=>true,xlwIsAncientCore:c=>c.id==='core',xlwIsAncientRemains:c=>!!c.remains,xlwIsHappyGraveyard:()=>true,xlwGetFactionFieldCard:()=>({id:'SKT-0019'}),showXLWConfirm:async()=>true,showXLWChoiceModal:async()=>0});
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../static/duel_consistency.js'),'utf8'),g);
 for(const [side,fn]of [['player','xlwGetEmptyPlayerSlots'],['enemy','xlwGetEmptyEnemySlots']])g[fn]=()=>['front','back'].flatMap(row=>g.field[side+'_'+row].flatMap((u,idx)=>u?[]:[{zone:side+'_'+row,idx}]));
 vm.runInContext(slice('window.xlwSpecialSummonUnit =','window.xlwIsImmediateEffectBlocked ='),g);return g;}
const grave=(g,own)=>own?g.graveyard:g.XLW_ENEMY.grave;
const setGrave=(g,own,cards)=>{if(own)g.graveyard=cards;else g.XLW_ENEMY.grave=g.enemyGraveyard=cards;};
const hand=(g,own)=>own?g.hand:g.XLW_ENEMY.hand;
for(const own of [true,false])for(const mode of ['replaced','removed','cancel','occupied'])test(`scrap revival preserves the live grave and never overwrites a slot: ${own}/${mode}`,async()=>{
 const g=fixture(),scrap=card('R-RBT-0031'),keep=card('keep');setGrave(g,own,[scrap,keep]);
 g.xlwIsAncientRemains=()=>false;g.xlwSpecialSummonUnitOriginal=g.xlwSpecialSummonUnit;
 const change=()=>{if(mode==='replaced')setGrave(g,own,[structuredClone(scrap),keep]);if(mode==='removed')setGrave(g,own,[keep]);if(mode==='occupied')for(const row of ['front','back'])g.field[(own?'player':'enemy')+'_'+row]=Array.from({length:5},()=>({card:keep}));};
 g.showXLWConfirm=async()=>{change();return true;};g.showXLWChoiceModal=async()=>{change();return mode==='cancel'?null:0;};
 if(!own)change();vm.runInContext(slice('window.xlwResolveMechanicalEffects =','async function xlwSeparateSingleFusedUnit('),g);
 await g.xlwResolveMechanicalEffects({sourceCard:card('a'),targetCard:card('b'),combinedCards:[],targetUnit:{card:card('result')},targetZone:(own?'player':'enemy')+'_front',targetIdx:0},own,[],true);
 const summoned=['front','back'].flatMap(r=>g.field[(own?'player':'enemy')+'_'+r]).filter(u=>u?.card?._xlwInstanceId===scrap._xlwInstanceId).length;
 const success=mode==='replaced'||(!own&&mode==='cancel');assert.equal(summoned,success?1:0);assert.equal(grave(g,own).some(c=>c._xlwInstanceId===scrap._xlwInstanceId),!success&&mode!=='removed');assert.ok(grave(g,own).includes(keep));
});
for(const own of [true,false])for(const mode of ['replaced','removed'])test(`mechanical right-hand retrieval commits against current piles: ${own}/${mode}`,async()=>{
 const g=fixture(),c=card('remains',{remains:true}),keep=card('keep');setGrave(g,own,[c,keep]);
 g.xlwChooseFactionAction=async()=>{setGrave(g,own,mode==='replaced'?[structuredClone(c),keep]:[keep]);if(own)g.hand=[card('drawn')];else g.XLW_ENEMY.hand=[card('drawn')];return 0;};g.isMultiplayer=true;
 vm.runInContext(slice('window.xlwResolveMechanicalEffects =','async function xlwSeparateSingleFusedUnit('),g);
 await g.xlwResolveMechanicalEffects({key:'right',sourceCard:card('RBT-0042'),targetCard:card('core'),combinedCards:[card('RBT-0042'),card('core')],targetUnit:{card:card('result')},targetZone:(own?'player':'enemy')+'_front',targetIdx:0},own,[card('RBT-0042')],false);
 assert.deepEqual(Array.from(hand(g,own),c=>c.id),mode==='replaced'?['drawn','remains']:['drawn']);assert.deepEqual(Array.from(grave(g,own),c=>c.id),['keep']);
});
for(const mode of ['replaced','removed','source_removed','cancel'])test(`fairy recovery revalidates its own source and current hand: ${mode}`,async()=>{
 const g=fixture(),src=card('R-EVL-0016',{fairy:true}),c=card('fairy',{fairy:true}),keep=card('keep');g.graveyard=[src,c,keep];
 g.showXLWChoiceModal=async()=>{g.hand=[card('drawn')];g.graveyard=mode==='source_removed'?[structuredClone(c),keep]:mode==='removed'?[structuredClone(src),keep]:[structuredClone(src),structuredClone(c),keep];return mode==='cancel'?-1:0;};
 vm.runInContext(slice('window.xlwRecoverFairyFromGrave =','window.xlwOnCardEntersGraveyard ='),g);
 assert.equal(await g.xlwRecoverFairyFromGrave(src,true),mode==='replaced');assert.deepEqual(Array.from(g.hand,c=>c.id),mode==='replaced'?['drawn','fairy']:['drawn']);assert.ok(g.graveyard.includes(keep));
});
for(const own of [true,false])for(const mode of ['replaced','removed'])test(`Happy Graveyard cannot exile a stale card or award twice: ${own}/${mode}`,async()=>{
 const g=fixture(),c=card('ordinary'),keep=card('keep');setGrave(g,own,[c,keep]);g.exileCard=(c,side)=>(side==='player'?g.playerExileZone:g.enemyExileZone).push(c);
 let confirms=0;g.showXLWConfirm=async()=>{if(confirms++===0)setGrave(g,own,mode==='replaced'?[structuredClone(c),keep]:[keep]);return true;};if(!own)setGrave(g,own,mode==='replaced'?[structuredClone(c),keep]:[keep]);
 vm.runInContext('async function run(card,isPlayer){'+slice('  // 快樂墓園 (SKT-0019)','  // 1. 炸骷')+'}',g);
 await g.run(c,own);await g.run(c,own);
 // Simulate the duplicate event without repopulating its source pile.
 const expected=mode==='replaced'?1:0;assert.equal((own?g.playerExileZone:g.enemyExileZone).length,expected);assert.equal(own?g.playerBonusScore:g.enemyBonusScore,expected);assert.deepEqual(Array.from(grave(g,own),c=>c.id),['keep']);
});
for(const mode of ['replaced','removed','cancel'])test(`Dream Adventurer searches the current deck without deleting its last unrelated card: ${mode}`,async()=>{
 const g=fixture(),chosen=card('VRT-target',{faction:'虛擬世界'}),keep=card('keep');g.deck=[chosen,keep];g.field.player_front[0]={card:card('VRT-0004'),tapped:true};g.isUnitSilenced=()=>false;g.showXLWChoiceModal=async()=>{g.hand=[card('drawn')];g.deck=mode==='removed'?[keep]:[structuredClone(chosen),keep];return mode==='cancel'?null:0;};
 vm.runInContext(slice('async function xlwResolveVirtualTurnStartEffects()','async function xlwOnUnitReturnedToDeck('),g);await g.xlwResolveVirtualTurnStartEffects();assert.ok(g.deck.includes(keep));assert.equal(g.hand.some(c=>c.id===chosen.id),mode==='replaced');
});
for(const mode of ['cancel','occupied','replaced','removed','cost_resisted'])test(`Big Skull revival pays destruction and retains unplaced grave cards: ${mode}`,async()=>{
 const g=fixture(),a=card('undead-a'),b=card('undead-b'),keep=card('keep');g.graveyard=[a,b,keep];g.getCardTributeCost=c=>c.id==='keep'?1:0;
 const host={card:card('R-SKT-0042')};g.field.player_front[0]=host;
 g.destroyUnit=async(z,i)=>{if(mode!=='cost_resisted')g.field[z][i]=null;};g.showXLWChoiceModal=async()=>{if(mode==='occupied')for(const row of ['front','back'])g.field['player_'+row]=Array.from({length:5},()=>({card:keep}));if(mode==='replaced')g.graveyard=structuredClone(g.graveyard);if(mode==='removed')g.graveyard=[keep];return mode==='cancel'?null:0;};
 vm.runInContext('async function run(card,isPlayer){const graveList=isPlayer?graveyard:XLW_ENEMY.grave;'+slice('  // 6. 大胖骷','window.xlwRecoverFairyFromGrave =').replace(/\n  return true;\n};\s*$/,'\n}') ,g);
 await g.run(card('exiled'),true);
 const units=['front','back'].flatMap(r=>g.field['player_'+r]).filter(u=>u?.card?.id?.startsWith('undead-')).length;assert.equal(units,mode==='replaced'?2:0);assert.ok(g.graveyard.some(c=>c.id==='keep'));if(['cancel','occupied','cost_resisted'].includes(mode))assert.equal(g.graveyard.length,3);
});
