(function (root) {
  const BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz";

  function encodeGeohash(lat, lon, precision) {
    const latRange = [-90, 90];
    const lonRange = [-180, 180];
    let hash = "";
    let bit = 0;
    let value = 0;
    let even = true;
    while (hash.length < precision) {
      if (even) {
        const mid = (lonRange[0] + lonRange[1]) / 2;
        if (lon >= mid) {
          value = (value << 1) | 1;
          lonRange[0] = mid;
        } else {
          value <<= 1;
          lonRange[1] = mid;
        }
      } else {
        const mid = (latRange[0] + latRange[1]) / 2;
        if (lat >= mid) {
          value = (value << 1) | 1;
          latRange[0] = mid;
        } else {
          value <<= 1;
          latRange[1] = mid;
        }
      }
      even = !even;
      bit += 1;
      if (bit === 5) {
        hash += BASE32[value];
        bit = 0;
        value = 0;
      }
    }
    return hash;
  }

  function decodeGeohash(hash) {
    const latRange = [-90, 90];
    const lonRange = [-180, 180];
    let even = true;
    for (const ch of hash) {
      const idx = BASE32.indexOf(ch);
      if (idx < 0) return null;
      for (let mask = 16; mask > 0; mask >>= 1) {
        if (even) {
          const mid = (lonRange[0] + lonRange[1]) / 2;
          if (idx & mask) lonRange[0] = mid;
          else lonRange[1] = mid;
        } else {
          const mid = (latRange[0] + latRange[1]) / 2;
          if (idx & mask) latRange[0] = mid;
          else latRange[1] = mid;
        }
        even = !even;
      }
    }
    return {
      lat: (latRange[0] + latRange[1]) / 2,
      lon: (lonRange[0] + lonRange[1]) / 2,
    };
  }

  function haversineM(lat1, lon1, lat2, lon2) {
    const radius = 6371000;
    const rad = (d) => (d * Math.PI) / 180;
    const dPhi = rad(lat2 - lat1);
    const dLam = rad(lon2 - lon1);
    const phi1 = rad(lat1);
    const phi2 = rad(lat2);
    const a = Math.sin(dPhi / 2) ** 2 + Math.cos(phi1) * Math.cos(phi2) * Math.sin(dLam / 2) ** 2;
    return 2 * radius * Math.asin(Math.min(1, Math.sqrt(a)));
  }

  function pointInPolygon(x, y, polygon) {
    let inside = false;
    let j = polygon.length - 1;
    for (let i = 0; i < polygon.length; i += 1) {
      const xi = polygon[i][0];
      const yi = polygon[i][1];
      const xj = polygon[j][0];
      const yj = polygon[j][1];
      if ((yi > y) !== (yj > y)) {
        const xCross = ((xj - xi) * (y - yi)) / (yj - yi) + xi;
        if (x < xCross) inside = !inside;
      }
      j = i;
    }
    return inside;
  }

  const PLACES = [
    ["天安门", 39.9087, 116.3975],
    ["故宫", 39.9163, 116.3972],
    ["北海", 39.928, 116.389],
    ["三里屯", 39.9372, 116.4551],
    ["国贸", 39.9086, 116.4596],
    ["北京南站", 39.8652, 116.3785],
    ["颐和园", 39.9999, 116.2755],
    ["奥森", 40.009, 116.391],
    ["首都机场", 40.0799, 116.6031],
    ["香山", 39.994, 116.186],
  ];

  function render(host) {
    host.innerHTML = `
      <p class="kicker">实验室</p>
      <h2>把公式放到手上</h2>
      <p class="muted">这些小工具和题解用的是同一套定义：Geohash 先经后纬，距离是 Haversine，围栏是射线法。地图只是示意，不是导航底图。</p>
      <div class="lab-grid">
        <section class="card">
          <h3>Geohash</h3>
          <label class="field">纬度<input id="ghLat" value="39.9087" /></label>
          <label class="field">经度<input id="ghLon" value="116.3975" /></label>
          <label class="field">位数<input id="ghPrec" type="number" min="1" max="12" value="7" /></label>
          <button class="btn primary" id="ghBtn" type="button">编码</button>
          <p id="ghOut"></p>
        </section>
        <section class="card">
          <h3>附近的地标</h3>
          <p class="muted">点一下示意地图，取最近的 3 个点。坐标是公开地标的近似值，用来核对排序。</p>
          <canvas class="plot" id="mapCanvas" width="640" height="460"></canvas>
          <p id="mapOut">还没有查询点。</p>
        </section>
        <section class="card">
          <h3>点在多边形内</h3>
          <p class="muted">凹多边形。点在内部会变成松绿，外部是朱红。边界点不稳定，业务里要单独约定。</p>
          <canvas class="plot" id="pipCanvas" width="640" height="420"></canvas>
          <p id="pipOut">点击画布。</p>
        </section>
        <section class="card">
          <h3>距离衰减</h3>
          <label class="field">σ（米）<input id="sigma" type="range" min="300" max="4000" value="1200" /></label>
          <p id="sigmaLabel"></p>
          <canvas class="plot" id="decayCanvas" width="640" height="360"></canvas>
        </section>
      </div>
    `;

    const ghOut = host.querySelector("#ghOut");
    const runHash = () => {
      const lat = Number(host.querySelector("#ghLat").value);
      const lon = Number(host.querySelector("#ghLon").value);
      const precision = Number(host.querySelector("#ghPrec").value);
      if (!Number.isFinite(lat) || !Number.isFinite(lon) || precision < 1) {
        ghOut.textContent = "输入无效。";
        return;
      }
      const hash = encodeGeohash(lat, lon, precision);
      const back = decodeGeohash(hash);
      ghOut.innerHTML = `<span class="example">${hash}</span><br />格子中心约 ${back.lat.toFixed(5)}, ${back.lon.toFixed(5)}。这是格子中心，不是原始点。`;
    };
    host.querySelector("#ghBtn").addEventListener("click", runHash);
    runHash();

    const mapCanvas = host.querySelector("#mapCanvas");
    const mapOut = host.querySelector("#mapOut");
    const bounds = {
      minLat: 39.82,
      maxLat: 40.12,
      minLng: 116.14,
      maxLng: 116.66,
    };
    const project = (lat, lng) => {
      const x = ((lng - bounds.minLng) / (bounds.maxLng - bounds.minLng)) * mapCanvas.width;
      const y = ((bounds.maxLat - lat) / (bounds.maxLat - bounds.minLat)) * mapCanvas.height;
      return [x, y];
    };
    let query = null;
    const drawMap = () => {
      const ctx = mapCanvas.getContext("2d");
      ctx.clearRect(0, 0, mapCanvas.width, mapCanvas.height);
      ctx.fillStyle = "#f4efe4";
      ctx.fillRect(0, 0, mapCanvas.width, mapCanvas.height);
      ctx.strokeStyle = "rgba(20,53,46,0.15)";
      for (let i = 1; i < 6; i += 1) {
        ctx.beginPath();
        ctx.moveTo((mapCanvas.width / 6) * i, 0);
        ctx.lineTo((mapCanvas.width / 6) * i, mapCanvas.height);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, (mapCanvas.height / 6) * i);
        ctx.lineTo(mapCanvas.width, (mapCanvas.height / 6) * i);
        ctx.stroke();
      }
      ctx.fillStyle = "#14352e";
      ctx.font = "14px sans-serif";
      PLACES.forEach(([name, lat, lng]) => {
        const [x, y] = project(lat, lng);
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillText(name, x + 8, y - 6);
      });
      if (query) {
        const [x, y] = project(query.lat, query.lng);
        ctx.strokeStyle = "#c6452f";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, Math.PI * 2);
        ctx.stroke();
      }
    };
    mapCanvas.addEventListener("click", (event) => {
      const rect = mapCanvas.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * mapCanvas.width;
      const y = ((event.clientY - rect.top) / rect.height) * mapCanvas.height;
      const lng = bounds.minLng + (x / mapCanvas.width) * (bounds.maxLng - bounds.minLng);
      const lat = bounds.maxLat - (y / mapCanvas.height) * (bounds.maxLat - bounds.minLat);
      query = { lat, lng };
      const ranked = PLACES.map(([name, plat, plng]) => ({
        name,
        dist: haversineM(lat, lng, plat, plng),
      })).sort((a, b) => a.dist - b.dist);
      mapOut.innerHTML = ranked
        .slice(0, 3)
        .map((item, index) => `${index + 1}. ${item.name} · ${(item.dist / 1000).toFixed(2)} km`)
        .join("<br />");
      drawMap();
    });
    drawMap();

    const pipCanvas = host.querySelector("#pipCanvas");
    const pipOut = host.querySelector("#pipOut");
    const polygon = [
      [80, 60],
      [360, 40],
      [520, 150],
      [470, 300],
      [280, 250],
      [300, 140],
      [180, 180],
      [70, 280],
    ];
    const drawPip = (point) => {
      const ctx = pipCanvas.getContext("2d");
      ctx.clearRect(0, 0, pipCanvas.width, pipCanvas.height);
      ctx.fillStyle = "#f7f3ea";
      ctx.fillRect(0, 0, pipCanvas.width, pipCanvas.height);
      ctx.beginPath();
      polygon.forEach(([x, y], index) => (index ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.closePath();
      ctx.fillStyle = "rgba(47, 107, 69, 0.16)";
      ctx.strokeStyle = "#14352e";
      ctx.lineWidth = 2;
      ctx.fill();
      ctx.stroke();
      if (point) {
        const inside = pointInPolygon(point[0], point[1], polygon);
        ctx.fillStyle = inside ? "#2f6b45" : "#c6452f";
        ctx.beginPath();
        ctx.arc(point[0], point[1], 7, 0, Math.PI * 2);
        ctx.fill();
        pipOut.textContent = inside ? "判定为内部。" : "判定为外部。";
      }
    };
    pipCanvas.addEventListener("click", (event) => {
      const rect = pipCanvas.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * pipCanvas.width;
      const y = ((event.clientY - rect.top) / rect.height) * pipCanvas.height;
      drawPip([x, y]);
    });
    drawPip(null);

    const decayCanvas = host.querySelector("#decayCanvas");
    const sigma = host.querySelector("#sigma");
    const sigmaLabel = host.querySelector("#sigmaLabel");
    const drawDecay = () => {
      const s = Number(sigma.value);
      sigmaLabel.textContent = `σ = ${s} 米。曲线是 exp(-d² / 2σ²)，阶梯是 1 / 3 / 5 公里分段。`;
      const ctx = decayCanvas.getContext("2d");
      const w = decayCanvas.width;
      const h = decayCanvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "#f7f3ea";
      ctx.fillRect(0, 0, w, h);
      const maxD = 8000;
      const xOf = (d) => 40 + (d / maxD) * (w - 60);
      const yOf = (v) => 20 + (1 - v) * (h - 50);
      ctx.strokeStyle = "rgba(20,53,46,0.2)";
      ctx.beginPath();
      ctx.moveTo(40, 20);
      ctx.lineTo(40, h - 30);
      ctx.lineTo(w - 20, h - 30);
      ctx.stroke();
      ctx.beginPath();
      ctx.strokeStyle = "#14352e";
      ctx.lineWidth = 2;
      for (let d = 0; d <= maxD; d += 40) {
        const v = Math.exp((-d * d) / (2 * s * s));
        const x = xOf(d);
        const y = yOf(v);
        if (d === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.beginPath();
      ctx.strokeStyle = "#c6452f";
      const pieces = [
        [0, 1],
        [1000, 1],
        [1000, 0.7],
        [3000, 0.7],
        [3000, 0.4],
        [5000, 0.4],
        [5000, 0.1],
        [8000, 0.1],
      ];
      pieces.forEach(([d, v], index) => {
        const x = xOf(d);
        const y = yOf(v);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
      ctx.fillStyle = "#5e584e";
      ctx.font = "12px sans-serif";
      ctx.fillText("0", 36, h - 12);
      ctx.fillText("8 km", w - 48, h - 12);
      ctx.fillText("高斯", 50, 36);
      ctx.fillStyle = "#c6452f";
      ctx.fillText("分段", 100, 36);
    };
    sigma.addEventListener("input", drawDecay);
    drawDecay();
  }

  root.LBSLab = { encodeGeohash, decodeGeohash, haversineM, pointInPolygon, render };
})(typeof globalThis !== "undefined" ? globalThis : this);
