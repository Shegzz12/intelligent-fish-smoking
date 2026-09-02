(() => {
  const translations = {
    en: {
      overview: "Overview",
      history: "Smoking history",
      settings: "System settings",
      control: "Control center / 01",
      smokingOverview: "Smoking overview",
      intelligent: "Intelligent control",
      controlMenu: "Control menu",
      hardware: "Hardware link",
      liveBackend: "Live backend connected",
      connecting: "Connecting to backend…",
      offline: "Backend unreachable",
      progress: "Session in progress",
      ready: "System ready",
      paused: "Session paused",
      stopped: "Stopped",
      hero: "The smoker at a glance.",
      intro: "Monitor your chamber, follow model predictions, and keep every batch traceable.",
      start: "Start session",
      current: "Current session",
      noSession: "No active session",
      startBatch: "Start a batch to begin live monitoring.",
      remaining: "Time remaining",
      readyWhen: "Ready when you are",
      autoStop: "Auto-stop enabled",
      percentComplete: "{n}% complete",
      awaitingPrediction: "Waiting for ESP32 sensors…",
      hoursMins: "{h}hrs {m} mins",
      hoursOnly: "{h}hrs",
      minsOnly: "{m} mins",
      connected: "ESP32-01 connected",
      lastSync: "Last sync {time}",
      model: "Model estimate",
      duration: "total duration",
      telemetry: "Live telemetry",
      conditions: "Chamber conditions",
      updates: "Updates every 3 sec",
      updatesLive: "Updates when packets arrive",
      waitingTelemetry: "Waiting for live samples…",
      now: "Now",
      health: "System health",
      nominal: "All systems nominal",
      awaitingSensors: "Awaiting sensors",
      traceability: "Traceability",
      viewAll: "View all",
      newBatch: "New batch",
      startTitle: "Start a smoking session",
      formIntro: "Enter the essentials. The model will estimate the duration from live sensor data.",
      fishType: "Fish type (required)",
      fishWeight: "Fish weight (kg)",
      weightHint: "Leave weight blank to capture it from the load cell.",
      begin: "Begin session",
      close: "Close form",
      chamber: "Chamber temp",
      humidity: "Humidity",
      gas: "Gas sensor",
      heater: "Heater reading",
      fishWeightShort: "Fish weight",
      target: "Target 65–72°C",
      within: "Within range",
      air: "Air quality",
      heaterOn: "Heater on",
      heaterOff: "Heater off",
      load: "Load cell active",
      awaiting: "Awaiting batch",
      prediction: "Prediction engine",
      calculated: "Calculated from temperature, humidity, gas, heater surface temperature, and fish weight.",
      fish: "Fish type",
      completed: "Completed",
      result: "Result",
      online: "Online",
      waiting: "Waiting",
      tempProbe: "Temperature probe",
      humiditySensor: "Humidity sensor",
      gasSensor: "Gas sensor",
      loadCell: "Load cell",
      heaterRelay: "Heater relay",
      durationCol: "Duration",
      emptyHistory: "No completed sessions yet.",
      historyIntro: "Only sessions started and stopped from this server are listed.",
      settingsTitle: "Control appearance and language.",
      settingsIntro: "Theme and language stay on this device. Session and sensor values always come from the live backend.",
      appearance: "Appearance",
      toggleTheme: "Toggle theme",
      language: "Language",
      languageHint: "English, Yorùbá, Igbo, Hausa",
      lightMode: "Light mode",
      darkMode: "Dark mode",
      kgBatch: "{n} kg batch · {model}",
      moreLive: "Live session {id}",
      moreIdle: "No live values until ESP32 packets arrive",
      awaitingHardware: "Waiting for ESP32",
      noTelemetryYet: "No telemetry yet",
      progressLabel: "Progress",
      stopSession: "Stop session",
    },
    yo: {
      overview: "Àkótán",
      history: "Ìtàn sìgá ẹja",
      settings: "Ètò ẹ̀rọ",
      control: "Àárín ìṣàkóso / 01",
      smokingOverview: "Àkótán sìgá ẹja",
      intelligent: "Ìṣàkóso ọlọ́gbọ́n",
      controlMenu: "Akojọ ìṣàkóso",
      hardware: "Ìjápọ̀ ohun èlò",
      connected: "ESP32 ti sopọ̀",
      lastSync: "Ìwífún tó kẹ́yìn {time}",
      liveBackend: "Backend láàyè ti sopọ̀",
      connecting: "Ń sopọ̀ mọ́ backend…",
      offline: "Backend kò ṣiṣẹ́",
      progress: "Àkókò ń lọ",
      ready: "Ètò ti ṣetán",
      paused: "Àkókò dúró díẹ̀",
      stopped: "Dúró",
      hero: "Ẹrọ sìgá ẹja ní ojú kan.",
      intro: "Bójútó iyẹ̀wu rẹ, tẹ̀lé àsọtẹ́lẹ̀, kí o sì tọ́jú gbogbo ìpele.",
      start: "Bẹ̀rẹ̀ àkókò",
      current: "Àkókò lọ́wọ́lọ́wọ́",
      noSession: "Kò sí àkókò lọ́wọ́lọ́wọ́",
      startBatch: "Bẹ̀rẹ̀ ìpele kan láti bẹ̀rẹ̀ ìmúdójúìwọ̀n.",
      remaining: "Àkókò tó kù",
      readyWhen: "A ti ṣetán",
      autoStop: "Dúró fúnra rẹ̀",
      percentComplete: "{n}% ti parí",
      awaitingPrediction: "Ń dúró de sensọ ESP32…",
      hoursMins: "wákàtí {h} ìṣẹ́jú {m}",
      hoursOnly: "wákàtí {h}",
      minsOnly: "ìṣẹ́jú {m}",
      model: "Àsọtẹ́lẹ̀ àwòṣe",
      duration: "àkókò lápapọ̀",
      telemetry: "Ìwífún láàyè",
      conditions: "Àwọn ipò iyẹ̀wu",
      updates: "Ó ń yí padà ní ìṣẹ́jú 3",
      updatesLive: "Ó ń yí padà nígbà tí ìwífún bá dé",
      waitingTelemetry: "Ń dúró de àwọn ìwọ̀n láàyè…",
      now: "Nísinsin yìí",
      health: "Ìlera ètò",
      nominal: "Gbogbo ètò dára",
      awaitingSensors: "Ń dúró de sensọ",
      traceability: "Títọ́pa",
      viewAll: "Wo gbogbo rẹ̀",
      newBatch: "Ìpele tuntun",
      startTitle: "Bẹ̀rẹ̀ àkókò sìgá ẹja",
      formIntro: "Tẹ àwọn ohun pàtàkì sílẹ̀. Àwòṣe yóò sọ àkókò di mímọ̀.",
      fishType: "Irú ẹja",
      fishWeight: "Ìwọ̀n ẹja (kg)",
      weightHint: "Fi ìwọ̀n sílẹ̀ láti gba àkọsílẹ̀ láti sẹ́ẹ̀lì ìwọ̀n.",
      begin: "Bẹ̀rẹ̀ àkókò",
      close: "Pa fọ́ọ̀mù",
      chamber: "Ìgbóná iyẹ̀wu",
      humidity: "Ọ̀rinrin",
      gas: "Sensọ gáàsì",
      heater: "Ìgbóná amúná",
      fishWeightShort: "Ìwọ̀n ẹja",
      target: "Àfojúsùn 65–72°C",
      within: "Ó wà ní ààlà",
      air: "Didara afẹ́fẹ́",
      heaterOn: "Amúná wà lórí",
      heaterOff: "Amúná wà ní pipa",
      load: "Sẹ́ẹ̀lì ìwọ̀n ń ṣiṣẹ́",
      awaiting: "Ń dúró de ìpele",
      prediction: "Ẹ̀rọ àsọtẹ́lẹ̀",
      calculated: "A ṣe ìṣirò rẹ̀ láti inú ìgbóná, ọ̀rinrin, gáàsì, amúná àti ìwọ̀n ẹja.",
      fish: "Irú ẹja",
      completed: "Parí",
      result: "Àbájáde",
      online: "Lórí ayélujára",
      waiting: "Ń dúró",
      tempProbe: "Sensọ ìgbóná",
      humiditySensor: "Sensọ ọ̀rinrin",
      gasSensor: "Sensọ gáàsì",
      loadCell: "Sẹ́ẹ̀lì ìwọ̀n",
      heaterRelay: "Rilé amúná",
      durationCol: "Àkókò",
      emptyHistory: "Kò sí àkókò tó ti parí síbẹ̀.",
      historyIntro: "Àwọn àkókò tí a bẹ̀rẹ̀ tí a sì dá dúró láti inú sèfá yìí nìkan ni a ṣe àkọsílẹ̀.",
      settingsTitle: "Ṣàkóso ìrísí àti èdè.",
      settingsIntro: "Àwọ̀ àti èdè wà lórí ẹ̀rọ yìí. Àwọn ìwọ̀n sensọ wá láti backend láàyè.",
      appearance: "Ìrísí",
      toggleTheme: "Yí àwọ̀ padà",
      language: "Èdè",
      languageHint: "English, Yorùbá, Igbo, Hausa",
      lightMode: "Ìrísí ìmọ́lẹ̀",
      darkMode: "Ìrísí òkùnkùn",
      kgBatch: "Ìpele {n} kg · {model}",
      moreLive: "Àkókò láàyè {id}",
      moreIdle: "Kò sí ìwọ̀n títí ìwífún ESP32 yóò fi dé",
      awaitingHardware: "Ń dúró de ESP32",
      noTelemetryYet: "Kò sí ìwífún síbẹ̀",
      progressLabel: "Ìlọsíwájú",
      stopSession: "Dá àkókò dúró",
    },
    ig: {
      overview: "Nchịkọta",
      history: "Akụkọ ịkwọ azụ",
      settings: "Ntọala sistemụ",
      control: "Ebe njikwa / 01",
      smokingOverview: "Nchịkọta ịkwọ azụ",
      intelligent: "Njikwa amamihe",
      controlMenu: "Nchịkọta njikwa",
      hardware: "Njikọ ngwa",
      connected: "ESP32 ejikọtala",
      lastSync: "Ngwugwu ikpeazụ {time}",
      liveBackend: "Backend dị ndụ ejikọtala",
      connecting: "Na-ejikọta na backend…",
      offline: "Backend adịghị",
      progress: "Oge na-aga",
      ready: "Sistemụ dị njikere",
      paused: "A kwụsịtụrụ oge",
      stopped: "Kwụsịrị",
      hero: "Onye na-ese azụ n’otu anya.",
      intro: "Nyochaa ọnụ ụlọ gị, soro amụma nlereanya, ma debe ndekọ nke batch ọ bụla.",
      start: "Malite oge",
      current: "Oge ugbu a",
      noSession: "Enweghị oge na-aga",
      startBatch: "Malite batch iji malite nlekọta ndụ.",
      remaining: "Oge fọdụrụ",
      readyWhen: "Ọ dị njikere",
      autoStop: "Ọ ga-akwụsị onwe ya",
      percentComplete: "{n}% ezuola",
      awaitingPrediction: "Na-eche sensọ ESP32…",
      hoursMins: "{h}hrs {m} mins",
      hoursOnly: "{h}hrs",
      minsOnly: "{m} mins",
      model: "Amụma nlereanya",
      duration: "ngụkọta oge",
      telemetry: "Data ndụ",
      conditions: "Ọnọdụ ọnụ ụlọ",
      updates: "Mmelite kwa sekọnd 3",
      updatesLive: "Ọ na-emelite mgbe ngwugwu rutere",
      waitingTelemetry: "Na-eche ihe nlele ndụ…",
      now: "Ugbu a",
      health: "Ahụike sistemụ",
      nominal: "Sistemụ niile dị mma",
      awaitingSensors: "Na-eche sensọ",
      traceability: "Nsochi ndekọ",
      viewAll: "Lee niile",
      newBatch: "Batch ọhụrụ",
      startTitle: "Malite oge ịkwọ azụ",
      formIntro: "Tinye ihe ndị dị mkpa. Nlereanya ga-atụ oge site na data sensọ.",
      fishType: "Ụdị azụ",
      fishWeight: "Ibu azụ (kg)",
      weightHint: "Hapụ ibu ka load cell jiri were ya.",
      begin: "Malite oge",
      close: "Mechie ụdị",
      chamber: "Okpomọkụ ọnụ ụlọ",
      humidity: "Mmiri ikuku",
      gas: "Sensọ gas",
      heater: "Ọgụgụ ọkụ",
      fishWeightShort: "Ibu azụ",
      target: "Ebumnuche 65–72°C",
      within: "Ọ dị n’ókè",
      air: "Ogo ikuku",
      heaterOn: "Igwe ọkụ dị ọkụ",
      heaterOff: "Igwe ọkụ kwụsịrị",
      load: "Load cell na-arụ ọrụ",
      awaiting: "Na-eche batch",
      prediction: "Igwe amụma",
      calculated: "A gbakọrọ ya site na okpomọkụ, mmiri ikuku, gas, ọkụ na ibu azụ.",
      fish: "Ụdị azụ",
      completed: "Emechara",
      result: "Nsonaazụ",
      online: "Ọ dị n’ịntanetị",
      waiting: "Na-eche",
      tempProbe: "Sensọ okpomọkụ",
      humiditySensor: "Sensọ mmiri ikuku",
      gasSensor: "Sensọ gas",
      loadCell: "Load cell",
      heaterRelay: "Relay ọkụ",
      durationCol: "Oge",
      emptyHistory: "O nwebeghị oge emechara.",
      historyIntro: "Naanị oge e malitere ma kwụsị site na sava a ka edepụtara.",
      settingsTitle: "Jikwaa ọdịdị na asụsụ.",
      settingsIntro: "Isiokwu na asụsụ nọ n’ngwaọrụ a. Ụkpụrụ sensọ na-abịa site na backend dị ndụ.",
      appearance: "Ọdịdị",
      toggleTheme: "Gbanwee isiokwu",
      language: "Asụsụ",
      languageHint: "English, Yorùbá, Igbo, Hausa",
      lightMode: "Ọdịdị ìhè",
      darkMode: "Ọdịdị ọchịchịrị",
      kgBatch: "Batch {n} kg · {model}",
      moreLive: "Oge dị ndụ {id}",
      moreIdle: "Enweghị ụkpụrụ ruo mgbe ngwugwu ESP32 rutere",
      awaitingHardware: "Na-eche ESP32",
      noTelemetryYet: "Enwebeghị data",
      progressLabel: "Ọganihu",
      stopSession: "Kwụsị oge",
    },
    ha: {
      overview: "Bayani",
      history: "Tarihin shan haya na kifi",
      settings: "Saitunan tsarin",
      control: "Cibiyar kulawa / 01",
      smokingOverview: "Bayanan shan haya",
      intelligent: "Kulawa mai hankali",
      controlMenu: "Mashigar kulawa",
      hardware: "Haɗin na’ura",
      connected: "ESP32 an haɗa",
      lastSync: "Sakamakon ƙarshe {time}",
      liveBackend: "Backend yana aiki",
      connecting: "Ana haɗawa da backend…",
      offline: "Ba a iya samun backend",
      progress: "Zama yana gudana",
      ready: "Tsarin a shirye yake",
      paused: "An dakatar da zama",
      stopped: "An tsayar",
      hero: "Na’urar shan haya a kallo ɗaya.",
      intro: "Kula da ɗakin, bi hasashen samfuri, kuma a adana kowane tsari.",
      start: "Fara zama",
      current: "Zama na yanzu",
      noSession: "Babu zama mai gudana",
      startBatch: "Fara tsari don kula kai tsaye.",
      remaining: "Lokacin da ya rage",
      readyWhen: "A shirye muke",
      autoStop: "Zai tsaya da kanta",
      percentComplete: "{n}% ya kammala",
      awaitingPrediction: "Ana jiran na’urorin ESP32…",
      hoursMins: "{h}hrs {m} mins",
      hoursOnly: "{h}hrs",
      minsOnly: "{m} mins",
      model: "Hasashen samfuri",
      duration: "jimlar lokaci",
      telemetry: "Bayanan kai tsaye",
      conditions: "Yanayin ɗakin",
      updates: "Sabuntawa kowane daƙiƙa 3",
      updatesLive: "Yana sabuntawa idan sakon ya iso",
      waitingTelemetry: "Ana jiran samfuran kai tsaye…",
      now: "Yanzu",
      health: "Lafiyar tsarin",
      nominal: "Duk tsarin suna da kyau",
      awaitingSensors: "Ana jiran na’urori",
      traceability: "Bin sawu",
      viewAll: "Duba duka",
      newBatch: "Sabon tsari",
      startTitle: "Fara zama na shan haya",
      formIntro: "Shigar da abubuwan mahimmanci. Samfurin zai kiyasta lokaci daga bayanan na’ura.",
      fishType: "Nau’in kifi",
      fishWeight: "Nauyin kifi (kg)",
      weightHint: "Bar nauyi fanko don ɗauka daga load cell.",
      begin: "Fara zama",
      close: "Rufe fom",
      chamber: "Zafin ɗaki",
      humidity: "Danshi",
      gas: "Na’urar iskar gas",
      heater: "Karatun zafi",
      fishWeightShort: "Nauyin kifi",
      target: "Manufa 65–72°C",
      within: "Yana cikin iyaka",
      air: "Ingancin iska",
      heaterOn: "Zafi a kunne",
      heaterOff: "Zafi a kashe",
      load: "Load cell yana aiki",
      awaiting: "Ana jiran tsari",
      prediction: "Na’urar hasashe",
      calculated: "An ƙidaya daga zafi, danshi, gas, zafin heater da nauyin kifi.",
      fish: "Nau’in kifi",
      completed: "An kammala",
      result: "Sakamako",
      online: "Kan layi",
      waiting: "Ana jira",
      tempProbe: "Na’urar zafi",
      humiditySensor: "Na’urar danshi",
      gasSensor: "Na’urar gas",
      loadCell: "Load cell",
      heaterRelay: "Relay na zafi",
      durationCol: "Lokaci",
      emptyHistory: "Babu zaman da aka kammala tukuna.",
      historyIntro: "Sai zaman da aka fara kuma aka tsayar daga wannan sava aka lissafa.",
      settingsTitle: "Sarrafa bayyanar da harshe.",
      settingsIntro: "Jigo da harshe suna kan wannan na’ura. Ƙimar na’urori tana zuwa daga backend kai tsaye.",
      appearance: "Bayyanar",
      toggleTheme: "Canja jigo",
      language: "Harshe",
      languageHint: "English, Yorùbá, Igbo, Hausa",
      lightMode: "Yanayin haske",
      darkMode: "Yanayin duhu",
      kgBatch: "Tsari {n} kg · {model}",
      moreLive: "Zama mai rai {id}",
      moreIdle: "Babu ƙima har sakon ESP32 ya iso",
      awaitingHardware: "Ana jiran ESP32",
      noTelemetryYet: "Babu bayanai tukuna",
      progressLabel: "Ci gaba",
      stopSession: "Tsayar da zama",
    },
  };

  const $ = (id) => document.getElementById(id);
  const state = {
    language: "en",
    dark: false,
    status: null,
    sessions: [],
    samples: [],
    backendOk: false,
    wsOpen: false,
    view: "overview",
  };

  function t(key, vars) {
    const table = translations[state.language] || translations.en;
    let value = table[key] || translations.en[key] || key;
    if (vars) {
      Object.keys(vars).forEach((k) => {
        value = value.replaceAll("{" + k + "}", String(vars[k]));
      });
    }
    return value;
  }

  function applyI18n() {
    document.documentElement.lang = state.language;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      el.textContent = t(el.getAttribute("data-i18n"));
    });
    $("language").value = state.language;
    if ($("language2")) $("language2").value = state.language;
    $("themeLabel").textContent = state.dark ? t("darkMode") : t("lightMode");
    const use = $("themeIcon").querySelector("use");
    use.setAttribute("href", state.dark ? "#i-sun" : "#i-moon");
    render();
  }

  function setLanguage(next) {
    if (!translations[next]) return;
    state.language = next;
    localStorage.setItem("smokehouse-language", next);
    applyI18n();
  }

  function setDark(next) {
    state.dark = next;
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("smokehouse-theme", next ? "dark" : "light");
    applyI18n();
  }

  function showView(name) {
    state.view = name;
    document.querySelectorAll(".view").forEach((el) => el.classList.toggle("active", el.id === "view-" + name));
    document.querySelectorAll("[data-nav]").forEach((el) => el.classList.toggle("active", el.getAttribute("data-nav") === name));
    $("mobileNav").classList.remove("open");
  }

  function hasTelemetry(status) {
    const tel = status && status.latest_telemetry;
    return !!(tel && tel.timestamp);
  }

  function num(value) {
    if (value === null || value === undefined || value === "") return null;
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  }

  function formatHoursMins(minutes) {
    if (minutes == null || !Number.isFinite(minutes) || minutes < 0) return "—";
    const total = Math.max(0, Math.round(minutes));
    const hours = Math.floor(total / 60);
    const mins = total % 60;
    if (hours > 0 && mins > 0) return t("hoursMins", { h: hours, m: mins });
    if (hours > 0) return t("hoursOnly", { h: hours });
    return t("minsOnly", { m: mins });
  }

  function formatTime(seconds) {
    if (seconds == null || !Number.isFinite(seconds) || seconds < 0) return "—";
    return formatHoursMins(seconds / 60);
  }

  function formatKg(grams) {
    const g = num(grams);
    if (g == null || g <= 0) return null;
    return (g / 1000).toFixed(g >= 1000 ? 2 : 2);
  }

  function relativeTime(iso) {
    const then = Date.parse(iso);
    if (!Number.isFinite(then)) return null;
    const sec = Math.max(0, Math.round((Date.now() - then) / 1000));
    if (sec < 5) return "just now";
    if (sec < 60) return sec + " seconds ago";
    if (sec < 3600) return Math.floor(sec / 60) + " min ago";
    return Math.floor(sec / 3600) + "h";
  }

  function telemetryFresh(status) {
    const iso = status && status.latest_telemetry && status.latest_telemetry.timestamp;
    if (!iso) return false;
    const then = Date.parse(iso);
    return Number.isFinite(then) && Date.now() - then < 45000;
  }

  function historyRows() {
    return (state.sessions || []).map((row) => {
      const grams = num(row.start_weight_g);
      const elapsed = num(row.elapsed_smoking_min) || 0;
      const result = row.result === "Stopped" || row.result === "stopped" ? t("stopped") : t("completed");
      const stopped = row.result === "Stopped" || row.result === "stopped";
      return {
        fish: row.fish_type || "—",
        weight: grams && grams > 0 ? (grams / 1000).toFixed(2) + " kg" : "—",
        duration: formatTime(elapsed * 60),
        date: row.timestamp || "—",
        result,
        stopped,
      };
    });
  }

  function fillTable(tbody, rows, limit) {
    const slice = limit ? rows.slice(0, limit) : rows;
    if (!slice.length) {
      tbody.innerHTML = '<tr><td class="empty-row" colspan="5">' + t("emptyHistory") + "</td></tr>";
      return;
    }
    tbody.innerHTML = slice
      .map(
        (row) =>
          "<tr><td>" +
          row.fish +
          '</td><td class="muted-cell">' +
          row.weight +
          "</td><td class=\"mono\">" +
          row.duration +
          '</td><td class="muted-cell">' +
          row.date +
          '</td><td class="right"><span class="badge' +
          (row.stopped ? "" : " ok") +
          '">' +
          row.result +
          "</span></td></tr>"
      )
      .join("");
  }

  function renderHealth(status) {
    const live = hasTelemetry(status);
    const running = status && status.session_state === "running";
    const items = [
      { key: "tempProbe", ok: live && num(status.latest_telemetry.oven_temp_c) != null },
      { key: "humiditySensor", ok: live && num(status.latest_telemetry.dht11_humidity_pct) != null },
      { key: "gasSensor", ok: live && num(status.latest_telemetry.mq6_adc) != null },
      { key: "loadCell", ok: live && num(status.latest_telemetry.weight_g) != null && status.latest_telemetry.weight_g > 0 },
      { key: "heaterRelay", ok: running && status.relay_state === "ON" },
    ];
    const allOk = items.every((item) => item.ok);
    $("healthTitle").textContent = live && allOk ? t("nominal") : t("awaitingSensors");
    $("healthList").innerHTML = items
      .map(
        (item) =>
          '<div class="health-row"><span>' +
          t(item.key) +
          '</span><span class="status"><span class="dot ' +
          (item.ok ? "teal" : "") +
          '"></span> ' +
          (item.ok ? t("online") : t("waiting")) +
          "</span></div>"
      )
      .join("");
  }

  function renderChart() {
    const chart = $("chart");
    const empty = $("chartEmpty");
    const samples = state.samples;
    chart.querySelectorAll(".bar").forEach((el) => el.remove());
    const temps = samples.map((s) => s.oven);
    const min = temps.length ? Math.min(...temps) : 0;
    const max = temps.length ? Math.max(...temps) : 1;
    for (let i = 0; i < 32; i += 1) {
      const bar = document.createElement("div");
      bar.className = "bar";
      const sample = samples[i];
      if (sample) {
        const pct = max === min ? 50 : 28 + ((sample.oven - min) / (max - min)) * 62;
        bar.style.height = pct + "%";
      } else {
        bar.style.height = "0%";
      }
      chart.appendChild(bar);
    }
    empty.style.display = samples.length ? "none" : "flex";
    empty.textContent = t("waitingTelemetry");
  }

  function pushSample(status) {
    if (!hasTelemetry(status)) return;
    const oven = num(status.latest_telemetry.oven_temp_c);
    if (oven == null) return;
    const stamp = status.latest_telemetry.timestamp;
    const last = state.samples[state.samples.length - 1];
    if (last && last.stamp === stamp) return;
    state.samples.push({ stamp, oven });
    if (state.samples.length > 32) state.samples.shift();
  }

  function render() {
    const status = state.status;
    const running = status && status.session_state === "running";
    const paused = status && status.session_state === "paused";
    const live = hasTelemetry(status);
    const tel = (status && status.latest_telemetry) || {};

    $("sessionCard").classList.toggle("active", !!running);
    $("statusDot").className = "dot " + (running ? "pulse" : "");
    $("statusLabel").textContent = running ? t("progress") : paused ? t("paused") : t("ready");

    $("sessionTitle").textContent = running || paused ? status.fish_type || status.session_id || t("current") : t("noSession");
    const kg = formatKg(status && status.start_weight_g);
    $("sessionSub").textContent =
      running || paused
        ? kg
          ? t("kgBatch", { n: kg, model: t("model") })
          : t("model")
        : t("startBatch");

    const remainMin = status ? num(status.predicted_remaining_min) : null;
    const elapsedMin = status ? num(status.elapsed_smoking_min) : null;
    // Only show predictions when session is running AND prediction is ready
    const ready = !!(status && status.session_state === "running" && status.prediction_ready && live && remainMin != null);
    const totalMin = ready && elapsedMin != null ? remainMin + elapsedMin : null;
    $("remainValue").textContent = ready ? formatHoursMins(remainMin) : "—";
    $("totalDuration").textContent = ready && totalMin != null ? formatHoursMins(totalMin) : "—";

    const progress =
      ready && totalMin ? Math.min(100, Math.max(0, (elapsedMin / totalMin) * 100)) : 0;
    $("progressFill").style.width = running && ready ? progress + "%" : "0%";
    $("progressPct").textContent = running && ready ? Math.round(progress) + "%" : "—";
    if (running && ready) {
      $("progressNote").textContent = t("percentComplete", { n: Math.round(progress) });
    } else if (running) {
      $("progressNote").textContent = t("awaitingPrediction");
    } else {
      $("progressNote").textContent = t("readyWhen");
    }
    $("autoStopNote").style.display = running ? "inline" : "none";
    $("autoStopNote").textContent = running ? t("autoStop") : "";
    $("stopBtn").style.display = running || paused ? "inline-flex" : "none";

    // Display sensor readings regardless of session status (as long as we have live telemetry)
    $("vTemp").textContent = live && num(tel.oven_temp_c) != null ? num(tel.oven_temp_c).toFixed(1) + "°C" : "—";
    $("vHum").textContent = live && num(tel.dht11_humidity_pct) != null ? Math.round(num(tel.dht11_humidity_pct)) + "%" : "—";
    $("vGas").textContent = live && num(tel.mq6_adc) != null ? String(Math.round(num(tel.mq6_adc))) : "—";
    $("vHeater").textContent = live && num(tel.oven_temp_c) != null ? Math.round(num(tel.oven_temp_c)) + "°C" : "—";
    const liveKg = live ? formatKg(tel.weight_g) : null;
    $("vWeight").textContent = liveKg ? liveKg + " kg" : kg && running ? kg + " kg" : "—";
    $("heaterDot").className = "dot " + (running && status.relay_state === "ON" ? "amber" : "teal");
    $("heaterNote").textContent = running && status.relay_state === "ON" ? t("heaterOn") : t("heaterOff");
    $("weightNote").textContent = running ? t("load") : t("awaiting");

    const hwLive = telemetryFresh(status);
    ["hwDot", "hwDot2"].forEach((id) => {
      const el = $(id);
      if (el) el.className = "dot " + (hwLive ? "teal" : "");
    });
    ["hwTitle", "hwTitle2"].forEach((id) => {
      const el = $(id);
      if (el) el.textContent = hwLive ? t("connected") : t("awaitingHardware");
    });
    const sync = live && tel.timestamp ? t("lastSync", { time: relativeTime(tel.timestamp) || "—" }) : t("noTelemetryYet");
    ["hwSync", "hwSync2"].forEach((id) => {
      const el = $(id);
      if (el) el.textContent = sync;
    });

    $("linkDot").className = "dot " + (state.wsOpen || state.backendOk ? "teal" : "");
    $("linkText").textContent = state.wsOpen || state.backendOk ? t("liveBackend") : t("connecting");
    $("moreText").textContent =
      running && status.session_id ? t("moreLive", { id: status.session_id }) : t("moreIdle");

    renderHealth(status);
    renderChart();
    const rows = historyRows();
    fillTable($("historyPreview"), rows, 5);
    fillTable($("historyFull"), rows);
  }

  async function api(path, opts) {
    const res = await fetch(path, Object.assign({ headers: { "Content-Type": "application/json" } }, opts || {}));
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(body.detail || res.statusText);
    return body;
  }

  async function poll() {
    try {
      const [status, history] = await Promise.all([api("/api/status"), api("/api/session/history")]);
      state.backendOk = true;
      state.status = status;
      state.sessions = Array.isArray(history.sessions) ? history.sessions : [];
      if (Array.isArray(history.history) && history.history.length) {
        const fromLog = history.history
          .filter((row) => num(row.oven_temp_c) != null && row.timestamp)
          .slice(-32)
          .map((row) => ({ stamp: String(row.timestamp), oven: num(row.oven_temp_c) }));
        if (fromLog.length) state.samples = fromLog;
      }
      pushSample(status);
      render();
    } catch (err) {
      state.backendOk = false;
      $("linkText").textContent = t("offline");
      $("linkDot").className = "dot amber";
    }
  }

  function connectWs() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(proto + "://" + location.host + "/api/ws");
    ws.onopen = () => {
      state.wsOpen = true;
      render();
    };
    ws.onclose = () => {
      state.wsOpen = false;
      render();
      setTimeout(connectWs, 2500);
    };
    ws.onerror = () => {
      try {
        ws.close();
      } catch (e) {}
    };
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.event === "pong") return;
        state.status = Object.assign({}, state.status || {}, msg);
        if (msg.event === "telemetry_update") pushSample(msg);
        render();
      } catch (e) {}
    };
  }

  function bindUi() {
    document.querySelectorAll("[data-nav]").forEach((btn) => {
      btn.addEventListener("click", () => showView(btn.getAttribute("data-nav")));
    });
    $("openMobile").onclick = () => $("mobileNav").classList.add("open");
    $("closeMobile").onclick = () => $("mobileNav").classList.remove("open");
    $("closeMobileBtn").onclick = () => $("mobileNav").classList.remove("open");
    $("openForm").onclick = () => $("startModal").classList.add("open");
    $("closeForm").onclick = () => $("startModal").classList.remove("open");
    $("closeFormScrim").onclick = () => $("startModal").classList.remove("open");
    $("themeBtn").onclick = () => setDark(!state.dark);
    $("themeBtn2").onclick = () => setDark(!state.dark);
    $("language").onchange = (e) => setLanguage(e.target.value);
    if ($("language2")) $("language2").onchange = (e) => setLanguage(e.target.value);
    $("moreBtn").onclick = (e) => {
      e.stopPropagation();
      $("moreMenu").classList.toggle("open");
    };
    document.addEventListener("click", () => $("moreMenu").classList.remove("open"));
    $("startForm").onsubmit = async (event) => {
      event.preventDefault();
      
      // Validate fish type selection
      const fishType = $("fishType").value.trim();
      if (!fishType) {
        alert("Please select a fish type (Shawa, Catfish, or Tuna)");
        return;
      }
      
      const kg = $("fishWeight").value.trim();
      const payload = { fish_type: fishType };
      if (kg) payload.start_weight_g = Number(kg) * 1000;
      
      try {
        await api("/api/session/start", { method: "POST", body: JSON.stringify(payload) });
        $("startModal").classList.remove("open");
        state.samples = [];
        state.status = Object.assign({}, state.status || {}, {
          session_state: "running",
          relay_state: "ON",
          fish_type: payload.fish_type,
          start_weight_g: payload.start_weight_g || 0,
          elapsed_smoking_min: 0,
          predicted_remaining_min: null,
          prediction_ready: false,
          latest_telemetry: {},
        });
        render();
        await poll();
      } catch (error) {
        alert("Failed to start session: " + (error.message || "Unknown error"));
      }
    };
    $("stopBtn").onclick = async () => {
      await api("/api/session/stop", { method: "POST" });
      await poll();
    };
  }

  function boot() {
    const savedTheme = localStorage.getItem("smokehouse-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    state.dark = savedTheme ? savedTheme === "dark" : prefersDark;
    document.documentElement.classList.toggle("dark", state.dark);
    const savedLang = localStorage.getItem("smokehouse-language");
    if (savedLang && translations[savedLang]) state.language = savedLang;
    bindUi();
    applyI18n();
    connectWs();
    poll();
    setInterval(poll, 10000);
  }

  boot();
})();
