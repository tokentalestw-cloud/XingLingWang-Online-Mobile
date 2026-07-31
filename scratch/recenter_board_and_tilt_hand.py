# -*- coding: utf-8 -*-
import sys, re

def recenter_and_tilt():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # 1. Recenter #boardWrap: shift top to 45% and adjust scale to 0.55
    old_board_block = """  #boardWrap {
    width: 1400px !important;
    height: 760px !important;
    min-width: 1400px !important;
    min-height: 760px !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) scale(0.68) !important;
    transform-origin: center center !important;
    margin: 0 !important;
  }"""

    new_board_block = """  #boardWrap {
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

    css_content = css_content.replace(old_board_block, new_board_block)

    # 2. Adjust hand card 3D tilt from rotateX(15deg) to rotateX(-15deg) for backward tilt
    old_hand_card_styles = """  .hand .card {
    width: 80px !important;
    height: 110px !important;
    min-width: 60px !important;
    flex: 0 0 80px !important;
    margin-left: -15px !important;
    border-radius: 6px !important;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.7) !important;
    transform: perspective(300px) rotateX(15deg) !important;
    transition: transform 0.25s cubic-bezier(0.25, 0.8, 0.25, 1), z-index 0.15s ease !important;
    transform-origin: bottom center !important;
  }"""

    new_hand_card_styles = """  .hand .card {
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

    css_content = css_content.replace(old_hand_card_styles, new_hand_card_styles)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Adjusted board position/scale and flipped card 3D tilt in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=18.60-recentered-and-tilted
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=18.60-recentered-and-tilted', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=18.60-recentered-and-tilted', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    recenter_and_tilt()
