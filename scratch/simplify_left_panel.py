# -*- coding: utf-8 -*-
import sys, re

def simplify_panel():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update index.html
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    new_panel_html = """<!-- 左側卡牌詳細資訊看板 (極簡高清放大版) -->
        <aside id="xlwLeftCardPanel" class="xlw-left-card-panel" onclick="this.style.display='none'">
          <div class="panel-inner">
            <div id="leftPanelPlaceholder" class="placeholder-text">點擊卡牌放大顯示</div>
            <div id="leftCardDetailView" class="card-detail-view" style="display: none;">
              <div class="detail-img-wrap">
                <img id="leftPanelImg" src="" alt="card detail image">
              </div>
            </div>
          </div>
        </aside>"""

    old_panel_pattern = r'<aside id="xlwLeftCardPanel".*?</aside>'
    idx_content = re.sub(old_panel_pattern, new_panel_html, idx_content, flags=re.DOTALL)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Simplified left card panel HTML in static/index.html successfully!")

    # 2. Update game_v8.js
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
    detailView.style.display = "block";
    detailView.style.position = "relative";

    // 若該單位有加裝裝備卡，將裝備效果說明直接覆蓋加在圖片上方
    if (equipments && equipments.length > 0) {
      const eqContainer = document.createElement("div");
      eqContainer.id = "leftPanelEquipmentsContainer";
      eqContainer.className = "xlw-left-panel-equipments-container";
      
      eqContainer.style.position = "absolute";
      eqContainer.style.top = "16px";
      eqContainer.style.left = "16px";
      eqContainer.style.right = "16px";
      eqContainer.style.zIndex = "10020";
      eqContainer.style.display = "flex";
      eqContainer.style.flexDirection = "column";
      eqContainer.style.gap = "8px";
      eqContainer.style.pointerEvents = "none";

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
        badge.style.background = "linear-gradient(135deg, rgba(20, 15, 10, 0.94), rgba(40, 30, 18, 0.96))";
        badge.style.border = "2px solid #ffe600";
        badge.style.borderRadius = "8px";
        badge.style.color = "#ffe600";
        badge.style.fontSize = "14px";
        badge.style.fontWeight = "bold";
        badge.style.padding = "8px 12px";
        badge.style.textAlign = "center";
        badge.style.boxShadow = "0 4px 15px rgba(0,0,0,0.9), 0 0 10px rgba(255, 230, 0, 0.4)";
        badge.style.textShadow = "1px 1px 2px #000";
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

    old_fn_start = "function showModal(card, equipments) {"
    old_fn_end = "function setStatus(t) {"

    m_start = js_content.find(old_fn_start)
    m_end = js_content.find(old_fn_end)

    if m_start >= 0 and m_end >= 0:
        js_content = js_content[:m_start] + new_show_modal_code + "\n\n" + js_content[m_end:]
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("2. Simplified showModal function in static/game_v8.js successfully!")

    # 3. Update style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Replace arcade card inspector CSS block with clean pure image panel CSS
    arcade_css_start = "/* ==========================================================================\n   ARCADE CARD INSPECTOR PANEL"
    arcade_css_end = "/* ==========================================================================\n   SLOTS & CARDS ARCADE ENHANCEMENTS"

    ac_s = css_content.find(arcade_css_start)
    ac_e = css_content.find(arcade_css_end)

    new_panel_css = """/* ==========================================================================
   PURE CARD INSPECTOR PANEL (極簡卡牌放大圖與裝備覆蓋)
   ========================================================================== */

.xlw-left-card-panel {
  width: 350px !important;
  height: 480px !important;
  left: -460px !important;
  background: rgba(12, 8, 14, 0.95) !important;
  border: 2.5px solid #ffe600 !important;
  border-radius: 16px !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.95), 0 0 20px rgba(255, 230, 0, 0.3) !important;
  padding: 10px !important;
  backdrop-filter: blur(14px) !important;
}

.xlw-left-card-panel .panel-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.xlw-left-card-panel .card-detail-view {
  width: 100%;
  height: 100%;
}

.xlw-left-card-panel .detail-img-wrap {
  width: 100%;
  height: 100%;
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.9);
  overflow: hidden;
  position: relative;
}

.xlw-left-card-panel .detail-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: fill;
}

.xlw-left-card-panel .placeholder-text {
  color: #ffe600;
  text-align: center;
  font-size: 15px;
  font-weight: bold;
}

"""

    if ac_s >= 0 and ac_e >= 0:
        css_content = css_content[:ac_s] + new_panel_css + css_content[ac_e:]
        open(css_path, 'w', encoding='utf-8').write(css_content)
        print("3. Updated left card panel CSS in static/style_v8.css successfully!")

if __name__ == '__main__':
    simplify_panel()
