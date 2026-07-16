// Forecast data drawer: tap a day -> bottom sheet with the raw transit math.
(function () {
  const drawer = document.getElementById("drawer");
  const backdrop = document.getElementById("drawer-backdrop");
  const content = document.getElementById("drawer-content");
  if (!drawer) return;
  const base = drawer.dataset.urlBase;

  function close() {
    drawer.hidden = true;
    backdrop.hidden = true;
  }

  function open() {
    drawer.hidden = false;
    backdrop.hidden = false;
  }

  function bandClass(band) {
    return "c-" + band;
  }

  function render(data) {
    const s = data.scores;
    const aspects = data.aspects.map((a) => `
      <div class="aspect-row">
        <div>${a.text}</div>
        <div class="aspect-motion">${a.type} · orb ${a.orb}°${a.days_to_exact ? " · exact ~" + a.days_to_exact + "d" : ""}</div>
      </div>`).join("") || '<div class="subtle">No close aspects this day.</div>';

    content.innerHTML = `
      <h3>${data.date}</h3>
      <p><span class="flow-pill ${bandClass(flowBand(data.flow))}">Flow ${data.flow}</span></p>
      <p class="fact-tag">RAW MATH — transiting aspects to your natal chart</p>
      ${aspects}
      <p class="fact-tag" style="margin-top:14px">OUR READ</p>
      <div class="subtle">Energy ${s.energy.level} · Focus ${s.focus.level} · Friction ${s.friction.level}</div>`;
  }

  function flowBand(v) {
    if (v >= 60) return "flow";
    if (v >= 40) return "standard";
    return "rest";
  }

  async function load(date) {
    content.innerHTML = '<div class="drawer-loading">Loading…</div>';
    open();
    try {
      const res = await fetch(base + date + "/");
      if (!res.ok) throw new Error("bad response");
      render(await res.json());
    } catch (e) {
      content.innerHTML = '<div class="subtle">Could not load this day (offline?).</div>';
    }
  }

  document.querySelectorAll(".trend-dot").forEach((dot) => {
    const go = () => load(dot.dataset.date);
    dot.addEventListener("click", go);
    dot.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); }
    });
  });
  backdrop.addEventListener("click", close);
})();
