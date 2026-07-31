# -*- coding: utf-8 -*-
import sys, re

def final_realign():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # 1. Move playerExile back to middle row next to playerRace (top: 467.5px)
    css_content = css_content.replace(
        "#playerExile { right: 330px !important; top: 781.5px !important; }",
        "#playerExile { right: 330px !important; top: 467.5px !important; }"
    )

    # 2. Position playerExtraDeck next to playerDeck in bottom row (right: 330px, top: 781.5px)
    css_content = css_content.replace(
        """#playerExtraDeck {
  right: -90px !important;
  top: 781.5px !important;
}""",
        """#playerExtraDeck {
  right: 330px !important;
  top: 781.5px !important;
}"""
    )

    # 3. Position preview panel to exact bottom-left edge (left: 0px, bottom: 0px)
    old_preview = """  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: fixed !important;
    left: -15px !important;
    bottom: 4px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(1.30) !important;
    transform-origin: bottom left !important;
  }"""

    new_preview = """  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: fixed !important;
    left: 0px !important;
    bottom: 0px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(1.30) !important;
    transform-origin: bottom left !important;
  }"""

    css_content = css_content.replace(old_preview, new_preview)

    # 4. Double topbar scale from 0.32 to 0.64
    css_content = css_content.replace(
        "transform: scale(0.32) !important;\n    transform-origin: top left !important;",
        "transform: scale(0.64) !important;\n    transform-origin: top left !important;"
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Successfully updated exile, extra deck, preview, and topbar scale in style_v8.css!")

    # 5. Update cache-buster in static/index.html to v=19.00-final-layout-fixed
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.00-final-layout-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.00-final-layout-fixed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    final_realign()
