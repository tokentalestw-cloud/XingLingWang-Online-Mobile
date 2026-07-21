# -*- coding: utf-8 -*-
import sys, re

def apply_targeted_theme():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/index.html to ensure clean left panel structure and update cache busters
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    clean_panel_html = """<!-- 左側卡牌詳細資訊看板 (分離裝備說明版) -->
        <aside id="xlwLeftCardPanel" class="xlw-left-card-panel" onclick="this.style.display='none'">
          <div class="panel-inner">
            <div id="leftPanelPlaceholder" class="placeholder-text">點擊卡牌<br>在此放大 4 倍顯示</div>
            <div id="leftCardDetailView" class="card-detail-view" style="display: none;">
              <div class="detail-img-wrap">
                <img id="leftPanelImg" src="" alt="card detail image">
              </div>
            </div>
          </div>
        </aside>"""

    idx_content = re.sub(r'<aside id="xlwLeftCardPanel".*?</aside>', clean_panel_html, idx_content, flags=re.DOTALL)
    
    # Remove manga host guide if present
    idx_content = re.sub(r'<!-- 右下角漫畫社長引導對話框 -->.*?</div>\s*</div>', '', idx_content, flags=re.DOTALL)
    idx_content = re.sub(r'<div id="xlwMangaGuideCorner".*?</div>\s*</div>', '', idx_content, flags=re.DOTALL)

    # Update cache-busters to v=9.00-separated-equipment-3d
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=9.00-separated-equipment-3d', idx_content)
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=9.00-separated-equipment-3d', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Updated static/index.html cleanly!")

    # 2. Update showModal in static/game_v8.js to place equipment badges below the image wrapper (separated)
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    new_show_modal_code = """function showModal(card, equipments) {
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
    detailView.style.display = "flex";
    detailView.style.flexDirection = "column";
    detailView.style.alignItems = "center";

    // 若該單位有加裝裝備卡，將裝備效果說明獨立放在圖片下方（不與圖片重疊）
    if (equipments && equipments.length > 0) {
      const eqContainer = document.createElement("div");
      eqContainer.id = "leftPanelEquipmentsContainer";
      eqContainer.className = "xlw-left-panel-equipments-container";

      equipments.forEach((eqName) => {
        let displayText = eqName;
        if (eqName.includes("符咒帽")) displayText = "🎩 符咒帽：魔法無效";
        else if (eqName.includes("菜刀")) displayText = "🔪 3星菜刀：攻擊力+3，獲得貫穿";
        else if (eqName.includes("弓箭")) displayText = "🏹 弓箭：獲得遠程+1";
        else if (eqName.includes("戰斧牛排")) displayText = "🥩 戰斬牛排：攻擊力+5";
        else if (eqName.includes("削弱藥水")) displayText = "🧪 削弱藥水：攻擊力-3";
        else if (eqName.includes("振奮藥水")) displayText = "🧪 振奮藥水：攻擊力+3";
        else if (eqName.includes("塗毒")) displayText = "🤢 塗毒：獲得劇毒效果";
        else if (eqName.includes("睡眠反擊拳")) displayText = "🥊 睡眠反擊拳：攻擊力+3";
        else if (eqName.includes("狼牙棒")) displayText = "🔨 狼牙棒：動態攻擊力加成";
        else if (eqName.includes("法術保護")) displayText = "🛡️ 法術保護：魔法無效";
        else if (eqName.includes("冰霜法師(-3)")) displayText = "❄️ 冰霜法師：星數-3⭐";

        const badge = document.createElement("div");
        badge.className = "xlw-left-panel-equipment-badge";
        badge.textContent = displayText;

        eqContainer.appendChild(badge);
      });

      detailView.appendChild(eqContainer);
    }
  }
  if (leftPanel) {
    leftPanel.style.display = "block";
  }
}"""

    m_start = js_content.find("function showModal(card, equipments) {")
    m_end = js_content.find("function logBattle(text) {")

    if m_start >= 0 and m_end >= 0:
        js_content = js_content[:m_start] + new_show_modal_code + "\n\n" + js_content[m_end:]
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("2. Updated showModal in static/game_v8.js successfully!")

    # 3. Append strictly scoped 3D button & separated equipment panel styles to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean previous targeted block if exists
    block_marker = "/* ==========================================================================\n   TARGETED 3D BUTTONS & SEPARATED EQUIPMENT PANEL"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    new_css_rules = """

/* ==========================================================================
   TARGETED 3D BUTTONS & SEPARATED EQUIPMENT PANEL (不改動任何戰場與卡牌比例)
   ========================================================================== */

/* 1. 頂部工具列與按鈕 3D 高級質感 (Strictly Scoped) */
.topbar button, .topbar select, .topbar a button, #scoreBtn, .close, .score-box button {
  background: linear-gradient(180deg, #fff47d 0%, #ffe600 48%, #d6a700 100%) !important;
  color: #000000 !important;
  border: 2px solid #000000 !important;
  border-bottom: 5px solid #7a5f00 !important;
  border-radius: 10px !important;
  font-family: system-ui, "Noto Sans TC", sans-serif !important;
  font-weight: 900 !important;
  letter-spacing: 0.5px !important;
  padding: 7px 16px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.7), 0 4px 12px rgba(0, 0, 0, 0.6), 0 2.5px 0 #000000 !important;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.4) !important;
  position: relative !important;
  cursor: pointer !important;
  transition: transform 0.12s cubic-bezier(0.2, 0.8, 0.4, 1), box-shadow 0.12s ease !important;
  user-select: none !important;
}

.topbar button:hover:not(:disabled), .topbar select:hover, .topbar a button:hover {
  transform: translateY(-2px) !important;
  background: linear-gradient(180deg, #ffffff 0%, #fff066 48%, #e6b800 100%) !important;
  border-bottom-width: 6px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.9), 0 8px 20px rgba(0, 0, 0, 0.7), 0 0 18px rgba(255, 230, 0, 0.65) !important;
}

.topbar button:active:not(:disabled), .topbar select:active, .topbar a button:active {
  transform: translateY(3px) !important;
  border-bottom-width: 2px !important;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.4), 0 2px 5px rgba(0, 0, 0, 0.5) !important;
}

/* 單人對抗 AI */
#newGameBtn {
  background: linear-gradient(180deg, #fff7a0 0%, #ffd700 48%, #c99c00 100%) !important;
  color: #000000 !important;
  border: 2px solid #000000 !important;
  border-bottom: 5px solid #695100 !important;
}

/* 線上雙人對決 */
#multiplayerBtn {
  background: linear-gradient(180deg, #ff6b8b 0%, #ff1f4c 48%, #b80024 100%) !important;
  color: #ffffff !important;
  border: 2.5px solid #ffe600 !important;
  border-bottom: 5px solid #5e0012 !important;
  text-shadow: 1.5px 1.5px 0px #000000 !important;
}

/* 戰局紀錄、牌組編輯器、卡牌編輯器 */
#scoreBtn, .topbar a button {
  background: linear-gradient(180deg, #2e263d 0%, #1c1628 48%, #100c17 100%) !important;
  color: #ffe600 !important;
  border: 2px solid #ffe600 !important;
  border-bottom: 5px solid #000000 !important;
}

/* 2. 左側卡牌放大面板 (尺寸適中，裝備說明獨立位於下方，絕不重疊) */
.xlw-left-card-panel {
  width: 340px !important;
  max-height: 590px !important;
  height: auto !important;
  left: -450px !important;
  background: rgba(12, 8, 14, 0.95) !important;
  border: 2.5px solid #ffe600 !important;
  border-radius: 16px !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.95), 0 0 20px rgba(255, 230, 0, 0.3) !important;
  padding: 10px !important;
  backdrop-filter: blur(14px) !important;
  overflow: hidden !important;
}

.xlw-left-card-panel .card-detail-view {
  width: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
}

.xlw-left-card-panel .detail-img-wrap {
  width: 100% !important;
  height: 420px !important;
  border-radius: 12px !important;
  border: 2px solid rgba(255, 255, 255, 0.6) !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.9) !important;
  overflow: hidden !important;
  position: relative !important;
  flex-shrink: 0 !important;
}

.xlw-left-card-panel .detail-img-wrap img {
  width: 100% !important;
  height: 100% !important;
  object-fit: fill !important;
}

.xlw-left-panel-equipments-container {
  width: 100% !important;
  margin-top: 10px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
}

.xlw-left-panel-equipment-badge {
  background: linear-gradient(180deg, #fff47d 0%, #ffe600 48%, #d6a700 100%) !important;
  color: #000000 !important;
  border: 2px solid #000000 !important;
  border-bottom: 4px solid #7a5f00 !important;
  border-radius: 8px !important;
  font-weight: 900 !important;
  font-size: 13px !important;
  padding: 6px 10px !important;
  text-align: center !important;
  box-shadow: 0 3px 8px rgba(0,0,0,0.7), 0 2px 0 #000 !important;
}

"""

    css_content += new_css_rules
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Appended strictly scoped 3D button & separated equipment panel styles to static/style_v8.css successfully!")

if __name__ == '__main__':
    apply_targeted_theme()
