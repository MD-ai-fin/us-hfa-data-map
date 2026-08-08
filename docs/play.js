/**
 * Play modes: My State, Spot outliers, Guess the state.
 * window.initHfaPlay(api) → { renderPlayLabels, onMapClick, onEscape }
 */
(function () {
  window.initHfaPlay = function initHfaPlay(api) {
    const {
      t, tMetric, getLang, getFocusedState, setFocusedState,
      getStateData, stateDisplayName, metricValueForState, fmt,
      rankedStates, setPrimaryMetricOnly,
      flyToState, clearHighlights, highlightAbbrs, refreshMap,
      applyHighlightClasses, buildShareUrl, syncUrlFromState,
      map, getDataset,
      closeComparePanel, setCompareMode, closeMetricsDrawer,
      isDrawerOpen, closeReport, isReportOpen,
    } = api;

    let playMode = null; // null | quiz
    let anomalyType = null;
    let quiz = { answer: null, metric: null, rank: null, score: 0, rounds: 0, awaiting: false, lastGuess: null };
    const ANOMALY_ORDER = ["growth_small", "assets_low_capita"];

    function $(id) { return document.getElementById(id); }

    function openPlayModal(title, { clearBackdrop = false, quizLayout = false } = {}) {
      if (isReportOpen()) closeReport();
      closeComparePanel();
      setCompareMode(false);
      if (isDrawerOpen()) closeMetricsDrawer();
      $("play-title").textContent = title;
      const modal = $("play-modal");
      modal.classList.toggle("map-clear", Boolean(clearBackdrop) && !quizLayout);
      modal.classList.toggle("quiz-open", Boolean(quizLayout));
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
    }

    function closePlayModal() {
      const modal = $("play-modal");
      modal.classList.remove("open", "map-clear", "quiz-open");
      modal.setAttribute("aria-hidden", "true");
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

    function exitQuiz() {
      playMode = null;
      quiz.awaiting = false;
      $("btn-quiz")?.classList.remove("active");
      document.body.classList.remove("quiz-mode");
    }

    function stopAnomaly() {
      anomalyType = null;
      $("btn-anomaly")?.classList.remove("active");
      clearHighlights();
      refreshMap();
    }

    /* —— My State —— */
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
        setFocusedState(e.target.value);
        renderMyState(e.target.value);
      };
      $("btn-my-state-goto").onclick = () => {
        closePlayModal();
        flyToState(abbr);
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
      exitQuiz();
      const abbr = getFocusedState() || "CA";
      openPlayModal(t("myStateTitle"), { clearBackdrop: true });
      renderMyState(abbr);
    }

    /* —— Anomalies —— */
    function applyAnomaly(type) {
      exitQuiz();
      anomalyType = type;
      const rows = findAnomalies(type);
      const metric = type === "growth_small" ? "net_position_growth_pct" : "total_assets";
      setPrimaryMetricOnly(metric);
      highlightAbbrs.clear();
      rows.forEach(r => highlightAbbrs.add(r.state));
      refreshMap();
      applyHighlightClasses(true);
      $("btn-anomaly").classList.add("active");
      openPlayModal(t("anomalyTitle"), { clearBackdrop: true });
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
      $("play-body").querySelectorAll("li[data-state]").forEach(li => {
        li.onclick = () => flyToState(li.dataset.state);
      });
      $("btn-anomaly-next").onclick = () => {
        const i = ANOMALY_ORDER.indexOf(type);
        applyAnomaly(ANOMALY_ORDER[(i + 1) % ANOMALY_ORDER.length]);
      };
      $("btn-anomaly-clear").onclick = () => {
        stopAnomaly();
        closePlayModal();
      };
    }

    function toggleAnomaly() {
      if (anomalyType) {
        const i = ANOMALY_ORDER.indexOf(anomalyType);
        applyAnomaly(ANOMALY_ORDER[(i + 1) % ANOMALY_ORDER.length]);
      } else {
        applyAnomaly(ANOMALY_ORDER[0]);
      }
    }

    /* —— Quiz —— */
    function renderQuiz() {
      const rec = getStateData(quiz.answer);
      const name = stateDisplayName(rec, quiz.answer);
      let result = "";
      if (quiz.lastGuess) {
        const ok = quiz.lastGuess === quiz.answer;
        result = `<p class="quiz-result ${ok ? "ok" : "bad"}">${ok
          ? t("quizCorrect").replace("{name}", name).replace("{abbr}", quiz.answer)
          : t("quizWrong")
            .replace("{guess}", quiz.lastGuess)
            .replace("{name}", name)
            .replace("{abbr}", quiz.answer)}</p>`;
      }
      $("play-body").innerHTML = `
        <p class="compare-hint">${t("quizHint")}</p>
        <p class="quiz-prompt">${t("quizPrompt")
          .replace("{metric}", tMetric(quiz.metric))
          .replace("{rank}", String(quiz.rank))}</p>
        <p class="quiz-score">${t("quizScore")
          .replace("{score}", String(quiz.score))
          .replace("{rounds}", String(quiz.rounds))}</p>
        ${result}
        <div class="play-actions">
          ${quiz.lastGuess ? `<button type="button" id="btn-quiz-next">${t("quizNext")}</button>` : ""}
          <button type="button" id="btn-quiz-exit">${t("quizExit")}</button>
        </div>`;
      if ($("btn-quiz-next")) $("btn-quiz-next").onclick = nextQuizRound;
      $("btn-quiz-exit").onclick = () => {
        exitQuiz();
        closePlayModal();
        map.closePopup();
        if (!anomalyType) {
          clearHighlights();
          refreshMap();
        }
      };
    }

    function nextQuizRound() {
      const metrics = ["net_position", "net_position_growth_pct", "net_position_per_capita", "total_assets"];
      const mkey = metrics[Math.floor(Math.random() * metrics.length)];
      const ranked = rankedStates(mkey, 9999);
      if (ranked.length < 5) {
        $("play-body").innerHTML = `<p class="compare-hint">${t("playNoData")}</p>`;
        return;
      }
      const idx = Math.floor(Math.random() * Math.min(12, ranked.length));
      quiz.answer = ranked[idx].state;
      quiz.metric = mkey;
      quiz.rank = idx + 1;
      quiz.lastGuess = null;
      quiz.awaiting = true;
      setPrimaryMetricOnly(mkey);
      highlightAbbrs.clear();
      refreshMap();
      renderQuiz();
    }

    function startQuiz() {
      stopAnomaly();
      exitQuiz();
      playMode = "quiz";
      quiz.score = 0;
      quiz.rounds = 0;
      quiz.lastGuess = null;
      document.body.classList.add("quiz-mode");
      $("btn-quiz").classList.add("active");
      openPlayModal(t("quizTitle"), { quizLayout: true });
      nextQuizRound();
    }

    function handleQuizGuess(abbr) {
      if (playMode !== "quiz" || !quiz.awaiting) return false;
      quiz.awaiting = false;
      quiz.rounds += 1;
      quiz.lastGuess = abbr;
      if (abbr === quiz.answer) quiz.score += 1;
      highlightAbbrs.clear();
      highlightAbbrs.add(quiz.answer);
      if (abbr !== quiz.answer) highlightAbbrs.add(abbr);
      refreshMap();
      applyHighlightClasses(true);
      flyToState(quiz.answer);
      renderQuiz();
      openPlayModal(t("quizTitle"), { quizLayout: true });
      return true;
    }

    function renderPlayLabels() {
      $("btn-my-state").textContent = t("myStateBtn");
      $("btn-anomaly").textContent = t("anomalyBtn");
      $("btn-quiz").textContent = t("quizBtn");
      $("btn-play-close").setAttribute("aria-label", t("closePlay"));
    }

    function onMapClick(abbr) {
      return handleQuizGuess(abbr);
    }

    function onEscape() {
      if ($("play-modal").classList.contains("open")) {
        if (playMode === "quiz") {
          exitQuiz();
          if (!anomalyType) {
            clearHighlights();
            refreshMap();
          }
        }
        closePlayModal();
        return true;
      }
      return false;
    }

    $("btn-my-state").onclick = openMyState;
    $("btn-anomaly").onclick = toggleAnomaly;
    $("btn-quiz").onclick = startQuiz;
    $("btn-play-close").onclick = () => {
      if (playMode === "quiz") {
        exitQuiz();
        if (!anomalyType) {
          clearHighlights();
          refreshMap();
        }
      }
      closePlayModal();
    };
    $("play-modal").onclick = e => {
      if (e.target.id === "play-modal" && playMode !== "quiz") closePlayModal();
    };

    renderPlayLabels();
    return { renderPlayLabels, onMapClick, onEscape };
  };
})();
