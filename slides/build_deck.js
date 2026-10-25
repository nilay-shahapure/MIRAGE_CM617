// Builds slides/MIRAGE_presentation.pptx from the figures and results.
// Run from the project root: node slides/build_deck.js
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");
const { applyTheme } = require("./apply_theme.js");

const ROOT = path.resolve(__dirname, "..");
const FIG = (n) => path.join(ROOT, "figures", n);
const R = JSON.parse(fs.readFileSync(path.join(ROOT, "results", "results.json")));
const pr = R.performance, mg = R.mandate_gap, cst = R.cost;

const THEME = {
  name: "MIRAGE water",
  headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "0F2A3F", lt1: "FFFFFF", dk2: "1F4E79", lt2: "EEF3FB", accent1: "2A78D6", accent2: "EB6834", accent3: "6250D6", accent4: "52514E", accent5: "8A8984", accent6: "1BAF7A", hlink: "2A78D6", folHlink: "6250D6" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";           // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "MIRAGE team, CM617"; pres.title = "MIRAGE: Measuring the Impact and Reality of Rainwater Harvesting Mandates";
const C = pres.SchemeColor;

// ---------- layouts ----------
pres.defineSlideMaster({ title: "DARK", background: { color: "0F2A3F" },
  objects: [{ text: { text: "MIRAGE | CM617 course project", options: { x: 0.5, y: 5.2, w: 5, h: 0.3, fontSize: 9, color: "8FB3D9", isTextBox: true, margin: 0 } } }],
  slideNumber: { x: 9.2, y: 5.2, w: 0.5, h: 0.3, fontSize: 9, color: "8FB3D9" } });
pres.defineSlideMaster({ title: "LIGHT", background: { color: "FFFFFF" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9, h: 0.7, fontSize: 26, bold: true, color: C.text2, margin: 0, valign: "middle" }, text: "" } },
    { text: { text: "MIRAGE | CM617 course project", options: { x: 0.5, y: 5.2, w: 5, h: 0.3, fontSize: 9, color: C.accent5, isTextBox: true, margin: 0 } } }],
  slideNumber: { x: 9.2, y: 5.2, w: 0.5, h: 0.3, fontSize: 9, color: C.accent5 } });

const body = (slide, text, o) => slide.addText(text, Object.assign({ fontSize: 14, color: C.text1, isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 6 }, o));
const bullets = (arr) => arr.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < arr.length - 1 } }));
const stat = (slide, x, y, w, big, small, col) => {
  slide.addText(big, { x, y, w, h: 0.8, fontSize: 40, bold: true, color: col || C.accent1, isTextBox: true, margin: 0, align: "left", valign: "bottom" });
  slide.addText(small, { x, y: y + 0.82, w, h: 0.7, fontSize: 12, color: C.accent4, isTextBox: true, margin: 0, valign: "top" });
};
const card = (slide, x, y, w, h, head, text, fill) => {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill || "EEF3FB" }, line: { color: fill || "EEF3FB" }, rectRadius: 0.08 });
  slide.addText(head, { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: 0.4, fontSize: 14, bold: true, color: C.text2, isTextBox: true, margin: 0 });
  slide.addText(text, { x: x + 0.15, y: y + 0.5, w: w - 0.3, h: h - 0.6, fontSize: 11.5, color: C.text1, isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 4 });
};
const pct = (v, d = 0) => (v * 100).toFixed(d) + "%";
const pngSize = (file) => { const b = fs.readFileSync(file); return { width: b.readUInt32BE(16), height: b.readUInt32BE(20) }; };
const ALT = { "fig1_performance_gap.png": "Reported yield against theoretical potential, by evidence tier", "fig2_mandate_gap.png": "Installation shares, functional shares and the Chennai cascade", "fig3_failure_modes.png": "Reported reasons systems fail, by number of sources", "fig4_cost_per_kL.png": "Levelised cost per kilolitre by building scale" };
const img = (slide, name, x, y, w, maxH) => { const d = pngSize(FIG(name)); let h = w * d.height / d.width; if (h > maxH) { h = maxH; w = h * d.width / d.height; } slide.addImage({ path: FIG(name), x, y, w, h, altText: ALT[name] || "figure" }); return h; };

// ---------- 1 title ----------
pres.addSection({ title: "Opening" });
let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Opening" });
s.addText("MIRAGE", { x: 0.6, y: 0.9, w: 8.8, h: 1.0, fontSize: 54, bold: true, color: "FFFFFF", fontFace: "Cambria", isTextBox: true, margin: 0 });
s.addText("Measuring the Impact and Reality of Rainwater Harvesting Mandates", { x: 0.6, y: 1.9, w: 8.8, h: 0.6, fontSize: 24, color: "CADCFC", isTextBox: true, margin: 0 });
s.addText("A meta-analysis of rooftop rainwater harvesting performance in Indian cities", { x: 0.6, y: 2.5, w: 8.8, h: 0.5, fontSize: 16, color: "8FB3D9", isTextBox: true, margin: 0 });
s.addText("Vedant Abhangrao (23B2262)  |  Nilay Shahapure (23B2206)  |  Arjun Jhunjhunwala (23B1245)  |  Yash Krishnani (23B1240)", { x: 0.6, y: 3.6, w: 8.8, h: 0.4, fontSize: 13, color: "FFFFFF", isTextBox: true, margin: 0 });
s.addText("CM617 Sustainability Principles and Practices, IIT Bombay. Pathway 1: Sustainability Research. Sector: Water.", { x: 0.6, y: 4.0, w: 8.8, h: 0.4, fontSize: 12, color: "8FB3D9", isTextBox: true, margin: 0 });
s.addNotes("Title slide. MIRAGE is a meta-analysis of published performance data for rooftop rainwater harvesting in Indian cities.");

// ---------- 2 problem ----------
pres.addSection({ title: "Problem and questions" });
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Problem and questions" });
s.addText("Twenty years of mandates, almost no measurement", { placeholder: "title" });
stat(s, 0.5, 1.2, 2.8, "2003", "Chennai makes RWH compulsory for every building; Bengaluru, Delhi, Mumbai and 20+ others follow");
stat(s, 3.6, 1.2, 2.8, "33", "states and union territories have adopted the Model Building Bye-Laws 2016 RWH provision");
stat(s, 6.7, 1.2, 2.8, "None", "consolidated quantitative syntheses of what installed systems deliver that we could find", C.accent2);
card(s, 0.5, 3.0, 9, 1.9, "The gap in the evidence",
  "Mandates are enforced at plan approval: no completion certificate or water connection without a structure. After that, checks are rare and results are not published. Single-building case studies, agency demonstration reports and newspaper audits exist, but we found no study that combines them. MIRAGE collects the published numbers, puts them on one scale and asks what the mandate delivers.");
s.addNotes("Set up the problem: compliance is enforced on paper, performance is not measured.");

// ---------- 3 questions and searches ----------
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Problem and questions" });
s.addText("Three questions, four searches", { placeholder: "title" });
card(s, 0.5, 1.15, 2.9, 1.7, "Q1. Performance gap", "How much of the theoretical rooftop potential do documented systems actually harvest or recharge?");
card(s, 3.55, 1.15, 2.9, 1.7, "Q2. Functionality", "What share of installed systems stay functional, and why do they fail?");
card(s, 6.6, 1.15, 2.9, 1.7, "Q3. Cost", "What does harvested water cost per kilolitre compared with piped, desalinated and tanker water?");
const strands = [["89", "performance site records"], ["43", "cost records + 37 price benchmarks"], ["46", "surveys, audits, inspections; 40 sources state failure reasons"], ["24", "mandate instruments"]];
strands.forEach((t, i) => stat(s, 0.5 + i * 2.3, 3.1, 2.2, t[0], t[1]));
body(s, "Sources: CGWB compilations and manual, CSE case studies, Lok Sabha replies, Delhi Jal Board and NGT reports, Arghyam, journal papers, campus and company reports, IMD normals, RBI CPI. Every number logged with its URL and the sentence or values taken from the page.", { x: 0.5, y: 4.55, w: 9, h: 0.6, fontSize: 11, color: C.accent4 });
s.addNotes("Explain the four parallel searches and the logging rule: no number without a URL and a quote.");

// ---------- 4 methods ----------
pres.addSection({ title: "Methods" });
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Methods" });
s.addText("One metric, three evidence tiers", { placeholder: "title" });
s.addShape(pres.ShapeType.roundRect, { x: 0.5, y: 1.15, w: 9, h: 0.75, fill: { color: "EEF3FB" }, line: { color: "EEF3FB" }, rectRadius: 0.08 });
s.addText([{ text: "Potential P = Area (m2) x Rainfall (mm) x C / 1000   [kL/yr]      ", options: { bold: true } }, { text: "Performance ratio = reported volume / P.   C = 0.80 (CGWB manual, Table 7.2: concrete 0.7 to GI sheet 0.9); sensitivity 0.70 and 0.90." }],
  { x: 0.7, y: 1.2, w: 8.6, h: 0.65, fontSize: 12.5, color: C.text1, isTextBox: true, margin: 0, valign: "middle" });
card(s, 0.5, 2.1, 2.9, 1.75, "Observed", `Source names a flow meter, a measuring device at the recharge well or a tank-filling record. ${pr.T1.n} observations, ${pr.T1.sites} sites.`, "E3EDFB");
card(s, 3.55, 2.1, 2.9, 1.75, "Agency-reported", `Annual volume stated by CGWB or another agency, no instrument named, or given as a share of estimated runoff. ${pr.T2.n} observations, ${pr.T2.sites} sites.`, "FBE8E0");
card(s, 6.6, 2.1, 2.9, 1.75, "Design calculation", `CSE model projects and one CGWB design note where the 'volume harvested' is a stated share of area x rainfall. ${pr.T3.n} sites.`, "ECEAFA");
body(s, bullets(["Screening: 89 site records found (17 not accessible, 7 added from the cost search and the CGWB compilation), 79 screened, 47 excluded (20 potential only, 9 no area or volume, 3 modelled, 10 no roof area, 5 mixed or inconsistent), 35 observations at 31 sites included",
  "Costs: deflated to 2024 rupees (CPI-IW); 15-year life and O&M 2% of capital are CGWB norms, 8% discount is our assumption (CGWB example: 15%); divided by design yield, then rescaled to observed yield",
  "Functionality: 13 functional-share estimates from 12 surveys; 90 failure-mode mentions from 40 sources coded into 11 categories"]), { x: 0.5, y: 4.0, w: 9, h: 1.2, fontSize: 11 });
s.addNotes("Walk through the formula and why the tiers matter: the method the source used decides what the number means.");

// ---------- 5 result 1 figure ----------
pres.addSection({ title: "Results" });
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Results" });
s.addText("Result 1: in the seven observed cases, yield is about a quarter of potential", { placeholder: "title" });
img(s, "fig1_performance_gap.png", 0.5, 1.1, 9.0, 2.9);
body(s, "Left: reported volume against potential (log scales), 1:1 and 1:4 lines. Right: performance ratio by evidence tier, bars are medians. Observed volumes sit well below agency-reported ones, which cluster at 100% of potential.", { x: 0.5, y: 4.15, w: 9, h: 0.9, fontSize: 11.5, color: C.accent4 });
s.addNotes("The headline figure. Point out the blue observed points below the 1:4 line and the orange agency points at or above 1:1.");

// ---------- 6 result 1 numbers ----------
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Results" });
s.addText("Who measured it decides the answer", { placeholder: "title" });
stat(s, 0.5, 1.15, 2.9, pct(pr.T1.median), `Observed median, n = ${pr.T1.n} at ${pr.T1.sites} sites. 95% CI ${pct(pr.T1.ci_lo)} to ${pct(pr.T1.ci_hi)}; range ${pct(pr.T1.min)} to ${Math.floor(pr.T1.max * 100)}%`);
stat(s, 3.55, 1.15, 2.9, pct(pr.T2.median), `Agency-reported median, n = ${pr.T2.n} at ${pr.T2.sites} sites. ${Math.round(pr.T2.share_ge_1 * pr.T2.n)} of ${pr.T2.n} at or above 99% of potential, the most a roof can give at C = 0.80`, C.accent2);
stat(s, 6.6, 1.15, 2.9, pct(pr.T3.median), `Design-calculated median, n = ${pr.T3.n}. These are the shares CSE assumed, not measurements`, C.accent3);
card(s, 0.5, 3.0, 4.4, 2.0, "Sensitivity checks",
  `Observed median between ${pct(pr.T1.median_c090)} and ${pct(pr.T1.median_c070)} for C from 0.90 to 0.70. Dropping the partial-year Goa 2008 observation: ${pct(pr.T1_excl_partial_year.median)}. Dropping the two storage-limited houses: ${pct(pr.T1_excl_storage_limited.median)}.\nObserved vs agency-reported: Mann-Whitney U = ${pr.T1_vs_T2_mannwhitney.U.toFixed(0)}, p = ${pr.T1_vs_T2_mannwhitney.p.toFixed(3)}.`);
card(s, 5.1, 3.0, 4.4, 2.0, "The one borderline case",
  `Warud (112%) counts as observed by the rule (flow meter named) but CGWB gives its volume as a round "90%" of rain received, so it may be an assumed share. Graded agency-reported instead: observed median ${pct(pr.T1_excl_warud.median)} (n = ${pr.T1_excl_warud.n}), agency-reported median ${pct(pr.T2_incl_warud.median)}, p = ${pr.T2_incl_warud.mannwhitney_p.toFixed(3)}.\nPanjab University's agency figure is stated as "93% of total generated runoff": a design share.`);
s.addNotes("The main inference: agency numbers are design numbers. The few metered sites are the only evidence of real performance.");

// ---------- 7 reconciliation with the mid-term progress report ----------
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Results" });
s.addText("The six midway cases, verified and recomputed", { placeholder: "title" });
const rows = [
  [{ text: "Case", options: { bold: true, color: "FFFFFF", fill: { color: "1F4E79" } } }, { text: "Midway check-in", options: { bold: true, color: "FFFFFF", fill: { color: "1F4E79" } } }, { text: "Final (C = 0.80, stated rainfall)", options: { bold: true, color: "FFFFFF", fill: { color: "1F4E79" } } }, { text: "Status", options: { bold: true, color: "FFFFFF", fill: { color: "1F4E79" } } }],
  ["KITS Ramtek (flow meter)", "about 9%", "11% of potential; 19 of 215.7 m3 received", "Verified in CGWB 2011 p.73; observed"],
  ["Goa University", "61 to 76%", "76% (2010); 28% (2008, partial); 19% (2009)", "Verified in CSE 2014; observed"],
  ["BEL Bengaluru", "63 to 75%", "64% (IMD normal 1,077.6 mm)", "Verified; storage, not recharge; agency-reported"],
  ["Panjab University", "about 79%", "112% (2,100 m2, 1,059 mm)", "Volume is '93% of runoff': design share; agency-reported"],
  ["Warud (flow meter)", "90% (runoff assumption)", "112% of potential; 90% of rain received", "Verified in CGWB 2011 p.73; observed by rule, agency-reported in sensitivity"],
  ["IIT Delhi Block VI", "not comparable (rainfall NR)", "82% with IMD Safdarjung normal", "Verified in CGWB 2011 p.44; agency-reported"],
];
s.addTable(rows, { x: 0.5, y: 1.1, w: 9, colW: [2.0, 1.8, 2.7, 2.5], fontSize: 9.5, color: C.text1, border: { type: "solid", pt: 0.5, color: "D9D9D9" }, rowH: 0.38, valign: "middle" });
body(s, "All six cases are kept. With one runoff coefficient and a stated rainfall basis, two cases (Panjab University, Warud) move above 100% of potential; a volume above potential is a design share, not a measurement. Umaid Heritage and PAU Ludhiana stay excluded (mixed catchment, no roof area); Sri Aurobindo Ashram is a design calculation.", { x: 0.5, y: 4.45, w: 9, h: 0.7, fontSize: 10.5, color: C.accent4 });
s.addNotes("Show continuity with the midway check-in and explain each revision.");

// ---------- 8 result 2 figure ----------
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Results" });
s.addText("Result 2: installed is not the same as working", { placeholder: "title" });
img(s, "fig2_mandate_gap.png", 0.5, 1.1, 9.0, 2.85);
body(s, `Installation: 60% of 2.72 lakh houses inspected in Chennai (2019), 56% in Hyderabad, 18% of connected properties in Bengaluru, below 1% in Pune and Nagpur. Functionality: ${mg.functionality_n} estimates from ${mg.functionality_surveys} surveys, median ${mg.functionality_median.toFixed(0)}% of installed systems working (0 to 84%). Dwarka 2024: 84% structurally intact, only 32% recharging water free of faecal coliform.`, { x: 0.5, y: 4.0, w: 9, h: 1.0, fontSize: 11.5, color: C.accent4 });
s.addNotes("Two separate gaps: installation and functionality. Definitions differ between surveys; sample sizes in brackets.");

// ---------- 9 cascade native chart ----------
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Results" });
s.addText("Chennai: from mandate to water delivered", { placeholder: "title" });
const casc = mg.chennai;
s.addChart(pres.ChartType.bar, [{ name: "Share of mandated potential", labels: ["Mandated", "With a structure", "Needing no repair", "Delivered at observed ratio"], values: [100, casc.with_structure * 100, casc.functional * 100, casc.delivered * 100].map(v => Math.round(v * 10) / 10) }],
  { x: 0.5, y: 1.1, w: 5.4, h: 3.9, barDir: "col", chartColors: ["2A78D6"], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0\"%\"", dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt", dataLabelColor: "0B0B0B",
    catAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", catAxisLabelColor: "52514E", valAxisLabelFontSize: 9, valAxisLabelFontFace: "+mn-lt", valAxisLabelColor: "52514E", valAxisMaxVal: 110, valAxisMinVal: 0, valGridLine: { color: "E6E5E1", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, showTitle: false, barGapWidthPct: 60 });
stat(s, 6.3, 1.2, 3.2, pct(casc.with_structure), "of 2.72 lakh inspected houses had a structure (GCC, Aug-Sep 2019 snapshot)");
stat(s, 6.3, 2.5, 3.2, pct(casc.functional), "needing no repair: 77% of the 1.62 lakh structures, same inspection", C.accent2);
stat(s, 6.3, 3.8, 3.2, pct(casc.delivered), `delivered, at the observed yield ratio of ${pct(pr.T1.median)} (${pct(mg.chennai_excl_warud_delivered)} with Warud regraded). Bengaluru by the same chain: about ${pct(mg.bengaluru.delivered)}`, C.text1);
s.addNotes("The cascade multiplies three independent figures. Say clearly that the last step uses the observed-tier median from a small sample.");

// ---------- 10 failure modes ----------
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Results" });
s.addText("Result 3: why systems fail", { placeholder: "title" });
img(s, "fig3_failure_modes.png", 0.5, 1.15, 5.2, 3.2);
const fmTop = R.failure_modes.slice(0, 4);
card(s, 6.0, 1.15, 3.5, 3.9, "Management causes are cited more often than component faults",
  fmTop.map(f => `${f.category}: ${f.distinct_sources} sources`).join("\n") + "\n\nNo maintenance is cited most often; missing incentive or enforcement ties with poor design or construction. Silted pits (7), disconnected downpipes (6) and clogged filters (3) are the faults a routine inspection would catch.");
body(s, `${R.failure_mode_counts.mentions} mentions from ${R.failure_mode_counts.sources} surveys, audits and reports, counted by distinct source, ${R.failure_mode_counts.categories} categories.`, { x: 0.5, y: 4.45, w: 5.2, h: 0.5, fontSize: 11, color: C.accent4 });
s.addNotes("Connect to the course theme: infrastructure as a service that needs an operator, not a one-time artefact.");

// ---------- 11 cost ----------
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Results" });
s.addText("Result 4: cheap at design yield, below tanker prices at observed yield", { placeholder: "title" });
img(s, "fig4_cost_per_kL.png", 0.5, 1.15, 5.6, 2.6);
stat(s, 6.4, 1.1, 3.1, `Rs ${cst.overall.median.toFixed(0)}/kL`, `median levelised cost at design yield, 27 systems (IQR ${cst.overall.q25.toFixed(0)} to ${cst.overall.q75.toFixed(0)}); recharge Rs ${cst.system_recharge.median.toFixed(0)}, storage Rs ${cst.system_storage.median.toFixed(0)}`);
stat(s, 6.4, 2.85, 3.1, `Rs ${cst.overall_delivered_median.toFixed(0)}/kL`, `at observed yield (multiplier ${cst.delivered_yield_multiplier.toFixed(1)}): within piped tariffs (Rs 7 to 48), below desalination (Rs 68) and tankers (Rs 78 to 375)`, C.accent2);
body(s, bullets([`Cost per kL falls steeply with catchment area (Spearman rho = ${cst.spearman_area_cost.rho.toFixed(2)}, p < 0.001); scale groups not separable at these counts (Kruskal-Wallis p = ${cst.kruskal_scale.p.toFixed(2)})`,
  `Twenty rows are CSE Delhi projects of 2000 to 2004 (median Rs ${cst.cse_delhi_only.median.toFixed(0)}); the five post-2010 rows median Rs ${cst.post2010.median.toFixed(0)}, about Rs ${cst.post2010_delivered_median.toFixed(0)} at observed yield, inside the tanker range. 2024 rupees, 15-year life, 8% (Rs ${cst.sensitivity_15pct_median.toFixed(0)} at 15%), O&M 2%`]), { x: 0.5, y: 3.85, w: 5.6, h: 1.3, fontSize: 10.5 });
s.addNotes("Cost does not explain the gap. Even at observed yield harvested water beats the tanker water the same cities buy in dry years.");

// ---------- 12 discussion ----------
pres.addSection({ title: "Discussion" });
s = pres.addSlide({ masterName: "DARK", sectionTitle: "Discussion" });
s.addText("Unmeasured and under-delivering; reported failures point to enforcement", { x: 0.5, y: 0.35, w: 9, h: 0.7, fontSize: 22, bold: true, color: "FFFFFF", fontFace: "Cambria", isTextBox: true, margin: 0 });
s.addText(bullets(["The mandates increased installation. Agencies report what they designed; we found only five metered sites, and those deliver about a quarter of potential.",
  "Structures installed is an output indicator. Water delivered is the outcome. The mandates count structures, not water.",
  "Reported failures point to maintenance and enforcement first; the technical faults listed are ones an inspection would catch.",
  "Cost: within piped tariffs at design yield and below tanker prices even at observed yield for the median system. For an owner, recharge still costs more than piped water while the benefit is shared, so incentives matter."]),
  { x: 0.5, y: 1.15, w: 4.6, h: 3.9, fontSize: 13, color: "FFFFFF", isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 8 });
const recs = [["1. Measure", "Require a flow meter or recharge-well level logger on systems above a size threshold, so performance can be verified at all."],
  ["2. Inspect, then pay", "Tie rebates and penalties to a periodic functional inspection, not a one-time completion certificate. Dwarka shows intact structures can recharge contaminated water."],
  ["3. Publish", "Report installed-versus-functional counts every year, as Chennai did in 2019, so the gap is visible."]];
recs.forEach((r, i) => { s.addShape(pres.ShapeType.roundRect, { x: 5.4, y: 1.15 + i * 1.3, w: 4.1, h: 1.15, fill: { color: "1F4E79" }, line: { color: "1F4E79" }, rectRadius: 0.08 });
  s.addText(r[0], { x: 5.55, y: 1.2 + i * 1.3, w: 3.8, h: 0.35, fontSize: 13, bold: true, color: "CADCFC", isTextBox: true, margin: 0 });
  s.addText(r[1], { x: 5.55, y: 1.55 + i * 1.3, w: 3.8, h: 0.75, fontSize: 10.5, color: "FFFFFF", isTextBox: true, margin: 0, valign: "top" }); });
s.addNotes("Close the argument and give the three recommendations.");

// ---------- 13 limitations ----------
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Discussion" });
s.addText("Limitations", { placeholder: "title" });
card(s, 0.5, 1.15, 4.4, 1.85, "Small observed tier", `${pr.T1.n} observations at ${pr.T1.sites} sites, two of them storage-limited houses and one borderline (Warud). The ${pct(pr.T1.median)} figure is indicative, not representative. Publication bias favours showcase systems, so the true gap is probably larger. Ramtek's low ratio is partly an intake limit of the dug well.`);
card(s, 5.1, 1.15, 4.4, 1.85, "Heterogeneous inputs", "Four observations use an IMD city normal and four a CSE city average, not the year's rainfall. Panjab University's area and volume come from different documents. CSE design calculations use roof plus paved area.");
card(s, 0.5, 3.15, 4.4, 1.85, "Surveys differ", "Definitions range from 'needing no repair' to 'dry pit'; two estimates come from one Dwarka report and one is an expert estimate. Several figures reach us only through press reports; originals cited where found.");
card(s, 5.1, 3.15, 4.4, 1.85, "Costs and causality", "Cost rows are dominated by one programme (CSE Delhi, 2000 to 2004) and depend on the discount rate. Associations are not causal; a weak private incentive to maintain recharge pits is a competing explanation. All of these show why metering is needed.");
s.addNotes("Be plain about what the data can and cannot support.");

// ---------- 14 contributions and package ----------
pres.addSection({ title: "Closing" });
s = pres.addSlide({ masterName: "LIGHT", sectionTitle: "Closing" });
s.addText("Contributions and what is submitted", { placeholder: "title" });
const team = [["Nilay Shahapure", "Analysis (harmonisation, statistics, figures); report, supplementary document, presentation"], ["Vedant Abhangrao", "Analysis (screening rules, evidence grading, cost method, reconciliation)"], ["Arjun Jhunjhunwala", "Sourcing: locating documents, extracting source records"], ["Yash Krishnani", "Sourcing: locating documents, extracting source records"]];
team.forEach((t, i) => card(s, 0.5, 1.15 + i * 0.9, 4.4, 0.8, t[0], t[1]));
card(s, 5.1, 1.15, 4.4, 3.65, "Submitted",
  "Report (2 pages, IMRaD) and Supplementary Information (15 pages: full tables, screening log, reconciliation with the mid-term report, 168 source URLs)\n\nData: harmonised dataset for performance, cost, functionality, installation, failure modes and mandates; source extraction tables with a URL and the quoted values for every number\n\nCode: Python scripts that rebuild the dataset, statistics, figures and tables\n\nEvery number in the report is traceable to a source URL and the sentence or values taken from the page.\n\nCode repository: github.com/nilay-shahapure/MIRAGE_CM617");
body(s, "AI tools helped with code, figures, searches and drafting; the statement is in the Supplementary Information.", { x: 0.5, y: 4.9, w: 4.4, h: 0.28, fontSize: 9.5, color: C.accent4 });
s.addNotes("Statement of contributions, as required for the final presentation.");

(async () => {
  const out = path.join(__dirname, "MIRAGE_presentation.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("written", out);
})();
