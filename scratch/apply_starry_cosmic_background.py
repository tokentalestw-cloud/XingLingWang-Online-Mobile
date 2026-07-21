# -*- coding: utf-8 -*-
import sys, re

def apply_starry_bg():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # 1. Update :root variables
    css_content = re.sub(
        r'--bg-cosmic:\s*linear-gradient\(135deg, #f5f8fd 0%, #eef4fc 50%, #f5eeff 100%\);[^\n]*',
        '--bg-cosmic: radial-gradient(circle at 50% 25%, #1d1242 0%, #0e0924 40%, #060412 75%, #020106 100%);',
        css_content
    )
    css_content = re.sub(
        r'--text-primary:\s*#18182a;[^\n]*',
        '--text-primary: #ffffff;',
        css_content
    )
    css_content = re.sub(
        r'--text-muted:\s*#4e5066;[^\n]*',
        '--text-muted: #ffe6a0;',
        css_content
    )

    # 2. Append Starry Cosmic Celestial background layer styles
    starry_bg_css = """

/* ==========================================================================
   STARRY COSMIC CELESTIAL BACKGROUND SYSTEM (「星靈王」燦爛星空主題)
   ========================================================================== */

html, body {
  background: var(--bg-cosmic) !important;
  color: #ffffff !important;
  position: relative !important;
  overflow: hidden !important;
}

/* 燦爛星空與星雲塵埃層 */
body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image: 
    radial-gradient(1.5px 1.5px at 15% 18%, #ffffff 100%, transparent),
    radial-gradient(2px 2px at 35% 42%, #ffd76a 100%, transparent),
    radial-gradient(1px 1px at 60% 15%, #ffffff 100%, transparent),
    radial-gradient(2.5px 2.5px at 78% 35%, #80e5ff 100%, transparent),
    radial-gradient(1.5px 1.5px at 88% 68%, #ffd76a 100%, transparent),
    radial-gradient(2px 2px at 22% 75%, #ffffff 100%, transparent),
    radial-gradient(1px 1px at 48% 85%, #80e5ff 100%, transparent),
    radial-gradient(2.5px 2.5px at 70% 78%, #ffffff 100%, transparent),
    radial-gradient(1.5px 1.5px at 10% 55%, #ffd76a 100%, transparent),
    radial-gradient(2px 2px at 52% 48%, #ffffff 100%, transparent),
    radial-gradient(1.5px 1.5px at 92% 12%, #80e5ff 100%, transparent),
    radial-gradient(2.5px 2.5px at 30% 90%, #ffd76a 100%, transparent);
  background-size: 550px 550px;
  animation: starfieldTwinkle 4s infinite alternate ease-in-out;
  opacity: 0.85;
}

/* 宇宙神秘紫金極光塵埃層 */
body::after {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(114, 46, 209, 0.18) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(0, 255, 200, 0.12) 0%, transparent 50%),
    radial-gradient(circle at 50% 85%, rgba(255, 215, 0, 0.1) 0%, transparent 45%);
  filter: blur(20px);
}

@keyframes starfieldTwinkle {
  0% {
    opacity: 0.65;
    transform: scale(1);
  }
  50% {
    opacity: 0.95;
    transform: scale(1.01);
  }
  100% {
    opacity: 0.7;
    transform: scale(1);
  }
}

"""

    css_content += starry_bg_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with starry cosmic celestial background successfully!")

    # Update cache-buster in static/index.html to v=10.90-starry-cosmic-background
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.90-starry-cosmic-background', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.90-starry-cosmic-background', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_starry_bg()
