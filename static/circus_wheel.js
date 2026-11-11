/* Presentation only. The game passes the exact card index chosen by its rules. */
(() => {
  const panel = document.getElementById("xlwCircusWheel");
  const face = panel.querySelector("canvas");
  const count = panel.querySelector(".circus-wheel-count");
  const result = panel.querySelector(".circus-wheel-result");
  const ctx = face.getContext("2d");
  const images = new Map();
  const center = face.width / 2;
  const radius = center - 2;
  const fullCircle = 2 * Math.PI;
  let cards = [];
  let key = "";
  let animation = null;

  function draw() {
    if (!ctx) return;
    ctx.clearRect(0, 0, face.width, face.height);
    const sectors = cards.length || 8;
    const slice = fullCircle / sectors;
    for (let i = 0; i < sectors; i++) {
      const start = -Math.PI / 2 + i * slice;
      const middle = start + slice / 2;
      ctx.beginPath();
      ctx.moveTo(center, center);
      ctx.arc(center, center, radius, start, start + slice);
      ctx.closePath();
      ctx.fillStyle = i % 2 ? "#162a44" : "#591d37";
      ctx.fill();
      const card = cards[i];
      const img = card && images.get(card.image);
      if (img?.naturalWidth) {
        ctx.save();
        ctx.clip();
        const x = center + Math.cos(middle) * radius * 0.55;
        const y = center + Math.sin(middle) * radius * 0.55;
        const scale = Math.max(radius * 1.4 / img.naturalWidth, radius * 1.4 / img.naturalHeight);
        const width = img.naturalWidth * scale;
        const height = img.naturalHeight * scale;
        ctx.drawImage(img, x - width / 2, y - height * 0.34, width, height);
        ctx.restore();
      }
      ctx.strokeStyle = "#dfb762";
      ctx.lineWidth = 3;
      ctx.stroke();
      if (card && cards.length <= 20) {
        const x = center + Math.cos(middle) * radius * 0.79;
        const y = center + Math.sin(middle) * radius * 0.79;
        ctx.font = "bold 24px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.strokeStyle = "#180e1c";
        ctx.lineWidth = 5;
        ctx.strokeText(String(i + 1), x, y);
        ctx.fillStyle = "#fff1bc";
        ctx.fillText(String(i + 1), x, y);
      }
    }
  }

  function setCards(next) {
    const signature = JSON.stringify(next.map(({ id, name, image }) => [id, name, image]));
    if (signature === key) return;
    key = signature;
    cards = next.slice();
    for (const card of cards) {
      if (!card.image || images.has(card.image)) continue;
      const img = new Image();
      images.set(card.image, img);
      img.onload = draw;
      img.src = card.image;
    }
    const names = cards.map((card, i) => `${i + 1}. ${card.name}`).join("、");
    panel.title = names || "尚未上靶";
    face.setAttribute("aria-label", names || "尚未上靶");
    count.textContent = cards.length ? `${cards.length} 張上靶` : "尚未上靶";
    draw();
  }

  window.XLWCircusWheel = {
    get spinning() { return animation !== null; },
    render(visible, next) {
      panel.hidden = !visible;
      if (visible && !animation) setCards(next);
    },
    position(forest) {
      if (panel.hidden || !forest) return;
      panel.style.left = `${forest.offsetLeft - panel.offsetWidth - 12}px`;
      panel.style.top = `${forest.offsetTop + (forest.offsetHeight - panel.offsetHeight) / 2}px`;
    },
    async reveal(snapshot, index) {
      if (panel.hidden || animation || !snapshot[index]) return;
      setCards(snapshot);
      result.textContent = "輪轉中…";
      result.removeAttribute("title");
      if (typeof face.animate !== "function") {
        result.textContent = `開盤：${snapshot[index].name}`;
        return;
      }
      const angle = 1440 - (index + 0.5) * 360 / snapshot.length;
      const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
      const spin = face.animate(
        [{ transform: "rotate(0deg)" }, { transform: `rotate(${angle}deg)` }],
        { duration: reduce ? 0 : 950, easing: "cubic-bezier(.14,.7,.16,1)", fill: "forwards" }
      );
      animation = spin;
      try {
        await spin.finished;
        result.textContent = `開盤：${snapshot[index].name}`;
        result.title = snapshot[index].name;
        await new Promise(resolve => setTimeout(resolve, reduce ? 0 : 330));
        if (animation !== spin) return false;
      } catch (_) {
        // Leaving the match cancels the visual only.
        return false;
      } finally {
        if (animation === spin) {
          spin.cancel();
          animation = null;
        }
      }
    },
    reset() {
      animation?.cancel();
      animation = null;
      panel.hidden = true;
      result.textContent = "";
      result.removeAttribute("title");
      setCards([]);
    }
  };
})();
