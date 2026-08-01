# -*- coding: utf-8 -*-
import os, sys, re

def apply_mobile_zoom():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    html_path = os.path.join(base_dir, 'static', 'deck_builder.html')

    content = open(html_path, encoding='utf-8').read()

    # 1. Inject CSS for Mobile responsive layout & Zoom Modal
    mobile_css = """
    /* ===== 📱 手機版 RWD 微縮卡牌與佈局優化 ===== */
    @media (max-width: 900px) {
      header {
        padding: 8px 12px !important;
      }
      header h1 {
        font-size: 15px !important;
      }
      .header-actions {
        gap: 8px !important;
      }
      .top-nav-btn {
        padding: 4px 8px !important;
        font-size: 11px !important;
      }
      
      .deck-controls-bar {
        padding: 8px 12px !important;
        gap: 8px !important;
        flex-wrap: wrap !important;
      }
      .deck-select-wrap, .preset-select-wrap {
        margin-left: 0 !important;
        padding-left: 0 !important;
        border-left: none !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
      }
      .deck-select {
        padding: 4px 8px !important;
        font-size: 12px !important;
      }
      .counter-badge {
        padding: 4px 10px !important;
        font-size: 11px !important;
      }
      .action-btn {
        padding: 5px 10px !important;
        font-size: 11px !important;
      }

      /* 雙面板佈局 */
      .main-layout {
        height: calc(100vh - 110px) !important;
        max-height: calc(100vh - 110px) !important;
      }
      .panels-container {
        flex-direction: row !important;
      }
      .library-panel {
        flex: 1.1 !important;
      }
      .deck-panel {
        flex: 0.9 !important;
      }

      .panel-header {
        padding: 8px 12px !important;
      }
      .panel-header h2 {
        font-size: 13px !important;
      }
      .search-input {
        width: 110px !important;
        font-size: 11px !important;
        padding: 3px 6px !important;
      }

      /* 網格與微縮卡片 (一頁可檢視多張卡牌) */
      .card-grid, .deck-list {
        padding: 8px !important;
        gap: 8px !important;
        grid-template-columns: repeat(auto-fill, minmax(76px, 1fr)) !important;
      }

      .card-tile {
        padding: 4px !important;
        gap: 4px !important;
        border-radius: 6px !important;
        position: relative !important;
      }

      /* 卡牌圖片縮小 (從 150px 縮小至 70px) */
      .card-tile-img {
        height: 70px !important;
      }

      .card-tile-name {
        font-size: 10px !important;
      }

      .card-tile-stats {
        font-size: 8.5px !important;
      }
      
      .extra-tag {
        font-size: 7px !important;
        padding: 1px 3px !important;
      }
    }

    /* 手機版卡牌右上角放大鏡按鈕 🔍 */
    .card-zoom-btn {
      position: absolute;
      bottom: 22px;
      right: 3px;
      background: rgba(10, 8, 20, 0.85);
      border: 1px solid var(--gold-accent);
      color: var(--gold-accent);
      border-radius: 50%;
      width: 20px;
      height: 20px;
      font-size: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 8;
      box-shadow: 0 2px 6px rgba(0,0,0,0.6);
      transition: all 0.2s ease;
    }
    .card-zoom-btn:hover {
      background: var(--gold-accent);
      color: #000;
      transform: scale(1.15);
    }

    /* ===== 手機版大圖卡牌放大 Modal ===== */
    .mobile-card-zoom-modal {
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: 100vw !important;
      height: 100vh !important;
      background: rgba(6, 4, 12, 0.95) !important;
      backdrop-filter: blur(10px) !important;
      z-index: 999999 !important;
      display: flex !important;
      justify-content: center !important;
      align-items: center !important;
      padding: 15px !important;
    }

    .mobile-zoom-content {
      background: linear-gradient(145deg, rgba(25, 18, 38, 0.98) 0%, rgba(12, 8, 20, 0.99) 100%) !important;
      border: 1.5px solid var(--gold-accent) !important;
      border-radius: 16px !important;
      width: 360px !important;
      max-width: 92vw !important;
      max-height: 90vh !important;
      box-shadow: 0 15px 50px rgba(0, 0, 0, 0.9), 0 0 25px rgba(255, 215, 106, 0.2) !important;
      display: flex !important;
      flex-direction: column !important;
      overflow-y: auto !important;
      position: relative !important;
      padding: 16px !important;
      gap: 10px !important;
    }

    .mobile-zoom-close {
      position: absolute !important;
      top: 10px !important;
      right: 12px !important;
      background: rgba(255, 92, 92, 0.2) !important;
      border: 1px solid var(--red-accent) !important;
      color: #ff7875 !important;
      font-size: 20px !important;
      width: 30px !important;
      height: 30px !important;
      border-radius: 50% !important;
      cursor: pointer !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
    }

    .mobile-zoom-img-wrap {
      width: 100% !important;
      height: 250px !important;
      display: flex !important;
      justify-content: center !important;
      align-items: center !important;
      background: #000000 !important;
      border-radius: 10px !important;
      border: 1px solid var(--border-color) !important;
      overflow: hidden !important;
    }

    .mobile-zoom-img-wrap img {
      max-width: 100% !important;
      max-height: 100% !important;
      object-fit: contain !important;
    }

    .mobile-zoom-header {
      display: flex !important;
      justify-content: space-between !important;
      align-items: center !important;
    }

    .mobile-zoom-header h3 {
      font-family: 'Cinzel', serif !important;
      font-size: 17px !important;
      color: var(--gold-accent) !important;
    }

    .mobile-zoom-type {
      font-size: 11px !important;
      background: rgba(255, 215, 106, 0.15) !important;
      border: 1px solid var(--gold-accent) !important;
      color: #ffe6a0 !important;
      padding: 2px 8px !important;
      border-radius: 4px !important;
    }

    .mobile-zoom-stats-row {
      display: flex !important;
      justify-content: space-between !important;
      font-size: 12px !important;
      font-weight: bold !important;
      color: var(--text-main) !important;
      background: rgba(255, 255, 255, 0.04) !important;
      padding: 6px 12px !important;
      border-radius: 6px !important;
    }

    .mobile-zoom-effect {
      font-size: 11.5px !important;
      color: #dddddd !important;
      line-height: 1.5 !important;
      background: rgba(0, 0, 0, 0.3) !important;
      padding: 8px 10px !important;
      border-radius: 6px !important;
      border: 1px solid rgba(255, 255, 255, 0.05) !important;
      max-height: 110px !important;
      overflow-y: auto !important;
    }

    .mobile-zoom-actions {
      display: flex !important;
      justify-content: center !important;
      margin-top: 4px !important;
    }
"""

    content = content.replace('</style>', mobile_css + '\n  </style>')

    # 2. Inject Mobile Zoom Modal HTML before </body>
    modal_html = """
  <!-- 手機版大圖卡牌放大預覽 Modal -->
  <div id="mobileCardZoomModal" class="mobile-card-zoom-modal" style="display: none !important;" onclick="closeMobileCardZoom(event)">
    <div class="mobile-zoom-content" onclick="event.stopPropagation()">
      <button class="mobile-zoom-close" onclick="closeMobileCardZoom()">&times;</button>
      <div class="mobile-zoom-img-wrap">
        <img id="mobileZoomImg" src="" alt="Card Enlarged View">
      </div>
      <div class="mobile-zoom-header">
        <h3 id="mobileZoomName">卡牌名稱</h3>
        <span id="mobileZoomType" class="mobile-zoom-type">單位卡</span>
      </div>
      <div id="mobileZoomStats" class="mobile-zoom-stats-row">
        <span id="mobileZoomAtk" style="color:#ffd76a;">⚔ 攻擊: 0</span>
        <span id="mobileZoomTribute" style="color:#ff7875;">祭品: 0</span>
        <span id="mobileZoomStars" style="color:#2de370;">★ 點數: 0</span>
      </div>
      <div id="mobileZoomEffect" class="mobile-zoom-effect">
        卡牌效果說明...
      </div>
      <div id="mobileZoomActions" class="mobile-zoom-actions">
        <button id="mobileZoomToggleBtn" class="action-btn save-btn" onclick="toggleCardFromModal()" style="width:100%; text-align:center;">加入 / 移出牌組</button>
      </div>
    </div>
  </div>
"""

    content = content.replace('</body>', modal_html + '\n</body>')

    # 3. Update renderLibrary tile innerHTML to include card-zoom-btn and mobile touch click
    old_lib_tile = """        div.innerHTML = `
          ${extraLabel}
          <img class="card-tile-img" src="${c.image || '/static/card_back.jpeg'}" alt="${c.name}">
          <div class="card-tile-name">${c.name}</div>
          <div class="card-tile-stats">
            <span class="stat-atk">${atkDisplay}</span>
            <span class="stat-tribute">祭 ${c.tribute || 0}</span>
            <span class="stat-stars">★ ${c.score || 0}</span>
          </div>
        `;"""

    new_lib_tile = """        div.innerHTML = `
          ${extraLabel}
          <div class="card-zoom-btn" onclick="openMobileCardZoom(event, '${c.id}')" title="點擊大圖預覽">🔍</div>
          <img class="card-tile-img" src="${c.image || '/static/card_back.jpeg'}" alt="${c.name}">
          <div class="card-tile-name">${c.name}</div>
          <div class="card-tile-stats">
            <span class="stat-atk">${atkDisplay}</span>
            <span class="stat-tribute">祭 ${c.tribute || 0}</span>
            <span class="stat-stars">★ ${c.score || 0}</span>
          </div>
        `;"""

    content = content.replace(old_lib_tile, new_lib_tile)

    # 4. Update createDeckTile innerHTML to include card-zoom-btn
    old_deck_tile = """      div.innerHTML = `
        ${extraLabel}
        <img class="card-tile-img" src="${c.image || '/static/card_back.jpeg'}" alt="${c.name}">
        <div class="card-tile-name">${c.name}</div>
        <div class="card-tile-stats">
          <span class="stat-atk">${atkDisplay}</span>
          <span class="stat-tribute">祭 ${c.tribute || 0}</span>
          <span class="stat-stars">★ ${c.score || 0}</span>
        </div>
      `;"""

    new_deck_tile = """      div.innerHTML = `
        ${extraLabel}
        <div class="card-zoom-btn" onclick="openMobileCardZoom(event, '${c.id}')" title="點擊大圖預覽">🔍</div>
        <img class="card-tile-img" src="${c.image || '/static/card_back.jpeg'}" alt="${c.name}">
        <div class="card-tile-name">${c.name}</div>
        <div class="card-tile-stats">
          <span class="stat-atk">${atkDisplay}</span>
          <span class="stat-tribute">祭 ${c.tribute || 0}</span>
          <span class="stat-stars">★ ${c.score || 0}</span>
        </div>
      `;"""

    content = content.replace(old_deck_tile, new_deck_tile)

    # 5. Add JS functions for Mobile Zoom Modal
    js_zoom_functions = """
    let currentModalCardId = null;

    function openMobileCardZoom(event, cardId) {
      if (event) event.stopPropagation();
      const card = allCards.find(c => c.id === cardId);
      if (!card) return;

      currentModalCardId = cardId;
      const modal = document.getElementById("mobileCardZoomModal");
      const img = document.getElementById("mobileZoomImg");
      const name = document.getElementById("mobileZoomName");
      const type = document.getElementById("mobileZoomType");
      const atk = document.getElementById("mobileZoomAtk");
      const tribute = document.getElementById("mobileZoomTribute");
      const stars = document.getElementById("mobileZoomStars");
      const effect = document.getElementById("mobileZoomEffect");
      const toggleBtn = document.getElementById("mobileZoomToggleBtn");

      img.src = card.image || '/static/card_back.jpeg';
      name.textContent = card.name || '未知卡牌';
      type.textContent = card.deck_eligible === false ? '★ 額外戰術卡' : (card.type || '單位卡');

      let atkText = card.attack;
      if (atkText === "盾" || String(atkText).includes("盾")) {
        atkText = "🛡 盾";
      } else {
        atkText = `⚔ 攻擊: ${atkText || 0}`;
      }
      atk.textContent = atkText;
      tribute.textContent = `祭品: ${card.tribute || 0}`;
      stars.textContent = `★ 點數: ${card.score || 0}`;

      effect.textContent = card.effect_text || card.description || '無特殊卡牌效果。';

      const isMain = card.deck_eligible !== false;
      const isSelected = isMain ? selectedMainIds.includes(cardId) : selectedExtraIds.includes(cardId);
      if (toggleBtn) {
        toggleBtn.textContent = isSelected ? '➖ 從牌組中移出' : '➕ 加入至牌組';
        toggleBtn.style.background = isSelected ? 'linear-gradient(135deg, #ad2102, #cf1322)' : 'linear-gradient(135deg, #23780a, #389e0d)';
      }

      if (modal) modal.style.setProperty("display", "flex", "important");
    }

    function closeMobileCardZoom(event) {
      if (event) event.stopPropagation();
      const modal = document.getElementById("mobileCardZoomModal");
      if (modal) modal.style.setProperty("display", "none", "important");
    }

    function toggleCardFromModal() {
      if (!currentModalCardId) return;
      const card = allCards.find(c => c.id === currentModalCardId);
      if (!card) return;

      const isMain = card.deck_eligible !== false;
      const isRemoving = isMain ? selectedMainIds.includes(currentModalCardId) : selectedExtraIds.includes(currentModalCardId);
      
      toggleSelectCard(currentModalCardId, isMain, isRemoving);
      
      // Update modal button state
      const isSelectedNow = isMain ? selectedMainIds.includes(currentModalCardId) : selectedExtraIds.includes(currentModalCardId);
      const toggleBtn = document.getElementById("mobileZoomToggleBtn");
      if (toggleBtn) {
        toggleBtn.textContent = isSelectedNow ? '➖ 從牌組中移出' : '➕ 加入至牌組';
        toggleBtn.style.background = isSelectedNow ? 'linear-gradient(135deg, #ad2102, #cf1322)' : 'linear-gradient(135deg, #23780a, #389e0d)';
      }
    }
"""

    content = content.replace('</script>', js_zoom_functions + '\n</script>')

    open(html_path, 'w', encoding='utf-8').write(content)
    print("SUCCESS: Injected mobile responsive styles, card-zoom-btn, and mobileCardZoomModal into deck_builder.html!")

if __name__ == '__main__':
    apply_mobile_zoom()
