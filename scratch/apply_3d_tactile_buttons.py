# -*- coding: utf-8 -*-
import sys

def apply_3d_buttons():
    sys.stdout.reconfigure(encoding='utf-8')
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Find the button block near line 3474
    old_btn_start = "button, select {"
    old_btn_end = "/* ==========================================================================\n   PURE CARD INSPECTOR PANEL"

    s_idx = css_content.find(old_btn_start)
    e_idx = css_content.find(old_btn_end)

    if s_idx < 0:
        s_idx = css_content.rfind("button, select")
    
    new_3d_button_css = """/* ==========================================================================
   ULTRA-TACTILE 3D ARCADE BUTTONS SYSTEM (高級立體質感按鈕系統)
   ========================================================================== */

button, select {
  background: linear-gradient(180deg, #fff47d 0%, #ffe600 48%, #d6a700 100%) !important;
  color: #000000 !important;
  border: 2px solid #000000 !important;
  border-bottom: 5px solid #7a5f00 !important;
  border-radius: 10px !important;
  font-family: system-ui, "Noto Sans TC", sans-serif !important;
  font-weight: 900 !important;
  letter-spacing: 0.5px !important;
  padding: 8px 18px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.7), 0 4px 12px rgba(0, 0, 0, 0.6), 0 2.5px 0 #000000 !important;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.4) !important;
  position: relative !important;
  cursor: pointer !important;
  transition: all 0.12s cubic-bezier(0.2, 0.8, 0.4, 1) !important;
  user-select: none !important;
}

button:hover:not(:disabled), select:hover {
  transform: translateY(-2px) !important;
  background: linear-gradient(180deg, #ffffff 0%, #fff066 48%, #e6b800 100%) !important;
  border-bottom-width: 6px !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.9), 0 8px 20px rgba(0, 0, 0, 0.7), 0 0 18px rgba(255, 230, 0, 0.65) !important;
}

button:active:not(:disabled), select:active {
  transform: translateY(3px) !important;
  border-bottom-width: 2px !important;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.4), 0 2px 5px rgba(0, 0, 0, 0.5) !important;
}

/* 1. 單人對抗 AI (核心黃金立體按鈕) */
#newGameBtn {
  background: linear-gradient(180deg, #fff7a0 0%, #ffd700 48%, #c99c00 100%) !important;
  color: #000000 !important;
  border: 2px solid #000000 !important;
  border-bottom: 5px solid #695100 !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.8), 0 5px 15px rgba(255, 215, 0, 0.4), 0 2.5px 0 #000000 !important;
}

#newGameBtn:hover {
  background: linear-gradient(180deg, #ffffff 0%, #ffe033 48%, #d4af37 100%) !important;
  box-shadow: inset 0 1.5px 0 #ffffff, 0 8px 22px rgba(255, 215, 0, 0.7), 0 0 20px rgba(255, 215, 0, 0.8) !important;
}

/* 2. 線上雙人對決 (強烈霓虹紅金立體按鈕) */
#multiplayerBtn {
  background: linear-gradient(180deg, #ff6b8b 0%, #ff1f4c 48%, #b80024 100%) !important;
  color: #ffffff !important;
  border: 2.5px solid #ffe600 !important;
  border-bottom: 5px solid #5e0012 !important;
  text-shadow: 1.5px 1.5px 0px #000000 !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.5), 0 5px 15px rgba(255, 31, 76, 0.5), 0 2.5px 0 #000000 !important;
}

#multiplayerBtn:hover {
  background: linear-gradient(180deg, #ff99af 0%, #ff335e 48%, #d6002c 100%) !important;
  box-shadow: inset 0 1.5px 0 #ffffff, 0 8px 22px rgba(255, 31, 76, 0.8), 0 0 22px rgba(255, 230, 0, 0.8) !important;
}

/* 3. 戰局紀錄、牌組編輯器、卡牌編輯器 (暗黑金邊水晶按鈕) */
#scoreBtn, .topbar a button {
  background: linear-gradient(180deg, #2e263d 0%, #1c1628 48%, #100c17 100%) !important;
  color: #ffe600 !important;
  border: 2px solid #ffe600 !important;
  border-bottom: 5px solid #000000 !important;
  text-shadow: 1px 1px 0px #000000 !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 230, 0, 0.4), 0 4px 12px rgba(0, 0, 0, 0.8), 0 2.5px 0 #000000 !important;
}

#scoreBtn:hover, .topbar a button:hover {
  background: linear-gradient(180deg, #44385c 0%, #2b223d 48%, #1a1426 100%) !important;
  color: #ffffff !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.6), 0 8px 20px rgba(0, 0, 0, 0.9), 0 0 15px rgba(255, 230, 0, 0.6) !important;
}

/* 4. Dropdown Select 下拉選單立體質感 */
select {
  padding-right: 28px !important;
  appearance: none !important;
  -webkit-appearance: none !important;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'></polyline></svg>") !important;
  background-repeat: no-repeat !important;
  background-position: right 8px center !important;
}

/* 5. Modal 與 彈窗按鈕 (.close, .btn) */
.close {
  background: linear-gradient(180deg, #ff5c5c 0%, #cc0000 100%) !important;
  color: #ffffff !important;
  border: 2px solid #000000 !important;
  border-bottom: 4px solid #660000 !important;
  border-radius: 50% !important;
  width: 32px !important;
  height: 32px !important;
  padding: 0 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 18px !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.5), 0 3px 8px rgba(0,0,0,0.6) !important;
}

.close:hover {
  transform: scale(1.1) translateY(-1px) !important;
  background: linear-gradient(180deg, #ff8080 0%, #e60000 100%) !important;
}

"""

    if s_idx >= 0 and e_idx >= 0:
        css_content = css_content[:s_idx] + new_3d_button_css + css_content[e_idx:]
    else:
        css_content += "\n\n" + new_3d_button_css

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("Applied ultra-tactile 3D buttons CSS to static/style_v8.css successfully!")

if __name__ == '__main__':
    apply_3d_buttons()
