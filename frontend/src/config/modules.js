export const MODULES = {
  khtt: {
    slug: "khtt",
    title: "K-HTT Analyst",
    short: "K-HTT",
    description:
      "Komatsu Hot Tube Tester — AI Vision rating endapan 0–10 (Nikko Color Scale) untuk oli & pelumas.",
    ratingOptions: ["Excellent", "Good", "Fair", "Poor", "Reject"],
    ratingLabel: "Overall Rating",
    parameters: [
      { key: "appearance", label: "Appearance", unit: "", type: "text" },
      { key: "color", label: "Color (ASTM D1500)", unit: "", type: "text" },
      { key: "water_content", label: "Water Content", unit: "% vol", type: "number" },
      { key: "sediment", label: "Sediment", unit: "% wt", type: "number" },
      { key: "total_acid_number", label: "Total Acid Number", unit: "mg KOH/g", type: "number" },
      { key: "kinematic_viscosity", label: "Kinematic Viscosity @40°C", unit: "cSt", type: "number" },
      { key: "flash_point", label: "Flash Point", unit: "°C", type: "number" },
      { key: "thermal_stability", label: "Thermal Stability Index", unit: "", type: "text" },
    ],
  },
  "copper-strip": {
    slug: "copper-strip",
    title: "Copper Strip ASTM D130",
    short: "Copper Strip",
    description:
      "Uji korosi bilah tembaga (copper strip corrosion) sesuai standar ASTM D130.",
    ratingOptions: ["1a", "1b", "2a", "2b", "2c", "2d", "2e", "3a", "3b", "4a", "4b", "4c"],
    ratingLabel: "Classification (ASTM D130)",
    parameters: [
      { key: "test_temperature", label: "Test Temperature", unit: "°C", type: "number" },
      { key: "test_duration", label: "Test Duration", unit: "hours", type: "number" },
      { key: "strip_appearance", label: "Strip Appearance", unit: "", type: "text" },
      { key: "tarnish_level", label: "Tarnish Level", unit: "", type: "text" },
      { key: "bath_medium", label: "Bath Medium", unit: "", type: "text" },
    ],
  },
  "rating-dka": {
    slug: "rating-dka",
    title: "Rating DKA",
    short: "Rating DKA",
    description:
      "Analisa batch hingga 4 tabung per foto dengan AI Vision + OCR label — kategori CLEAR · Aspect 1 · Aspect 2 · Aspect 3.",
    ratingOptions: ["A - Sangat Baik", "B - Baik", "C - Cukup", "D - Kurang", "E - Buruk"],
    ratingLabel: "DKA Rating",
    parameters: [
      { key: "deposit_level", label: "Deposit Level", unit: "merit", type: "number" },
      { key: "carbon_residue", label: "Carbon Residue", unit: "% wt", type: "number" },
      { key: "oxidation_stability", label: "Oxidation Stability", unit: "min", type: "number" },
      { key: "sludge_content", label: "Sludge Content", unit: "mg/100ml", type: "number" },
      { key: "varnish_rating", label: "Varnish Rating", unit: "merit", type: "number" },
      { key: "color_change", label: "Color Change", unit: "", type: "text" },
    ],
  },
};

export const MODULE_LIST = Object.values(MODULES);
