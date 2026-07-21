# -*- coding: utf-8 -*-
import sys, re

def apply_deck_builder_title():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update topbar-brand HTML in static/index.html
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Ensure Cinzel font link is present in head
    cinzel_font_link = '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;900&family=Outfit:wght@400;700&display=swap" rel="stylesheet">'
    if 'family=Cinzel' not in idx_content:
        idx_content = idx_content.replace('</head>', f'  {cinzel_font_link}\n</head>')

    old_brand_html = '<div class="topbar-brand">✨ 星靈王</div>'
    new_brand_html = """<div class="topbar-brand">
      <span>XINGLINGWANG</span>
      <span style="color: rgba(255,255,255,0.25); font-size: 15px; margin: 0 4px;">|</span>
      <span style="font-size: 15px; color: #ffffff; letter-spacing: 0.5px; font-weight: bold;">星靈王</span>
    </div>"""

    if old_brand_html in idx_content:
        idx_content = idx_content.replace(old_brand_html, new_brand_html)
        print("1. Replaced topbar-brand HTML in static/index.html successfully!")

    # Update cache-buster to v=13.40-cinzel-deck-builder-title
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.40-cinzel-deck-builder-title', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.40-cinzel-deck-builder-title', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)

    # 2. Update .topbar-brand CSS in static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean previous .topbar-brand CSS block
    css_content = re.sub(
        r'\.topbar-brand\s*\{[^}]*\}',
        """.topbar-brand {
  font-family: 'Cinzel', serif !important;
  font-size: 22px !important;
  font-weight: 900 !important;
  color: #ffd76a !important;
  text-shadow: 0 0 12px rgba(255, 215, 106, 0.45) !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  letter-spacing: 1px !important;
  white-space: nowrap !important;
}""",
        css_content
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated .topbar-brand CSS in static/style_v8.css with Cinzel serif style successfully!")

if __name__ == '__main__':
    apply_deck_builder_title()
