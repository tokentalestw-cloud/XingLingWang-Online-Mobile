# -*- coding: utf-8 -*-
import sys, re

def restore_position():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Replace position: relative !important; with position: absolute !important; for forest containers
    old_rule = """#playerForest, #enemyForest {
  overflow: hidden !important;
  position: relative !important;
}"""

    new_rule = """#playerForest, #enemyForest {
  overflow: hidden !important;
  position: absolute !important;
}"""

    if old_rule in css_content:
        css_content = css_content.replace(old_rule, new_rule)
        open(css_path, 'w', encoding='utf-8').write(css_content)
        print("1. Restored position: absolute !important on #playerForest and #enemyForest in static/style_v8.css!")
    else:
        # Regex replacement if whitespace differs
        css_content = re.sub(
            r'#playerForest,\s*#enemyForest\s*\{\s*overflow:\s*hidden\s*!important;\s*position:\s*relative\s*!important;\s*\}',
            '#playerForest, #enemyForest {\n  overflow: hidden !important;\n  position: absolute !important;\n}',
            css_content
        )
        open(css_path, 'w', encoding='utf-8').write(css_content)
        print("1. Restored position: absolute !important via regex in static/style_v8.css!")

    # Update cache-buster in static/index.html to v=9.80-forest-position-restored
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=9.80-forest-position-restored', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=9.80-forest-position-restored', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    restore_position()
