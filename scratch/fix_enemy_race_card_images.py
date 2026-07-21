# -*- coding: utf-8 -*-
import sys, re, os, shutil

def fix_race_card_images():
    sys.stdout.reconfigure(encoding='utf-8')

    race_dir = 'static/race_cards'
    mapping = {
        '#U55b5#U55b5#U8cca.png': '喵喵賊.png',
        '#U5996#U602a#U6751#U838a.png': '妖怪村莊.png',
        '#U5996#U7cbe.png': '妖精.png',
        '#U5c71#U7f8a#U65cf.png': '山羊族.png',
        '#U6a5f#U68b0#U8ecd#U5718.png': '機械軍團.png',
        '#U6b61#U6a02#U5cf6.png': '歡樂島.png',
        '#U7279#U6b8a#U65c5#U4eba.png': '特殊旅人.png',
        '#U7378#U4eba.png': '獸人.png',
        '#U751c#U9ede#U738b#U570b.png': '甜點王國.png',
        '#U767c#U96fb#U7378.png': '發電獸.png',
        '#U78b3#U78b3#U65cf.png': '碳碳族.png',
        '#U84b8#U6c23#U4e16#U754c.png': '蒸氣世界.png',
        '#U85dd#U8853#U54c1.png': '藝術品.png',
        '#U865b#U64ec#U4e16#U754c.png': '虛擬世界.png',
        '#U9032#U5316#U91ce#U4eba.png': '進化野人.png',
        '#U99ac#U6232#U5718.png': '馬戲團.png',
        '#U9ab7#U9acf#U4eba.png': '骷髏人.png',
    }

    # Ensure clean Chinese filenames exist for all factions
    for src, dst in mapping.items():
        src_path = os.path.join(race_dir, src)
        dst_path = os.path.join(race_dir, dst)
        if os.path.exists(src_path) and not os.path.exists(dst_path):
            shutil.copy2(src_path, dst_path)
            print(f"Copied {src} -> {dst}")

    # Copy 勇者公會 if missing
    brav_src = os.path.join(race_dir, '喵喵賊.png')
    brav_dst = os.path.join(race_dir, '勇者公會.png')
    if os.path.exists(brav_src) and not os.path.exists(brav_dst):
        shutil.copy2(brav_src, brav_dst)
        print("Copied 勇者公會.png fallback")

    # Update getRaceCardSrc and raceCardImgHtml in static/game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    old_get_race_src = """function getRaceCardSrc(deckName) {
  const n = normDeckName(deckName || "喵喵賊");
  const f = XLW_RACE_CARD_FILES[n];
  if (f) return `/static/race_cards/${f}?v=20260613-mobile-realfix`;
  return `/static/race_cards/${encodeURIComponent(n)}.png?v=20260613-mobile-realfix`;
}
function raceCardImgHtml(name) {
  const n = normDeckName(name || "喵喵賊");
  const primary = getRaceCardSrc(n);
  const fallback = `/static/race_cards/${encodeURIComponent(n)}.png?v=20260613-mobile-realfix`;
  return `<img src="${primary}" onerror="if(!this.dataset.fallback){this.dataset.fallback='1';this.src='${fallback}';}else{this.onerror=null;this.src='/static/card_back.jpeg';}" style="width:100%;height:100%;object-fit:cover;border-radius:8px;" alt="${n}" title="${n}">`;
}"""

    new_get_race_src = """function getRaceCardSrc(deckName) {
  const n = normDeckName(deckName || "妖怪村莊");
  return `/static/race_cards/${encodeURIComponent(n)}.png?v=20260721-real-race-card`;
}
function raceCardImgHtml(name) {
  const n = normDeckName(name || "妖怪村莊");
  const primary = getRaceCardSrc(n);
  const fallback = `/static/race_cards/${XLW_RACE_CARD_FILES[n] || encodeURIComponent(n) + '.png'}?v=20260721-real-race-card`;
  return `<img src="${primary}" onerror="if(!this.dataset.fallback){this.dataset.fallback='1';this.src='${fallback}';}else{this.onerror=null;this.src='/static/card_back.jpeg';}" style="width:100%;height:100%;object-fit:cover;border-radius:8px;" alt="${n}" title="${n}">`;
}"""

    if old_get_race_src in js_content:
        js_content = js_content.replace(old_get_race_src, new_get_race_src)
        print("1. Updated getRaceCardSrc and raceCardImgHtml in static/game_v8.js successfully!")

    open(js_path, 'w', encoding='utf-8').write(js_content)

    # Update cache-buster in static/index.html to v=11.50-fix-enemy-race-card-image
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=11.50-fix-enemy-race-card-image', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=11.50-fix-enemy-race-card-image', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_race_card_images()
