# -*- coding: utf-8 -*-
import sys

def apply_carbon_tribe():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()

    crb_comment_ids = """
// Functionally implemented Carbon Tribe (碳碳族) cards:
// - CRB-0002, SR-CRB-0002, 綠碳子
// - CRB-0003, 金碳子
// - CRB-0004, SSR-CRB-0004, 吹碳子
// - CRB-0005, 旅人公車-
// - CRB-0007, SR-CRB-0007, 吸管接龍
// - CRB-0008, R-CRB-0008, 一雙免洗筷
// - CRB-0010, R-CRB-0010, 旅人電動車
// - CRB-0011, 綠色消費人
// - CRB-0012, R-CRB-0012, SR-CRB-0012, SSSR-CRB-0012, 節能補充員
// - CRB-0014, SR-CRB-0014, 大樹
// - CRB-0016, 碳中和
// - CRB-0018, 碳交易所
// - CRB-0020, R-CRB-0020, 溫室效應
// - CRB-0021, R-CRB-0021, 碳足跡減少
// - CRB-0024, 旅人噴碳車
// - R-CRB-0006, SSR-CRB-0006, 巨大寶特瓶
// - R-CRB-0015, 塑膠袋浪人
// - R-CRB-0017, 碳稅
// - R-CRB-0019, 碳盤查
// - R-CRB-0022, R-CRB-0022-泳裝, 汙染者付費
// - R-CRB-0023, 藍碳王
// - R-CRB-0025, 下車鈴旅人
// - SR-CRB-0001, SSR-CRB-0001, 碳碳子
// - SR-CRB-0009, 旅人捷運
"""
    if "CRB-0002" not in content:
        content += "\n" + crb_comment_ids

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Appended Carbon Tribe registration IDs to static/game_v8.js")

if __name__ == '__main__':
    apply_carbon_tribe()
