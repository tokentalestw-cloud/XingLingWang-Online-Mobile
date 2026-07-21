# -*- coding: utf-8 -*-
import sys, re

def clear_initial_img():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/index.html
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Ensure leftPanelImg starts with completely empty src and detailView is hidden
    old_panel_html = r'<aside id="xlwLeftCardPanel".*?</aside>'
    new_panel_html = """<aside id="xlwLeftCardPanel" class="xlw-left-card-panel" onclick="this.style.display='none'">
          <div class="panel-inner">
            <div id="leftPanelPlaceholder" class="placeholder-text">點擊卡牌<br>在此放大 4 倍顯示</div>
            <div id="leftCardDetailView" class="card-detail-view" style="display: none !important;">
              <div class="detail-img-wrap">
                <img id="leftPanelImg" src="" alt="card detail image">
              </div>
            </div>
          </div>
        </aside>"""

    idx_content = re.sub(old_panel_html, new_panel_html, idx_content, flags=re.DOTALL)

    # Update cache-buster to v=9.90-clean-initial-panel-no-img
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=9.90-clean-initial-panel-no-img', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=9.90-clean-initial-panel-no-img', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Updated static/index.html cleanly!")

    # 2. Update showModal in static/game_v8.js
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
    leftImg.onerror = function() {
      this.onerror = null;
      this.src = "/static/card_back.jpeg";
    };
    leftImg.src = (card && card.image) ? card.image : "/static/card_back.jpeg";
    placeholder.style.display = "none";
    detailView.style.setProperty("display", "flex", "important");
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
        js_content = js_content[:m_start] + new_modal_code + "\n\n" + js_content[m_end:]
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("2. Updated showModal in static/game_v8.js successfully!")

if __name__ == '__main__':
    clear_initial_img()
