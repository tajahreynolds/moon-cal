// Onboarding city autocomplete + manual coordinate fallback.
(function () {
  const form = document.getElementById("onboarding-form");
  if (!form) return;
  const url = form.dataset.citiesUrl;
  const cityInput = form.querySelector("#id_city");
  const results = document.getElementById("city-results");
  const latField = form.querySelector("#id_latitude");
  const lonField = form.querySelector("#id_longitude");
  const tzField = form.querySelector("#id_timezone");
  let timer = null;

  function setLocation(lat, lon, tz, label) {
    latField.value = lat;
    lonField.value = lon;
    tzField.value = tz;
    if (label) cityInput.value = label;
  }

  function clearResolved() {
    latField.value = "";
    lonField.value = "";
    tzField.value = "";
  }

  async function query(q) {
    if (!q || q.length < 2) { results.hidden = true; return; }
    try {
      const res = await fetch(url + "?q=" + encodeURIComponent(q));
      const data = await res.json();
      results.innerHTML = "";
      if (!data.results.length) { results.hidden = true; return; }
      data.results.forEach((c) => {
        const li = document.createElement("li");
        li.textContent = c.label + "  ·  " + c.tz;
        li.addEventListener("click", () => {
          setLocation(c.lat, c.lon, c.tz, c.label);
          results.hidden = true;
        });
        results.appendChild(li);
      });
      results.hidden = false;
    } catch (e) { results.hidden = true; }
  }

  cityInput.addEventListener("input", () => {
    clearResolved();
    clearTimeout(timer);
    timer = setTimeout(() => query(cityInput.value.trim()), 200);
  });

  // Manual fallback.
  const applyBtn = document.getElementById("apply-manual");
  if (applyBtn) {
    applyBtn.addEventListener("click", () => {
      const lat = document.getElementById("manual-lat").value;
      const lon = document.getElementById("manual-lon").value;
      const tz = document.getElementById("manual-tz").value.trim();
      if (lat && lon && tz) {
        setLocation(lat, lon, tz);
        if (!cityInput.value) cityInput.value = `${lat}, ${lon}`;
        results.hidden = true;
        applyBtn.textContent = "✓ Set";
      }
    });
  }
})();
