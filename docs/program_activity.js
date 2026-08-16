/**
 * State FY2025 HFA program-activity explorer (multi-state, config-driven).
 * Started as an Illinois-only pilot (IHDA's Report of Activities); generalized
 * to any state registered in STATE_CONFIGS below, each backed by its own
 * {abbr_lowercase}_program_activity.json built by a matching
 * FY2025/program_activity/build_{abbr}_program_activity.py script. Data for a
 * given state is fetched lazily -- only when its modal is actually opened --
 * so states with no program-activity module (currently every state outside
 * STATE_CONFIGS) never trigger an extra request.
 * Renders, per state:
 *   - one KPI card per macro category (non-overlapping ones get a stacked bar,
 *     overlapping ones get reference chips with an explicit overlap flag)
 *   - a geographic bubble map of the multifamily category's closed/awarded
 *     projects (marker precision depends on what the source document
 *     discloses -- street address, city/county center, etc. -- per state)
 *   - FY2025-actual vs FY2026-projected badges (never a fabricated number)
 * window.initProgramActivity(api) → { deactivate, onEscape, renderLabels, isAvailable }
 */
(function () {
  // Add an entry here once a state's build script + JSON + i18n strings
  // (`{prefix}ModalTitle`, `{prefix}Cat_*`, `{prefix}Sub_*`, and any
  // note_key/label_key strings referenced by that state's JSON) are in
  // place. `prefix` namespaces the i18n keys generated at render time
  // (`${prefix}Cat_${cat.key}` etc); `mapCenter`/`mapZoom` frame the
  // Leaflet bubble map on that state.
  const STATE_CONFIGS = {
    IL: {
      file: "il_program_activity.json", prefix: "il",
      modalTitleKey: "ilModalTitle", mapCenter: [40.05, -89.2], mapZoom: 6.3,
    },
    PA: {
      file: "pa_program_activity.json", prefix: "pa",
      modalTitleKey: "paModalTitle", mapCenter: [40.9, -77.7], mapZoom: 6.7,
    },
    FL: {
      file: "fl_program_activity.json", prefix: "fl",
      modalTitleKey: "flModalTitle", mapCenter: [28.4, -82.0], mapZoom: 6.3,
    },
    OH: {
      file: "oh_program_activity.json", prefix: "oh",
      modalTitleKey: "ohModalTitle", mapCenter: [40.3, -82.8], mapZoom: 6.8,
    },
    WA: {
      file: "wa_program_activity.json", prefix: "wa",
      modalTitleKey: "waModalTitle", mapCenter: [47.4, -120.5], mapZoom: 6.7,
    },
    TX: {
      file: "tx_program_activity.json", prefix: "tx",
      modalTitleKey: "txModalTitle", mapCenter: [31.0, -99.3], mapZoom: 6,
    },
    MA: {
      file: "ma_program_activity.json", prefix: "ma",
      modalTitleKey: "maModalTitle", mapCenter: [42.2, -71.5], mapZoom: 8,
    },
    NY: {
      file: "ny_program_activity.json", prefix: "ny",
      modalTitleKey: "nyModalTitle", mapCenter: [42.9, -75.5], mapZoom: 6.3,
    },
    CA: {
      file: "ca_program_activity.json", prefix: "ca",
      modalTitleKey: "caModalTitle", mapCenter: [37.2, -119.5], mapZoom: 6,
    },
    CT: {
      file: "ct_program_activity.json", prefix: "ct",
      modalTitleKey: "ctModalTitle", mapCenter: [41.6, -72.7], mapZoom: 8.5,
    },
    MI: {
      file: "mi_program_activity.json", prefix: "mi",
      modalTitleKey: "miModalTitle", mapCenter: [44.3, -85.6], mapZoom: 6.3,
    },
    MN: {
      file: "mn_program_activity.json", prefix: "mn",
      modalTitleKey: "mnModalTitle", mapCenter: [46.0, -94.3], mapZoom: 6,
    },
    IA: {
      file: "ia_program_activity.json", prefix: "ia",
      modalTitleKey: "iaModalTitle", mapCenter: [42.0, -93.5], mapZoom: 7,
    },
    WI: {
      file: "wi_program_activity.json", prefix: "wi",
      modalTitleKey: "wiModalTitle", mapCenter: [44.5, -89.5], mapZoom: 6.5,
    },
    HI: {
      file: "hi_program_activity.json", prefix: "hi",
      modalTitleKey: "hiModalTitle", mapCenter: [20.5, -157.5], mapZoom: 6.5,
    },
    VA: {
      file: "va_program_activity.json", prefix: "va",
      modalTitleKey: "vaModalTitle", mapCenter: [37.5, -78.5], mapZoom: 6.8,
    },
    AK: {
      file: "ak_program_activity.json", prefix: "ak",
      modalTitleKey: "akModalTitle", mapCenter: [64.0, -153.0], mapZoom: 4,
    },
    CO: {
      file: "co_program_activity.json", prefix: "co",
      modalTitleKey: "coModalTitle", mapCenter: [39.0, -105.5], mapZoom: 7,
    },
    NC: {
      file: "nc_program_activity.json", prefix: "nc",
      modalTitleKey: "ncModalTitle", mapCenter: [35.5, -79.0], mapZoom: 7,
    },
    UT: {
      file: "ut_program_activity.json", prefix: "ut",
      modalTitleKey: "utModalTitle", mapCenter: [39.5, -111.5], mapZoom: 6.5,
    },
    AZ: {
      file: "az_program_activity.json", prefix: "az",
      modalTitleKey: "azModalTitle", mapCenter: [34.3, -111.7], mapZoom: 6.5,
    },
    NH: {
      file: "nh_program_activity.json", prefix: "nh",
      modalTitleKey: "nhModalTitle", mapCenter: [43.7, -71.6], mapZoom: 7,
    },
    OR: {
      file: "or_program_activity.json", prefix: "or",
      modalTitleKey: "orModalTitle", mapCenter: [44.0, -120.5], mapZoom: 6.6,
    },
    RI: {
      file: "ri_program_activity.json", prefix: "ri",
      modalTitleKey: "riModalTitle", mapCenter: [41.7, -71.5], mapZoom: 9,
    },
    IN: {
      file: "in_program_activity.json", prefix: "in",
      modalTitleKey: "inModalTitle", mapCenter: [39.9, -86.2], mapZoom: 6.8,
    },
    ME: {
      file: "me_program_activity.json", prefix: "me",
      modalTitleKey: "meModalTitle", mapCenter: [45.25, -69.0], mapZoom: 6.5,
    },
    AR: {
      file: "ar_program_activity.json", prefix: "ar",
      modalTitleKey: "arModalTitle", mapCenter: [34.9, -92.3], mapZoom: 7,
    },
    GA: {
      file: "ga_program_activity.json", prefix: "ga",
      modalTitleKey: "gaModalTitle", mapCenter: [32.7, -83.4], mapZoom: 7,
    },
  };

  window.initProgramActivity = function initProgramActivity(api) {
    const {
      t, getLang,
      clearExclusiveTools,
      closeMetricsDrawer, isDrawerOpen,
      closeReport, isReportOpen,
    } = api;

    const dataCache = {};       // abbr -> payload once loaded
    const loadPromises = {};    // abbr -> in-flight/settled fetch promise
    const loadFailedSet = new Set();
    let currentAbbr = null;
    let isOpen = false;
    let bubbleMap = null;       // Leaflet instance, created once and reused
    let bubbleMapAbbr = null;   // which state's data the reused instance was last framed for

    const COLOR_GROUP_HEX = { bond: "#38bdf8", credit: "#4ade80", trust: "#a78bfa", capital: "#fb923c" };
    // Per-category icon/color used to originally be a flat lookup keyed on
    // IL's own 4 category keys (multifamily_new_preserve/homebuyer_loans/
    // repair_counseling/covid_emergency), so every other state's categories
    // silently fell back to a generic "📊"/blue stacked-bar regardless of
    // what the category was actually about. Kept those 4 explicit entries
    // (exact, curated) but added a keyword-based fallback below so any
    // state's category key -- past or future -- gets a semantically
    // reasonable icon/color instead of the generic default. Checked in
    // order; first matching bucket wins.
    const CATEGORY_ICON_OVERRIDE = {
      multifamily_new_preserve: "🏗️",
      homebuyer_loans: "🏡",
      repair_counseling: "🔧",
      covid_emergency: "🆘",
    };
    const CATEGORY_HEX_OVERRIDE = {
      homebuyer_loans: "#22c55e",
      repair_counseling: "#f59e0b",
      covid_emergency: "#f43f5e",
    };
    const CATEGORY_KEYWORD_BUCKETS = [
      { re: /homeown|homebuyer|single_family|downpayment|sonyma|covenant/, icon: "🏡", hex: "#22c55e" },
      { re: /repair|renew|rehab|counsel/, icon: "🔧", hex: "#f59e0b" },
      { re: /covid|emergency|foreclosure|homeless/, icon: "🆘", hex: "#f43f5e" },
      { re: /weatheriz|energy|liheap/, icon: "⚡", hex: "#eab308" },
      { re: /lihtc|tax_credit|credit_award|hmmf|lmir|legislative_loan|mortgage/, icon: "🏦", hex: "#4ade80" },
      { re: /trust_fund|phare|grant|reach_virginia|federal_assistance|home_program/, icon: "💰", hex: "#fb923c" },
      // Ongoing rental assistance/vouchers/public-housing operating support
      // -- checked before the general multifamily/rental bucket below so it
      // doesn't get lumped in with new-construction categories just because
      // both keys happen to contain "rental" (e.g. TX's own
      // multifamily_rental_production vs. rental_assistance_community_affairs).
      { re: /rental_assistance|community_affairs|voucher|public_housing|section_?8|tbra|housing_stability/, icon: "🏘️", hex: "#a78bfa" },
      { re: /multifamily|rental|units_completed|placed_in_service|build_for|neighborhood|housing_solutions/, icon: "🏗️", hex: "#38bdf8" },
    ];
    function categoryIcon(key) {
      if (CATEGORY_ICON_OVERRIDE[key]) return CATEGORY_ICON_OVERRIDE[key];
      const hit = CATEGORY_KEYWORD_BUCKETS.find(b => b.re.test(key));
      return hit ? hit.icon : "📊";
    }
    function categoryBaseHex(key) {
      if (CATEGORY_HEX_OVERRIDE[key]) return CATEGORY_HEX_OVERRIDE[key];
      const hit = CATEGORY_KEYWORD_BUCKETS.find(b => b.re.test(key));
      return hit ? hit.hex : "#38bdf8";
    }
    const UNIT_ICON = { units: "🏠", households: "🧑" };
    // GASB fund-type classification, sourced from each state's own FY2025
    // ACFR (fund descriptions in Note 2 + combining schedules), not from the
    // program-activity report itself -- see the matching
    // build_{abbr}_program_activity.py module docstring for methodology.
    const FUND_TYPE_ICON = {
      governmental: "🏛️", proprietary: "🏢", off_balance_sheet: "🧾", mixed: "🔀",
    };
    const FUND_TYPE_LABEL_KEY = {
      governmental: "ilFundGovernmental", proprietary: "ilFundProprietary",
      off_balance_sheet: "ilFundOffBalance", mixed: "ilFundMixed",
    };

    function $(id) { return document.getElementById(id); }

    function data() { return dataCache[currentAbbr] || null; }
    function prefix() { return (STATE_CONFIGS[currentAbbr] || {}).prefix || ""; }

    function fundTypeBadge(sp) {
      if (!sp.fund_type) return "";
      const icon = FUND_TYPE_ICON[sp.fund_type] || "";
      let tip = t(FUND_TYPE_LABEL_KEY[sp.fund_type] || "");
      if (sp.fund_name) tip += ` — ${t("ilFundNameLabel")}: ${sp.fund_name}`;
      return `<span class="il-fund-flag" tabindex="0" title="${escapeHtml(tip)}">${icon}</span>`;
    }

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

    function loadData(abbr) {
      if (loadPromises[abbr]) return loadPromises[abbr];
      const config = STATE_CONFIGS[abbr];
      loadPromises[abbr] = fetch(config.file)
        .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
        .then(json => { dataCache[abbr] = json[abbr]; })
        .catch(err => {
          loadFailedSet.add(abbr);
          console.error(`${config.file} load failed:`, err);
        });
      return loadPromises[abbr];
    }

    // fy2026 shape: { value, amount, closed, note_key }. `value` (units/
    // households) and `amount` ($) are disclosed independently by the
    // agency -- many subprograms give a dollar figure with no unit count, or
    // vice versa -- so both are shown whenever present, and only a program
    // with neither gets the neutral "pending" badge.
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
      const projects = (data().projects || []).filter(p =>
        p.funding_sources.includes(subKey) && p.funding_sources.length > 1);
      const others = new Set();
      projects.forEach(p => p.funding_sources.forEach(s => { if (s !== subKey) others.add(s); }));
      return [...others];
    }

    function renderCategoryCard(cat) {
      const px = prefix();
      const uIcon = UNIT_ICON[cat.unit_type] || "";
      const title = escapeHtml(t(`${px}Cat_${cat.key}`));
      const badge = fy2026Badge(cat.fy2026, cat.unit_type);
      const amountsHtml = (cat.fy2025_amounts || [])
        .map(a => `<span class="il-amount-chip">${escapeHtml(t(a.label_key))}: ${fmtUsd(a.amount)}</span>`)
        .join("");
      let subHtml;
      if (cat.additive) {
        const base = categoryBaseHex(cat.key);
        const total = cat.subprograms.reduce((s, sp) => s + sp.fy2025_units, 0) || 1;
        let acc = 0;
        const n = cat.subprograms.length;
        const segs = cat.subprograms.map((sp, i) => {
          const pct = (sp.fy2025_units / total) * 100;
          const left = (acc / total) * 100;
          acc += sp.fy2025_units;
          const f = n > 1 ? 1 - (i / (n - 1)) * 0.55 : 1;
          const label = `${escapeHtml(t(`${px}Sub_${sp.key}`))}: ${fmtNum(sp.fy2025_units)} ${uIcon} · ${fmtUsd(sp.fy2025_amount)}`;
          return `<span class="il-seg" title="${label}" style="left:${left}%;width:${pct}%;background:${shade(base, f)}"></span>`;
        }).join("");
        const legend = cat.subprograms.map((sp, i) => {
          const f = n > 1 ? 1 - (i / (n - 1)) * 0.55 : 1;
          const amt = fmtUsd(sp.fy2025_amount);
          return `<span class="il-sub-chip"><span class="il-dot" style="background:${shade(base, f)}"></span>${escapeHtml(t(`${px}Sub_${sp.key}`))} ${fmtNum(sp.fy2025_units)}${amt ? " · " + amt : ""}${fundTypeBadge(sp)}</span>`;
        }).join("");
        subHtml = `<div class="il-stack-track">${segs}</div><div class="il-sub-legend">${legend}</div>`;
      } else {
        const chips = cat.subprograms.map(sp => {
          const overlapWith = overlapSourcesFor(sp.key);
          let warn = "";
          if (overlapWith.length) {
            const names = listJoin(overlapWith.map(k => t(`${px}Sub_${k}`)));
            const tip = t("ilOverlapTooltip").replace("{others}", names);
            warn = `<span class="il-overlap-flag" tabindex="0" title="${escapeHtml(tip)}">⚠</span>`;
          }
          const hex = COLOR_GROUP_HEX[sp.color_group] || "#94a3b8";
          const amt = fmtUsd(sp.fy2025_amount);
          return `<span class="il-ref-chip"><span class="il-dot" style="background:${hex}"></span>${escapeHtml(t(`${px}Sub_${sp.key}`))} ${fmtNum(sp.fy2025_units)} ${uIcon}${amt ? " · " + amt : ""}${fundTypeBadge(sp)}${warn}</span>`;
        }).join("");
        subHtml = `<div class="il-chip-row">${chips}</div><p class="il-chip-note">${escapeHtml(t("ilNotAdditiveNote"))}</p>`;
      }
      return `<div class="il-kpi-card">
        <div class="il-kpi-head"><span class="il-kpi-icon">${categoryIcon(cat.key)}</span><span class="il-kpi-title">${title}</span></div>
        <div class="il-kpi-value">${fmtNum(cat.fy2025_actual)} <span class="il-unit-icon">${uIcon}</span></div>
        ${amountsHtml ? `<div class="il-amount-row">${amountsHtml}</div>` : ""}
        <div class="il-kpi-fy26">${badge}</div>
        ${subHtml}
      </div>`;
    }

    function primaryColorGroup(project) {
      // Project funding_sources keys are subprogram keys from whichever
      // category the bubble map represents (multifamily, by convention) --
      // that category's own `key` string varies by state (IL uses
      // "multifamily_new_preserve", PA uses "multifamily_awards", etc.), so
      // search all categories' subprograms rather than hardcoding one.
      for (const cat of data().categories) {
        const sp = (cat.subprograms || []).find(s => s.key === project.funding_sources[0]);
        if (sp) return sp.color_group;
      }
      return "capital";
    }

    function renderMap() {
      const wrap = $("il-bubble-map");
      const config = STATE_CONFIGS[currentAbbr];
      if (!wrap || !config || typeof L === "undefined") return;
      // renderBody() rebuilds #il-activity-body's innerHTML on every call
      // (language switch, reopen, switching to a different state, etc.),
      // which creates a brand-new #il-bubble-map element each time. A
      // previously-created Leaflet map instance still points at the old,
      // now-detached element, so it must be torn down and recreated against
      // the current one -- otherwise the map renders into a disconnected
      // node and appears blank.
      if (bubbleMap && (bubbleMap.getContainer() !== wrap || bubbleMapAbbr !== currentAbbr)) {
        bubbleMap.remove();
        bubbleMap = null;
      }
      if (!bubbleMap) {
        bubbleMap = L.map(wrap, { attributionControl: false, zoomSnap: 0.25, zoomDelta: 0.5 })
          .setView(config.mapCenter, config.mapZoom);
        L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
          subdomains: "abcd", maxZoom: 19,
        }).addTo(bubbleMap);
        bubbleMapAbbr = currentAbbr;
      }
      bubbleMap.eachLayer(layer => { if (layer instanceof L.CircleMarker) bubbleMap.removeLayer(layer); });
      const px = prefix();
      const projects = (data().projects || []).filter(p => p.lat != null && p.lon != null);
      projects.forEach(p => {
        const group = primaryColorGroup(p);
        const color = COLOR_GROUP_HEX[group] || "#94a3b8";
        const radius = 4 + Math.sqrt(Math.max(p.units, 1)) * 1.1;
        const marker = L.circleMarker([p.lat, p.lon], {
          radius, color: "#0f172a", weight: 1, fillColor: color, fillOpacity: 0.8,
        }).addTo(bubbleMap);
        const totalAmt = fmtUsd(p.total_amount);
        let tip = `<div class="il-tooltip"><strong>${escapeHtml(p.name)}</strong><br>${escapeHtml(p.city)}, ${currentAbbr} — ${fmtNum(p.units)} ${UNIT_ICON.units}`;
        if (totalAmt) tip += ` — ${totalAmt}`;
        const sourceLines = p.funding_sources.map(s => {
          const amt = fmtUsd((p.source_amounts || {})[s]);
          return `${escapeHtml(t(`${px}Sub_${s}`))}${amt ? ": " + amt : ""}`;
        }).join("<br>");
        tip += `<br>${sourceLines}`;
        if (p.overlaps) {
          const others = listJoin(p.funding_sources.map(s => t(`${px}Sub_${s}`)));
          tip += `<span class="il-tt-overlap">${escapeHtml(t("ilProjectOverlapNote").replace("{sources}", others))}</span>`;
        }
        tip += `</div>`;
        marker.bindTooltip(tip, { sticky: true });
      });
      setTimeout(() => bubbleMap.invalidateSize({ animate: false }), 50);
    }

    function renderBody() {
      const body = $("il-activity-body");
      const d = data();
      if (!body) return;
      if (loadFailedSet.has(currentAbbr) || !d) {
        body.innerHTML = `<p class="il-error">${escapeHtml(t("ilLoadError"))}</p>`;
        return;
      }
      const cards = d.categories.map(renderCategoryCard).join("");
      const mfProjects = (d.projects || []).length;
      const mapLegend = `<div class="il-map-legend">
        <span><span class="il-dot" style="background:${COLOR_GROUP_HEX.bond}"></span>${escapeHtml(t("ilMapLegendBond"))}</span>
        <span><span class="il-dot" style="background:${COLOR_GROUP_HEX.credit}"></span>${escapeHtml(t("ilMapLegendCredit"))}</span>
        <span><span class="il-dot" style="background:${COLOR_GROUP_HEX.trust}"></span>${escapeHtml(t("ilMapLegendTrust"))}</span>
        <span><span class="il-dot" style="background:${COLOR_GROUP_HEX.capital}"></span>${escapeHtml(t("ilMapLegendCapital"))}</span>
        <span>${escapeHtml(t("ilMapSizeLegend"))}</span>
        <span>${escapeHtml(t("ilMapCount").replace("{n}", String(mfProjects)))}</span>
      </div>`;
      const retrieved = d.retrieved || "";
      const sourceNote = escapeHtml(t("ilSourceNote"))
        .replace("{agency}", escapeHtml(d.hfa_name || d.hfa_abbr || ""))
        .replace("{title}", escapeHtml(d.source_title || ""))
        .replace("{fy}", escapeHtml(d.fiscal_year || ""))
        .replace("{retrieved}", escapeHtml(retrieved));
      const fundLegend = `<div class="il-legend-units">
        <span>${escapeHtml(t("ilFundLegend"))}</span>
        <span>${FUND_TYPE_ICON.governmental} ${escapeHtml(t("ilFundGovernmental"))}</span>
        <span>${FUND_TYPE_ICON.proprietary} ${escapeHtml(t("ilFundProprietary"))}</span>
        <span>${FUND_TYPE_ICON.off_balance_sheet} ${escapeHtml(t("ilFundOffBalance"))}</span>
        <span>${FUND_TYPE_ICON.mixed} ${escapeHtml(t("ilFundMixed"))}</span>
      </div>`;
      body.innerHTML = `
        <div class="il-kpi-grid">${cards}</div>
        <div class="il-legend-units"><span>${escapeHtml(t("ilUnitsLegend"))}</span><span>${escapeHtml(t("ilHouseholdsLegend"))}</span></div>
        ${fundLegend}
        <div class="il-section-title">${escapeHtml(t("ilMapTitle").replace("{fy}", d.fiscal_year || ""))}</div>
        <div class="il-map-wrap"><div id="il-bubble-map"></div>${mapLegend}</div>
        <p class="il-footnote">${sourceNote}<br><a href="${d.source_url}" target="_blank" rel="noopener noreferrer">${escapeHtml(d.source_file || d.source_url)}</a></p>
      `;
      renderMap();
    }

    function openModal(abbr) {
      const config = STATE_CONFIGS[abbr];
      if (!config) return;
      if (isReportOpen?.()) closeReport();
      if (isDrawerOpen?.()) closeMetricsDrawer();
      clearExclusiveTools?.({ except: "program-activity" });
      const modal = $("il-activity-modal");
      if (!modal) return;
      currentAbbr = abbr;
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
      isOpen = true;
      $("il-activity-title").textContent = t(config.modalTitleKey);
      const body = $("il-activity-body");
      if (body) body.innerHTML = "";
      loadData(abbr).then(() => { if (currentAbbr === abbr) renderBody(); });
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
      if (isOpen && currentAbbr) {
        $("il-activity-title").textContent = t(STATE_CONFIGS[currentAbbr].modalTitleKey);
        if (data()) renderBody();
      }
    }

    function isAvailable(abbr) { return !!STATE_CONFIGS[abbr]; }

    document.addEventListener("click", e => {
      const btn = e.target.closest("#btn-il-activity");
      if (btn) openModal(btn.dataset.abbr);
    });
    $("btn-il-activity-close")?.addEventListener("click", closeModal);
    $("il-activity-modal")?.addEventListener("click", e => {
      if (e.target.id === "il-activity-modal") closeModal();
    });

    return { deactivate, onEscape, renderLabels, isAvailable };
  };
})();
