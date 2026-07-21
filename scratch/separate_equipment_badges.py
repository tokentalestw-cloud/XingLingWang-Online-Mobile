# -*- coding: utf-8 -*-
import sys, re

def separate_equipment():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update game_v8.js showModal function
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
      
      eqContainer.style.width = "100%";
      eqContainer.style.marginTop = "10px";
      eqContainer.style.display = "flex";
      eqContainer.style.flexDirection = "column";
      eqContainer.style.gap = "6px";

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
        badge.style.background = "linear-gradient(135deg, #ffe600 0%, #ffd700 100%)";
        badge.style.border = "2px solid #000000";
        badge.style.borderRadius = "8px";
        badge.style.color = "#000000";
        badge.style.fontSize = "13px";
        badge.style.fontWeight = "900";
        badge.style.padding = "6px 10px";
        badge.style.textAlign = "center";
        badge.style.boxShadow = "2px 2px 0px #000000";
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
        print("1. Updated showModal in static/game_v8.js successfully!")

    # 2. Update style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    css_start = "/* ==========================================================================\n   PURE CARD INSPECTOR PANEL"
    css_end = "/* ==========================================================================\n   SLOTS & CARDS ARCADE ENHANCEMENTS"

    c_s = css_content.find(css_start)
    c_e = css_content.find(css_end)

    new_css = """/* ==========================================================================
   PURE CARD INSPECTOR PANEL (圖片與裝備說明分離版)
   ========================================================================== */

.xlw-left-card-panel {
  width: 340px !important;
  max-height: 580px !important;
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

.xlw-left-card-panel .panel-inner {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.xlw-left-card-panel .card-detail-view {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.xlw-left-card-panel .detail-img-wrap {
  width: 100%;
  height: 420px;
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.9);
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}

.xlw-left-card-panel .detail-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: fill;
}

.xlw-left-panel-equipments-container {
  width: 100%;
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.xlw-left-card-panel .placeholder-text {
  color: #ffe600;
  text-align: center;
  font-size: 15px;
  font-weight: bold;
  padding: 180px 0;
}

"""

    if c_s >= 0 and c_e >= 0:
        css_content = css_content[:c_s] + new_css + css_content[c_e:]
        open(css_path, 'w', encoding='utf-8').write(css_content)
        print("2. Updated left card panel CSS in static/style_v8.css successfully!")

if __name__ == '__main__':
    separate_equipment()
