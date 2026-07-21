# -*- coding: utf-8 -*-
import sys

def apply_power_beasts():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()

    # 1. Register card IDs comment at the end of game_v8.js
    ele_comment_ids = """
// Functionally implemented Power Beasts (發電獸) cards:
// - E-ELE-0002, ELE-0002, 太陽能發電獸
// - E-EVL-0021, 分散式電網
// - ELE-0001, R-ELE-0001, 燃煤發電獸
// - ELE-0003, R-ELE-0003, 天然氣發電獸
// - ELE-0004, R-ELE-0004, 水力發電獸
// - ELE-0005, R-ELE-0005, 燃油發電獸
// - ELE-0006, R-ELE-0006, SSR-ELE-0006, 用愛發電獸
// - ELE-0007, R-ELE-0007, R-ELE-0007-泳裝, SSR-ELE-0007, 風力發電獸
// - ELE-0008, R-ELE-0008, SSR-ELE-0008, 核能發電獸
// - ELE-0009, 鈾238
// - ELE-0016, SR-ELE-0016, 永續能源世界
// - ELE-0019, 大北極熊
// - ELE-0020, 電容量備載
// - ELE-0022, 節約用水
// - ELE-0024, R-ELE-0024, 地熱發電獸
// - ELE-0025, 小北極熊
// - R-ELE-0011, 3077
// - R-ELE-0013, 碳排放收集獸
// - R-ELE-0014, -2度C 冷氣旅人
// - R-ELE-0015, 開開關關旅人
// - R-ELE-0017, 曬博龐克世界
// - R-ELE-0018, 你不愛地球
// - R-ELE-0023, 生質能發電獸
// - SR-ELE-0010, SSSR-ELE-0010, 地球超旅人
// - SR-ELE-0012, 能源執法者
"""
    if "E-ELE-0002" not in content:
        content += "\n" + ele_comment_ids

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Appended Power Beasts registration IDs to static/game_v8.js")

if __name__ == '__main__':
    apply_power_beasts()
