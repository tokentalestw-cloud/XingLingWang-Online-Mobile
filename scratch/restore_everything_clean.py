# -*- coding: utf-8 -*-
import sys, shutil, re

def restore_clean():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Restore style_v8.css from style.css
    shutil.copy('static/style.css', 'static/style_v8.css')
    print("1. Restored static/style_v8.css from static/style.css successfully!")

    # 2. Restore index.html left panel & cache busters
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Clean left panel HTML
    clean_panel_html = """<!-- 左側卡牌詳細資訊看板 -->
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
    idx_content = re.sub(r'<!-- 右下角漫畫社長引導對話框 -->.*?</div>\s*</div>', '', idx_content, flags=re.DOTALL)
    idx_content = re.sub(r'<div id="xlwMangaGuideCorner".*?</div>\s*</div>', '', idx_content, flags=re.DOTALL)

    # Update cache-busters to v=8.90-restored-clean
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=8.90-restored-clean', idx_content)
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=8.90-restored-clean', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Restored static/index.html clean layout successfully!")

    # 3. Clean showModal in game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    clean_show_modal = """function showModal(card, equipments) {
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

    if (equipments && equipments.length > 0) {
      const eqContainer = document.createElement("div");
      eqContainer.id = "leftPanelEquipmentsContainer";
      eqContainer.className = "xlw-left-panel-equipments-container";
      
      eqContainer.style.position = "absolute";
      eqContainer.style.top = "20px";
      eqContainer.style.left = "15px";
      eqContainer.style.right = "15px";
      eqContainer.style.zIndex = "10020";
      eqContainer.style.display = "flex";
      eqContainer.style.flexDirection = "column";
      eqContainer.style.gap = "8px";
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
        badge.style.background = "linear-gradient(135deg, rgba(28, 24, 19, 0.98), rgba(45, 38, 30, 0.98))";
        badge.style.border = "2px solid #ffd76a";
        badge.style.borderRadius = "8px";
        badge.style.color = "#ffd76a";
        badge.style.fontSize = "15px";
        badge.style.fontWeight = "bold";
        badge.style.padding = "6px 12px";
        badge.style.textAlign = "center";
        badge.style.boxShadow = "0 4px 10px rgba(0,0,0,0.8), 0 0 8px rgba(212, 175, 55, 0.5)";
        badge.style.textShadow = "0 0 3px rgba(0,0,0,1)";
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
}"""

    old_s = js_content.find("function showModal(card, equipments) {")
    old_e = js_content.find("function logBattle(text) {")

    if old_s >= 0 and old_e >= 0:
      js_content = js_content[:old_s] + clean_show_modal + "\n\n" + js_content[old_e:]
      open(js_path, 'w', encoding='utf-8').write(js_content)
      print("3. Restored clean showModal function in static/game_v8.js successfully!")

if __name__ == '__main__':
    restore_clean()
