(() => {
  const canvas = document.getElementById("xlwArenaTerrain");
  const ctx = canvas?.getContext("2d");
  if (!ctx) return;

  // Model coordinates are x, elevation, and depth. The orthographic camera
  // uses the same view and light for every surface on both islands.
  const view = [0.39, 0.75, 0.53];
  const light = [-0.58, 0.77, 0.26];
  const dot = (a, b) => a.reduce((sum, value, i) => sum + value * b[i], 0);
  const stone = [83, 101, 122];
  const rim = [160, 119, 78];
  const faces = [];
  let scene = faces;

  function frustum(x, y, z, bottom, top, height, color, sides = 8, angle = Math.PI / 8, ratio = 1) {
    const ring = (radius, level) => Array.from({length: sides}, (_, i) => {
      const t = angle + i * 2 * Math.PI / sides;
      return [x + Math.cos(t) * radius, level, z + Math.sin(t) * radius * ratio];
    });
    const base = ring(bottom, y);
    const crown = ring(top, y + height);
    for (let i = 0; i < sides; i++) {
      const j = (i + 1) % sides;
      const t = angle + (i + .5) * 2 * Math.PI / sides;
      const slope = (bottom - top) / height;
      const normal = [Math.cos(t), slope, Math.sin(t) / ratio];
      const length = Math.hypot(...normal);
      const unit = normal.map(value => value / length);
      if (dot(unit, view) > 0) scene.push({points: [base[i], base[j], crown[j], crown[i]], normal: unit, color});
    }
    scene.push({points: crown, normal: [0, 1, 0], color});
  }

  function pillar(x, y, z, height, crystal) {
    frustum(x, y, z, 23, 21, 10, rim);
    frustum(x, y + 10, z, 18, 15, height, stone);
    frustum(x, y + height + 10, z, 17, 20, 7, rim);
    if (crystal) {
      frustum(x, y + height + 17, z, 3, 14, 16, crystal, 5, .4);
      frustum(x, y + height + 33, z, 14, 0, 26, crystal, 5, .4);
    }
  }

  function island(crystal, tall) {
    scene = [];
    frustum(0, 0, 0, 56, 101, 38, [38, 48, 65], 9, .2, .85);
    frustum(0, 38, 0, 101, 96, 12, stone, 9, .2, .85);
    frustum(-15, 50, -10, 63, 60, 8, rim, 8);
    frustum(-15, 58, -10, 60, 57, 11, stone, 8);
    frustum(-15, 69, -10, 48, 45, 10, stone, 8);
    pillar(-23, 79, -18, tall ? 66 : 50, crystal);
    pillar(37, 50, -29, tall ? 30 : 48);
    pillar(-57, 50, 24, 24);
    frustum(22, 50, 53, 30, 27, 9, rim, 6);
    frustum(22, 59, 53, 27, 24, 10, stone, 6);
    frustum(58, 50, 19, 12, 8, 13, stone, 5, .6);
    return scene.map(face => ({
      ...face, depth: face.points.reduce((sum, p) => sum + dot(p, view), 0) / face.points.length
    })).sort((a, b) => a.depth - b.depth);
  }

  const west = island([81, 201, 218], true);
  const east = island([217, 135, 172], false);

  function drawIsland(mesh, x, y, scale, mirror) {
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale * mirror, scale);
    const shadow = ctx.createRadialGradient(0, 0, 10, 0, 0, 112);
    shadow.addColorStop(0, "#03060dcc");
    shadow.addColorStop(1, "#03060d00");
    ctx.save();
    ctx.scale(1, .32);
    ctx.fillStyle = shadow;
    ctx.fillRect(-112, -112, 224, 224);
    ctx.restore();

    for (const {points, normal, color} of mesh) {
      const intensity = .54 + Math.max(0, dot(normal, light)) * .57;
      const rgb = color.map(v => Math.min(255, Math.round(v * intensity)));
      ctx.beginPath();
      points.forEach(([u, height, depth], i) => {
        const px = .805 * u - .593 * depth;
        const py = .447 * u + .604 * depth - .66 * height;
        if (i) ctx.lineTo(px, py);
        else ctx.moveTo(px, py);
      });
      ctx.closePath();
      ctx.fillStyle = "rgb(" + rgb.join(",") + ")";
      ctx.fill();
      ctx.strokeStyle = "#0d182b48";
      ctx.lineWidth = .85;
      ctx.stroke();
    }
    ctx.restore();
  }

  function render() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (!width || !height) return;
    const pixelRatio = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.round(width * pixelRatio);
    canvas.height = Math.round(height * pixelRatio);
    ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    const scale = Math.min(width / 1050, height / 460);
    drawIsland(west, width * .125, height * .64, scale, 1);
    drawIsland(east, width * .875, height * .60, scale, -1);
  }

  if (window.ResizeObserver) new ResizeObserver(render).observe(canvas);
  else window.addEventListener("resize", render);
  render();
})();
