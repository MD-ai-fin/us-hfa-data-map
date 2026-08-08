/**
 * Chart views: full state Rankings + Scatter correlation explorer.
 * window.initHfaCharts(api) → { renderChartLabels, deactivate, onEscape }
 */
(function () {
  window.initHfaCharts = function initHfaCharts(api) {
    const {
      t, tMetric, getLang,
      getStateData, stateDisplayName, metricValueForState, fmt,
      METRIC_KEYS, METRIC_COLORS,
      rankedStates, metricValues, metricRange,
      flyToState, clearHighlights, highlightAbbrs, refreshMap, applyHighlightClasses,
      getDataset,
      closeMetricsDrawer, isDrawerOpen,
      closeReport, isReportOpen,
      clearExclusiveTools,
      reduceMotion,
    } = api;

    let activeView = null; // "rank" | "scatter" | null
    let rankMetric = "net_position";
    let scatterX = "poverty_rate";
    let scatterY = "net_position";
    let selectedAbbr = null;

    function $(id) { return document.getElementById(id); }

    function escapeXml(str) {
      return String(str).replace(/[&<>"']/g, c => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;",
      }[c]));
    }

    function openChartModal(view) {
      if (isReportOpen()) closeReport();
      if (isDrawerOpen()) closeMetricsDrawer();
      clearExclusiveTools?.({ except: "charts" });
      const modal = $("chart-modal");
      if (!modal) return;
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
      switchView(view);
    }

    function switchView(view) {
      activeView = view;
      $("btn-rank-chart")?.classList.toggle("active", view === "rank");
      $("btn-scatter")?.classList.toggle("active", view === "scatter");
      const title = $("chart-title");
      if (title) title.textContent = view === "scatter" ? t("scatterTitle") : t("rankChartTitle");
      if (view === "scatter") renderScatterView(); else renderRankView();
    }

    function deactivate() {
      const modal = $("chart-modal");
      if (!modal) return;
      modal.classList.remove("open");
      modal.setAttribute("aria-hidden", "true");
      $("btn-rank-chart")?.classList.remove("active");
      $("btn-scatter")?.classList.remove("active");
      activeView = null;
    }

    function closeChartModal() {
      deactivate();
      clearHighlights();
      refreshMap();
    }

    function selectState(abbr) {
      if (!abbr) return;
      selectedAbbr = abbr;
      flyToState(abbr, { openPopup: false });
      highlightAbbrs.clear();
      highlightAbbrs.add(abbr);
      refreshMap();
      applyHighlightClasses(true);
      const body = $("chart-body");
      body?.querySelectorAll(".is-selected").forEach(el => el.classList.remove("is-selected"));
      body?.querySelectorAll(`[data-state="${abbr}"]`).forEach(el => el.classList.add("is-selected"));
    }

    // ---------- Ranking chart ----------

    function renderRankView() {
      const body = $("chart-body");
      if (!body) return;
      const metric = rankMetric;
      const rows = rankedStates(metric, 9999);
      const { min, max } = metricRange(metric);
      const domMin = Math.min(0, min);
      const domMax = Math.max(0, max);
      const span = (domMax - domMin) || 1;
      const zeroPct = ((0 - domMin) / span) * 100;
      const color = METRIC_COLORS[metric] || "var(--accent)";
      const options = METRIC_KEYS
        .map(k => `<option value="${k}" ${k === metric ? "selected" : ""}>${tMetric(k)}</option>`)
        .join("");
      const hint = t("rankChartHint").replace("{n}", String(rows.length));
      const listHtml = rows.map((r, i) => {
        const name = stateDisplayName(r.rec, r.state);
        const val = fmt(r.value, metric);
        const valPct = ((r.value - domMin) / span) * 100;
        const left = Math.max(0, Math.min(100, Math.min(zeroPct, valPct)));
        const right = Math.max(0, Math.min(100, Math.max(zeroPct, valPct)));
        const width = Math.max(0, right - left);
        const selected = r.state === selectedAbbr ? " is-selected" : "";
        const motionClass = reduceMotion ? " no-motion" : "";
        return `<li class="chart-rank-row${selected}${motionClass}" data-state="${r.state}" tabindex="0">
          <span class="rk">${i + 1}</span>
          <span class="abbr">${r.state}</span>
          <span class="bar-track"><span class="bar-fill" style="left:${left}%;width:${width}%;background:${color};"></span></span>
          <span class="val">${val}</span>
          <span class="name-line">${name}</span>
        </li>`;
      }).join("");
      body.innerHTML = `
        <div class="chart-controls">
          <label class="chart-field">
            <span>${t("rankChartMetricLabel")}</span>
            <select id="chart-metric-select">${options}</select>
          </label>
        </div>
        <p class="chart-hint">${hint}</p>
        <ol class="chart-rank-list" id="chart-rank-list">${listHtml}</ol>`;
      $("chart-metric-select").onchange = e => {
        rankMetric = e.target.value;
        renderRankView();
      };
      body.querySelectorAll(".chart-rank-row").forEach(row => {
        const go = () => selectState(row.dataset.state);
        row.onclick = go;
        row.onkeydown = e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } };
      });
    }

    // ---------- Scatter plot ----------

    function domainFor(values) {
      if (!values.length) return { min: 0, max: 1 };
      let min = Math.min(...values), max = Math.max(...values);
      if (min === max) {
        const eps = Math.abs(min) > 0 ? Math.abs(min) * 0.1 : 1;
        min -= eps; max += eps;
      }
      const pad = (max - min) * 0.08;
      return { min: min - pad, max: max + pad };
    }

    function leastSquares(pts) {
      const n = pts.length;
      if (n < 3) return null;
      const meanX = pts.reduce((s, p) => s + p.x, 0) / n;
      const meanY = pts.reduce((s, p) => s + p.y, 0) / n;
      let sxy = 0, sxx = 0, syy = 0;
      for (const p of pts) {
        const dx = p.x - meanX, dy = p.y - meanY;
        sxy += dx * dy;
        sxx += dx * dx;
        syy += dy * dy;
      }
      if (sxx === 0 || syy === 0) return null;
      const slope = sxy / sxx;
      const intercept = meanY - slope * meanX;
      const r = sxy / Math.sqrt(sxx * syy);
      return { slope, intercept, r, n };
    }

    function buildScatterSvg(points, xKey, yKey, fit) {
      const W = 760, H = 460;
      const M = { top: 20, right: 24, bottom: 46, left: 68 };
      const plotW = W - M.left - M.right;
      const plotH = H - M.top - M.bottom;
      const xs = points.map(p => p.x), ys = points.map(p => p.y);
      const { min: xMin, max: xMax } = domainFor(xs);
      const { min: yMin, max: yMax } = domainFor(ys);
      const xScale = v => M.left + ((v - xMin) / (xMax - xMin)) * plotW;
      const yScale = v => M.top + plotH - ((v - yMin) / (yMax - yMin)) * plotH;
      const TICK_COUNT = 5;
      const ticksFor = (min, max) =>
        Array.from({ length: TICK_COUNT }, (_, i) => min + (i / (TICK_COUNT - 1)) * (max - min));
      const xTicks = ticksFor(xMin, xMax);
      const yTicks = ticksFor(yMin, yMax);

      let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${escapeXml(tMetric(xKey))} / ${escapeXml(tMetric(yKey))}">`;
      svg += `<clipPath id="chart-plot-clip"><rect x="${M.left}" y="${M.top}" width="${plotW}" height="${plotH}"/></clipPath>`;

      xTicks.forEach(tv => {
        const x = xScale(tv);
        svg += `<line class="grid-line" x1="${x}" y1="${M.top}" x2="${x}" y2="${M.top + plotH}"/>`;
        svg += `<text class="tick-label" x="${x}" y="${M.top + plotH + 16}" text-anchor="middle">${escapeXml(fmt(tv, xKey))}</text>`;
      });
      yTicks.forEach(tv => {
        const y = yScale(tv);
        svg += `<line class="grid-line" x1="${M.left}" y1="${y}" x2="${M.left + plotW}" y2="${y}"/>`;
        svg += `<text class="tick-label" x="${M.left - 8}" y="${y + 3}" text-anchor="end">${escapeXml(fmt(tv, yKey))}</text>`;
      });

      svg += `<line class="axis-line" x1="${M.left}" y1="${M.top}" x2="${M.left}" y2="${M.top + plotH}"/>`;
      svg += `<line class="axis-line" x1="${M.left}" y1="${M.top + plotH}" x2="${M.left + plotW}" y2="${M.top + plotH}"/>`;

      svg += `<text class="axis-label" x="${M.left + plotW / 2}" y="${H - 8}" text-anchor="middle">${escapeXml(tMetric(xKey))}</text>`;
      svg += `<text class="axis-label" x="${-(M.top + plotH / 2)}" y="14" text-anchor="middle" transform="rotate(-90)">${escapeXml(tMetric(yKey))}</text>`;

      if (fit) {
        const y1 = fit.intercept + fit.slope * xMin;
        const y2 = fit.intercept + fit.slope * xMax;
        svg += `<path class="trend-line" clip-path="url(#chart-plot-clip)" d="M${xScale(xMin)},${yScale(y1)} L${xScale(xMax)},${yScale(y2)}"/>`;
      }

      points.forEach(p => {
        const cx = xScale(p.x), cy = yScale(p.y);
        const name = stateDisplayName(p.rec, p.abbr);
        const label = `${name} ${p.abbr}: ${tMetric(xKey)} ${fmt(p.x, xKey)}, ${tMetric(yKey)} ${fmt(p.y, yKey)}`;
        const selected = p.abbr === selectedAbbr ? " is-selected" : "";
        svg += `<circle class="pt${selected}" data-state="${p.abbr}" cx="${cx.toFixed(2)}" cy="${cy.toFixed(2)}" r="5" tabindex="0" role="button" aria-label="${escapeXml(label)}"></circle>`;
        svg += `<text class="pt-label" x="${(cx + 7).toFixed(2)}" y="${(cy + 3).toFixed(2)}">${p.abbr}</text>`;
      });

      svg += `</svg>`;
      return svg;
    }

    function wireScatterInteractions(points, xKey, yKey) {
      const wrap = $("chart-scatter-wrap");
      const tooltip = $("chart-tooltip");
      if (!wrap) return;
      const byAbbr = new Map(points.map(p => [p.abbr, p]));
      wrap.querySelectorAll(".pt").forEach(circle => {
        const abbr = circle.dataset.state;
        const p = byAbbr.get(abbr);
        if (!p) return;
        const show = () => {
          if (!tooltip) return;
          const name = stateDisplayName(p.rec, abbr);
          tooltip.innerHTML = `<strong>${name} (${abbr})</strong><br>${tMetric(xKey)}: ${fmt(p.x, xKey)}<br>${tMetric(yKey)}: ${fmt(p.y, yKey)}`;
          const wrapRect = wrap.getBoundingClientRect();
          const circleRect = circle.getBoundingClientRect();
          tooltip.style.left = `${circleRect.left - wrapRect.left + circleRect.width / 2}px`;
          tooltip.style.top = `${circleRect.top - wrapRect.top - 8}px`;
          tooltip.classList.add("show");
        };
        const hide = () => tooltip?.classList.remove("show");
        circle.addEventListener("mouseenter", show);
        circle.addEventListener("mouseleave", hide);
        circle.addEventListener("focus", show);
        circle.addEventListener("blur", hide);
        const go = () => selectState(abbr);
        circle.addEventListener("click", go);
        circle.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
      });
    }

    function renderScatterView() {
      const body = $("chart-body");
      if (!body) return;
      const xKey = scatterX, yKey = scatterY;
      const allStates = getDataset()?.states || [];
      const points = allStates
        .map(s => ({
          abbr: s.state,
          rec: s,
          x: metricValueForState(s, xKey),
          y: metricValueForState(s, yKey),
        }))
        .filter(p => p.x != null && p.y != null && Number.isFinite(p.x) && Number.isFinite(p.y));
      const shown = points.length;
      const excluded = Math.max(0, allStates.length - shown);
      const fit = leastSquares(points);
      const hint = t("scatterHint").replace("{shown}", String(shown)).replace("{excluded}", String(excluded));
      const corrText = fit
        ? t("scatterCorrelation").replace("{r}", fit.r.toFixed(2)).replace("{n}", String(fit.n))
        : t("scatterInsufficientData");
      const optionsFor = key => METRIC_KEYS
        .map(k => `<option value="${k}" ${k === key ? "selected" : ""}>${tMetric(k)}</option>`)
        .join("");
      body.innerHTML = `
        <div class="chart-controls">
          <label class="chart-field">
            <span>${t("scatterXLabel")}</span>
            <select id="chart-x-select">${optionsFor(xKey)}</select>
          </label>
          <label class="chart-field">
            <span>${t("scatterYLabel")}</span>
            <select id="chart-y-select">${optionsFor(yKey)}</select>
          </label>
        </div>
        <p class="chart-hint">${hint} ${corrText}</p>
        <div class="chart-scatter-wrap" id="chart-scatter-wrap">
          ${buildScatterSvg(points, xKey, yKey, fit)}
          <div class="chart-tooltip" id="chart-tooltip"></div>
        </div>`;
      $("chart-x-select").onchange = e => { scatterX = e.target.value; renderScatterView(); };
      $("chart-y-select").onchange = e => { scatterY = e.target.value; renderScatterView(); };
      wireScatterInteractions(points, xKey, yKey);
    }

    // ---------- Public surface ----------

    function renderChartLabels() {
      const rankBtn = $("btn-rank-chart");
      if (rankBtn) rankBtn.textContent = t("rankChartBtn");
      const scatterBtn = $("btn-scatter");
      if (scatterBtn) scatterBtn.textContent = t("scatterBtn");
      $("btn-chart-close")?.setAttribute("aria-label", t("closeChart"));
      const modal = $("chart-modal");
      if (modal?.classList.contains("open") && activeView) {
        const title = $("chart-title");
        if (title) title.textContent = activeView === "scatter" ? t("scatterTitle") : t("rankChartTitle");
        if (activeView === "scatter") renderScatterView(); else renderRankView();
      }
    }

    function onEscape() {
      if ($("chart-modal")?.classList.contains("open")) {
        closeChartModal();
        return true;
      }
      return false;
    }

    $("btn-rank-chart").onclick = () => {
      if (activeView === "rank" && $("chart-modal")?.classList.contains("open")) { closeChartModal(); return; }
      openChartModal("rank");
    };
    $("btn-scatter").onclick = () => {
      if (activeView === "scatter" && $("chart-modal")?.classList.contains("open")) { closeChartModal(); return; }
      openChartModal("scatter");
    };
    $("btn-chart-close").onclick = closeChartModal;
    $("chart-modal").onclick = e => { if (e.target.id === "chart-modal") closeChartModal(); };

    renderChartLabels();
    return { renderChartLabels, deactivate, onEscape };
  };
})();
