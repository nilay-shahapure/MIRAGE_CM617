"""Generate LaTeX table fragments for the supplementary document from data/*.csv and research/*.csv.
Writes report/tables/*.tex. Run from the project root: python3 code/make_supplementary_tables.py
"""
from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA, RES, OUT = ROOT / "data", ROOT / "research", ROOT / "report" / "tables"
OUT.mkdir(exist_ok=True)
R = json.load(open(ROOT / "results" / "results.json"))
TIERNAME = {"T1": "Observed", "T2": "Agency", "T3": "Design"}

def esc(x):
    if x is None or (isinstance(x, float) and np.isnan(x)): return "NR"
    s = str(x)
    for a, b in [("\u20b9", "Rs "), ("\u2265", ">="), ("\u2264", "<="), ("\u2192", "->"), ("\u00d7", "x"), ("\u00b0", " deg"), ("\u2013", "-"), ("\u2014", "-"), ("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " "), ("\u2082", "2"), ("\u00b2", "2"), ("\u00b3", "3"), ("\u2248", "approx. ")]:
        s = s.replace(a, b)
    for a, b in [("\\", "\\textbackslash "), ("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"), ("_", "\\_"), ("{", "\\{"), ("}", "\\}"), ("~", "\\textasciitilde "), ("^", "\\textasciicircum ")]:
        s = s.replace(a, b)
    return s

def url(u):
    if not isinstance(u, str) or not u.strip() or u == "NR": return "NR"
    u = u.split(";")[0].strip().replace(" ", "%20")
    return "\\url{" + u + "}"

def num(x, nd=0):
    try:
        v = float(x)
        if np.isnan(v): return "NR"
        return f"{v:,.{nd}f}"
    except Exception:
        return esc(x)

def longtable(cols, rows, caption, label, colspec, fontsize="\\scriptsize"):
    out = [f"{{{fontsize}\\setlength{{\\tabcolsep}}{{3pt}}", f"\\begin{{longtable}}{{{colspec}}}", f"\\caption{{{caption}}}\\label{{{label}}}\\\\", "\\toprule"]
    out.append(" & ".join(f"\\textbf{{{c}}}" for c in cols) + "\\\\ \\midrule\\endfirsthead")
    out.append("\\toprule " + " & ".join(f"\\textbf{{{c}}}" for c in cols) + "\\\\ \\midrule\\endhead")
    out.append("\\bottomrule\\endfoot")
    for r in rows: out.append(" & ".join(r) + "\\\\")
    out += ["\\end{longtable}}", ""]
    return "\n".join(out)

# ---------------- S-A performance dataset ----------------
p = pd.read_csv(DATA / "mirage_performance.csv")
rows = []
for i, (_, r) in enumerate(p.iterrows()):
    rows.append([str(i + 1), esc(r.site) if str(r.city).split(" (")[0] in str(r.site) else esc(r.site) + ", " + esc(r.city), TIERNAME[r.tier], esc(r.building_type) + " / " + esc(r.system_type), num(r.catchment_area_m2), num(r.rainfall_mm) + " (" + esc(r.rainfall_basis) + ")",
                 esc(r.year_of_volume), num(r.reported_volume_kL, 1), num(r.potential_kL), f"{r.performance_ratio*100:.0f}", f"{r.performance_ratio_c070*100:.0f}--{r.performance_ratio_c090*100:.0f}"])
(OUT / "perf_table.tex").write_text(longtable(["No.", "Site", "Evidence", "Type / system", "Area m$^2$", "Rain mm (basis)", "Year", "Vol. kL", "Pot. kL", "Ratio \\%", "C 0.7--0.9"], rows,
    "Performance dataset: all 35 observations. Evidence: Observed (instrument or tank record named), Agency (agency-reported, no instrument named), Design (design calculation). Potential uses runoff coefficient 0.80; the last column gives the ratio for C = 0.70 and 0.90. Rainfall basis: site-year (reported for that site and year), site-avg (average quoted by the source), city-avg (CSE city figure), city-normal (IMD normal), implied (rain received on roof divided by area).",
    "tab:perf", "l p{2.7cm} l >{\\raggedright\\arraybackslash}p{1.6cm} r p{1.6cm} p{1.1cm} r r r l"))
rows = [[str(i + 1), esc(r.measurement_note), esc(r.source), url(r.url)] for i, (_, r) in enumerate(p.iterrows()) if r.tier != "T3"]
(OUT / "perf_notes.tex").write_text(longtable(["No.", "Measurement note", "Source", "URL"], rows, "Measurement notes and sources for the observed and agency-reported observations (numbers as in Table~\\ref{tab:perf}). The design-calculated rows come from CSE model-project pages, \\url{https://www.cseindia.org/rainwater-harvesting-case-studies}, with volumes stated as a fixed share of area $\\times$ rainfall, and from the CGWB design note for Shram Shakti Bhawan.", "tab:perfnotes", "l p{7.5cm} p{3cm} p{5cm}"))

# ---------------- reconciliation with the mid-term progress report ----------------
recon = [
 ("KITS Ramtek", "about 9\\% (19 of 215.7 m$^3$ received)", "11\\% (19 kL against potential 172.6 kL at C = 0.80); 8.8\\% of rain received; observed tier", "Numbers verified word for word in CGWB (2011) p.73; the midway ratio divided by gross rain, the final divides by potential (rain $\\times$ 0.8). The implied rainfall (599 mm) is below the Ramtek taluka average of 1,043.7 mm, so the monitored period was probably not a full year; with the taluka average the ratio would be 6\\%."),
 ("Goa University", "61--76\\% (900 kL, about 400 m$^2$)", "76\\% in 2010 (3.7 m rainfall); 28\\% in 2008 (partial year) and 19\\% in 2009 using the IMD Panaji normal", "Midway used a range of runoff coefficients; final fixes C = 0.80 and adds the two earlier years reported in the same CSE table."),
 ("BEL Bengaluru", "63--75\\% (about 1,100 kL recharged)", "64\\% (1,100 kL, 2,000 m$^2$, IMD Bengaluru normal 1,077.6 mm)", "Source says the water is harvested and stored for DM-water production, so the system type is storage, not recharge as the midway said."),
 ("Panjab University", "about 79\\% (1,985 m$^3$)", "112\\% (2,100 m$^2$, 1,059.3 mm, C = 0.80); agency-reported tier", "The midway figure used an unstated area or rainfall. The Lok Sabha source gives the volume as ``93\\% of total generated runoff'', i.e. a design share, which is why the ratio exceeds 100\\%."),
 ("Warud", "90\\% (derived from runoff assumption)", "112\\% against potential; 90\\% of rain received; observed tier by the stated rule (flow meter named), with a sensitivity case grading it agency-reported", "Confirmed in CGWB (2011) p.73 (500 m$^2$, 311.30 m$^3$ received, 280.17 m$^3$ recharged). The CGWB wording is identical to Ramtek, so one rule must grade both the same way; the round 90\\% suggests an assumed share, which is why both gradings are reported."),
 ("IIT Delhi Block VI", "not comparable (rainfall NR)", "82\\% using the IMD Safdarjung normal (762.3 mm); agency-reported tier, rainfall basis flagged", "Confirmed in CGWB (2011) p.44 (830 m$^3$ from 1,660 m$^2$). Rainfall period still not reported, so the ratio is indicative."),
 ("Umaid Heritage, Sri Aurobindo Ashram, PAU Ludhiana", "supplementary (mixed catchments or calculated)", "Umaid Heritage excluded (110-acre mixed catchment, internal inconsistency 21.1 vs 2.1 ML); Sri Aurobindo Ashram included as a design calculation (43\\% of potential); PAU excluded (no roof area)", "As the midway said: these are not comparable rooftop cases."),
]
rows = [[esc(a), b, c, d] for a, b, c, d in recon]
(OUT / "recon_table.tex").write_text(longtable(["Case", "Midway check-in", "Final", "Reason for change"], rows, "Reconciliation of the six midway check-in cases with the final dataset. All six are retained; ratios were recomputed with one stated runoff coefficient and a stated rainfall basis.", "tab:recon", "p{2.3cm} p{3.4cm} p{4.6cm} p{5.6cm}"))

# ---------------- S-C screening log ----------------
log = pd.read_csv(DATA / "screening_log.csv")
STEPFIX = lambda t: t.replace("T1 observed volumes (instrument or tank record named)", "observed volumes (instrument or tank record named)").replace("T2 agency-reported volumes", "agency-reported volumes").replace("T3 design calculations", "design calculations")
rows = [[esc(STEPFIX(r["step"])), num(r["count"])] for _, r in log.iterrows()]
(OUT / "screening_table.tex").write_text(longtable(["Step", "Count"], rows, "Screening and inclusion log (counts behind the flow diagram above).", "tab:screen", "p{13cm} r"))

# ---------------- S-D statistics ----------------
pr = R["performance"]; rg = pr["regression"]
stats_tex = r"""
\begin{table}[H]\centering\small
\caption{Performance ratio statistics by evidence tier (runoff coefficient 0.80 unless stated). Observed: instrument or tank record named; Agency: agency-reported, no instrument named; Design: design calculation.}\label{tab:stats}
\begin{tabular}{lrrrrrr}\toprule
Tier & n (sites) & Median & 95\% CI & Range & Share $\geq$ 99\% & Median at C 0.70 / 0.90\\ \midrule
""" + "\n".join(f"{TIERNAME[t]} & {pr[t]['n']} ({pr[t]['sites']}) & {pr[t]['median']*100:.1f}\\% & {pr[t]['ci_lo']*100:.0f}--{pr[t]['ci_hi']*100:.0f}\\% & {pr[t]['min']*100:.0f}--{pr[t]['max']*100:.0f}\\% & {pr[t]['share_ge_1']*100:.0f}\\% & {pr[t]['median_c070']*100:.0f}\\% / {pr[t]['median_c090']*100:.0f}\\%\\\\" for t in ["T1", "T2", "T3"]) + r"""
\bottomrule\end{tabular}
\end{table}

\begin{table}[H]\centering\small
\caption{Exploratory OLS: performance ratio on evidence tier and catchment area, observed and agency-reported observations only (n = """ + str(rg["n"]) + ", R$^2$ = " + f"{rg['r2']:.2f}" + r""").}\label{tab:ols}
\begin{tabular}{lrrr}\toprule
Term & Coefficient & 95\% CI & p\\ \midrule
""" + "\n".join(f"{ {'const': 'Intercept', 'observed': 'Observed tier (1 = yes)', 'log10_area': 'log10 catchment area'}[k] } & {rg['params'][k]:.3f} & {rg['conf_int'][k][0]:.3f} to {rg['conf_int'][k][1]:.3f} & {rg['pvalues'][k]:.3f}\\\\" for k in ["const", "observed", "log10_area"]) + r"""
\bottomrule\end{tabular}
\end{table}
Other tests: Mann-Whitney U (observed vs agency-reported) = """ + f"{pr['T1_vs_T2_mannwhitney']['U']:.0f}, p = {pr['T1_vs_T2_mannwhitney']['p']:.4f}" + r"""; Spearman $\rho$ of ratio against $\log_{10}$ area: all observed and agency-reported """ + f"{rg['spearman_area_all']['rho']:.2f} (p = {rg['spearman_area_all']['p']:.3f})" + r""", observed only """ + f"{rg['spearman_area_T1']['rho']:.2f} (p = {rg['spearman_area_T1']['p']:.2f})" + r""". The positive area correlation across the two tiers reflects the tier split (large agency-monitored institutional roofs are agency-reported, small metered houses are observed) and is not significant within the observed tier. With Warud in the observed tier the OLS tier coefficient is not significant; the regression is exploratory and is not used for any claim in the main report. Observed median excluding the partial-year Goa 2008 observation: """ + f"{pr['T1_excl_partial_year']['median']*100:.1f}\\% (n = {pr['T1_excl_partial_year']['n']})" + r"""; excluding the two storage-limited houses: """ + f"{pr['T1_excl_storage_limited']['median']*100:.1f}\\% (n = {pr['T1_excl_storage_limited']['n']})" + r"""; Warud graded agency-reported instead of observed: observed median """ + f"{pr['T1_excl_warud']['median']*100:.1f}\\% (n = {pr['T1_excl_warud']['n']}), agency-reported median {pr['T2_incl_warud']['median']*100:.1f}\\% (n = {pr['T2_incl_warud']['n']}), Mann-Whitney U = {pr['T2_incl_warud']['mannwhitney_U']:.0f}, p = {pr['T2_incl_warud']['mannwhitney_p']:.4f}" + r"""; site-level medians (years averaged): observed """ + f"{pr['site_level']['T1']['median']*100:.1f}\\%" + r""", agency-reported """ + f"{pr['site_level']['T2']['median']*100:.1f}\\%" + r""".
"""
(OUT / "stats.tex").write_text(stats_tex)

# ---------------- S-E cost dataset ----------------
c = pd.read_csv(DATA / "mirage_cost.csv")
rows = [[str(i + 1), esc(r.site) if str(r.city) in str(r.site) else esc(r.site) + ", " + esc(r.city), esc(r.building_scale) + " / " + esc(r.system_type), num(r.catchment_area_m2), num(r.capital_cost_inr), str(int(r.cost_year)), num(r.annual_yield_kL), esc(r.yield_basis), num(r.capital_2024_inr), num(r.cost_per_kL_design_2024, 1)] for i, (_, r) in enumerate(c.iterrows())]
(OUT / "cost_table.tex").write_text(longtable(["No.", "Site", "Scale / system", "Area m$^2$", "Capital Rs", "Year", "Yield kL/yr", "Yield basis", "Capital 2024 Rs", "Rs/kL"], rows,
    "Cost dataset: 27 systems. Capital deflated to 2024 rupees with CPI-IW (RBI Table 37, linked series); levelised cost = capital $\\times$ (CRF at 8\\%, 15 years + 0.02) / annual yield. The 8\\% rate is our assumption; the 15-year life and 2\\% O\\&M are the CGWB manual's norms and its example uses 15\\% (Table~\\ref{tab:coststats}). Source URLs and quotes for every row are in the source extraction table supplied with the data.",
    "tab:cost", "l p{3.2cm} p{2.3cm} r r l r p{1.6cm} r r"))
cst = R["cost"]
cost_stats = r"""
\begin{table}[H]\centering\small
\caption{Levelised cost per kL of design yield (2024 rupees) by group, and sensitivity.}\label{tab:coststats}
\begin{tabular}{lrrr}\toprule
Group & n & Median Rs/kL & Range\\ \midrule
All & """ + f"{cst['overall']['n']} & {cst['overall']['median']:.1f} (95\\% CI {cst['overall']['ci_lo']:.1f}--{cst['overall']['ci_hi']:.1f}) & IQR {cst['overall']['q25']:.1f}--{cst['overall']['q75']:.1f}" + r"""\\
""" + "\n".join(f"{g} & {cst[g]['n']} & {cst[g]['median']:.1f} & {cst[g]['min']:.1f}--{cst[g]['max']:.1f}\\\\" for g in ["individual house", "residential colony", "institutional", "industrial"]) + "\n" + "\n".join(f"system: {g} & {cst['system_'+g]['n']} & {cst['system_'+g]['median']:.1f} & \\\\" for g in ["recharge", "storage", "both"]) + r"""
CSE Delhi-NCR rows (2000--2004) & """ + f"{cst['cse_delhi_only']['n']} & {cst['cse_delhi_only']['median']:.1f} &" + r"""\\
Rows with cost year $\geq$ 2010 & """ + f"{cst['post2010']['n']} & {cst['post2010']['median']:.1f} &" + r"""\\
Sensitivity: 20-year life, 6\% discount & 27 & """ + f"{cst['sensitivity_20yr_6pct_median']:.1f} &" + r"""\\
Sensitivity: 15\% discount (the CGWB example rate) & 27 & """ + f"{cst['sensitivity_15pct_median']:.1f} &" + r"""\\
Rows with cost year $\geq$ 2010 at observed yield & 5 & """ + f"{cst['post2010_delivered_median']:.0f} &" + r"""\\
At observed yield (multiplier """ + f"{cst['delivered_yield_multiplier']:.2f}" + r""") & 27 & """ + f"{cst['overall_delivered_median']:.0f} &" + r"""\\
\bottomrule\end{tabular}
\end{table}
Kruskal-Wallis across the four building-scale groups: H = """ + f"{cst['kruskal_scale']['H']:.2f}, p = {cst['kruskal_scale']['p']:.3f}" + r""". Spearman $\rho$ of $\log_{10}$ area against Rs/kL: """ + f"{cst['spearman_area_cost']['rho']:.2f} (p = {cst['spearman_area_cost']['p']:.4f}, n = {cst['spearman_area_cost']['n']})" + r"""; against capital per m$^2$: """ + f"{cst['spearman_area_capital_per_m2']['rho']:.2f} (p = {cst['spearman_area_capital_per_m2']['p']:.4f})" + r""". The delivered-yield multiplier is the design-calculated median ratio (design yield as a share of potential, """ + f"{pr['T3']['median']:.2f}" + r""") divided by the observed median (""" + f"{pr['T1']['median']:.2f}" + r""").
"""
(OUT / "cost_stats.tex").write_text(cost_stats)
b = pd.read_csv(RES / "cost_benchmarks.csv")
rows = [[esc(r["item"]), esc(r["city"]), esc(r["value"]), esc(r["unit"]), esc(r["year"]), url(r["url"])] for _, r in b.iterrows()]
(OUT / "bench_table.tex").write_text(longtable(["Item", "City", "Value", "Unit", "Year", "URL"], rows, "Price benchmarks collected. The eight used in the cost figure of the main report are the Chennai lowest and top domestic slabs, the Delhi 20--30 kL slab, the BWSSB production cost, Chennai desalination O\\&M, the Metrowater 9 kL tanker, and the Bengaluru 2024 and Chennai 2019 private tanker prices (Rs per load divided by load volume).", "tab:bench", "p{4cm} p{1.5cm} p{2.5cm} p{2.1cm} p{1.7cm} p{3.4cm}", "\\tiny"))

# ---------------- S-F functionality ----------------
f = pd.read_csv(DATA / "mirage_functionality.csv")
rows = [[str(i + 1), esc(r.label), esc(r.population), num(r.sample_n), f"{r.pct_functional:.0f}", esc(r.definition), esc(r.conducted_by)] for i, (_, r) in enumerate(f.iterrows())]
(OUT / "func_table.tex").write_text(longtable(["No.", "Survey", "Population", "n", "Functional \\%", "Definition used", "Conducted by (reported via)"], rows, "Functional-share estimates: 13 estimates from 12 surveys (the two Dwarka rows are two definitions applied to one DJB report). URLs and quotes are in the source extraction table supplied with the data.", "tab:func", "l p{2.8cm} p{2.6cm} r r p{4.6cm} p{2.9cm}"))
cm = pd.read_csv(DATA / "mirage_compliance.csv")
rows = [[esc(r.label), esc(r.population), num(r.denominator), num(r.numerator), f"{r.pct_with_structure:.1f}", esc(r.definition)] for _, r in cm.iterrows()]
(OUT / "compl_table.tex").write_text(longtable(["City", "Population", "Denominator", "With RWH", "\\%", "Definition"], rows, "Installation (compliance) figures used in the mandate-gap figure of the main report.", "tab:compl", "p{2.5cm} p{3.4cm} r r r p{5.5cm}"))
fm = pd.read_csv(DATA / "mirage_failure_modes.csv")
rows = [[esc(r.category), num(r.distinct_sources), num(r.mentions), esc(r.cities)] for _, r in fm.iterrows()]
(OUT / "fm_table.tex").write_text(longtable(["Failure mode", "Sources", "Mentions", "Cities"], rows, f"Failure-mode categories ({len(fm)} after collapsing), number of distinct sources citing each (90 mentions from 40 distinct sources; these overlap with but are not the same set as the 46 survey records), and the cities concerned. Every mention with URL and quote is in the source extraction table supplied with the data.", "tab:fm", "p{5cm} r r p{7.5cm}"))

# ---------------- S-G mandates ----------------
m = pd.read_csv(DATA / "mirage_mandates.csv")
rows = [[esc(r.jurisdiction), esc(r.instrument), esc(r.year_enacted), esc(r.applicability_threshold), esc(r.penalty_or_incentive), esc(r.reported_compliance)] for _, r in m.iterrows()]
(OUT / "mandate_table.tex").write_text(longtable(["Jurisdiction", "Instrument", "Year", "Applies to", "Penalty / incentive", "Reported compliance"], rows, "Mandate landscape, 24 jurisdictions. URLs and quotes are in the source extraction table supplied with the data.", "tab:mandates", "p{2.1cm} p{3cm} p{1.3cm} p{3cm} p{2.9cm} p{3.4cm}", "\\tiny"))
ri = pd.read_csv(RES / "reference_inputs.csv")
rows = [[esc(r["item"]), esc(r["value"]), esc(r["unit"]), esc(r["period_or_year"]), esc(r["source_document"])] for _, r in ri.iterrows() if str(r["item"]).startswith(("Runoff", "Normal", "Average"))]
(OUT / "refinputs_table.tex").write_text(longtable(["Item", "Value", "Unit", "Period", "Source document"], rows, "Runoff coefficients and rainfall normals used. The CGWB (2007) Table 7.2 values were verified directly in the manual.", "tab:refinputs", "p{4.8cm} p{2.3cm} p{1.4cm} p{2.1cm} p{5.2cm}"))

# ---------------- S-H source list ----------------
srcs = []
for fn, idcol, namecol in [("performance_cases.csv", "case_id", "case_name"), ("cost_cases.csv", "case_id", "case_name"), ("functionality_surveys.csv", "survey_id", "conducted_by"), ("mandates.csv", None, "jurisdiction"), ("cost_benchmarks.csv", None, "item")]:
    d = pd.read_csv(RES / fn)
    for _, r in d.iterrows():
        u = str(r.url) if "url" in d.columns else ""
        for uu in u.replace("|", ";").split(";"):
            uu = uu.strip()
            if uu and uu != "NR" and uu.startswith("http"):
                srcs.append((uu.replace(" ", "%20"), {"performance_cases": "Performance", "cost_cases": "Cost", "functionality_surveys": "Functionality", "mandates": "Mandates", "cost_benchmarks": "Benchmarks"}[fn.replace(".csv", "")], str(r[namecol])[:60]))
S = pd.DataFrame(srcs, columns=["url", "strand", "used_for"]).drop_duplicates("url")
S = S.sort_values("url")
rows = [["\\url{" + r.url + "}", esc(r.strand), esc(r.used_for)] for _, r in S.iterrows()]
(OUT / "sources_table.tex").write_text(longtable(["URL", "Strand", "First use"], rows, f"All {len(S)} distinct source URLs used, with the strand and the first record each supports.", "tab:sources", "p{9.2cm} p{2.5cm} p{4.2cm}", "\\tiny"))
print("tables written; sources:", len(S))
