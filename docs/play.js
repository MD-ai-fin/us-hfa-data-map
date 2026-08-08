/**
 * Play modes: My State, Contrasts.
 * window.initHfaPlay(api) → { renderPlayLabels, onMapClick, onEscape }
 */
(function () {
  window.initHfaPlay = function initHfaPlay(api) {
    const {
      t, tMetric, getLang, getFocusedState, setFocusedState,
      getStateData, stateDisplayName, fmt,
      rankedStates, setPrimaryMetricOnly,
      flyToState, clearHighlights, highlightAbbrs, refreshMap,
      applyHighlightClasses, buildShareUrl, syncUrlFromState,
      getDataset,
      closeMetricsDrawer,
      isDrawerOpen, closeReport, isReportOpen,
      clearExclusiveTools,
    } = api;

    let anomalyType = null;
    let myStateMode = false;
    const ANOMALY_ORDER = ["growth_small", "assets_low_capita"];
    let dragBound = false;

    function $(id) { return document.getElementById(id); }

    function resetPanelPosition() {
      const panel = $("play-panel") || document.querySelector("#play-modal .play-panel");
      if (!panel) return;
      panel.style.left = "";
      panel.style.top = "";
      panel.style.transform = "";
      panel.style.right = "";
      panel.style.bottom = "";
    }

    function bindPanelDrag() {
      if (dragBound) return;
      const modal = $("play-modal");
      const panel = modal?.querySelector(".play-panel");
      const handle = panel?.querySelector(".compare-header");
      if (!modal || !panel || !handle) return;
      dragBound = true;

      handle.addEventListener("pointerdown", e => {
        if (!modal.classList.contains("map-clear")) return;
        if (e.target.closest("button, a, input, select, textarea, label")) return;
        e.preventDefault();
        const rect = panel.getBoundingClientRect();
        panel.style.left = `${rect.left}px`;
        panel.style.top = `${rect.top}px`;
        panel.style.transform = "none";
        const startX = e.clientX;
        const startY = e.clientY;
        const origLeft = rect.left;
        const origTop = rect.top;
        handle.setPointerCapture(e.pointerId);

        const onMove = ev => {
          const w = panel.offsetWidth;
          const h = panel.offsetHeight;
          let nx = origLeft + (ev.clientX - startX);
          let ny = origTop + (ev.clientY - startY);
          nx = Math.max(8, Math.min(nx, window.innerWidth - w - 8));
          ny = Math.max(8, Math.min(ny, window.innerHeight - Math.min(h, 80) - 8));
          panel.style.left = `${nx}px`;
          panel.style.top = `${ny}px`;
        };
        const onUp = ev => {
          try { handle.releasePointerCapture(ev.pointerId); } catch (_err) { /* ignore */ }
          handle.removeEventListener("pointermove", onMove);
          handle.removeEventListener("pointerup", onUp);
          handle.removeEventListener("pointercancel", onUp);
        };
        handle.addEventListener("pointermove", onMove);
        handle.addEventListener("pointerup", onUp);
        handle.addEventListener("pointercancel", onUp);
      });
    }

    function setMapHighlights(abbrs, { pulse = true } = {}) {
      highlightAbbrs.clear();
      (abbrs || []).forEach(a => { if (a) highlightAbbrs.add(a); });
      refreshMap();
      if (pulse) applyHighlightClasses(true);
    }

    function openPlayModal(title, { clearBackdrop = false, keepPosition = false } = {}) {
      if (isReportOpen()) closeReport();
      if (isDrawerOpen()) closeMetricsDrawer();
      $("play-title").textContent = title;
      const modal = $("play-modal");
      if (!keepPosition) resetPanelPosition();
      modal.classList.toggle("map-clear", Boolean(clearBackdrop));
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
      bindPanelDrag();
    }

    function deactivate() {
      const modal = $("play-modal");
      if (!modal) return;
      modal.classList.remove("open", "map-clear");
      modal.setAttribute("aria-hidden", "true");
      $("btn-my-state")?.classList.remove("active");
      $("btn-anomaly")?.classList.remove("active");
      resetPanelPosition();
      myStateMode = false;
      anomalyType = null;
    }

    function closePlayModal() {
      deactivate();
      clearHighlights();
      refreshMap();
    }

    function rankInfo(mkey, abbr) {
      const rows = rankedStates(mkey, 9999);
      const idx = rows.findIndex(r => r.state === abbr);
      if (idx < 0) return null;
      return { rank: idx + 1, n: rows.length, value: rows[idx].value };
    }

    function findAnomalies(type) {
      const np = rankedStates("net_position", 9999);
      const growth = rankedStates("net_position_growth_pct", 9999);
      const assets = rankedStates("total_assets", 9999);
      const capita = rankedStates("net_position_per_capita", 9999);
      const rankOf = (rows) => {
        const m = new Map();
        rows.forEach((r, i) => m.set(r.state, { rank: i + 1, n: rows.length, value: r.value }));
        return m;
      };
      if (type === "growth_small") {
        const g = rankOf(growth);
        const n = rankOf(np);
        return [...g.keys()]
          .filter(st => n.has(st)
            && g.get(st).rank <= Math.max(1, Math.ceil(g.get(st).n * 0.25))
            && n.get(st).rank > Math.floor(n.get(st).n * 0.5))
          .map(st => ({ state: st, growth: g.get(st), net: n.get(st) }))
          .sort((a, b) => a.growth.rank - b.growth.rank);
      }
      if (type === "assets_low_capita") {
        const a = rankOf(assets);
        const c = rankOf(capita);
        return [...a.keys()]
          .filter(st => c.has(st)
            && a.get(st).rank <= Math.max(1, Math.ceil(a.get(st).n * 0.25))
            && c.get(st).rank > Math.floor(c.get(st).n * 0.5))
          .map(st => ({ state: st, assets: a.get(st), capita: c.get(st) }))
          .sort((a, b) => a.assets.rank - b.assets.rank);
      }
      return [];
    }

    function stopAnomaly() {
      anomalyType = null;
      $("btn-anomaly")?.classList.remove("active");
      if (!myStateMode) {
        clearHighlights();
        refreshMap();
      }
    }

    function renderMyState(abbr) {
      const rec = getStateData(abbr);
      if (!rec) {
        $("play-body").innerHTML = `<p class="compare-hint">${t("playNoData")}</p>`;
        return;
      }
      const name = stateDisplayName(rec, abbr);
      const np = rankInfo("net_position", abbr);
      const gr = rankInfo("net_position_growth_pct", abbr);
      const cap = rankInfo("net_position_per_capita", abbr);
      const lines = [];
      if (np) {
        lines.push(t("myStateLineNp")
          .replace("{name}", name).replace("{abbr}", abbr)
          .replace("{rank}", String(np.rank)).replace("{n}", String(np.n))
          .replace("{val}", fmt(np.value, "net_position")));
      }
      if (gr) {
        lines.push(t("myStateLineGrowth")
          .replace("{rank}", String(gr.rank)).replace("{n}", String(gr.n))
          .replace("{val}", fmt(gr.value, "net_position_growth_pct")));
      }
      if (cap) {
        lines.push(t("myStateLineCapita")
          .replace("{rank}", String(cap.rank)).replace("{n}", String(cap.n))
          .replace("{val}", fmt(cap.value, "net_position_per_capita")));
      }
      if (!lines.length) lines.push(t("playNoData"));

      const opts = (getDataset()?.states || [])
        .slice()
        .sort((a, b) => a.state.localeCompare(b.state))
        .map(s => {
          const label = getLang() === "zh"
            ? `${s.state} · ${s.name_zh || s.name_en}`
            : `${s.state} · ${s.name_en || s.state}`;
          return `<option value="${s.state}" ${s.state === abbr ? "selected" : ""}>${label}</option>`;
        })
        .join("");

      $("play-body").innerHTML = `
        <label class="play-field">
          <span>${t("myStatePick")}</span>
          <select id="my-state-select">${opts}</select>
        </label>
        <ul class="play-bullets">${lines.map(l => `<li>${l}</li>`).join("")}</ul>
        <div class="play-actions">
          <button type="button" id="btn-my-state-goto">${t("myStateGoto")}</button>
          <button type="button" id="btn-my-state-copy">${t("shareBtn")}</button>
        </div>`;
      $("my-state-select").onchange = e => {
        const next = e.target.value;
        setFocusedState(next);
        setMapHighlights([next]);
        renderMyState(next);
      };
      $("btn-my-state-goto").onclick = () => {
        flyToState(abbr, { openPopup: false });
        setMapHighlights([abbr]);
      };
      $("btn-my-state-copy").onclick = async () => {
        setFocusedState(abbr);
        setPrimaryMetricOnly("net_position");
        syncUrlFromState();
        const url = buildShareUrl();
        try {
          await navigator.clipboard.writeText(url);
          $("btn-my-state-copy").textContent = t("shareCopied");
        } catch (_e) {
          window.prompt(t("shareBtn"), url);
        }
      };
    }

    function openMyState() {
      if (myStateMode && $("play-modal")?.classList.contains("open")) {
        closePlayModal();
        return;
      }
      clearExclusiveTools?.({ except: "play" });
      anomalyType = null;
      myStateMode = true;
      $("btn-my-state")?.classList.add("active");
      $("btn-anomaly")?.classList.remove("active");
      const abbr = getFocusedState() || "CA";
      setFocusedState(abbr);
      setMapHighlights([abbr]);
      openPlayModal(t("myStateTitle"), { clearBackdrop: true });
      renderMyState(abbr);
    }

    function applyAnomaly(type) {
      myStateMode = false;
      anomalyType = type;
      const rows = findAnomalies(type);
      const abbrs = rows.map(r => r.state);
      // Map metric chosen so matched states are not mid-scale yellow fills
      // (yellow rim would otherwise look like the whole state lighting up).
      const metric = type === "growth_small"
        ? "net_position_growth_pct"
        : "net_position_per_capita";
      setPrimaryMetricOnly(metric);
      $("btn-anomaly").classList.add("active");
      $("btn-my-state")?.classList.remove("active");
      const panelAlreadyOpen = $("play-modal")?.classList.contains("open");
      openPlayModal(t("anomalyTitle"), {
        clearBackdrop: true,
        keepPosition: panelAlreadyOpen,
      });
      const explain = type === "growth_small" ? t("anomalyGrowthSmall") : t("anomalyAssetsLowCapita");
      const list = rows.slice(0, 12).map(r => {
        const rec = getStateData(r.state);
        const name = stateDisplayName(rec, r.state);
        if (type === "growth_small") {
          return `<li data-state="${r.state}"><strong>${r.state}</strong> ${name}
            <span>${tMetric("net_position_growth_pct")} #${r.growth.rank} · ${tMetric("net_position")} #${r.net.rank}</span></li>`;
        }
        return `<li data-state="${r.state}"><strong>${r.state}</strong> ${name}
          <span>${tMetric("total_assets")} #${r.assets.rank} · ${tMetric("net_position_per_capita")} #${r.capita.rank}</span></li>`;
      }).join("");
      $("play-body").innerHTML = `
        <p class="compare-hint">${explain}</p>
        <p class="compare-hint">${t("anomalyCount").replace("{n}", String(rows.length))}</p>
        <ul class="play-list">${list || `<li>${t("playNoData")}</li>`}</ul>
        <div class="play-actions">
          <button type="button" id="btn-anomaly-next">${t("anomalyNext")}</button>
          <button type="button" id="btn-anomaly-clear">${t("anomalyClear")}</button>
        </div>`;
      // No pulse: keeps rim weight/brightness identical across states (MI reference)
      setMapHighlights(abbrs, { pulse: false });
      $("play-body").querySelectorAll("li[data-state]").forEach(li => {
        li.onclick = () => {
          const st = li.dataset.state;
          flyToState(st, { openPopup: false });
          setMapHighlights(abbrs, { pulse: false });
        };
      });
      $("btn-anomaly-next").onclick = () => {
        const i = ANOMALY_ORDER.indexOf(anomalyType || type);
        applyAnomaly(ANOMALY_ORDER[(i + 1) % ANOMALY_ORDER.length]);
      };
      $("btn-anomaly-clear").onclick = () => {
        stopAnomaly();
        closePlayModal();
      };
    }

    function toggleAnomaly() {
      if (anomalyType && $("play-modal")?.classList.contains("open")) {
        closePlayModal();
        return;
      }
      clearExclusiveTools?.({ except: "play" });
      applyAnomaly(ANOMALY_ORDER[0]);
    }

    function renderPlayLabels() {
      $("btn-my-state").textContent = t("myStateBtn");
      $("btn-anomaly").textContent = t("anomalyBtn");
      $("btn-play-close").setAttribute("aria-label", t("closePlay"));
    }

    function onMapClick(abbr) {
      if (!myStateMode || !$("play-modal")?.classList.contains("open")) return false;
      if (!abbr || !getStateData(abbr)) return true;
      setFocusedState(abbr);
      setMapHighlights([abbr]);
      renderMyState(abbr);
      return true; // suppress default report popup
    }

    function onEscape() {
      if ($("play-modal").classList.contains("open")) {
        closePlayModal();
        return true;
      }
      return false;
    }

    $("btn-my-state").onclick = openMyState;
    $("btn-anomaly").onclick = toggleAnomaly;
    $("btn-play-close").onclick = closePlayModal;

    renderPlayLabels();
    return { renderPlayLabels, onMapClick, onEscape, deactivate };
  };
})();
