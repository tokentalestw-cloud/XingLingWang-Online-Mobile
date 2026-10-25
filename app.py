import os
import json
import shutil
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional

BASE = Path(__file__).parent
app = FastAPI(title="星靈王 Web Final")

from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response

# 啟用全域高速 GZip 壓縮（體積 > 1000 bytes 自動壓縮，減少 80% 傳輸量）
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_smart_cache_headers(request, call_next):
    response = await call_next(request)
    path = request.url.path

    # API 端點：動態資料絕不快取
    if path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    elif path.endswith(".html") or path == "/":
        # HTML 頁面：採用 no-cache 搭配 revalidate，確保即時取得最新代碼版號
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response

class OptimizedStaticFiles(StaticFiles):
    """高效分級靜態資源快取：圖片/音效/字體長效快取，JS/CSS 與 JSON 依版號快取，消除 Render 網路延遲與卡頓"""
    def file_response(self, *args, **kwargs) -> Response:
        response = super().file_response(*args, **kwargs)
        path = str(args[0]) if args else ""
        ext = os.path.splitext(path)[1].lower()

        # 圖片、音效、字型資源：長效快取 30 天，秒開 0ms 記憶體讀取，徹底解決牌面無法立即顯示問題
        if ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico", ".mp3", ".wav", ".woff", ".woff2", ".ttf"]:
            response.headers["Cache-Control"] = "public, max-age=2592000, immutable"
            response.headers["Pragma"] = "public"
        # JavaScript 與 CSS 資源：搭配 query string (?v=...) 快取 24 小時
        elif ext in [".js", ".css"]:
            response.headers["Cache-Control"] = "public, max-age=86400, stale-while-revalidate=3600"
        # 靜態 JSON 牌庫資料
        elif ext == ".json":
            response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=60"
        # HTML 檔案
        elif ext == ".html":
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
        else:
            response.headers["Cache-Control"] = "public, max-age=3600"

        return response

app.mount("/static", OptimizedStaticFiles(directory=BASE / "static"), name="static")

# ===== 線上雙人即時房間管理器 =====
class ConnectionManager:
    def __init__(self):
        # room_id -> {
        #   "player1": (player_id, ws),
        #   "player2": (player_id, ws),
        #   "decks": { "player1": dict, "player2": dict },
        #   "sync_decks": { "player1": dict, "player2": dict },
        #   "last_state": { "player1": dict, "player2": dict }
        # }
        self.rooms = {}

    def _ensure_room_meta(self, room_id: str):
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        r = self.rooms[room_id]
        if "decks" not in r:
            r["decks"] = {}
        if "sync_decks" not in r:
            r["sync_decks"] = {}
        if "last_state" not in r:
            r["last_state"] = {}
        return r

    async def connect(self, room_id: str, player_id: str, role: str, websocket: WebSocket):
        await websocket.accept()
        r = self._ensure_room_meta(room_id)
        
        is_reconnect = False
        role_assigned = role
        
        if not role_assigned:
            # 決定玩家角色 (Player1 或 Player2) 並支援斷線重連
            if "player1" in r and r["player1"][0] == player_id:
                role_assigned = "player1"
                is_reconnect = True
            elif "player2" in r and r["player2"][0] == player_id:
                role_assigned = "player2"
                is_reconnect = True
            else:
                if "player1" not in r:
                    role_assigned = "player1"
                elif "player2" not in r:
                    role_assigned = "player2"
                else:
                    # 檢查舊連線是否已失效，若是同一位或死連線則允許接管
                    print(f"Room {room_id}: connection rejected for {player_id}.")
                    await websocket.send_json({
                        "type": "error",
                        "message": "房間已滿或您已在連線中！"
                    })
                    await websocket.close()
                    return
        else:
            # 使用指定角色，若已被其他 player_id 連線，檢查舊連線是否存活
            if role_assigned in r:
                existing_player_id, existing_ws = r[role_assigned]
                if existing_player_id != player_id:
                    print(f"Room {room_id}: connection rejected for {player_id} (role {role_assigned} already occupied by {existing_player_id}).")
                    await websocket.send_json({
                        "type": "error",
                        "message": "該角色已在連線中！"
                    })
                    await websocket.close()
                    return
                else:
                    is_reconnect = True

        r[role_assigned] = (player_id, websocket)
        print(f"Room {room_id}: {role_assigned} ({player_id}) connected. Is reconnect: {is_reconnect}")
        
        await websocket.send_json({
            "type": "welcome",
            "role": role_assigned,
            "is_reconnect": is_reconnect,
            "message": f"成功連接房間 {room_id}！角色為 {role_assigned}。"
        })
        
        # 通知雙方
        if "player1" in r and "player2" in r:
            p1_id, p1_ws = r["player1"]
            p2_id, p2_ws = r["player2"]
            other_role = "player2" if role_assigned == "player1" else "player1"
            other_ws = p2_ws if role_assigned == "player1" else p1_ws
            this_ws = p1_ws if role_assigned == "player1" else p2_ws
            
            if is_reconnect:
                try:
                    await other_ws.send_json({
                        "type": "opponent_rejoined",
                        "message": "對手已重新連線！對決繼續。"
                    })
                except:
                    pass
                try:
                    await this_ws.send_json({
                        "type": "opponent_rejoined_ack",
                        "message": "已成功重新連接到對決！"
                    })
                except:
                    pass
                # 若對手已選過牌組，補發給重連方
                if other_role in r.get("decks", {}):
                    try:
                        await this_ws.send_json(r["decks"][other_role])
                    except:
                        pass
            else:
                try:
                    await p1_ws.send_json({
                        "type": "opponent_joined",
                        "message": "對手已進入房間，遊戲即將開始！"
                    })
                except:
                    pass
                try:
                    await p2_ws.send_json({
                        "type": "opponent_joined",
                        "message": "已連接到房主，遊戲即將開始！"
                    })
                except:
                    pass
                # 若有一方在對手進房前就已經先送出 multi_deck_selected，自動補發給剛進房的對手
                if other_role in r.get("decks", {}):
                    try:
                        await this_ws.send_json(r["decks"][other_role])
                    except:
                        pass

    def disconnect(self, room_id: str, player_id: str, websocket: WebSocket = None):
        if room_id in self.rooms:
            r = self.rooms[room_id]
            if "player1" in r and r["player1"][0] == player_id:
                if websocket is None or r["player1"][1] is websocket:
                    r.pop("player1", None)
                    print(f"Room {room_id}: Player1 disconnected.")
            elif "player2" in r and r["player2"][0] == player_id:
                if websocket is None or r["player2"][1] is websocket:
                    r.pop("player2", None)
                    print(f"Room {room_id}: Player2 disconnected.")
            
            if not r.get("player1") and not r.get("player2"):
                self.rooms.pop(room_id, None)
                print(f"Room {room_id} is now empty and destroyed.")

    async def broadcast_to_other(self, room_id: str, sender_id: str, message: dict):
        if room_id in self.rooms:
            r = self._ensure_room_meta(room_id)
            sender_role = None
            target_ws = None
            if "player1" in r and r["player1"][0] == sender_id:
                sender_role = "player1"
                if "player2" in r:
                    target_ws = r["player2"][1]
            elif "player2" in r and r["player2"][0] == sender_id:
                sender_role = "player2"
                if "player1" in r:
                    target_ws = r["player1"][1]

            action = message.get("action")
            if sender_role:
                if action == "multi_deck_selected":
                    r["decks"][sender_role] = json.loads(json.dumps(message))
                elif action == "sync_deck":
                    r["sync_decks"][sender_role] = json.loads(json.dumps(message))
                elif action == "sync_game_state":
                    r["last_state"][sender_role] = json.loads(json.dumps(message))
                elif action == "new_game":
                    r["decks"].clear()
                    r["sync_decks"].clear()
                    r["last_state"].clear()
            
            if target_ws:
                try:
                    # 自動翻轉座標，保證兩端視角都是我方在下、對手在上
                    flipped_message = self.flip_message_coordinates(message)
                    await target_ws.send_json(flipped_message)
                except Exception as e:
                    print(f"Error broadcasting message to target player: {e}")

    def flip_message_coordinates(self, msg: dict) -> dict:
        flipped = json.loads(json.dumps(msg))
        if flipped.get("action") == "sync_game_state":
            # sync_game_state 包含全域戰場 field，由前端在接收時專屬對稱翻轉
            return flipped

        zone_map = {
            "player_front": "enemy_front",
            "player_back": "enemy_back",
            "enemy_front": "player_front",
            "enemy_back": "player_back"
        }

        def flip_recursive(obj):
            if isinstance(obj, dict):
                for k, v in list(obj.items()):
                    if isinstance(v, str) and v in zone_map:
                        obj[k] = zone_map[v]
                    elif isinstance(v, (dict, list)):
                        flip_recursive(v)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        flip_recursive(item)

        flip_recursive(flipped)
        return flipped

manager = ConnectionManager()

@app.websocket("/ws/battle/{room_id}/{player_id}")
@app.websocket("/ws/battle/{room_id}/{player_id}/{role}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, player_id: str, role: str = None):
    await manager.connect(room_id, player_id, role, websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                if message.get("action") == "ping":
                    # 傳回 pong 以維持雙向活躍連線，防止 Render 50 秒閒置逾時斷線
                    await websocket.send_json({"action": "pong"})
                    continue
                await manager.broadcast_to_other(room_id, player_id, message)
            except WebSocketDisconnect:
                raise
            except Exception as e:
                print(f"Error in websocket loop for room {room_id}, player {player_id}: {e}")
    except WebSocketDisconnect:
        manager.disconnect(room_id, player_id, websocket)
        if room_id in manager.rooms:
            r = manager.rooms[room_id]
            remaining_ws = None
            if "player1" in r:
                remaining_ws = r["player1"][1]
            elif "player2" in r:
                remaining_ws = r["player2"][1]
            if remaining_ws:
                try:
                    await remaining_ws.send_json({
                        "type": "opponent_disconnected",
                        "temporary": True,
                        "message": "對手連線已中斷，正在等待其重新連接..."
                    })
                except:
                    pass

def is_neutral_card(card_obj: dict, cid: str) -> bool:
    if not card_obj:
        return False
    id_upper = cid.upper()
    return (
        card_obj.get("faction") in ["中立", "中立單位"] or
        card_obj.get("race") in ["中立", "中立單位"] or
        card_obj.get("deck") in ["中立", "中立單位"] or
        id_upper.startswith("NEU-")
    )

# 卡牌表單結構
class CardSaveSchema(BaseModel):
    id: str
    name: str
    deck: str
    type: str
    faction: str
    attack: str # 可以是數字字串，也可以是 "盾"
    score: int
    tribute: int
    keywords: List[str]
    effect_text: str
    is_extra_deck: bool
    extra_deck_limit: int
    art_subtype: Optional[str] = ""
    original_file: str # 例如 "喵喵賊/IMG_5796.JPG"
    mana: int
    usable_phases: List[str]
    trigger_condition: Optional[str] = ""
    previous_id: Optional[str] = None

@app.get("/")
def index():
    response = FileResponse(BASE / "static" / "index.html")
    response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response

@app.get("/api/cards")
def get_cards():
    cards_file = BASE / "data" / "cards.json"
    if not cards_file.exists():
        return []
    return json.loads(cards_file.read_text(encoding="utf-8"))

@app.get("/api/decks")
def get_decks():
    decks_file = BASE / "data" / "decks.json"
    if not decks_file.exists():
        return {}
    return json.loads(decks_file.read_text(encoding="utf-8"))

class ClientErrorLog(BaseModel):
    message: str
    source: str
    lineno: int
    colno: int
    stack: str

@app.post("/api/log_error")
def log_client_error(err: ClientErrorLog):
    print("---------------------------------------------")
    print(f"🛑 CLIENT-SIDE ERROR LOGGED:")
    print(f"Message: {err.message}")
    print(f"Source: {err.source}:{err.lineno}:{err.colno}")
    print(f"Stack Trace:\n{err.stack}")
    print("---------------------------------------------")
    return {"status": "ok"}

# 1. 取得未處理與已處理的照片列表
@app.get("/api/admin/unprocessed")
def get_unprocessed_images():
    src_dir = Path("C:/Users/a2132/Downloads/星靈王圖片")
    
    # 讀取目前資料庫中已經關聯的原始相片檔名，避免重複錄入
    cards_file = BASE / "data" / "cards.json"
    processed_files = set()
    cards_data = []
    if cards_file.exists():
        try:
            cards_data = json.loads(cards_file.read_text(encoding="utf-8"))
            for c in cards_data:
                orig = c.get("original_file")
                if orig:
                    processed_files.add(orig.replace('\\', '/').strip())
        except Exception as e:
            print("讀取 cards.json 失敗:", e)

    subdirs = [
        "中立單位", "喵喵賊", "妖怪村莊", "藝術品", "獸人", "虛擬世界",
        "勇者公會", "妖精", "山羊族", "機械軍團", "歡樂島", "特殊旅人",
        "甜點王國", "發電獸", "碳碳族", "蒸汽世界",
        "進化野人", "馬戲團", "骷髏人"
    ]
    unprocessed = []
    
    # 1. 掃描本機下載資料夾得到未處理圖片
    if src_dir.exists():
        for sub in subdirs:
            subpath = src_dir / sub
            if subpath.exists():
                for f in sorted(os.listdir(subpath)):
                    if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        rel_path = f"{sub}/{f}"
                        photo_obj = {
                            "subdir": sub,
                            "filename": f,
                            "rel_path": rel_path,
                            "size": os.path.getsize(subpath / f)
                        }
                        if rel_path not in processed_files:
                            unprocessed.append(photo_obj)

    # 2. 已入庫卡片：直接使用 cards.json 裡的所有卡片，即使本地 Downloads 照片已被刪除也可以進行編輯！
    processed = []
    for c in cards_data:
        orig = c.get("original_file") or ""
        # 推導 subdir 和 filename 供前端顯示與預覽
        subdir = "中立單位" if c.get("deck") == "中立" else c.get("deck")
        if "/" in orig:
            parts = orig.split("/")
            subdir = parts[0]
            filename = parts[1]
        else:
            filename = os.path.basename(c.get("image") or "") or f"{c.get('id')}.jpeg"

        processed.append({
            "id": c.get("id"),
            "name": c.get("name"),
            "subdir": subdir,
            "filename": filename,
            "rel_path": orig,
            "size": 0
        })
                        
    return {"status": "success", "unprocessed": unprocessed, "processed": processed}

# 2. 串流下載目錄中的卡牌原始照片
@app.get("/api/admin/image/{subdir}/{filename}")
def get_admin_image(subdir: str, filename: str):
    src_path = Path("C:/Users/a2132/Downloads/星靈王圖片") / subdir / filename
    if not src_path.exists():
        raise HTTPException(status_code=404, detail="圖片檔案不存在")
    return FileResponse(src_path)

# 3. 儲存卡牌、更新 JSON 並複製/重命名照片
@app.post("/api/admin/save")
def save_new_card(card: CardSaveSchema):
    # 1. 統一將 ID 轉為小寫，底線分隔，如 ART-0001 轉為 art_0001.jpeg，CAT-001 轉為 cat_001.jpeg
    clean_id = card.id.strip().lower().replace("-", "_")
    dest_filename = f"{clean_id}.jpeg"
    dest_dir = BASE / "static" / "card_images"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / dest_filename

    src_path = Path("C:/Users/a2132/Downloads/星靈王圖片") / card.original_file if card.original_file else None

    # 2. 讀取並更新 cards.json
    cards_file = BASE / "data" / "cards.json"
    cards_file.parent.mkdir(parents=True, exist_ok=True)
    cards = []
    if cards_file.exists():
        try:
            cards = json.loads(cards_file.read_text(encoding="utf-8"))
        except:
            cards = []

    # 尋找是否已有這張卡牌的已入庫資料
    existing_card = None
    if card.previous_id:
        existing_card = next((c for c in cards if c.get("id") == card.previous_id), None)
    elif card.original_file:
        existing_card = next((c for c in cards if c.get("original_file") == card.original_file), None)

    # 處理圖片拷貝/重命名
    old_clean_id = existing_card.get("id").strip().lower().replace("-", "_") if existing_card else None
    old_dest_filename = f"{old_clean_id}.jpeg" if old_clean_id else None
    old_dest_path = dest_dir / old_dest_filename if old_dest_filename else None

    if src_path and src_path.exists():
        try:
            shutil.copy2(src_path, dest_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"複製照片失敗: {str(e)}")
    elif old_dest_path and old_dest_path.exists():
        if old_dest_path != dest_path:
            try:
                shutil.copy2(old_dest_path, dest_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"複製快取照片失敗: {str(e)}")
    elif not dest_path.exists():
        raise HTTPException(status_code=400, detail=f"找不到原始照片且伺服器端無快取")

    # 如果修改了 ID 且舊圖片存在，則刪除舊的圖片檔
    if old_dest_path and old_dest_path.exists() and old_dest_path != dest_path:
        try:
            os.remove(old_dest_path)
        except Exception as e:
            print(f"刪除舊圖片 {old_dest_path} 失敗:", e)

    # 刪除已存在的卡牌（覆寫）
    if card.previous_id:
        cards = [c for c in cards if c.get("id") != card.previous_id]
    cards = [c for c in cards if c.get("id") != card.id]

    # 建構卡牌對象，若勾選額外牌組，則 deck_eligible = false (不入一般牌組)
    new_card_obj = {
        "id": card.id,
        "name": card.name,
        "deck": "中立" if card.deck == "中立單位" else card.deck,
        "type": card.type,
        "faction": "中立" if card.faction == "中立單位" else card.faction,
        "race": "中立" if card.faction == "中立單位" else card.faction, # 種族與陣營名稱一致
        "attack": card.attack,
        "score": card.score,
        "tribute": card.tribute,
        "keywords": card.keywords,
        "effect_text": card.effect_text,
        "image": f"/static/card_images/{dest_filename}",
        "original_file": card.original_file,
        "deck_eligible": not card.is_extra_deck,
        "mana": card.mana,
        "usable_phases": card.usable_phases,
        "trigger_condition": card.trigger_condition,
    }
    
    if card.is_extra_deck:
        new_card_obj["extra_deck_limit"] = card.extra_deck_limit
    if card.art_subtype:
        new_card_obj["art_subtype"] = card.art_subtype

    cards.append(new_card_obj)
    
    # 依 ID 排序使資料庫整齊
    cards.sort(key=lambda x: x.get("id", ""))
    cards_file.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3. 讀取並更新 decks.json
    decks_file = BASE / "data" / "decks.json"
    decks_data = {}
    if decks_file.exists():
        try:
            decks_data = json.loads(decks_file.read_text(encoding="utf-8"))
        except:
            decks_data = {}

    # 移除舊 ID
    if card.previous_id:
        for dname in list(decks_data.keys()):
            if card.previous_id in decks_data[dname]:
                decks_data[dname].remove(card.previous_id)

    # 確保對應的牌組陣列存在
    deck_name = card.deck
    if deck_name not in decks_data:
        decks_data[deck_name] = []

    # 將卡牌 ID 加入陣列（避免重複）
    if card.id not in decks_data[deck_name]:
        decks_data[deck_name].append(card.id)
        decks_data[deck_name].sort()

    # 新增：若更新後的牌組是 "藝術品"，清除不屬於藝術品陣營的卡片 ID
    if deck_name == "藝術品":
        # 建立 id -> card mapping
        cards_file = BASE / "data" / "cards.json"
        card_map = {}
        if cards_file.exists():
            try:
                all_cards = json.loads(cards_file.read_text(encoding="utf-8"))
                for c in all_cards:
                    cid = c.get("id")
                    if cid:
                        card_map[cid] = c
            except:
                pass
        # 保留僅 faction 為 藝術品 或中立的卡片 ID
        valid_ids = []
        for cid in decks_data[deck_name]:
            card_obj = card_map.get(cid)
            if card_obj and (card_obj.get("faction") == "藝術品" or is_neutral_card(card_obj, cid)):
                valid_ids.append(cid)
        decks_data[deck_name] = valid_ids

    decks_file.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 同步複製一份 decks.json 到 static/ 目錄，讓前端讀取
    static_decks = BASE / "static" / "decks.json"
    static_decks.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"status": "success", "message": f"成功建立卡牌 {card.name}，照片已命名為 {dest_filename}"}

# 牌組儲存表單結構
class DeckSaveSchema(BaseModel):
    deck_name: str
    card_ids: List[str]
    extra_card_ids: Optional[List[str]] = None

# 新增：清理藝術品牌組中不屬於藝術品陣營的卡片 (可手動呼叫)
@app.post("/api/clean_art_deck")
def clean_art_deck():
    decks_file = BASE / "data" / "decks.json"
    if not decks_file.exists():
        raise HTTPException(status_code=404, detail="decks.json not found")
    decks_data = json.loads(decks_file.read_text(encoding="utf-8"))
    if "藝術品" not in decks_data:
        return {"status": "success", "message": "藝術品牌組不存在，無需清理"}
    # 讀取所有卡片資料以驗證陣營
    cards_file = BASE / "data" / "cards.json"
    card_map = {}
    if cards_file.exists():
        all_cards = json.loads(cards_file.read_text(encoding="utf-8"))
        for c in all_cards:
            cid = c.get("id")
            if cid:
                card_map[cid] = c
    # 只保留 faction 為 藝術品 或中立的卡片 ID
    valid_ids = [cid for cid in decks_data["藝術品"] if card_map.get(cid, {}).get("faction") == "藝術品" or is_neutral_card(card_map.get(cid), cid)]
    removed = len(decks_data["藝術品"]) - len(valid_ids)
    decks_data["藝術品"] = valid_ids
    # 寫回檔案
    decks_file.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
    # 同步 static
    static_decks = BASE / "static" / "decks.json"
    static_decks.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "success", "message": f"已移除 {removed} 張不屬於藝術品陣營的卡片"}

# 4. 儲存/重構整套牌組
@app.post("/api/decks/save")
def save_deck(data: DeckSaveSchema):
    decks_file = BASE / "data" / "decks.json"
    decks_data = {}
    if decks_file.exists():
        try:
            decks_data = json.loads(decks_file.read_text(encoding="utf-8"))
        except:
            decks_data = {}

    # 嚴格後端陣營排他性過濾
    cards_file = BASE / "data" / "cards.json"
    card_map = {}
    if cards_file.exists():
        try:
            all_cards = json.loads(cards_file.read_text(encoding="utf-8"))
            for c in all_cards:
                cid = c.get("id")
                if cid:
                    card_map[cid] = c
        except:
            pass

    cleaned_ids = []
    deck_name = data.deck_name
    for cid in data.card_ids:
        card_obj = card_map.get(cid)
        if not card_obj:
            continue
        
        id_upper = cid.upper()
        is_valid = True
        
        if not is_neutral_card(card_obj, cid):
            faction_prefixes = {
                "藝術品": ["ART"],
                "喵喵賊": ["CAT"],
                "妖怪村莊": ["VLG"],
                "獸人": ["ORC"],
                "虛擬世界": ["VRT", "CRP"],
                "勇者公會": ["BRV"],
                "妖精": ["EVL"],
                "山羊族": ["GOT"],
                "機械軍團": ["RBT"],
                "歡樂島": ["FMS"],
                "特殊旅人": ["SPT"],
                "甜點王國": ["CND"],
                "發電獸": ["ELE"],
                "碳碳族": ["CRB"],
                "蒸汽世界": ["STP"],
                "進化野人": ["EWD"],
                "馬戲團": ["CCS"],
                "骷髏人": ["SKT"]
            }
            deck_faction = None
            for fac in faction_prefixes.keys():
                if fac in deck_name:
                    deck_faction = fac
                    break
            if deck_faction:
                belongs_to_other = False
                for fac, prefixes in faction_prefixes.items():
                    if fac != deck_faction:
                        if any(p in id_upper for p in prefixes) or card_obj.get("faction") == fac or card_obj.get("race") == fac:
                            belongs_to_other = True
                            break
                if belongs_to_other:
                    is_valid = False
                else:
                    prefixes = faction_prefixes[deck_faction]
                    card_faction = card_obj.get("faction") or card_obj.get("deck") or ""
                    matches_faction = (card_faction == deck_faction) or any(id_upper.startswith(p) for p in prefixes)
                    if not matches_faction:
                        is_valid = False
                
        if is_valid:
            cleaned_ids.append(cid)

    # 覆寫該牌組（已過濾乾淨）
    total_mana = sum(int(card_map.get(cid, {}).get("mana") or 0) for cid in cleaned_ids if card_map.get(cid))
    if len(cleaned_ids) != 20:
        raise HTTPException(status_code=400, detail="主牌組必須剛好為 20 張才能儲存！")
    if total_mana > 15:
        raise HTTPException(status_code=400, detail="主牌組法力值總和不可超過 15 點！")

    decks_data[data.deck_name] = cleaned_ids

    # 處理並過濾額外牌組
    if data.extra_card_ids is not None:
        cleaned_extra_ids = []
        for cid in data.extra_card_ids:
            card_obj = card_map.get(cid)
            if not card_obj:
                continue
            
            id_upper = cid.upper()
            is_valid = True
            
            if not is_neutral_card(card_obj, cid):
                faction_prefixes = {
                    "藝術品": ["ART"],
                    "喵喵賊": ["CAT"],
                    "妖怪村莊": ["VLG"],
                    "獸人": ["ORC"],
                    "虛擬世界": ["VRT", "CRP"],
                    "勇者公會": ["BRV"],
                    "妖精": ["EVL"],
                    "山羊族": ["GOT"],
                    "機械軍團": ["RBT"],
                    "歡樂島": ["FMS"],
                    "特殊旅人": ["SPT"],
                    "甜點王國": ["CND"],
                    "發電獸": ["ELE"],
                    "碳碳族": ["CRB"],
                    "蒸汽世界": ["STP"],
                    "進化野人": ["EWD"],
                    "馬戲團": ["CCS"],
                    "骷髏人": ["SKT"]
                }
                deck_faction = None
                for fac in faction_prefixes.keys():
                    if fac in deck_name:
                        deck_faction = fac
                        break
                if deck_faction:
                    belongs_to_other = False
                    for fac, prefixes in faction_prefixes.items():
                        if fac != deck_faction:
                            if any(p in id_upper for p in prefixes) or card_obj.get("faction") == fac or card_obj.get("race") == fac:
                                belongs_to_other = True
                                break
                    if belongs_to_other:
                        is_valid = False
                    else:
                        prefixes = faction_prefixes[deck_faction]
                        card_faction = card_obj.get("faction") or card_obj.get("deck") or ""
                        matches_faction = (card_faction == deck_faction) or any(id_upper.startswith(p) for p in prefixes)
                        if not matches_faction:
                            is_valid = False
                    
            if is_valid:
                cleaned_extra_ids.append(cid)
        decks_data[data.deck_name + "_extra"] = cleaned_extra_ids

    try:
        decks_file.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # 同步複製一份 decks.json 到 static/ 目錄，讓前端讀取
        static_decks = BASE / "static" / "decks.json"
        static_decks.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"儲存牌組失敗: {str(e)}")

    return {"status": "success", "message": f"成功儲存 {data.deck_name} 牌組！"}


class DeckDeleteSchema(BaseModel):
    deck_name: str


@app.post("/api/decks/delete")
def delete_deck(data: DeckDeleteSchema):
    decks_file = BASE / "data" / "decks.json"
    if not decks_file.exists():
        raise HTTPException(status_code=404, detail="decks.json not found")
    
    decks_data = json.loads(decks_file.read_text(encoding="utf-8"))
    
    base_factions = [
        "藝術品", "喵喵賊", "妖怪村莊", "獸人", "虛擬世界",
        "勇者公會", "妖精", "山羊族", "機械軍團", "歡樂島", "特殊旅人",
        "甜點王國", "發電獸", "碳碳族", "蒸汽世界", "進化野人", "馬戲團", "骷髏人"
    ]
    if data.deck_name in base_factions:
        raise HTTPException(status_code=400, detail="不可刪除基礎種族牌組！")
        
    if data.deck_name in decks_data:
        del decks_data[data.deck_name]
    extra_key = data.deck_name + "_extra"
    if extra_key in decks_data:
        del decks_data[extra_key]
        
    try:
        decks_file.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # Sync to static/decks.json
        static_decks = BASE / "static" / "decks.json"
        static_decks.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刪除牌組失敗: {str(e)}")
        
    return {"status": "success", "message": f"成功刪除預設牌組 {data.deck_name}。"}


class DeckRenameSchema(BaseModel):
    old_name: str
    new_name: str


@app.post("/api/decks/rename")
def rename_deck(data: DeckRenameSchema):
    decks_file = BASE / "data" / "decks.json"
    if not decks_file.exists():
        raise HTTPException(status_code=404, detail="decks.json not found")
        
    decks_data = json.loads(decks_file.read_text(encoding="utf-8"))
    
    base_factions = [
        "藝術品", "喵喵賊", "妖怪村莊", "獸人", "虛擬世界",
        "勇者公會", "妖精", "山羊族", "機械軍團", "歡樂島", "特殊旅人",
        "甜點王國", "發電獸", "碳碳族", "蒸汽世界", "進化野人", "馬戲團", "骷髏人"
    ]
    if data.old_name in base_factions:
        raise HTTPException(status_code=400, detail="不可修改基礎種族牌組名稱！")
        
    if data.old_name not in decks_data:
        raise HTTPException(status_code=404, detail="找不到指定的舊牌組！")
        
    # Validation check for new_name
    has_faction = any(fac in data.new_name for fac in base_factions)
    if not has_faction:
        raise HTTPException(status_code=400, detail="新牌組名稱必須包含所屬種族名稱（例如：喵喵賊、妖怪村莊、藝術品、獸人、虛擬世界、山羊族、妖精等）！")
        
    # Rename main and extra
    decks_data[data.new_name] = decks_data[data.old_name]
    del decks_data[data.old_name]
    
    old_extra = data.old_name + "_extra"
    new_extra = data.new_name + "_extra"
    if old_extra in decks_data:
        decks_data[new_extra] = decks_data[old_extra]
        del decks_data[old_extra]
        
    try:
        decks_file.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # Sync to static/decks.json
        static_decks = BASE / "static" / "decks.json"
        static_decks.write_text(json.dumps(decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新命名牌組失敗: {str(e)}")
        
    return {"status": "success", "message": f"成功將牌組名稱修改為 {data.new_name}。"}


class DeckReorderSchema(BaseModel):
    ordered_decks: list[str]


@app.post("/api/decks/reorder")
def reorder_decks(data: DeckReorderSchema):
    decks_file = BASE / "data" / "decks.json"
    if not decks_file.exists():
        raise HTTPException(status_code=404, detail="decks.json not found")
        
    decks_data = json.loads(decks_file.read_text(encoding="utf-8"))
    
    new_decks_data = {}
    
    # 保持中立單位在最前
    if "中立單位" in decks_data:
        new_decks_data["中立單位"] = decks_data["中立單位"]
        
    # 依 ordered_decks 的順序放入，並將其 _extra 伴隨其後
    for deck_name in data.ordered_decks:
        if deck_name in decks_data:
            new_decks_data[deck_name] = decks_data[deck_name]
            extra_key = deck_name + "_extra"
            if extra_key in decks_data:
                new_decks_data[extra_key] = decks_data[extra_key]
                
    # 將任何未包含在 ordered_decks 中的牌組按原順序補在最後
    for k, v in decks_data.items():
        if k == "中立單位" or k.endswith("_extra"):
            continue
        if k not in new_decks_data:
            new_decks_data[k] = v
            extra_k = k + "_extra"
            if extra_k in decks_data:
                new_decks_data[extra_k] = decks_data[extra_k]
                
    try:
        decks_file.write_text(json.dumps(new_decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
        static_decks = BASE / "static" / "decks.json"
        static_decks.write_text(json.dumps(new_decks_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"儲存牌組順序失敗: {str(e)}")
        
    return {"status": "success", "message": "牌組順序已成功更新！"}


DEFAULT_FACTIONS = [
    "藝術品", "喵喵賊", "妖怪村莊", "獸人", "虛擬世界",
    "勇者公會", "妖精", "山羊族", "機械軍團", "歡樂島", "特殊旅人",
    "甜點王國", "發電獸", "碳碳族", "蒸汽世界", "進化野人", "馬戲團", "骷髏人"
]


@app.get("/api/factions")
def get_factions():
    factions_file = BASE / "data" / "factions.json"
    if factions_file.exists():
        try:
            return json.loads(factions_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_FACTIONS


class FactionReorderSchema(BaseModel):
    ordered_factions: list[str]


@app.post("/api/factions/reorder")
def reorder_factions(data: FactionReorderSchema):
    factions_file = BASE / "data" / "factions.json"
    static_file = BASE / "static" / "factions.json"
    
    cleaned = []
    seen = set()
    for fac in data.ordered_factions:
        if fac in DEFAULT_FACTIONS and fac not in seen:
            cleaned.append(fac)
            seen.add(fac)
    for fac in DEFAULT_FACTIONS:
        if fac not in seen:
            cleaned.append(fac)
            seen.add(fac)
            
    try:
        factions_file.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
        static_file.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"儲存種族順序失敗: {str(e)}")
        
    return {"status": "success", "message": "種族順序已成功更新！", "factions": cleaned}




