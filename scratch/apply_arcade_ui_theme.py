# -*- coding: utf-8 -*-
import sys, re

def apply_ui_upgrade():
    sys.stdout.reconfigure(encoding='utf-8')

    # ==========================================
    # 1. UPDATE index.html
    # ==========================================
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Replace Left Card Panel HTML inside index.html
    old_panel = r'<aside id="xlwLeftCardPanel".*?</aside>'
    new_panel = """<!-- 左側卡牌詳細資訊看板 (Arcade Comic Style) -->
        <aside id="xlwLeftCardPanel" class="xlw-left-card-panel" onclick="this.style.display='none'">
          <div class="panel-inner">
            <div id="leftPanelPlaceholder" class="placeholder-text">點擊或停懸卡牌<br>在此開啟特寫與技能面板</div>
            <div id="leftCardDetailView" class="card-detail-view" style="display: none;">
              <!-- 頂部英雄/卡牌抬頭斜角橫幅 -->
              <div class="arcade-card-header">
                <div class="arcade-type-badge" id="leftCardTypeBadge">
                  <div class="badge-icon">🛡️</div>
                  <div class="badge-text" id="leftCardTypeSub">防禦型<br><small>TYPE</small></div>
                </div>
                <div class="arcade-title-box">
                  <div class="arcade-card-no" id="leftCardNo">No.009</div>
                  <div class="arcade-card-title" id="leftCardTitle">肉囚貓</div>
                  <div class="arcade-card-sub" id="leftCardSub">MEAT PRISONER CAT</div>
                </div>
                <div class="arcade-rating-box">
                  <div class="stars" id="leftCardStars">⭐⭐⭐</div>
                  <div class="rating-label">能力評級</div>
                </div>
              </div>

              <!-- 中央角色立體展示區 -->
              <div class="arcade-showcase-wrap">
                <div class="arcade-target-aura"></div>
                <div class="detail-img-wrap">
                  <img id="leftPanelImg" src="" alt="card detail image">
                </div>
                <!-- 右側黃色高亮屬性板 -->
                <div class="arcade-stat-panel">
                  <div class="stat-pill">
                    <span class="stat-label">攻擊 ATTACK</span>
                    <span class="stat-val" id="leftCardAtk">9 🔼</span>
                  </div>
                  <div class="stat-pill">
                    <span class="stat-label">星數 STARS</span>
                    <span class="stat-val" id="leftCardScore">3 ⭐</span>
                  </div>
                  <div class="stat-pill">
                    <span class="stat-label">祭品 TRIBUTE</span>
                    <span class="stat-val" id="leftCardTrib">0 ⚡</span>
                  </div>
                  <div class="stat-pill">
                    <span class="stat-label">陣營 FACTION</span>
                    <span class="stat-val" id="leftCardFaction">中立 🏷️</span>
                  </div>
                </div>
              </div>

              <!-- 底部對話說明對話框 -->
              <div class="arcade-quote-bubble">
                <div class="quote-tag" id="leftCardQuoteTag">「強烈技能 Callout」</div>
                <div class="quote-text" id="leftCardEffectText">擁有強化戰術與技能對決的強力效果。</div>
              </div>
            </div>
          </div>
        </aside>"""

    idx_content = re.sub(old_panel, new_panel, idx_content, flags=re.DOTALL)

    # Add Manga Host Corner Avatar at bottom of index.html before body
    if 'xlw-manga-guide-corner' not in idx_content:
        guide_html = """
  <!-- 右下角漫畫社長引導對話框 -->
  <div id="xlwMangaGuideCorner" class="xlw-manga-guide-corner">
    <div class="speech-bubble">
      <div id="mangaGuideText" class="speech-text">左右滑動手牌或選擇卡牌，決定後開始對戰吧！</div>
    </div>
    <div class="guide-avatar-wrap">
      <img src="/static/comic_host_avatar.png" alt="午飯社長" class="guide-avatar-img">
      <div class="guide-name-tag">午飯社長</div>
    </div>
  </div>
"""
        idx_content = idx_content.replace('</body>', guide_html + '\n</body>')

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Updated static/index.html structure successfully!")

    # ==========================================
    # 2. UPDATE game_v8.js (showModal implementation)
    # ==========================================
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    old_modal_start = "function showModal(card, equipments) {"
    old_modal_end = "function setStatus(t) {"

    m_start = js_content.find(old_modal_start)
    m_end = js_content.find(old_modal_end)

    if m_start >= 0 and m_end >= 0:
        new_modal_code = """function showModal(card, equipments) {
  if (!card) return;
  const leftPanel = $("xlwLeftCardPanel");
  const leftImg = $("leftPanelImg");
  const placeholder = $("leftPanelPlaceholder");
  const detailView = $("leftCardDetailView");

  // 清除舊裝備標籤
  const oldContainer = $("leftPanelEquipmentsContainer");
  if (oldContainer) oldContainer.remove();

  if (leftImg && placeholder && detailView) {
    leftImg.src = card.image || "/static/little_traveler.jpeg";
    placeholder.style.display = "none";
    detailView.style.display = "block";

    // 填入街機美學資料
    const cardNoEl = $("leftCardNo");
    if (cardNoEl) cardNoEl.textContent = card.id || "No.000";

    const cardTitleEl = $("leftCardTitle");
    if (cardTitleEl) cardTitleEl.textContent = card.name || "未知卡牌";

    const cardSubEl = $("leftCardSub");
    if (cardSubEl) cardSubEl.textContent = (card.deck || card.faction || "NEUTRAL") + " FACTION";

    const cardAtkEl = $("leftCardAtk");
    if (cardAtkEl) {
      const atkVal = card.attack !== undefined ? card.attack : (card.atk !== undefined ? card.atk : "-");
      cardAtkEl.textContent = `${atkVal} 🔼`;
    }

    const cardScoreEl = $("leftCardScore");
    if (cardScoreEl) cardScoreEl.textContent = `${card.score || 0} ⭐`;

    const cardTribEl = $("leftCardTrib");
    if (cardTribEl) {
      const tribVal = typeof getCardTributeCost === "function" ? getCardTributeCost(card) : (card.tribute || 0);
      cardTribEl.textContent = `${tribVal} ⚡`;
    }

    const cardFactionEl = $("leftCardFaction");
    if (cardFactionEl) cardFactionEl.textContent = `${card.faction || card.deck || "中立"} 🏷️`;

    const cardStarsEl = $("leftCardStars");
    if (cardStarsEl) {
      const starsCount = Math.min(5, Math.max(1, Number(card.score || 3)));
      cardStarsEl.textContent = "⭐".repeat(starsCount);
    }

    const cardTypeBadge = $("leftCardTypeBadge");
    const cardTypeSub = $("leftCardTypeSub");
    if (cardTypeBadge && cardTypeSub) {
      if (card.type === "unit" || card.type === "單位") {
        const atk = parseInt(card.attack, 10) || 0;
        if (atk >= 6) {
          cardTypeBadge.className = "arcade-type-badge attack-type";
          cardTypeSub.innerHTML = `攻擊型<br><small>ATTACK</small>`;
        } else {
          cardTypeBadge.className = "arcade-type-badge defensive-type";
          cardTypeSub.innerHTML = `防禦型<br><small>DEFENSE</small>`;
        }
      } else {
        cardTypeBadge.className = "arcade-type-badge spell-type";
        cardTypeSub.innerHTML = `魔法型<br><small>SPELL</small>`;
      }
    }

    const cardQuoteTag = $("leftCardQuoteTag");
    if (cardQuoteTag) cardQuoteTag.textContent = `【${card.faction || '陣營'}】${card.type === 'unit' ? '單位戰術' : '魔法卡'}`;

    const cardEffectText = $("leftCardEffectText");
    if (cardEffectText) cardEffectText.textContent = card.effect_text || card.description || "此卡片擁有經典戰場效果。";

    // 裝備卡標籤渲染
    if (equipments && equipments.length > 0) {
      const eqContainer = document.createElement("div");
      eqContainer.id = "leftPanelEquipmentsContainer";
      eqContainer.className = "xlw-left-panel-equipments-container";
      
      eqContainer.style.position = "absolute";
      eqContainer.style.top = "15px";
      eqContainer.style.left = "15px";
      eqContainer.style.right = "15px";
      eqContainer.style.zIndex = "10020";
      eqContainer.style.display = "flex";
      eqContainer.style.flexDirection = "column";
      eqContainer.style.gap = "6px";
      eqContainer.style.pointerEvents = "none";

      equipments.forEach((eqName) => {
        let displayText = eqName;
        if (eqName.includes("符咒帽")) displayText = "🎩 符咒帽 (魔免)";
        else if (eqName.includes("菜刀")) displayText = "🔪 3星菜刀 (貫穿)";
        else if (eqName.includes("弓箭")) displayText = "🏹 弓箭 (遠程+1)";
        else if (eqName.includes("戰斧牛排")) displayText = "🥩 戰斬牛排 (+5)";
        else if (eqName.includes("削弱藥水")) displayText = "🧪 削弱藥水 (-3)";
        else if (eqName.includes("振奮藥水")) displayText = "🧪 振奮藥水 (+3)";
        else if (eqName.includes("塗毒")) displayText = "🤢 塗毒 (劇毒)";

        const badge = document.createElement("div");
        badge.className = "xlw-left-panel-equipment-badge";
        badge.style.background = "#ffe600";
        badge.style.border = "2px solid #000";
        badge.style.borderRadius = "6px";
        badge.style.color = "#000";
        badge.style.fontSize = "13px";
        badge.style.fontWeight = "bold";
        badge.style.padding = "4px 10px";
        badge.style.textAlign = "center";
        badge.style.boxShadow = "2px 2px 0px #000";
        badge.textContent = displayText;

        eqContainer.appendChild(badge);
      });

      detailView.appendChild(eqContainer);
    }
  }
  if (leftPanel) {
    leftPanel.style.display = "block";
  }
}

function setStatus(t) {
  const s = $("status");
  if (s) s.textContent = t;
  const guideText = $("mangaGuideText");
  if (guideText && t) {
    guideText.textContent = t;
  }
}
"""
        js_content = js_content[:m_start] + new_modal_code + js_content[m_end:]
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("2. Updated static/game_v8.js showModal implementation successfully!")

    # ==========================================
    # 3. APPEND CSS TO style_v8.css
    # ==========================================
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    new_css_rules = """

/* ==========================================================================
   ARCADE COMIC DESIGN THEME (Matching Reference Image Aesthetics)
   ========================================================================== */

/* 全域背景：紅/暗紅雙色漫畫格子圖騰紋理 */
body {
  background: radial-gradient(circle at 50% 50%, rgba(120, 20, 30, 0.45) 0%, rgba(20, 5, 10, 0.95) 100%),
              url('/static/red_cat_checkerboard.png') repeat !important;
  background-size: cover, 180px 180px !important;
}

/* 頂部 Header 重塑：金/黃亮光漫畫標頭 */
.topbar {
  background: linear-gradient(180deg, #181215 0%, #0d080a 100%) !important;
  border-bottom: 3px solid #ffe600 !important;
  box-shadow: 0 4px 20px rgba(255, 230, 0, 0.25), 0 4px 10px rgba(0,0,0,0.8) !important;
}

.title {
  font-family: 'Cinzel', 'Outfit', sans-serif !important;
  font-size: 22px !important;
  font-weight: 900 !important;
  color: #ffe600 !important;
  text-shadow: 3px 3px 0px #000, 0 0 12px rgba(255, 230, 0, 0.7) !important;
  font-style: italic !important;
  letter-spacing: 1.5px !important;
}

button, select {
  background: #ffe600 !important;
  color: #000000 !important;
  border: 2px solid #000000 !important;
  border-radius: 8px !important;
  font-weight: 900 !important;
  box-shadow: 2.5px 2.5px 0px #000000 !important;
  transition: all 0.15s ease !important;
}

button:hover, select:hover {
  transform: translate(-1px, -1px) !important;
  box-shadow: 4px 4px 0px #000000 !important;
  background: #ffffff !important;
  color: #000000 !important;
}

button:active, select:active {
  transform: translate(1px, 1px) !important;
  box-shadow: 1px 1px 0px #000000 !important;
}

/* 我方與對手按鈕差異色 */
#newGameBtn {
  background: linear-gradient(135deg, #ffe600 0%, #ffcc00 100%) !important;
  color: #000 !important;
  border: 2.5px solid #000 !important;
}

#multiplayerBtn {
  background: linear-gradient(135deg, #ff3366 0%, #e60039 100%) !important;
  color: #fff !important;
  border: 2.5px solid #000 !important;
  text-shadow: 1px 1px 0 #000;
}

/* ==========================================================================
   ARCADE CARD INSPECTOR PANEL (Left Side Detail View)
   ========================================================================== */

.xlw-left-card-panel {
  width: 440px !important;
  height: 620px !important;
  left: -550px !important;
  background: rgba(18, 12, 16, 0.94) !important;
  border: 3px solid #ffe600 !important;
  border-radius: 20px !important;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.95), 0 0 25px rgba(255, 230, 0, 0.35) !important;
  padding: 14px !important;
  backdrop-filter: blur(16px) !important;
}

/* 抬頭斜角橫幅 */
.arcade-card-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #2b1f24 0%, #150f12 100%);
  border: 2.5px solid #ffe600;
  border-radius: 12px;
  padding: 8px 12px;
  margin-bottom: 12px;
  box-shadow: 3px 3px 0px #000;
  clip-path: polygon(0 0, 100% 0, 96% 100%, 0% 100%);
}

.arcade-type-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #ffe600;
  color: #000;
  border: 2px solid #000;
  border-radius: 50px;
  padding: 4px 10px;
  font-weight: 900;
  box-shadow: 2px 2px 0 #000;
}

.arcade-type-badge.defensive-type {
  background: #ffe600;
  color: #000;
}

.arcade-type-badge.attack-type {
  background: #ff3344;
  color: #fff;
  text-shadow: 1px 1px 0 #000;
}

.arcade-type-badge.spell-type {
  background: #00e5ff;
  color: #000;
}

.badge-icon {
  font-size: 18px;
}

.badge-text {
  font-size: 12px;
  line-height: 1.1;
  text-align: center;
}

.arcade-title-box {
  flex: 1;
}

.arcade-card-no {
  font-size: 11px;
  color: #ffe600;
  font-weight: bold;
  letter-spacing: 1px;
}

.arcade-card-title {
  font-size: 20px;
  font-weight: 900;
  color: #ffe600;
  text-shadow: 2px 2px 0px #000, 0 0 10px rgba(255, 230, 0, 0.5);
  line-height: 1.1;
}

.arcade-card-sub {
  font-size: 10px;
  color: #ccc;
  font-weight: bold;
  letter-spacing: 0.5px;
}

.arcade-rating-box {
  text-align: center;
}

.arcade-rating-box .stars {
  font-size: 16px;
  color: #ffe600;
  text-shadow: 0 0 6px rgba(255, 230, 0, 0.8);
}

.arcade-rating-box .rating-label {
  font-size: 10px;
  color: #fff;
  font-weight: bold;
}

/* 中央角色立體展示與黃色屬性面板 */
.arcade-showcase-wrap {
  width: 100%;
  height: 380px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle, rgba(220, 30, 60, 0.45) 0%, rgba(30, 10, 15, 0.9) 70%);
  border: 2.5px solid #ffe600;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.8), 3px 3px 0 #000;
  margin-bottom: 12px;
}

.arcade-target-aura {
  position: absolute;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  border: 3px dashed rgba(255, 230, 0, 0.5);
  box-shadow: 0 0 40px rgba(255, 50, 80, 0.6), inset 0 0 40px rgba(255, 230, 0, 0.4);
  animation: spin 20s linear infinite;
  pointer-events: none;
}

.arcade-showcase-wrap .detail-img-wrap {
  width: 250px;
  height: 350px;
  border-radius: 14px;
  border: 3.5px solid #ffffff !important;
  box-shadow: 0 0 25px rgba(255, 230, 0, 0.6), 0 10px 30px rgba(0,0,0,0.9) !important;
  overflow: hidden;
  z-index: 2;
}

.arcade-showcase-wrap .detail-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: fill;
}

/* 右側黃色屬性資訊卡 (Matching reference screenshot) */
.arcade-stat-panel {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 135px;
  background: #ffe600;
  border: 3px solid #000000;
  border-radius: 14px;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 4px 4px 0px #000000;
  z-index: 10;
}

.stat-pill {
  background: #000000;
  border-radius: 8px;
  padding: 6px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 1px 1px 0px rgba(255,255,255,0.2);
}

.stat-label {
  font-size: 10px;
  color: #ffe600;
  font-weight: 900;
  letter-spacing: 0.5px;
}

.stat-val {
  font-size: 14px;
  color: #ffffff;
  font-weight: 900;
  text-shadow: 1px 1px 0 #000;
}

/* 底部對話說明框 */
.arcade-quote-bubble {
  width: 100%;
  background: rgba(0, 0, 0, 0.85);
  border: 2px solid #ffe600;
  border-radius: 12px;
  padding: 10px 14px;
  box-shadow: 3px 3px 0 #000;
}

.quote-tag {
  font-size: 12px;
  color: #ffe600;
  font-weight: 900;
  margin-bottom: 4px;
}

.quote-text {
  font-size: 13px;
  color: #ffffff;
  line-height: 1.4;
  font-weight: bold;
}

/* ==========================================================================
   MANGA GUIDE CORNER (Bottom Right Host Character & Speech Bubble)
   ========================================================================== */

.xlw-manga-guide-corner {
  position: fixed;
  right: 25px;
  bottom: 15px;
  display: flex;
  align-items: flex-end;
  gap: 12px;
  z-index: 9999;
  pointer-events: none;
}

.speech-bubble {
  background: #ffffff;
  border: 3.5px solid #000000;
  border-radius: 20px;
  padding: 14px 20px;
  max-width: 280px;
  box-shadow: 5px 5px 0px #000000;
  position: relative;
  pointer-events: auto;
  animation: bubbleFloat 3s ease-in-out infinite alternate;
}

.speech-bubble::after {
  content: '';
  position: absolute;
  right: -14px;
  bottom: 25px;
  width: 0;
  height: 0;
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
  border-left: 14px solid #000000;
}

.speech-bubble::before {
  content: '';
  position: absolute;
  right: -9px;
  bottom: 27px;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 11px solid #ffffff;
  z-index: 2;
}

.speech-text {
  color: #000000;
  font-size: 14px;
  font-weight: 900;
  line-height: 1.5;
  font-family: 'Noto Sans TC', system-ui, sans-serif;
}

.guide-avatar-wrap {
  position: relative;
  width: 130px;
  height: 160px;
  pointer-events: auto;
}

.guide-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(4px 4px 0px #000000) drop-shadow(0 0 10px rgba(255, 230, 0, 0.4));
  transition: transform 0.2s ease;
}

.guide-avatar-img:hover {
  transform: scale(1.05) rotate(-2deg);
}

.guide-name-tag {
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffe600;
  color: #000;
  border: 2px solid #000;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 900;
  box-shadow: 2px 2px 0 #000;
  white-space: nowrap;
}

@keyframes bubbleFloat {
  0% { transform: translateY(0px); }
  100% { transform: translateY(-6px); }
}

/* ==========================================================================
   SLOTS & CARDS ARCADE ENHANCEMENTS
   ========================================================================== */

.slot {
  border: 2px solid rgba(255, 230, 0, 0.45) !important;
  border-radius: 12px !important;
  background: rgba(15, 10, 20, 0.75) !important;
  box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.8) !important;
  transition: all 0.25s ease !important;
}

.slot:hover {
  border-color: #ffe600 !important;
  box-shadow: 0 0 20px rgba(255, 230, 0, 0.5), inset 0 0 15px rgba(255, 230, 0, 0.2) !important;
}

.card {
  border: 2px solid #ffffff !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.85), 0 0 8px rgba(255, 230, 0, 0.3) !important;
  transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.2s ease !important;
}

.card:hover {
  transform: scale(1.06) translateY(-4px) !important;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.95), 0 0 18px rgba(255, 230, 0, 0.7) !important;
  z-index: 50 !important;
}

/* 星星戰線條帶 */
.battle-line-strip {
  background: linear-gradient(90deg, rgba(255, 230, 0, 0.15) 0%, rgba(255, 230, 0, 0.35) 50%, rgba(255, 230, 0, 0.15) 100%) !important;
  border-top: 2.5px solid #ffe600 !important;
  border-bottom: 2.5px solid #ffe600 !important;
  box-shadow: 0 0 20px rgba(255, 230, 0, 0.4) !important;
}

.battle-cell {
  background: #ffe600 !important;
  color: #000000 !important;
  border: 2px solid #000000 !important;
  border-radius: 8px !important;
  font-weight: 900 !important;
  font-size: 15px !important;
  box-shadow: 2px 2px 0px #000000 !important;
  text-shadow: none !important;
}

"""
    open(css_path, 'a', encoding='utf-8').write(new_css_rules)
    print("3. Appended Arcade Comic theme styles to static/style_v8.css successfully!")

if __name__ == '__main__':
    apply_ui_upgrade()
