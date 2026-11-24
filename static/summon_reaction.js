/* Bounded decisions share one deadline for each summoned unit. */
(function (global) {
  "use strict";
  let current = null;
  let close = null;
  const duration = 8000;
  function begin(card) {
    end();
    current = {card, deadline: Date.now() + duration};
    return current;
  }
  function end() {
    close?.(null);
    current = null;
  }
  function choose(title, message, options) {
    const context = current || {deadline: Date.now() + duration};
    if (Date.now() >= context.deadline) return Promise.resolve(null);
    return new Promise(resolve => {
      const overlay = document.createElement("div");
      overlay.className = "xlw-reaction-overlay";
      const panel = document.createElement("section");
      panel.className = "xlw-reaction-panel";
      panel.setAttribute("role", "dialog");
      panel.setAttribute("aria-modal", "true");
      panel.setAttribute("aria-label", title);
      const heading = document.createElement("h2");
      heading.textContent = title;
      const timer = document.createElement("p");
      timer.setAttribute("role", "timer");
      const description = document.createElement("p");
      description.textContent = message;
      const details = document.createElement("div");
      details.className = "xlw-reaction-cards";
      const cards = [...new Set([context.card, ...options.map(option => option.card)].filter(Boolean))];
      for (const card of cards) {
        const article = document.createElement("article");
        if (card.image) {
          const image = document.createElement("img");
          image.src = card.image;
          image.alt = card.name || card.id;
          article.append(image);
        }
        const text = document.createElement("div");
        const name = document.createElement("h3");
        name.textContent = card.name || card.id;
        const stats = document.createElement("p");
        stats.textContent = `攻擊力 ${card.attack ?? "—"}　星數 ${card.score ?? "—"}　祭品 ${card.tribute ?? 0}`;
        const effect = document.createElement("p");
        effect.textContent = card.effect_text || "";
        const condition = document.createElement("p");
        condition.textContent = card.extra_summon_condition || card.trigger_condition || "";
        const identity = document.createElement("p");
        identity.textContent = [card.faction || card.deck, card.art_subtype,
          ...(Array.isArray(card.keywords) ? card.keywords : [])].filter(Boolean).join(" · ");
        text.append(name, stats, identity, effect, condition);
        article.append(text);
        details.append(article);
      }
      const actions = document.createElement("div");
      actions.className = "xlw-reaction-actions";
      let finished = false;
      let interval;
      let timeout;
      const finish = value => {
        if (finished) return;
        finished = true;
        clearInterval(interval);
        clearTimeout(timeout);
        document.removeEventListener("visibilitychange", tick);
        document.removeEventListener("keydown", keyboard);
        overlay.remove();
        if (close === finish) close = null;
        resolve(value);
      };
      const tick = () => {
        const remaining = context.deadline - Date.now();
        timer.textContent = `剩餘 ${Math.max(0, Math.ceil(remaining / 1000))} 秒，逾時視為不發動`;
        if (remaining <= 0) finish(null);
      };
      const keyboard = event => {
        if (event.key === "Escape") finish(null);
        if (event.key === "Tab") {
          const buttons = [...actions.querySelectorAll("button")];
          const first = buttons[0], last = buttons.at(-1);
          if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
          if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
        }
      };
      for (const option of options) {
        const button = document.createElement("button");
        button.textContent = option.text;
        button.onclick = () => finish(Date.now() < context.deadline ? option.value : null);
        actions.append(button);
      }
      const decline = document.createElement("button");
      decline.textContent = "不發動，繼續";
      decline.onclick = () => finish(null);
      actions.append(decline);
      panel.append(heading, timer, description, details, actions);
      overlay.append(panel);
      document.body.append(overlay);
      close = finish;
      interval = setInterval(tick, 200);
      timeout = setTimeout(() => finish(null), Math.max(0, context.deadline - Date.now()));
      document.addEventListener("visibilitychange", tick);
      document.addEventListener("keydown", keyboard);
      tick();
      decline.focus();
    });
  }
  async function flash(card, side) {
    if (!card) return;
    const overlay = document.createElement("div");
    overlay.className = "xlw-immediate-flash";
    const label = document.createElement("strong");
    label.textContent = (side === "player" ? "我方" : "對手") + "・立即效果";
    const image = document.createElement("img");
    image.src = card.image || "";
    image.alt = card.name || card.id;
    const name = document.createElement("span");
    name.textContent = card.name || card.id;
    overlay.append(label, image, name);
    document.body.append(overlay);
    try { await new Promise(resolve => setTimeout(resolve, 700)); }
    finally { overlay.remove(); }
  }
  const sameCard=(a,b)=>a&&b&&(a._xlwInstanceId||b._xlwInstanceId?a._xlwInstanceId&&a._xlwInstanceId===b._xlwInstanceId:a.id===b.id&&a.name===b.name);
  global.XLWSummonReaction = {begin, end, flash, ensure: card => { if (!sameCard(current?.card,card)) begin(card); }, choose, confirm: async (title, message) =>
    (await choose(title, message, [{text: "發動", value: true}])) === true};
})(window);
