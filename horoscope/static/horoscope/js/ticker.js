// Live countdown to the next major transit shift.
(function () {
  const el = document.getElementById("ticker");
  if (!el) return;
  const countEl = document.getElementById("ticker-count");
  let target = new Date(el.dataset.atUtc).getTime();

  function fmt(ms) {
    if (ms <= 0) return "now";
    const s = Math.floor(ms / 1000);
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    if (h > 0) return `in ${h}h ${m}m`;
    const sec = s % 60;
    return `in ${m}m ${sec}s`;
  }

  async function refresh() {
    // After the shift passes, fetch the next one from the server.
    try {
      const res = await fetch(el.dataset.url, { headers: { "X-Requested-With": "fetch" } });
      if (!res.ok) return;
      const data = await res.json();
      if (data.label) {
        el.querySelector(".ticker-label").textContent = data.label;
        target = new Date(data.at_utc).getTime();
      }
    } catch (e) { /* offline: keep showing last value */ }
  }

  function tick() {
    const remaining = target - Date.now();
    countEl.textContent = fmt(remaining);
    if (remaining <= 0) refresh();
  }

  tick();
  setInterval(tick, 1000);
})();
