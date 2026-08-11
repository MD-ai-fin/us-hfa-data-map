/**
 * Illinois FY2025 IHDA program-activity explorer (state-specific pilot).
 * Fetches il_program_activity.json lazily (only when opened, so the other
 * 49 states' page load is unaffected) and renders:
 *   - 4 KPI cards (one per non-overlapping macro category)
 *   - a geographic bubble map of Category-1 (multifamily) closed projects
 *   - explicit overlap flags wherever subprogram figures share projects
 *   - FY2025-actual vs FY2026-projected badges (never a fabricated number)
 * window.initIlActivity(api) → { deactivate, onEscape, renderLabels, isAvailable }
 */
(function () {
  window.initIlActivity = function initIlActivity(api) {
    const {
      t, getLang,
      clearExclusiveTools,
      closeMetricsDrawer, isDrawerOpen,
      closeReport, isReportOpen,
    } = api;

    let data = null;          // .IL payload once loaded
    let loadPromise = null;
    let loadFailed = false;
    let isOpen = false;
    let bubbleMap = null;     // Leaflet instance, created once and reused

    const COLOR_GROUP_HEX = { bond: "#38bdf8", credit: "#4ade80", trust: "#a78bfa", capital: "#fb923c" };
    const CATEGORY_BASE_HEX = {
      homebuyer_loans: "#22c55e",
      repair_counseling: "#f59e0b",
      covid_emergency: "#f43f5e",
    };
    const CATEGORY_ICON = {
      multifamily_new_preserve: "🏗️",
      homebuyer_loans: "🏡",
      repair_counseling: "🔧",
      covid_emergency: "🆘",
    };
    const UNIT_ICON = { units: "🏠", households: "🧑" };

    function $(id) { return document.getElementById(id); }

    function escapeHtml(str) {
      return String(str).replace(/[&<>"']/g, c => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
      }[c]));
    }

    function fmtNum(n) {
      if (n == null) return "—";
      const locale = { zh: "zh-CN", en: "en-US", es: "es-ES", pl: "pl-PL" }[getLang()] || "en-US";
      return n.toLocaleString(locale);
    }

    function fmtUsd(n) {
      if (n == null) return null;
      const abs = Math.abs(n);
      if (abs >= 1e9) return "$" + (n / 1e9).toFixed(2) + "B";
      if (abs >= 1e6) return "$" + (n / 1e6).toFixed(2) + "M";
      if (abs >= 1e3) return "$" + (n / 1e3).toFixed(0) + "K";
      return "$" + fmtNum(n);
    }

    function listJoin(items) {
      return items.join(getLang() === "zh" ? "、" : ", ");
    }

    // Lighten/darken a #rrggbb hex color toward white (factor 0..1, 1 = original).
    function shade(hex, factor) {
      const n = parseInt(hex.slice(1), 16);
      let r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
      r = Math.round(r * factor + 255 * (1 - factor));
      g = Math.round(g * factor + 255 * (1 - factor));
      b = Math.round(b * factor + 255 * (1 - factor));
      return `rgb(${r},${g},${b})`;
    }

    function loadData() {
      if (loadPromise) return loadPromise;
      loadPromise = fetch("il_program_activity.json")
        .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
        .then(json => { data = json.IL; })
        .catch(err => {
          loadFailed = true;
          console.error("il_program_activity.json load failed:", err);
        });
      return loadPromise;
    }
    // Kick off a background prefetch so the modal usually opens instantly.
    loadData();

    // fy2026 shape: { value, amount, closed, note_key }. `value` (units/
    // households) and `amount` ($) are disclosed independently by IHDA --
    // many subprograms give a dollar figure with no unit count, or vice
    // versa -- so both are shown whenever present, and only a program with
    // neither gets the neutral "pending" badge.
    function fy2026Badge(fy2026, unitType) {
      if (!fy2026) return "";
      if (fy2026.closed) {
        return `<span class="il-fy26-badge il-fy26-closed">${escapeHtml(t("ilFy2026Closed"))}</span>`;
      }
      const parts = [];
      if (fy2026.value != null) parts.push(`${fmtNum(fy2026.value)} ${UNIT_ICON[unitType] || ""}`);
      if (fy2026.amount != null) parts.push(fmtUsd(fy2026.amount));
      if (parts.length) {
        return `<span class="il-fy26-badge il-fy26-numeric">${escapeHtml(t("ilFy2026Label"))}: ${parts.join(" · ")}</span>`;
      }
      return `<span class="il-fy26-badge il-fy26-pending">⏳ ${escapeHtml(t("ilFy2026Pending"))}</span>`;
    }

    function overlapSourcesFor(subKey) {
      const projects = (data.projects || []).filter(p =>
        p.funding_sources.includes(subKey) && p.funding_sources.length > 1);
      const others = new Set();
      projects.forEach(p => p.funding_sources.forEach(s => { if (s !== subKey) others.add(s); }));
      return [...others];
    }

    function renderCategoryCard(cat) {
      const uIcon = UNIT_ICON[cat.unit_type] || "";
      const title = escapeHtml(t(`ilCat_${cat.key}`));
      const badge = fy2026Badge(cat.fy2026, cat.unit_type);
      const amountsHtml = (cat.fy2025_amounts || [])
        .map(a => `<span class="il-amount-chip">${escapeHtml(t(a.label_key))}: ${fmtUsd(a.amount)}</span>`)
        .join("");
      let subHtml;
      if (cat.additive) {
        const base = CATEGORY_BASE_HEX[cat.key] || "#38bdf8";
        const total = cat.subprograms.reduce((s, sp) => s + sp.fy2025_units, 0) || 1;
        let acc = 0;
        const n = cat.subprograms.length;
        const segs = cat.subprograms.map((sp, i) => {
          const pct = (sp.fy2025_units / total) * 100;
          const left = (acc / total) * 100;
          acc += sp.fy2025_units;
          const f = n > 1 ? 1 - (i / (n - 1)) * 0.55 : 1;
          const label = `${escapeHtml(t(`ilSub_${sp.key}`))}: ${fmtNum(sp.fy2025_units)} ${uIcon} · ${fmtUsd(sp.fy2025_amount)}`;
          return `<span class="il-seg" title="${label}" style="left:${left}%;width:${pct}%;background:${shade(base, f)}"></span>`;
        }).join("");
        const legend = cat.subprograms.map((sp, i) => {
          const f = n > 1 ? 1 - (i / (n - 1)) * 0.55 : 1;
          const amt = fmtUsd(sp.fy2025_amount);
          return `<span class="il-sub-chip"><span class="il-dot" style="background:${shade(base, f)}"></span>${escapeHtml(t(`ilSub_${sp.key}`))} ${fmtNum(sp.fy2025_units)}${amt ? " · " + amt : ""}</span>`;
        }).join("");
        subHtml = `<div class="il-stack-track">${segs}</div><div class="il-sub-legend">${legend}</div>`;
      } else {
        const chips = cat.subprograms.map(sp => {
          const overlapWith = overlapSourcesFor(sp.key);
          let warn = "";
          if (overlapWith.length) {
            const names = listJoin(overlapWith.map(k => t(`ilSub_${k}`)));
            const tip = t("ilOverlapTooltip").replace("{others}", names);
            warn = `<span class="il-overlap-flag" tabindex="0" title="${escapeHtml(tip)}">⚠</span>`;
          }
          const hex = COLOR_GROUP_HEX[sp.color_group] || "#94a3b8";
          const amt = fmtUsd(sp.fy2025_amount);
          return `<span class="il-ref-chip"><span class="il-dot" style="background:${hex}"></span>${escapeHtml(t(`ilSub_${sp.key}`))} ${fmtNum(sp.fy2025_units)} ${uIcon}${amt ? " · " + amt : ""}${warn}</span>`;
        }).join("");
        subHtml = `<div class="il-chip-row">${chips}</div><p class="il-chip-note">${escapeHtml(t("ilNotAdditiveNote"))}</p>`;
      }
      return `<div class="il-kpi-card">
        <div class="il-kpi-head"><span class="il-kpi-icon">${CATEGORY_ICON[cat.key] || "📊"}</span><span class="il-kpi-title">${title}</span></div>
        <div class="il-kpi-value">${fmtNum(cat.fy2025_actual)} <span class="il-unit-icon">${uIcon}</span></div>
        ${amountsHtml ? `<div class="il-amount-row">${amountsHtml}</div>` : ""}
        <div class="il-kpi-fy26">${badge}</div>
        ${subHtml}
      </div>`;
    }

    function primaryColorGroup(project) {
      const first = data.categories
        .find(c => c.key === "multifamily_new_preserve").subprograms
        .find(sp => sp.key === project.funding_sources[0]);
      return first ? first.color_group : "capital";
    }

    function renderMap() {
      const wrap = $("il-bubble-map");
      if (!wrap || typeof L === "undefined") return;
      // renderBody() rebuilds #il-activity-body's innerHTML on every call
      // (language switch, reopen, etc.), which creates a brand-new
      // #il-bubble-map element each time. A previously-created Leaflet map
      // instance still points at the old, now-detached element, so it must
      // be torn down and recreated against the current one -- otherwise the
      // map renders into a disconnected node and appears blank.
      if (bubbleMap && bubbleMap.getContainer() !== wrap) {
        bubbleMap.remove();
        bubbleMap = null;
      }
      if (!bubbleMap) {
        bubbleMap = L.map(wrap, { attributionControl: false, zoomSnap: 0.25, zoomDelta: 0.5 })
          .setView([40.05, -89.2], 6.3);
        L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
          subdomains: "abcd", maxZoom: 19,
        }).addTo(bubbleMap);
      }
      bubbleMap.eachLayer(layer => { if (layer instanceof L.CircleMarker) bubbleMap.removeLayer(layer); });
      const projects = (data.projects || []).filter(p => p.lat != null && p.lon != null);
      projects.forEach(p => {
        const group = primaryColorGroup(p);
        const color = COLOR_GROUP_HEX[group] || "#94a3b8";
        const radius = 4 + Math.sqrt(Math.max(p.units, 1)) * 1.1;
        const marker = L.circleMarker([p.lat, p.lon], {
          radius, color: "#0f172a", weight: 1, fillColor: color, fillOpacity: 0.8,
        }).addTo(bubbleMap);
        const totalAmt = fmtUsd(p.total_amount);
        let tip = `<div class="il-tooltip"><strong>${escapeHtml(p.name)}</strong><br>${escapeHtml(p.city)}, IL — ${fmtNum(p.units)} ${UNIT_ICON.units}`;
        if (totalAmt) tip += ` — ${totalAmt}`;
        const sourceLines = p.funding_sources.map(s => {
          const amt = fmtUsd((p.source_amounts || {})[s]);
          return `${escapeHtml(t(`ilSub_${s}`))}${amt ? ": " + amt : ""}`;
        }).join("<br>");
        tip += `<br>${sourceLines}`;
        if (p.overlaps) {
          const others = listJoin(p.funding_sources.map(s => t(`ilSub_${s}`)));
          tip += `<span class="il-tt-overlap">${escapeHtml(t("ilProjectOverlapNote").replace("{sources}", others))}</span>`;
        }
        tip += `</div>`;
        marker.bindTooltip(tip, { sticky: true });
      });
      setTimeout(() => bubbleMap.invalidateSize({ animate: false }), 50);
    }

    function renderBody() {
      const body = $("il-activity-body");
      if (!body) return;
      if (loadFailed || !data) {
        body.innerHTML = `<p class="il-error">${escapeHtml(t("ilLoadError"))}</p>`;
        return;
      }
      const cards = data.categories.map(renderCategoryCard).join("");
      const mfProjects = (data.projects || []).length;
      const mapLegend = `<div class="il-map-legend">
        <span><span class="il-dot" style="background:${COLOR_GROUP_HEX.bond}"></span>${escapeHtml(t("ilMapLegendBond"))}</span>
        <span><span class="il-dot" style="background:${COLOR_GROUP_HEX.credit}"></span>${escapeHtml(t("ilMapLegendCredit"))}</span>
        <span><span class="il-dot" style="background:${COLOR_GROUP_HEX.trust}"></span>${escapeHtml(t("ilMapLegendTrust"))}</span>
        <span><span class="il-dot" style="background:${COLOR_GROUP_HEX.capital}"></span>${escapeHtml(t("ilMapLegendCapital"))}</span>
        <span>${escapeHtml(t("ilMapSizeLegend"))}</span>
        <span>${escapeHtml(t("ilMapCount").replace("{n}", String(mfProjects)))}</span>
      </div>`;
      const retrieved = data.retrieved || "";
      const sourceNote = escapeHtml(t("ilSourceNote"))
        .replace("{agency}", escapeHtml(data.hfa_name || data.hfa_abbr || "IHDA"))
        .replace("{title}", escapeHtml(data.source_title || ""))
        .replace("{fy}", escapeHtml(data.fiscal_year || ""))
        .replace("{retrieved}", escapeHtml(retrieved));
      body.innerHTML = `
        <div class="il-kpi-grid">${cards}</div>
        <div class="il-legend-units"><span>${escapeHtml(t("ilUnitsLegend"))}</span><span>${escapeHtml(t("ilHouseholdsLegend"))}</span></div>
        <div class="il-section-title">${escapeHtml(t("ilMapTitle"))}</div>
        <div class="il-map-wrap"><div id="il-bubble-map"></div>${mapLegend}</div>
        <p class="il-footnote">${sourceNote}<br><a href="${data.source_url}" target="_blank" rel="noopener noreferrer">${escapeHtml(data.source_file || data.source_url)}</a></p>
      `;
      renderMap();
    }

    function openModal() {
      if (isReportOpen?.()) closeReport();
      if (isDrawerOpen?.()) closeMetricsDrawer();
      clearExclusiveTools?.({ except: "il-activity" });
      const modal = $("il-activity-modal");
      if (!modal) return;
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
      isOpen = true;
      $("il-activity-title").textContent = t("ilModalTitle");
      const body = $("il-activity-body");
      if (body) body.innerHTML = "";
      loadData().then(renderBody);
    }

    function deactivate() {
      const modal = $("il-activity-modal");
      if (!modal) return;
      modal.classList.remove("open");
      modal.setAttribute("aria-hidden", "true");
      isOpen = false;
    }

    function closeModal() { deactivate(); }

    function onEscape() {
      if (isOpen) { closeModal(); return true; }
      return false;
    }

    function renderLabels() {
      $("btn-il-activity-close")?.setAttribute("aria-label", t("closeChart"));
      if (isOpen) {
        $("il-activity-title").textContent = t("ilModalTitle");
        if (data) renderBody();
      }
    }

    function isAvailable() { return true; }

    document.addEventListener("click", e => {
      if (e.target.closest("#btn-il-activity")) openModal();
    });
    $("btn-il-activity-close")?.addEventListener("click", closeModal);
    $("il-activity-modal")?.addEventListener("click", e => {
      if (e.target.id === "il-activity-modal") closeModal();
    });

    return { deactivate, onEscape, renderLabels, isAvailable };
  };
})();
