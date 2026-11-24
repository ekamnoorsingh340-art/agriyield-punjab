const API_BASE = "https://agriyield-punjab.onrender.com";

// Full Punjab Variety Catalog (PAU Recommended + Farmer High-Yield Pusa Lines + PAU Potato Series)
const PUNJAB_VARIETY_CATALOG = {
  Rice: [
    {
      name: "PR 126",
      backendKey: "PR 126",
      type: "Parmal Paddy",
      benchmark: 30.0,
      seedToSeedDays: "123 days",
      fieldDays: "~93 days post-transplant",
      sowingWindow: "Nursery: May 25 – Jun 20 · Transplant: Jun 25 – Jul 20 (strict 30-day nursery)",
      waterDemand: "Low–Moderate (Saves 4–5 irrigations)",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 90 kg Urea (2 bags/ekad) in 3 equal splits: 1/3rd within 7 days of transplanting, 1/3rd at 21 days, and final 1/3rd at 35–42 days. Avoid Urea after 45 days to prevent lodging and blast.",
      agronomyNote:
        "Fast-maturing flagship PAU variety. Requires young 25–30 day seedlings; transplanting older seedlings reduces tillering and yield. Clears fields early for potato or timely wheat."
    },
    {
      name: "PR 131",
      backendKey: "PR 131",
      type: "Parmal Paddy",
      benchmark: 31.0,
      seedToSeedDays: "140 days",
      fieldDays: "~110 days post-transplant",
      sowingWindow: "Nursery: May 15 – May 30 · Transplant: Jun 15 – Jun 30",
      waterDemand: "Moderate",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 90 kg Urea (2 bags/ekad) in 3 splits (7, 21, and 42 DAT). Apply 25 kg Zinc Sulphate (21%) during puddling if previous wheat showed zinc deficiency.",
      agronomyNote:
        "High-yielding medium-duration PAU Parmal variety resistant to all 10 pathotypes of Bacterial Leaf Blight (BLB) prevalent in Punjab."
    },
    {
      name: "PR 118",
      backendKey: "PR 118",
      type: "Parmal Paddy",
      benchmark: 29.0,
      seedToSeedDays: "158 days",
      fieldDays: "~128 days post-transplant",
      sowingWindow: "Nursery: May 10 – May 25 · Transplant: Jun 10 – Jun 25",
      waterDemand: "Moderate–High",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 90 kg Urea (2 bags/ekad) in 3 equal splits (7, 21, and 42 DAT). No DAP/MOP required if Rabi wheat received full recommended phosphorus.",
      agronomyNote:
        "Stiff-strawed, lodging-resistant medium-long PAU variety suited for fertile central plain soils."
    },
    {
      name: "PR 111",
      backendKey: "PR 111",
      type: "Parmal Paddy",
      benchmark: 27.5,
      seedToSeedDays: "138 days",
      fieldDays: "~108 days post-transplant",
      sowingWindow: "Nursery: May 15 – May 30 · Transplant: Jun 15 – Jun 30",
      waterDemand: "Moderate",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 90 kg Urea (2 bags/ekad) in 3 equal splits at 7, 21, and 42 days after transplanting.",
      agronomyNote:
        "Reliable medium-duration PAU variety with good grain quality and bacterial blight tolerance."
    },
    {
      name: "Chitta Pusa",
      backendKey: "PR 118",
      type: "High-Yield Pusa Line",
      benchmark: 35.5,
      seedToSeedDays: "155–165 days",
      fieldDays: "~125–135 days post-transplant",
      sowingWindow: "Nursery: May 1 – May 15 · Transplant: Jun 10 – Jun 20",
      waterDemand: "Very High (+25% tubewell cycles)",
      status: "⚠️ PAU Restricted / High Water",
      restricted: true,
      warningTitle: "High Groundwater Consumption & Long Duration Warning (155–165 Days)",
      warningText:
        "While Chitta Pusa delivers 34–38 q/ekad on heavy soils, it takes 155–165 days, consumes ~25% more tubewell water than PR 126, leaves heavy paddy straw, and pushes harvest into November—tightening the sowing window for Rabi wheat or potatoes. Officially discouraged/restricted in Punjab to protect falling water tables.",
      fertSchedule:
        "Farmers typically apply 2.2–2.5 bags Urea/ekad across 3 splits, though excess nitrogen beyond 45 DAT increases false smut, neck blast, and late-season lodging risk.",
      agronomyNote:
        "Widely grown across Malwa districts for maximum quintals per ekad, but carries higher electricity/diesel pumping load and late-harvest moisture penalties if harvested in November."
    },
    {
      name: "Peeli Pusa (Pusa 44)",
      backendKey: "PR 118",
      type: "High-Yield Pusa Line",
      benchmark: 34.5,
      seedToSeedDays: "155–160 days",
      fieldDays: "~125–130 days post-transplant",
      sowingWindow: "Nursery: May 1 – May 15 · Transplant: Jun 10 – Jun 20",
      waterDemand: "Very High (+22–28% tubewell cycles)",
      status: "⚠️ Banned / High Water",
      restricted: true,
      warningTitle: "Punjab Govt Ban & Severe Water-Table Drawdown Alert (155–160 Days)",
      warningText:
        "Peeli Pusa (Pusa 44) is officially banned by the Punjab Government due to extreme groundwater extraction (155–160 day cycle), high susceptibility to Bacterial Leaf Blight & false smut, and heavy stubble load that delays Rabi wheat sowing.",
      fertSchedule:
        "Heavy vegetative growth makes Pusa 44 prone to Brown Plant Hopper (BPH) and blast if Urea exceeds 2 bags/ekad or is applied late.",
      agronomyNote:
        "Historically popular for 33–37 q/ekad yields, now officially replaced in PAU advisories by PR 126 and PR 131."
    },
    {
      name: "Dogar Pusa",
      backendKey: "PR 118",
      type: "High-Yield Pusa Line",
      benchmark: 36.5,
      seedToSeedDays: "160–165 days",
      fieldDays: "~130–135 days post-transplant",
      sowingWindow: "Nursery: May 1 – May 12 · Transplant: Jun 10 – Jun 18",
      waterDemand: "Extreme (Longest irrigation window)",
      status: "⚠️ PAU Restricted / High Water",
      restricted: true,
      warningTitle: "Extreme Duration (160–165 Days) & Heavy Irrigation Warning",
      warningText:
        "Dogar Pusa can reach 35–38+ q/ekad on fertile irrigated land, but its 160–165 day cycle demands continuous late-season irrigation into October, increases lodging risk during autumn winds, and significantly delays next-crop sowing.",
      fertSchedule:
        "Avoid heavy late nitrogen top-dressing; monitor closely for false smut and sheath blight during humid September weather.",
      agronomyNote:
        "Chosen purely for peak raw tonnage; unsuitable if you plan early potato or multi-crop rotations."
    },
    {
      name: "Pusa Basmati 1121",
      backendKey: "Pusa Basmati 1121",
      type: "Aromatic Basmati",
      benchmark: 17.0,
      seedToSeedDays: "137 days",
      fieldDays: "~107 days post-transplant",
      sowingWindow: "Nursery: Jun 1 – Jun 15 · Transplant: Jul 1 – Jul 15",
      waterDemand: "Low–Moderate (July transplanting uses monsoon rains)",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Basmati requires HALF the nitrogen of Parmal paddy: apply only 36 kg Urea (0.8 bag/ekad) in 2 splits (21 and 42 DAT). Excess Urea causes tall lodging and ruins grain aroma.",
      agronomyNote:
        "World-renowned extra-long slender grain Basmati. Lower quintal yield than Parmal paddy, but commands open-market mandi prices typically 1.5x–1.8x higher than MSP."
    },
    {
      name: "Pusa Basmati 1718",
      backendKey: "Pusa Basmati 1718",
      type: "Aromatic Basmati",
      benchmark: 18.5,
      seedToSeedDays: "136 days",
      fieldDays: "~106 days post-transplant",
      sowingWindow: "Nursery: Jun 1 – Jun 15 · Transplant: Jul 1 – Jul 15",
      waterDemand: "Low–Moderate",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 36 kg Urea (0.8 bag/ekad) in 2 splits at 21 and 42 days after transplanting. Do not over-fertilize.",
      agronomyNote:
        "Improved bacterial-blight-resistant version of PB 1121 with stronger stems and slightly higher yield."
    },
    {
      name: "Pusa Basmati 1885",
      backendKey: "Pusa Basmati 1718",
      type: "Aromatic Basmati",
      benchmark: 19.0,
      seedToSeedDays: "135 days",
      fieldDays: "~105 days post-transplant",
      sowingWindow: "Nursery: Jun 1 – Jun 15 · Transplant: Jul 1 – Jul 15",
      waterDemand: "Low–Moderate",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 36 kg Urea (0.8 bag/ekad) in 2 splits (21 and 42 DAT).",
      agronomyNote:
        "Next-generation marker-assisted Basmati with strong resistance against both Bacterial Leaf Blight and Blast."
    },
    {
      name: "Pusa Basmati 1509",
      backendKey: "Pusa Basmati 1509",
      type: "Short-Duration Basmati",
      benchmark: 19.5,
      seedToSeedDays: "120 days",
      fieldDays: "~90 days post-transplant",
      sowingWindow: "Nursery: Jun 10 – Jun 25 · Transplant: Jul 10 – Jul 25",
      waterDemand: "Low (Ideal for 3-crop / 4-crop rotations)",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 45 kg Urea (1 bag/ekad) in 2 splits at 15 and 35 days after transplanting.",
      agronomyNote:
        "Early-maturing non-lodging Basmati that harvests by early October—leaving an ideal window for autumn potatoes or peas before wheat."
    }
  ],
  Wheat: [
    {
      name: "PBW 826",
      backendKey: "PBW 826",
      type: "Timely-Sown Wheat",
      benchmark: 24.0,
      seedToSeedDays: "148 days",
      fieldDays: "Full Rabi cycle",
      sowingWindow: "Oct 25 – Nov 15",
      waterDemand: "4–5 irrigations (Crown root, tillering, jointing, flowering, milk stage)",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 55 kg DAP (1.1 bags/ekad) at sowing + 110 kg Urea (2.4 bags/ekad) split between 1st irrigation (21–25 DAS) and 2nd irrigation (45–50 DAS).",
      agronomyNote:
        "Top-performing heat-tolerant PAU wheat variety with bold amber grains and strong yellow/brown rust resistance."
    },
    {
      name: "PBW 872",
      backendKey: "PBW 872",
      type: "High-Yield Timely Wheat",
      benchmark: 24.5,
      seedToSeedDays: "152 days",
      fieldDays: "Full Rabi cycle",
      sowingWindow: "Oct 25 – Nov 10",
      waterDemand: "4–5 irrigations",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 55 kg DAP (1.1 bags/ekad) at drilling + 110 kg Urea (2.4 bags/ekad) in 2 splits before 2nd irrigation.",
      agronomyNote:
        "High-potential timely-sown variety suited for high-fertility irrigated soils across Punjab."
    },
    {
      name: "PBW 803",
      backendKey: "PBW 803",
      type: "Timely-Sown Wheat",
      benchmark: 23.0,
      seedToSeedDays: "150 days",
      fieldDays: "Full Rabi cycle",
      sowingWindow: "Oct 25 – Nov 15",
      waterDemand: "4–5 irrigations",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 55 kg DAP at sowing + 110 kg Urea in 2 equal splits at 1st and 2nd irrigation.",
      agronomyNote:
        "Consistent performer with strong lodging resistance and stripe rust tolerance."
    },
    {
      name: "Unnat PBW 343",
      backendKey: "Unnat PBW 343",
      type: "Timely-Sown Wheat",
      benchmark: 23.5,
      seedToSeedDays: "155 days",
      fieldDays: "Full Rabi cycle",
      sowingWindow: "Oct 25 – Nov 15",
      waterDemand: "4–5 irrigations",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 55 kg DAP at sowing + 110 kg Urea in 2 equal splits at 1st and 2nd irrigation.",
      agronomyNote:
        "Rust-resistant upgrade of the classic PBW 343 mega-variety with excellent chapati quality."
    },
    {
      name: "PBW 1 Zn",
      backendKey: "PBW 1 Zn",
      type: "Biofortified Wheat",
      benchmark: 22.5,
      seedToSeedDays: "151 days",
      fieldDays: "Full Rabi cycle",
      sowingWindow: "Oct 25 – Nov 15",
      waterDemand: "4–5 irrigations",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 55 kg DAP at sowing + 110 kg Urea in 2 splits; foliar spray of 0.5% Zinc Sulphate at booting boosts grain zinc.",
      agronomyNote:
        "High-zinc biofortified PAU variety delivering superior nutritional value and steady yields."
    },
    {
      name: "PBW 752",
      backendKey: "PBW 752",
      type: "Late-Sown Wheat (Post-Potato)",
      benchmark: 19.5,
      seedToSeedDays: "130 days",
      fieldDays: "Short Rabi cycle",
      sowingWindow: "Nov 25 – Dec 25 (up to early Jan after potato harvest)",
      waterDemand: "3–4 irrigations (Critical at grain filling in March)",
      status: "PAU Recommended (Late Sown)",
      restricted: false,
      fertSchedule:
        "For late sowing after potatoes, skip DAP if potato received heavy phosphorus; apply ~85–90 kg Urea (2 bags/ekad) in 2 quick splits.",
      agronomyNote:
        "Specifically bred for late sowing after potato, cotton, or long-duration paddy—tolerates late-season March heat without severe shriveling."
    }
  ],
  Potato: [
    {
      name: "Punjab Potato 102 (PP-102)",
      backendKey: "PP-102",
      type: "PAU Peak-Yield Table Potato",
      benchmark: 184.0,
      seedToSeedDays: "100–110 days",
      fieldDays: "Main Autumn Season",
      sowingWindow: "Oct 1 – Oct 20 (Peak Autumn Planting)",
      waterDemand: "7–8 light ridge irrigations (keep soil moist during tuber bulking)",
      status: "PAU Recommended (Highest Yield)",
      restricted: false,
      fertSchedule:
        "Apply 20 tonnes FYM + 110 kg Urea (2.4 bags), 135 kg SSP (2.7 bags), and 40 kg MOP (0.8 bag) per ekad. Apply half Urea + full SSP & MOP at planting; remaining half Urea at earthing-up (25–30 DAP).",
      agronomyNote:
        "Highest-yielding potato variety released by PAU Ludhiana (184 q/ekad average). Produces uniform oval-round, shallow-eyed tubers with light-brown skin and creamy-yellow flesh."
    },
    {
      name: "Punjab Potato 103 (PP-103)",
      backendKey: "PP-103",
      type: "PAU 80-Day Early-Bulking Potato",
      benchmark: 142.0,
      seedToSeedDays: "80–90 days (180 q/ekad at full maturity)",
      fieldDays: "Early-Harvest / 4-Crop Rotation",
      sowingWindow: "Sep 25 – Oct 15 (Harvest late Dec for PBW 752 wheat)",
      waterDemand: "6–7 light ridge irrigations",
      status: "PAU Recommended (Early Rotation)",
      restricted: false,
      fertSchedule:
        "Apply 20 tonnes FYM + 110 kg Urea (half at planting, half at earthing-up at 25 DAP) + 135 kg SSP + 40 kg MOP per ekad.",
      agronomyNote:
        "PAU's extra-early bulking specialist—delivers ~142 q/ekad in just 80–90 days (or 180 q/ekad if held longer), making it ideal before late-sown PBW 752 wheat."
    },
    {
      name: "Punjab Potato 101 (PP-101)",
      backendKey: "PP-101",
      type: "PAU Early-Bulking Table Potato",
      benchmark: 178.0,
      seedToSeedDays: "90–100 days",
      fieldDays: "Early–Main Autumn Season",
      sowingWindow: "Sep 25 – Oct 15",
      waterDemand: "6–8 light ridge irrigations",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 20 tonnes FYM + 110 kg Urea (split at planting & earthing-up) + 135 kg SSP + 40 kg MOP per ekad.",
      agronomyNote:
        "Early-bulking PAU table variety with uniform oval-round light-brown tubers and creamy-white flesh suited for fresh mandi sales."
    },
    {
      name: "Punjab Potato 104 (PP-104)",
      backendKey: "PP-104",
      type: "PAU Late-Blight Resistant Potato",
      benchmark: 174.0,
      seedToSeedDays: "105–115 days",
      fieldDays: "Medium-Late Autumn Season",
      sowingWindow: "Oct 5 – Oct 25",
      waterDemand: "7–8 light ridge irrigations",
      status: "PAU Recommended (Blight Shield)",
      restricted: false,
      fertSchedule:
        "Apply 20 tonnes FYM + 110 kg Urea (split) + 135 kg SSP + 40 kg MOP per ekad.",
      agronomyNote:
        "PAU variety carrying moderate resistance to Late Blight—recommended for humid pockets or fields with recurring blight pressure."
    },
    {
      name: "Kufri Sindhuri (Lal Sindhuri)",
      backendKey: "Kufri Sindhuri",
      type: "Red-Skinned Storage Potato",
      benchmark: 135.0,
      seedToSeedDays: "110–120 days",
      fieldDays: "Main / Late-Planted Autumn",
      sowingWindow: "Oct 10 – Nov 10 (Tolerates planting up to mid-November)",
      waterDemand: "7–8 light irrigations (tolerates mild water/heat stress)",
      status: "PAU Recommended (Red Skin)",
      restricted: false,
      fertSchedule:
        "Apply 20 tonnes FYM + 110 kg Urea (half at sowing, half at 30 DAP earthing-up) + 135 kg SSP + 40 kg MOP per ekad.",
      agronomyNote:
        "Classic round, red-skinned potato with dull-white flesh. Known for slow seed degeneration, frost/heat tolerance, and top cold-storage keeping quality."
    },
    {
      name: "Kufri Pukhraj",
      backendKey: "Kufri Pukhraj",
      type: "Early Table Potato",
      benchmark: 155.0,
      seedToSeedDays: "75–90 days",
      fieldDays: "Early Autumn Season",
      sowingWindow: "Sep 25 – Oct 15",
      waterDemand: "6–7 light ridge irrigations",
      status: "PAU Recommended",
      restricted: false,
      fertSchedule:
        "Apply 20 tonnes FYM + 110 kg Urea (split) + 135 kg SSP + 40 kg MOP per ekad.",
      agronomyNote:
        "Popular early-maturing large oval white-skinned potato resistant to early blight."
    }
  ]
};

// State Standard Variety Baselines for Varietal Adjustment Multiplier
const CROP_STANDARD_BENCHMARKS = {
  Rice: 30.0,     // PR 126 state standard baseline
  Wheat: 23.5,    // Unnat PBW 343 state standard baseline
  Potato: 165.0   // Punjab regional irrigated potato baseline
};

// Default MSP / Mandi Rates (₹/quintal - Kharif 2026-27 & Rabi 2027-28)
const DEFAULT_MANDI_RATES = {
  Rice: 2461,         // Grade A Paddy MSP 2026-27 (Common: ₹2441)
  Basmati: 3800,      // Indicative Punjab Mandi Open Market Rate
  Wheat: 2610,        // Rabi 2027-28 MSP
  Potato: 1100,       // Indicative Punjab Mandi / Cold-Store Benchmark
  Moong: 8780,        // Kharif 2026-27 MSP (matches "Moong" & "Moong(Green Gram)")
  Urad: 8200,         // Kharif 2026-27 MSP
  Arhar: 8450,        // Kharif 2026-27 MSP
  Gram: 5958,         // Rabi 2027-28 MSP
  Masoor: 7390,       // Rabi 2027-28 MSP
  Mustard: 6613,      // Rabi 2027-28 MSP
  Cotton: 8667,       // Long Staple MSP 2026-27
  Maize: 2410,        // Kharif 2026-27 MSP
  Bajra: 2900,        // Kharif 2026-27 MSP
  Jowar: 4023,        // Kharif 2026-27 MSP
  Sunflower: 8343,    // Kharif 2026-27 MSP
  Groundnut: 7517,    // Kharif 2026-27 MSP
  Sesamum: 10346,     // Kharif 2026-27 MSP
  Sugarcane: 365      // FRP 2026-27 (₹/quintal)
};


let METADATA = null;
let LAST_API_DATA = null;

const statusBadge = document.getElementById("api-status");
const districtSelect = document.getElementById("district");
const cropSeasonSelect = document.getElementById("crop-season");
const varietySelect = document.getElementById("variety");
const areaInput = document.getElementById("area-ekad");
const mandiRateInput = document.getElementById("mandi-rate");
const form = document.getElementById("predict-form");
const submitBtn = document.getElementById("submit-btn");
const errorBox = document.getElementById("error-box");
const welcomeCard = document.getElementById("welcome-placeholder");
const resultsSection = document.getElementById("results");

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.classList.remove("hidden");
}

function clearError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function getSelectedCatalogVariety() {
  const [crop] = (cropSeasonSelect.value || "").split("||");
  const list = PUNJAB_VARIETY_CATALOG[crop] || [];
  return list.find((v) => v.name === varietySelect.value) || null;
}

function updateDefaultMandiRate() {
  const [crop] = (cropSeasonSelect.value || "").split("||");
  const vObj = getSelectedCatalogVariety();
  if (vObj && vObj.type.includes("Basmati")) {
    mandiRateInput.value = DEFAULT_MANDI_RATES.Basmati;
    return;
  }
  mandiRateInput.value = DEFAULT_MANDI_RATES[crop] || 2500;
}

function populateCropSeasons() {
  const selectedDistrict = districtSelect.value;
  const combos = METADATA.combinations.filter((c) => c.district === selectedDistrict);

  cropSeasonSelect.innerHTML = "";
  combos.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = `${c.crop}||${c.season}`;
    opt.textContent = `${c.crop} (${c.season})`;
    if (c.crop === "Rice" && c.season === "Kharif") opt.selected = true;
    cropSeasonSelect.appendChild(opt);
  });

  // Always include Potato (Autumn / Main) with PAU PP-101–104 & Kufri Sindhuri benchmarks
  const potatoOpt = document.createElement("option");
  potatoOpt.value = "Potato||Autumn";
  potatoOpt.textContent = "Potato (Autumn / Main)";
  cropSeasonSelect.appendChild(potatoOpt);

  populateVarieties();
}

function populateVarieties() {
  const [crop] = (cropSeasonSelect.value || "").split("||");
  const catalogList = PUNJAB_VARIETY_CATALOG[crop] || [];

  varietySelect.innerHTML = "";
  if (catalogList.length === 0) {
    const backendVarieties = METADATA.pau_varieties || {};
    const matches = Object.entries(backendVarieties).filter(
      ([, info]) => (info.crop || "").toLowerCase() === (crop || "").toLowerCase()
    );
    if (matches.length === 0) {
      const opt = document.createElement("option");
      opt.value = "";
      opt.textContent = "Standard District Baseline";
      varietySelect.appendChild(opt);
    } else {
      matches.forEach(([name, info]) => {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = `${name} (${info.pau_avg_yield_q_ekad} q/ekad)`;
        varietySelect.appendChild(opt);
      });
    }
    updateDefaultMandiRate();
    return;
  }

  catalogList.forEach((v) => {
    const opt = document.createElement("option");
    opt.value = v.name;
    const tag = v.restricted ? "⚠️ High Water / 155d+" : v.type;
    opt.textContent = `${v.name} — ${v.benchmark} q/ekad (${tag})`;
    varietySelect.appendChild(opt);
  });

  updateDefaultMandiRate();
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
varietySelect.addEventListener("change", updateDefaultMandiRate);
mandiRateInput.addEventListener("input", () => {
  if (LAST_API_DATA) renderResults(LAST_API_DATA);
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  submitBtn.disabled = true;
  submitBtn.textContent = "Running ML Prediction...";

  try {
    const [crop, season] = cropSeasonSelect.value.split("||");
    const areaEkad = parseFloat(areaInput.value);
    const catVar = getSelectedCatalogVariety();

    // PAU Horticulture Benchmark Module for Potato (not in DES foodgrain dataset)
    if (crop === "Potato") {
      // Query Wheat/Rice for same district so we still pull real district irrigation & NABARD zone metadata
      const refRes = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          district: districtSelect.value,
          crop: "Wheat",
          season: "Rabi",
          area_ekad: areaEkad,
          variety: "PBW 826"
        })
      });
      const refData = refRes.ok ? await refRes.json() : null;

      const potatoData = {
        district: districtSelect.value,
        crop: "Potato",
        season: "Autumn",
        area_ekad: areaEkad,
        is_pau_horticulture_module: true,
        prediction: {
          expected_yield_q_ekad: CROP_STANDARD_BENCHMARKS.Potato,
          latest_des_observed_year: "PAU 2025",
          latest_des_yield_q_ekad: CROP_STANDARD_BENCHMARKS.Potato
        },
        pau_advisory: {
          variety_details: { pau_avg_yield_q_ekad: catVar ? catVar.benchmark : 165.0 },
          total_fertilizer_bags_for_area: {
            "Urea (45kg)": +(2.44 * areaEkad).toFixed(1),
            "SSP (50kg)": +(2.7 * areaEkad).toFixed(1),
            "MOP (50kg)": +(0.8 * areaEkad).toFixed(1)
          },
          total_fertilizer_kg_for_area: {
            "Urea (45kg)": Math.round(110 * areaEkad),
            "SSP (50kg)": Math.round(135 * areaEkad),
            "MOP (50kg)": Math.round(40 * areaEkad)
          }
        },
        nabard_agro_climatic_zone: refData?.nabard_agro_climatic_zone || {
          code: "PB-AZ",
          name: "Punjab Irrigated Plains"
        },
        district_irrigation_profile: refData?.district_irrigation_profile || {
          tubewell_share_pct: 72,
          canal_share_pct: 28,
          irrigation_intensity_pct: 198
        }
      };

      LAST_API_DATA = potatoData;
      renderResults(potatoData);
      return;
    }

    const payload = {
      district: districtSelect.value,
      crop,
      season,
      area_ekad: areaEkad,
      variety: catVar ? catVar.backendKey : varietySelect.value || null,
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
    LAST_API_DATA = data;
    renderResults(data);
  } catch (err) {
    showError(err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Predict Yield & Generate Field Report";
  }
});

function formatINR(amount) {
  return "₹" + Math.round(amount).toLocaleString("en-IN");
}

function renderResults(data) {
  const pred = data.prediction;
  const pau = data.pau_advisory;
  const irr = data.district_irrigation_profile;
  const catVar = getSelectedCatalogVariety();

  const isRice = (data.crop || "").toLowerCase() === "rice";
  const MILLING_RECOVERY = 0.67;

  // Raw district baseline in quintals/ekad
  const districtBaselineYield = isRice
    ? +(pred.expected_yield_q_ekad / MILLING_RECOVERY).toFixed(2)
    : pred.expected_yield_q_ekad;

  // Apply Varietal Adjustment Factor so Expected Yield responds to selected seed variety
  const stdBenchmark = CROP_STANDARD_BENCHMARKS[data.crop];
  const varietyFactor =
    catVar && stdBenchmark ? catVar.benchmark / stdBenchmark : 1.0;

  const adjustedYield = +(districtBaselineYield * varietyFactor).toFixed(2);
  const totalQuintals = +(adjustedYield * data.area_ekad).toFixed(2);
  const mandiRate = parseFloat(mandiRateInput.value) || 0;
  const grossRevenue = totalQuintals * mandiRate;

  // Warning Banner for High-Water / Long-Duration Pusa Varieties
  const alertBox = document.getElementById("variety-alert");
  if (catVar && catVar.restricted) {
    alertBox.className = "alert-banner danger";
    alertBox.innerHTML = `<strong>⚠️ ${catVar.warningTitle}</strong>${catVar.warningText}`;
    alertBox.classList.remove("hidden");
  } else {
    alertBox.classList.add("hidden");
  }

  // KPI 1: Expected Field Yield (Variety-Adjusted)
  document.getElementById("res-yield").textContent = isRice
    ? `${adjustedYield} q/ekad (Paddy)`
    : `${adjustedYield} q/ekad`;

  if (isRice) {
    document.getElementById(
      "res-des-compare"
    ).textContent = `District ML Baseline: ${districtBaselineYield} q/ekad Paddy · Varietal Factor: ${varietyFactor.toFixed(2)}x (${catVar ? catVar.name : "Standard"})`;
  } else if (data.is_pau_horticulture_module) {
    document.getElementById(
      "res-des-compare"
    ).textContent = `PAU Ludhiana Trial Benchmark (${catVar ? catVar.name : "Potato"}) · 20 tonnes/ekad FYM recommended`;
  } else {
    document.getElementById(
      "res-des-compare"
    ).textContent = `District ML Baseline: ${districtBaselineYield} q/ekad · Latest DES (${pred.latest_des_observed_year}): ${pred.latest_des_yield_q_ekad} q/ekad`;
  }

  // KPI 2: Total Expected Harvest
  document.getElementById("res-total").textContent = `${totalQuintals} q`;
  document.getElementById("res-area-sub").textContent = isRice
    ? `Across ${data.area_ekad} ekad (raw harvested paddy)`
    : `Across ${data.area_ekad} ekad`;

  // KPI 3: Variety Benchmark
  const bench = catVar
    ? catVar.benchmark
    : pau.variety_details?.pau_avg_yield_q_ekad;

  if (bench) {
    document.getElementById("res-pau-bench").textContent = `${bench} q/ekad`;
    const gap = +(bench - adjustedYield).toFixed(2);
    document.getElementById("res-pau-gap").textContent =
      gap > 0
        ? `+${gap} q/ekad ideal soil upside vs district forecast`
        : `${Math.abs(gap) === 0 ? "Matches" : Math.abs(gap) + " q/ekad above"} PAU variety benchmark`;
  } else {
    document.getElementById("res-pau-bench").textContent = "N/A";
    document.getElementById("res-pau-gap").textContent = "District crop baseline";
  }

  // KPI 4: Gross Mandi Revenue
  document.getElementById("res-revenue").textContent = formatINR(grossRevenue);
  const lakhs = (grossRevenue / 100000).toFixed(2);
  document.getElementById(
    "res-revenue-sub"
  ).textContent = `₹${lakhs} Lakh gross @ ₹${mandiRate.toLocaleString("en-IN")}/q`;

  // Variety Agronomic Profile Card
  const varBadge = document.getElementById("res-var-badge");
  const specsGrid = document.getElementById("var-specs-grid");
  const agronomyNote = document.getElementById("var-agronomy-note");

  if (catVar) {
    varBadge.textContent = catVar.status;
    varBadge.className = catVar.restricted ? "badge-pill warn" : "badge-pill ok";
    specsGrid.innerHTML = `
      <div class="spec-item"><span>Selected Variety</span><strong>${catVar.name} (${catVar.type})</strong></div>
      <div class="spec-item"><span>Seed-to-Seed Duration</span><strong>${catVar.seedToSeedDays}</strong></div>
      <div class="spec-item"><span>Main Field Duration</span><strong>${catVar.fieldDays}</strong></div>
      <div class="spec-item"><span>Water Requirement</span><strong>${catVar.waterDemand}</strong></div>
      <div class="spec-item" style="grid-column: 1 / -1;"><span>Optimal Sowing &amp; Transplanting Window</span><strong>${catVar.sowingWindow}</strong></div>
    `;
    agronomyNote.textContent = catVar.agronomyNote;
  } else {
    varBadge.textContent = "District Crop Baseline";
    varBadge.className = "badge-pill";
    specsGrid.innerHTML = `
      <div class="spec-item"><span>Crop &amp; Season</span><strong>${data.crop} (${data.season})</strong></div>
      <div class="spec-item"><span>Observed DES History</span><strong>1997–${pred.latest_des_observed_year}</strong></div>
    `;
    agronomyNote.textContent =
      "Refer to PAU Ludhiana Package of Practices for district-specific seed rate and sowing schedule.";
  }

  // Fertilizer Bag Calculator + Split Application Schedule
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
  } else {
    fertPills.innerHTML = `<div class="pill">Consult PAU Ludhiana Package of Practices for exact dose.</div>`;
  }

  const schedBox = document.getElementById("fert-schedule-box");
  if (catVar && catVar.fertSchedule) {
    schedBox.innerHTML = `<strong>Split Application &amp; Field Guidance:</strong> ${catVar.fertSchedule}`;
  } else {
    schedBox.innerHTML = `<strong>Application Guidance:</strong> Apply basal phosphorus at sowing/puddling and split nitrogen across active vegetative growth stages.`;
  }

  // District Irrigation & Rotation Profile
  document.getElementById(
    "res-zone-tag"
  ).textContent = `${data.nabard_agro_climatic_zone.code} · ${data.nabard_agro_climatic_zone.name}`;

  const irrPills = document.getElementById("irr-pills");
  irrPills.innerHTML = `
    <div class="pill">Tubewell Share: <strong>${irr.tubewell_share_pct ?? "N/A"}%</strong></div>
    <div class="pill">Canal Share: <strong>${irr.canal_share_pct ?? "N/A"}%</strong></div>
    <div class="pill">Irrigation Intensity: <strong>${irr.irrigation_intensity_pct ?? "N/A"}%</strong></div>
  `;

  const tw = irr.tubewell_share_pct ?? 0;
  document.getElementById("district-advisory-text").textContent =
    tw >= 60
      ? `${data.district} relies heavily on groundwater tubewells (${tw}% share). Short-duration varieties like PR 126, PB 1509, or early-bulking PP-103 reduce pumping load and fit cleanly into multi-crop rotations.`
      : `${data.district} benefits from strong canal irrigation coverage (${irr.canal_share_pct ?? 0}% share) alongside tubewells (${tw}%), supporting high double-cropping intensity (${irr.irrigation_intensity_pct ?? 0}%).`;

  welcomeCard.classList.add("hidden");
  resultsSection.classList.remove("hidden");
}

initApp();
