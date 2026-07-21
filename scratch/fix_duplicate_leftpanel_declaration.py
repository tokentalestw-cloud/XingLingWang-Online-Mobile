# -*- coding: utf-8 -*-
import sys, re

def fix_leftpanel():
    sys.stdout.reconfigure(encoding='utf-8')
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    old_show_modal = """function showModal(card, equipments) {
  if (!card) return;

  // 附加上放大預視窗 SR/SSR 雷射虹光圖層
  const leftPanel = $("xlwLeftCardPanel");
  if (leftPanel) {
    let holoFoil = leftPanel.querySelector(".xlw-holo-foil");
    if (window.xlwIsHoloCard(card)) {
      if (!holoFoil) {
        holoFoil = document.createElement("div");
        holoFoil.className = "xlw-holo-foil";
        leftPanel.appendChild(holoFoil);
      }
      holoFoil.style.display = "block";
    } else if (holoFoil) {
      holoFoil.style.display = "none";
    }
  }
  if (!card) return;
  const leftPanel = $("xlwLeftCardPanel");
  const leftImg = $("leftPanelImg");
  const placeholder = $("leftPanelPlaceholder");
  const detailView = $("leftCardDetailView");"""

    new_show_modal = """function showModal(card, equipments) {
  if (!card) return;
  const leftPanel = $("xlwLeftCardPanel");
  const leftImg = $("leftPanelImg");
  const placeholder = $("leftPanelPlaceholder");
  const detailView = $("leftCardDetailView");

  // 附加上放大預視窗 SR/SSR 雷射虹光圖層
  if (leftPanel) {
    let holoFoil = leftPanel.querySelector(".xlw-holo-foil");
    if (window.xlwIsHoloCard(card)) {
      if (!holoFoil) {
        holoFoil = document.createElement("div");
        holoFoil.className = "xlw-holo-foil";
        leftPanel.appendChild(holoFoil);
      }
      holoFoil.style.display = "block";
    } else if (holoFoil) {
      holoFoil.style.display = "none";
    }
  }"""

    if old_show_modal in js_content:
        js_content = js_content.replace(old_show_modal, new_show_modal)
        print("1. Cleaned up duplicate leftPanel declaration in static/game_v8.js successfully!")

    open(js_path, 'w', encoding='utf-8').write(js_content)

    # Update cache-buster in static/index.html to v=12.10-fix-duplicate-leftpanel
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=12.10-fix-duplicate-leftpanel', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=12.10-fix-duplicate-leftpanel', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_leftpanel()
