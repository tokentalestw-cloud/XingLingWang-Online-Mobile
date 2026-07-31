# -*- coding: utf-8 -*-
import sys, re

def shift_top_right():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # 1. Update #boardWrap to top: 30% and scale(0.46)
    old_board_block = """  #boardWrap {
    width: 1400px !important;
    height: 760px !important;
    min-width: 1400px !important;
    min-height: 760px !important;
    position: absolute !important;
    top: 45% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) scale(0.55) !important;
    transform-origin: center center !important;
    margin: 0 !important;
  }"""

    new_board_block = """  #boardWrap {
    width: 1400px !important;
    height: 760px !important;
    min-width: 1400px !important;
    min-height: 760px !important;
    position: absolute !important;
    top: 30% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) scale(0.46) !important;
    transform-origin: center center !important;
    margin: 0 !important;
  }"""

    css_content = css_content.replace(old_board_block, new_board_block)

    # 2. Re-adjust hand-panel height to 90px
    old_hand_panel = """  .hand-panel {
    position: fixed !important;
    bottom: 4px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 650px !important; /* 固定寬度，防範 iOS Safari 寬度崩塌 */
    max-width: 90vw !important;
    height: 130px !important;
    min-height: 130px !important;
    max-height: 130px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    display: flex !important;
    align-items: flex-end !important;
    overflow: visible !important;
    z-index: 10010 !important;
    margin: 0 !important;
    padding: 0 !important;
  }"""

    new_hand_panel = """  .hand-panel {
    position: fixed !important;
    bottom: 4px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 650px !important; /* 固定寬度，防範 iOS Safari 寬度崩塌 */
    max-width: 90vw !important;
    height: 90px !important;
    min-height: 90px !important;
    max-height: 90px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    display: flex !important;
    align-items: flex-end !important;
    overflow: visible !important;
    z-index: 10010 !important;
    margin: 0 !important;
    padding: 0 !important;
  }"""

    css_content = css_content.replace(old_hand_panel, new_hand_panel)

    # 3. Re-adjust hand card sizes to 66px x 90px
    old_card_styles = """  .hand .card {
    width: 80px !important;
    height: 110px !important;
    min-width: 60px !important;
    flex: 0 0 80px !important;
    margin-left: -15px !important;
    border-radius: 6px !important;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.7) !important;
    transform: perspective(300px) rotateX(-15deg) !important;
    transition: transform 0.25s cubic-bezier(0.25, 0.8, 0.25, 1), z-index 0.15s ease !important;
    transform-origin: bottom center !important;
  }"""

    new_card_styles = """  .hand .card {
    width: 66px !important;
    height: 90px !important;
    min-width: 50px !important;
    flex: 0 0 66px !important;
    margin-left: -10px !important;
    border-radius: 5px !important;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.7) !important;
    transform: perspective(300px) rotateX(-15deg) !important;
    transition: transform 0.25s cubic-bezier(0.25, 0.8, 0.25, 1), z-index 0.15s ease !important;
    transform-origin: bottom center !important;
  }"""

    css_content = css_content.replace(old_card_styles, new_card_styles)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Adjusted boardWrap position/scale and shunk hand cards size in style_v8.css successfully!")

    # 4. Update cache-buster in static/index.html to v=18.70-topbar-and-overlap-fixed
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=18.70-topbar-and-overlap-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=18.70-topbar-and-overlap-fixed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    shift_top_right()
