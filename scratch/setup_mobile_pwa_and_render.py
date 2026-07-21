# -*- coding: utf-8 -*-
import sys, os, re
from PIL import Image, ImageDraw, ImageFont

def setup_pwa_and_render():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Create PWA App Icons (192x192 and 512x512)
    def create_app_icon(size, filename):
        img = Image.new('RGBA', (size, size), color=(14, 10, 20, 255))
        draw = ImageDraw.Draw(img)

        # Gold gradient outer border
        draw.rounded_rectangle([8, 8, size - 8, size - 8], radius=int(size * 0.22), fill=(18, 12, 28, 255), outline=(255, 215, 106, 255), width=int(size * 0.035))
        draw.rounded_rectangle([int(size * 0.08), int(size * 0.08), size - int(size * 0.08), size - int(size * 0.08)], radius=int(size * 0.18), fill=(26, 18, 38, 255), outline=(212, 175, 55, 180), width=int(size * 0.02))

        # Center star/symbol
        center = size // 2
        r = int(size * 0.22)
        # Gold Star polygon
        points = []
        import math
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            radius = r if i % 2 == 0 else r * 0.45
            x = center + int(radius * math.cos(angle))
            y = center + int(radius * math.sin(angle))
            points.append((x, y))

        draw.polygon(points, fill=(255, 230, 0, 255), outline=(255, 255, 255, 220))

        img.save(os.path.join('static', filename))
        print(f"Generated static/{filename} successfully!")

    create_app_icon(192, 'icon-192.png')
    create_app_icon(512, 'icon-512.png')

    # 2. Create static/manifest.json
    manifest_path = 'static/manifest.json'
    manifest_content = """{
  "name": "星靈王 XingLingWang",
  "short_name": "星靈王",
  "description": "星靈王 - 3D 橫向全畫面雙人對戰卡牌遊戲",
  "start_url": "/",
  "display": "standalone",
  "orientation": "landscape",
  "background_color": "#070505",
  "theme_color": "#161020",
  "icons": [
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/static/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
"""
    open(manifest_path, 'w', encoding='utf-8').write(manifest_content)
    print("2. Created static/manifest.json successfully!")

    # 3. Update static/index.html with iOS & PWA meta tags and Mobile Landscape Rotation Prompt
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    pwa_meta_tags = """  <!-- iOS & PWA 全螢幕橫向 App 支援標籤 -->
  <link rel="manifest" href="/static/manifest.json">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="星靈王">
  <link rel="apple-touch-icon" href="/static/icon-192.png">
  <meta name="theme-color" content="#161020">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">"""

    # Replace viewport meta tag if existing
    idx_content = re.sub(r'<meta name="viewport"[^>]*>', '', idx_content)
    if '</head>' in idx_content and 'apple-mobile-web-app-capable' not in idx_content:
        idx_content = idx_content.replace('</head>', f'{pwa_meta_tags}\n</head>')

    # Add mobile landscape orientation prompt overlay to HTML body
    landscape_prompt_html = """  <!-- 手機直向旋轉提示遮罩 (Mobile Portrait Rotate Prompt) -->
  <div id="xlwMobileRotatePrompt" class="xlw-mobile-rotate-prompt">
    <div class="rotate-card">
      <div class="rotate-icon">📱 ↷</div>
      <h2>請旋轉手機至橫向螢幕</h2>
      <p>《星靈王》專為手機橫向全螢幕對戰打造<br>請將手機轉為橫向以獲得最佳對戰視角</p>
      <div class="ios-install-tip">
        💡 <b>iPhone 桌面 App 設定提示：</b><br>
        點擊 Safari 下方「<b>分享</b>」按鈕 ➔ 選擇「<b>加入主畫面</b>」<br>即可像原生 App 一樣全螢幕開啟！
      </div>
    </div>
  </div>"""

    if 'xlwMobileRotatePrompt' not in idx_content:
        idx_content = idx_content.replace('</body>', f'{landscape_prompt_html}\n</body>')

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html with iOS PWA meta tags & mobile orientation prompt successfully!")

    # 4. Append Mobile Landscape CSS to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    mobile_landscape_css = """

/* ==========================================================================
   MOBILE LANDSCAPE FULLSCREEN PWA & ORIENTATION PROMPT
   (手機橫向全螢幕 PWA 與直向轉橫向提示遮罩)
   ========================================================================== */

/* 全螢幕 Viewport 滿版鎖定 */
html, body {
  width: 100vw !important;
  height: 100vh !important;
  overflow: hidden !important;
  padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left) !important;
}

/* 直向持握時顯示旋轉提示遮罩 */
.xlw-mobile-rotate-prompt {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(7, 5, 12, 0.98);
  backdrop-filter: blur(15px);
  z-index: 999999;
  justify-content: center;
  align-items: center;
  padding: 24px;
  box-sizing: border-box;
}

@media (max-width: 900px) and (orientation: portrait) {
  .xlw-mobile-rotate-prompt {
    display: flex !important;
  }
}

.rotate-card {
  background: linear-gradient(145deg, rgba(25, 18, 38, 0.95), rgba(12, 8, 20, 0.98));
  border: 1.5px solid #ffd76a;
  border-radius: 18px;
  padding: 30px 24px;
  text-align: center;
  max-width: 340px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.9), 0 0 30px rgba(255, 215, 106, 0.3);
}

.rotate-icon {
  font-size: 54px;
  color: #ffe600;
  margin-bottom: 12px;
  animation: rotatePhoneAnim 2.5s infinite ease-in-out;
}

@keyframes rotatePhoneAnim {
  0% { transform: rotate(0deg); }
  50% { transform: rotate(-90deg); }
  100% { transform: rotate(-90deg); }
}

.rotate-card h2 {
  color: #ffe600;
  font-size: 20px;
  font-weight: 900;
  margin-bottom: 10px;
}

.rotate-card p {
  color: #d1d5db;
  font-size: 13.5px;
  line-height: 1.6;
  margin-bottom: 18px;
}

.ios-install-tip {
  background: rgba(255, 215, 106, 0.08);
  border: 1px solid rgba(255, 215, 106, 0.3);
  border-radius: 10px;
  padding: 12px;
  color: #fef08a;
  font-size: 12px;
  line-height: 1.5;
  text-align: left;
}

"""

    css_content += mobile_landscape_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("4. Appended Mobile Landscape CSS to static/style_v8.css successfully!")

    # 5. Create Render Deployment Files (Procfile and render.yaml)
    procfile_path = 'Procfile'
    procfile_content = "web: uvicorn app:app --host 0.0.0.0 --port $PORT\n"
    open(procfile_path, 'w', encoding='utf-8').write(procfile_content)

    render_yaml_path = 'render.yaml'
    render_yaml_content = """services:
  - type: web
    name: xinglingwang-web
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
"""
    open(render_yaml_path, 'w', encoding='utf-8').write(render_yaml_content)
    print("5. Created Procfile and render.yaml for Render deployment successfully!")

if __name__ == '__main__':
    setup_pwa_and_render()
