const API_BASE = "https://agriyield-punjab.onrender.com";

const PAU_GROUP_ALIASES = {
  Rice: ["Paddy", "Basmati"],
  Wheat: ["Wheat"],
  Potato: ["Potato"],
  Moong: ["Summer_Moong"],
};

let METADATA = null;

const statusBadge = document.getElementById("api-status");
const districtSelect = document.getElementById("district");
const cropSeasonSelect = document.getElementById("crop-season");
const varietySelect = document.getElementById("variety");
const areaInput = document.getElementById("area-ekad");
const form = document.getElementById("predict-form");
const submitBtn = document.getElementById("submit-btn");
const errorBox = document.getElementById("error-box");
const resultsSection = document.getElementById("results");

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.classList.remove("hidden");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function populateCropSeasons() {
  const selectedDistrict = districtSelect.value;
  const combos = METADATA.combinations.filter((c) => c.district === selectedDistrict);

  cropSeasonSelect.innerHTML = "";
  combos.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = `${c.crop}||${c.season}`;
    opt.textContent = `${c.crop} (${c.season})`;
    if (c.crop === "Wheat" && c.season === "Rabi") opt.selected = true;
    cropSeasonSelect.appendChild(opt);
  });

  populateVarieties();
}

function populateVarieties() {
  const [crop] = (cropSeasonSelect.value || "").split("||");
  const allowedGroups = PAU_GROUP_ALIASES[crop] || [];
  const varieties = METADATA.pau_varieties || {};

  varietySelect.innerHTML = "";
  const matches = Object.entries(varieties).filter(([, info]) =>
    allowedGroups.includes(info.crop)
  );

  if (matches.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "Standard District Baseline";
    varietySelect.appendChild(opt);
    return;
  }

  matches.forEach(([name, info]) => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = `${name} (${info.crop} · ${info.pau_avg_yield_q_ekad} q/ekad)`;
    varietySelect.appendChild(opt);
  });
}

async function initApp() {
  try {
    statusBadge.textContent = "Waking ML API (~15s on cold start)...";
    const res = await fetch(`${API_BASE}/metadata`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    METADATA = await res.json();

    const r2 = METADATA.model_metrics?.temporal_holdout_r2;
    statusBadge.textContent = `ML API Online · Holdout R² ${r2}`;
    statusBadge.classList.add("online");

    districtSelect.innerHTML = "";
    METADATA.districts.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = d.district;
      opt.textContent = `${d.district} (${d.nabard_az_code})`;
      if (d.district === "Bathinda") opt.selected = true;
      districtSelect.appendChild(opt);
    });

    populateCropSeasons();
  } catch (err) {
    statusBadge.textContent = "API Offline / Retrying";
    showError("Could not reach AgriYield API. Please wait 20 seconds and refresh.");
  }
}

districtSelect.addEventListener("change", populateCropSeasons);
cropSeasonSelect.addEventListener("change", populateVarieties);

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  submitBtn.disabled = true;
  submitBtn.textContent = "Running ML Prediction...";

  try {
    const [crop, season] = cropSeasonSelect.value.split("||");
    const payload = {
      district: districtSelect.value,
      crop,
      season,
      area_ekad: parseFloat(areaInput.value),
      variety: varietySelect.value || null,
    };

    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Prediction failed");
    }

    const data = await res.json();
    renderResults(data);
  } catch (err) {
    showError(err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Predict Yield & Calculate Inputs";
  }
});

function renderResults(data) {
  const pred = data.prediction;
  const pau = data.pau_advisory;
  const irr = data.district_irrigation_profile;

  const isRice = (data.crop || "").toLowerCase() === "rice";
  const MILLING_RECOVERY = 0.67;

  const displayYield = isRice
    ? +(pred.expected_yield_q_ekad / MILLING_RECOVERY).toFixed(2)
    : pred.expected_yield_q_ekad;

  const displayTotal = isRice
    ? +(displayYield * data.area_ekad).toFixed(2)
    : pred.total_expected_production_quintals;

  document.getElementById("res-yield").textContent = isRice
    ? `${displayYield} q/ekad (Paddy)`
    : `${displayYield} q/ekad`;

  if (isRice) {
    const latestPaddy = +(pred.latest_des_yield_q_ekad / MILLING_RECOVERY).toFixed(2);
    document.getElementById(
      "res-des-compare"
    ).textContent = `DES Milled Rice: ${pred.expected_yield_q_ekad} q/ekad (67%) · Latest DES (${pred.latest_des_observed_year}): ${latestPaddy} q/ekad Paddy`;
  } else {
    document.getElementById(
      "res-des-compare"
    ).textContent = `Latest DES (${pred.latest_des_observed_year}): ${pred.latest_des_yield_q_ekad} q/ekad`;
  }

  document.getElementById("res-total").textContent = `${displayTotal} q`;
  document.getElementById("res-area-sub").textContent = isRice
    ? `Across ${data.area_ekad} ekad (raw paddy)`
    : `Across ${data.area_ekad} ekad`;

  if (pau.variety_details) {
    const bench = pau.variety_details.pau_avg_yield_q_ekad;
    document.getElementById("res-pau-bench").textContent = `${bench} q/ekad`;
    const gap = +(bench - displayYield).toFixed(2);
    document.getElementById("res-pau-gap").textContent =
      gap > 0
        ? `${gap} q/ekad upside potential vs district avg`
        : `${Math.abs(gap)} q/ekad above PAU average`;
  } else {
    document.getElementById("res-pau-bench").textContent = "N/A";
    document.getElementById("res-pau-gap").textContent = "No PAU variety entry";
  }

  const fertPills = document.getElementById("fert-pills");
  fertPills.innerHTML = "";
  if (pau.total_fertilizer_bags_for_area) {
    Object.entries(pau.total_fertilizer_bags_for_area).forEach(([fert, bags]) => {
      const kg = pau.total_fertilizer_kg_for_area[fert];
      const div = document.createElement("div");
      div.className = "pill";
      div.innerHTML = `${fert}: <strong>${bags} bags</strong> (${kg} kg)`;
      fertPills.appendChild(div);
    });
    document.getElementById(
      "sowing-note"
    ).textContent = `Variety: ${pau.selected_variety} · Maturity: ${pau.variety_details.maturity_days} days · Optimal Sowing: ${pau.variety_details.sowing_window}`;
  } else {
    fertPills.innerHTML = `<div class="pill">Consult PAU Ludhiana Package of Practices for exact dose.</div>`;
    document.getElementById("sowing-note").textContent = "";
  }

  const irrPills = document.getElementById("irr-pills");
  irrPills.innerHTML = `
    <div class="pill">Zone: <strong>${data.nabard_agro_climatic_zone.code}</strong> (${data.nabard_agro_climatic_zone.name})</div>
    <div class="pill">Tubewell Share: <strong>${irr.tubewell_share_pct ?? "N/A"}%</strong></div>
    <div class="pill">Canal Share: <strong>${irr.canal_share_pct ?? "N/A"}%</strong></div>
    <div class="pill">Irrigation Intensity: <strong>${irr.irrigation_intensity_pct ?? "N/A"}%</strong></div>
  `;

  resultsSection.classList.remove("hidden");
}

initApp();
