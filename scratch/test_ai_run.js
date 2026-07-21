const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;

const html = fs.readFileSync('static/index.html', 'utf8');
const dom = new JSDOM(html, {
  url: 'http://localhost/',
  runScripts: 'dangerously',
  resources: 'usable'
});

const { window } = dom;
const { document } = window;

// Mock window functions needed by game_v8.js
window.matchMedia = window.matchMedia || function() {
  return {
    matches: false,
    addListener: function() {},
    removeListener: function() {}
  };
};

window.scrollTo = window.scrollTo || function() {};
window.requestAnimationFrame = window.requestAnimationFrame || function(cb) { return setTimeout(cb, 0); };
window.cancelAnimationFrame = window.cancelAnimationFrame || function(id) { clearTimeout(id); };

// Load cards and decks JSON into memory
const cardsJson = JSON.parse(fs.readFileSync('data/cards.json', 'utf8'));
const decksJson = JSON.parse(fs.readFileSync('data/decks.json', 'utf8'));

// Fetch replacement mock
window.fetch = async function(url) {
  if (url.includes('cards.json')) {
    return { ok: true, json: async () => cardsJson };
  }
  if (url.includes('decks.json')) {
    return { ok: true, json: async () => decksJson };
  }
  return { ok: false };
};

// Load game_v8.js code into dom context
const gameJsCode = fs.readFileSync('static/game_v8.js', 'utf8');
const scriptEl = document.createElement('script');
scriptEl.textContent = gameJsCode;
document.body.appendChild(scriptEl);

// Run tests after DOM load
setTimeout(async () => {
  try {
    console.log("=== Testing Single Player Game & AI Turn ===");
    
    // Simulate init
    window.allCards = cardsJson;
    window.decks = decksJson;
    
    // Start game
    console.log("1. Executing newGame()...");
    window.newGame();
    
    // Check initial state
    console.log("Player hand count:", window.hand ? window.hand.length : 0);
    console.log("Enemy hand count:", window.XLW_ENEMY.hand ? window.XLW_ENEMY.hand.length : 0);
    console.log("Enemy deck count:", window.XLW_ENEMY.deck ? window.XLW_ENEMY.deck.length : 0);
    
    // Confirm mulligan
    console.log("2. Executing confirmMulligan()...");
    await window.confirmMulligan();
    
    console.log("3. Executing endPlayerTurnAndRunEnemy()...");
    await window.endPlayerTurnAndRunEnemy();
    
    console.log("=== AI Turn Finished Successfully! ===");
    console.log("Enemy field front:", window.field.enemy_front.map(u => u ? u.card.name : "null"));
    console.log("Enemy field back:", window.field.enemy_back.map(u => u ? u.card.name : "null"));
    console.log("Battle log length:", window.battleLog.length);
    console.log("Recent log lines:\n" + window.battleLog.slice(-10).join("\n"));
  } catch (err) {
    console.error("CRITICAL ERROR during simulation:", err);
  }
}, 500);
