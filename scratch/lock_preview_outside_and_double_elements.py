# -*- coding: utf-8 -*-
import sys, re

def lock_and_double():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Relocate #xlwLeftCardPanel in static/index.html to be outside .game-shell and right before </body>
    idx_content = open(idx_path, encoding='utf-8').read()

    panel_html = """        <aside id="xlwLeftCardPanel" class="xlw-left-card-panel" onclick="this.style.display='none'">
          <div class="panel-inner">
            <div id="leftPanelPlaceholder" class="placeholder-text">點擊卡牌<br>在此放大 4 倍顯示</div>
            <div id="leftCardDetailView" class="card-detail-view" style="display: none !important;">
              <div class="detail-img-wrap">
                <img id="leftPanelImg" src="" alt="card detail image">
              </div>
            </div>
          </div>
        </aside>"""

    # Remove from original position
    idx_content = idx_content.replace(panel_html, "")

    # Place right before </body>
    idx_content = idx_content.replace("</body>", panel_html + "\n</body>")
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Relocated #xlwLeftCardPanel to end of body in index.html successfully!")

    # 2. Modify static/style_v8.css: double scale of preview, action panel, and phase panel width
    css_content = open(css_path, encoding='utf-8').read()

    # Update xlwLeftCardPanel layout
    old_preview_style = """  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: fixed !important;
    left: 0px !important;
    bottom: 0px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(1.30) !important;
    transform-origin: bottom left !important;
  }"""

    new_preview_style = """  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: fixed !important;
    left: 0px !important;
    bottom: 0px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(1.60) !important;
    transform-origin: bottom left !important;
  }"""

    css_content = css_content.replace(old_preview_style, new_preview_style)

    # Double stableActionPanel scale to 0.64
    css_content = css_content.replace(
        "transform: scale(0.32) !important;\n    transform-origin: bottom right !important;",
        "transform: scale(0.64) !important;\n    transform-origin: bottom right !important;"
    )

    # Double phaseDisplayPanelHard width to 960px and add nowrap to its text
    old_phase_panel = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 20px !important;
    left: 450px !important;
    transform: scale(0.48) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
  }"""

    new_phase_panel = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 20px !important;
    left: 450px !important;
    width: 960px !important;
    transform: scale(0.48) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
  }
  #phaseDisplayPanelHard .phase-hard-help {
    white-space: nowrap !important;
  }"""

    css_content = css_content.replace(old_phase_panel, new_phase_panel)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Doubled scale values and set phase panel widths in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=19.10-layout-micro-fixes
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.10-layout-micro-fixes', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.10-layout-micro-fixes', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    lock_and_double()
