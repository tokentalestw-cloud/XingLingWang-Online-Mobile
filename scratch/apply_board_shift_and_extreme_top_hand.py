# -*- coding: utf-8 -*-
import os, sys, re

def apply_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Move #boardWrap downward by 100px
    css_content = css_content.replace(
        'top: 50% !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.44) !important;',
        'top: calc(50% + 100px) !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.44) !important;'
    )

    css_content = css_content.replace(
        'top: 30% !important;\n    left: 50% !important;\n    transform: translate(-42.5%, -50%) scale(0.46) !important;',
        'top: calc(30% + 100px) !important;\n    left: 50% !important;\n    transform: translate(-42.5%, -50%) scale(0.46) !important;'
    )

    # Move .xlw-enemy-floating-hand upward to extreme limit (top: -20px) and hide count badge text
    old_floating_hand_css = """.xlw-enemy-floating-hand {
  position: absolute !important;
  top: 8px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  z-index: 99999999 !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  pointer-events: none !important;
  filter: none !important;
  backdrop-filter: none !important;
}

.floating-enemy-hand-wrap {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 2px !important;
}

.floating-enemy-count-badge {
  font-size: 10px !important;
  font-weight: bold !important;
  color: #ffd76a !important;
  background: rgba(12, 8, 22, 0.95) !important;
  border: 1px solid rgba(255, 215, 106, 0.4) !important;
  border-radius: 12px !important;
  padding: 2px 8px !important;
  white-space: nowrap !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.8) !important;
}"""

    new_floating_hand_css = """.xlw-enemy-floating-hand {
  position: absolute !important;
  top: -20px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  z-index: 99999999 !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  pointer-events: none !important;
  filter: none !important;
  backdrop-filter: none !important;
}

.floating-enemy-hand-wrap {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 0px !important;
}

.floating-enemy-count-badge {
  display: none !important;
}"""

    css_content = css_content.replace(old_floating_hand_css, new_floating_hand_css)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated style_v8.css with +100px board downward shift & extreme top opponent hand without count badge successfully!")

    # 2. Update index.html cache-buster
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=21.60-board-shifted-down-100-extreme-top-hand', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=21.60-board-shifted-down-100-extreme-top-hand', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_fixes()
