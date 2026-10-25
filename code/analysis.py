"""MIRAGE analysis: statistics and figures.

Reads  data/mirage_*.csv
Writes figures/fig*.png (300 dpi) and figures/fig*.pdf, results/results.json, results/results.md
Run:   python3 code/analysis.py   (from the project root)
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats
import statsmodels.api as sm
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import style  # noqa: E402

style.apply()
DATA, FIG, RESD = ROOT / "data", ROOT / "figures", ROOT / "results"
FIG.mkdir(exist_ok=True); RESD.mkdir(exist_ok=True)
rng = np.random.default_rng(2206)

BLUE, ORANGE, VIOLET, INK, INK2, MUTED, GRID = "#2a78d6", "#eb6834", "#6250d6", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
TIER = {"T1": ("Observed volume (instrument or tank record)", BLUE, "o"),
        "T2": ("Agency-reported volume", ORANGE, "s"),
        "T3": ("Design calculation (CSE, CGWB design notes)", VIOLET, "^")}

perf = pd.read_csv(DATA / "mirage_performance.csv")
cost = pd.read_csv(DATA / "mirage_cost.csv")
func = pd.read_csv(DATA / "mirage_functionality.csv")
compl = pd.read_csv(DATA / "mirage_compliance.csv")
fm = pd.read_csv(DATA / "mirage_failure_modes.csv")
fm_long = pd.read_csv(DATA / "mirage_failure_modes_long.csv")
N_FM_SOURCES = int(fm_long.survey_or_source_id.nunique()); N_FM_MENTIONS = int(len(fm_long)); N_FM_CATS = int(fm.category.nunique())
R = {}

def r0(v):
    """Round half up to an integer, for labels (Python rounds half to even)."""
    import math
    return int(math.floor(v + 0.5))

def save(fig, name, tight=True):
    bb = "tight" if tight else None
    fig.savefig(FIG / f"{name}.png", bbox_inches=bb); fig.savefig(FIG / f"{name}.pdf", bbox_inches=bb); plt.close(fig)

def boot_median(x, n=5000):
    x = np.asarray(x, float); meds = [np.median(rng.choice(x, len(x), replace=True)) for _ in range(n)]
    return float(np.median(x)), float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))

# ----------------------------------------------------------------------------
# 1. Performance gap
# ----------------------------------------------------------------------------
pr = {}
for t in ["T1", "T2", "T3"]:
    x = perf.loc[perf.tier == t, "performance_ratio"]
    med, lo, hi = boot_median(x)
    pr[t] = dict(n=int(len(x)), sites=int(perf.loc[perf.tier == t, "site"].str.replace(r", \d{4}.*", "", regex=True).str.replace(" (partial year)", "").nunique()),
                 median=med, ci_lo=lo, ci_hi=hi, min=float(x.min()), max=float(x.max()),
                 share_ge_1=float((x >= 0.99).mean()),
                 median_c070=float(perf.loc[perf.tier == t, "performance_ratio_c070"].median()),
                 median_c090=float(perf.loc[perf.tier == t, "performance_ratio_c090"].median()))
t1, t2 = perf.loc[perf.tier == "T1", "performance_ratio"], perf.loc[perf.tier == "T2", "performance_ratio"]
u = stats.mannwhitneyu(t1, t2, alternative="two-sided")
pr["T1_vs_T2_mannwhitney"] = dict(U=float(u.statistic), p=float(u.pvalue))
t1x = perf.loc[(perf.tier == "T1") & (perf.obs_id != "P06"), "performance_ratio"]   # drop partial-year Goa 2008
pr["T1_excl_partial_year"] = dict(n=int(len(t1x)), median=float(t1x.median()))
t1s = perf.loc[(perf.tier == "T1") & (~perf.obs_id.isin(["P16", "P17"])), "performance_ratio"]  # drop storage-limited houses
pr["T1_excl_storage_limited"] = dict(n=int(len(t1s)), median=float(t1s.median()))
t1w = perf.loc[(perf.tier == "T1") & (perf.obs_id != "P02"), "performance_ratio"]   # Warud graded T2 instead
pr["T1_excl_warud"] = dict(n=int(len(t1w)), median=float(t1w.median()))
t2w = pd.concat([perf.loc[perf.tier == "T2", "performance_ratio"], perf.loc[perf.obs_id == "P02", "performance_ratio"]])
uw = stats.mannwhitneyu(t1w, t2w, alternative="two-sided")
pr["T2_incl_warud"] = dict(n=int(len(t2w)), median=float(t2w.median()), mannwhitney_U=float(uw.statistic), mannwhitney_p=float(uw.pvalue))
# site-level (average the Goa years) so one site does not dominate
site = perf[perf.tier.isin(["T1", "T2"])].copy()
site["site_key"] = site.site.str.replace(r", \d{4}.*", "", regex=True).str.replace(" (partial year)", "")
site_level = site.groupby(["site_key", "tier"], as_index=False).performance_ratio.mean()
pr["site_level"] = {t: dict(n=int((site_level.tier == t).sum()), median=float(site_level.loc[site_level.tier == t, "performance_ratio"].median())) for t in ["T1", "T2"]}
# exploratory regression (T1 + T2 only)
d = perf[perf.tier.isin(["T1", "T2"])].copy()
d["observed"] = (d.tier == "T1").astype(int)
X = sm.add_constant(d[["observed", "log10_area"]])
ols = sm.OLS(d.performance_ratio, X).fit()
rho = stats.spearmanr(d.log10_area, d.performance_ratio)
rho_t1 = stats.spearmanr(perf.loc[perf.tier == "T1", "log10_area"], perf.loc[perf.tier == "T1", "performance_ratio"])
pr["regression"] = dict(n=int(ols.nobs), r2=float(ols.rsquared), params={k: float(v) for k, v in ols.params.items()},
                        pvalues={k: float(v) for k, v in ols.pvalues.items()}, conf_int={k: [float(a), float(b)] for k, (a, b) in ols.conf_int().iterrows()},
                        spearman_area_all=dict(rho=float(rho.statistic), p=float(rho.pvalue)), spearman_area_T1=dict(rho=float(rho_t1.statistic), p=float(rho_t1.pvalue)))
R["performance"] = pr

# Figure 1: scatter + strip
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 1.85), gridspec_kw=dict(width_ratios=[1.25, 1]))
lim = [5, 3e5]
ax1.plot(lim, lim, color=INK2, lw=0.9, ls="--", zorder=1)
ax1.plot(lim, [v * 0.25 for v in lim], color=GRID, lw=0.9, ls=":", zorder=1)
ax1.text(1.6e5, 1.75e5, "1:1", fontsize=7, color=INK2, ha="right")
ax1.text(4e4, 6.5e3, "1:4", fontsize=7, color=INK2, ha="right")
for t, (lab, col, mk) in TIER.items():
    s = perf[perf.tier == t]
    ax1.scatter(s.potential_kL, s.reported_volume_kL, s=34, c=col, marker=mk, edgecolor="white", linewidth=0.6, label=lab, zorder=3)
ax1.set_xscale("log"); ax1.set_yscale("log"); ax1.set_xlim(lim); ax1.set_ylim(lim)
ax1.set_xlabel("Potential, catchment area x rainfall x 0.8 (kL/yr)"); ax1.set_ylabel("Reported volume (kL/yr)")
ax1.set_title("a. Reported yield against potential", loc="left")
h, l = ax1.get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=3, fontsize=6.5, handletextpad=0.3, columnspacing=1.2, bbox_to_anchor=(0.5, -0.1), frameon=False)
# strip plot
xpos = {"T1": 0, "T2": 1, "T3": 2}
for t, (lab, col, mk) in TIER.items():
    s = perf[perf.tier == t]
    jitter = rng.uniform(-0.16, 0.16, len(s))
    ax2.scatter(xpos[t] + jitter, s.performance_ratio * 100, s=30, c=col, marker=mk, edgecolor="white", linewidth=0.6, zorder=3)
    ax2.hlines(pr[t]["median"] * 100, xpos[t] - 0.3, xpos[t] + 0.3, color=INK, lw=1.6, zorder=4)
    ax2.text(xpos[t] + 0.33, pr[t]["median"] * 100, f"{pr[t]['median']*100:.0f}%", fontsize=7.5, va="center", color=INK)
ax2.axhline(100, color=INK2, lw=0.9, ls="--")
ax2.text(2.58, 96, "100% at C = 0.80", fontsize=6.3, color=INK2, ha="right", va="top")
ax2.set_xticks([0, 1, 2]); ax2.set_xticklabels([f"Observed\n(n={pr['T1']['n']})", f"Agency-\nreported (n={pr['T2']['n']})", f"Design\ncalc. (n={pr['T3']['n']})"], fontsize=7.5)
ax2.set_ylabel("Ratio (% of potential)"); ax2.set_ylim(0, 140); ax2.set_xlim(-0.5, 2.6)
ax2.set_title("b. Ratio by evidence tier (bar = median)", loc="left")
fig.tight_layout(w_pad=1.5); save(fig, "fig1_performance_gap")

# ----------------------------------------------------------------------------
# 2. Mandate gap: installation, functionality, cascade
# ----------------------------------------------------------------------------
chennai_install = float(compl.loc[compl.label == "Chennai 2019", "pct_with_structure"].iloc[0]) / 100
chennai_func = float(func.loc[func.func_id == "F02", "pct_functional"].iloc[0]) / 100
t1_med = pr["T1"]["median"]
cascade = dict(mandated=1.0, with_structure=chennai_install, functional=chennai_install * chennai_func, delivered=chennai_install * chennai_func * t1_med)
blr_install = float(compl.loc[compl.label == "Bengaluru 2023", "pct_with_structure"].iloc[0]) / 100
blr_func = float(func.loc[func.func_id == "F12", "pct_functional"].iloc[0]) / 100
R["mandate_gap"] = dict(chennai=cascade, bengaluru=dict(with_structure=blr_install, functional=blr_install * blr_func, delivered=blr_install * blr_func * t1_med),
                        functionality_median=float(func.pct_functional.median()), functionality_n=int(len(func)), functionality_surveys=int(func.research_id.str.replace(r"/.*", "", regex=True).nunique()),
                        functionality_min=float(func.pct_functional.min()), functionality_max=float(func.pct_functional.max()),
                        functionality_structural_only_median=float(func[~func.func_id.isin(["F11"])].pct_functional.median()),
                        chennai_excl_warud_delivered=float(chennai_install * chennai_func * pr["T1_excl_warud"]["median"]))

SHORT = {"Chennai 2019 city inspection": "Chennai 2019, all inspected (2.7 lakh)", "Chennai 2019, houses with a structure": "Chennai 2019, needing no repair (1.6 lakh)",
         "Chennai Gandhinagar 2003": "Chennai Gandhinagar 2003 (309)", "Chennai approved buildings 2001-02": "Chennai approved bldgs 2002 (25)",
         "Karnataka school structures 2007": "Karnataka schools 2007 (1,269)", "Karnataka model schools 2009": "Karnataka model schools 2009 (27)",
         "Faridabad public systems 2018-19": "Faridabad public 2018-19 (190)", "Faridabad public systems 2024": "Faridabad public 2024 (200)",
         "Gurugram pits 2023": "Gurugram pits 2023 (500)", "Delhi Dwarka societies 2024 (structural)": "Dwarka 2024, structural (176)",
         "Delhi Dwarka societies 2024 (clean recharge)": "Dwarka 2024, clean water (176)", "Bengaluru BWSSB connections 2023 (expert estimate)": "Bengaluru 2023, expert estimate",
         "Kaithal government buildings 2018": "Kaithal govt bldgs 2018 (5)", "Sirsa park systems 2025": "Sirsa parks 2025 (4)"}
fig = plt.figure(figsize=(7.2, 1.85))
axes = [fig.add_axes([0.11, 0.2, 0.14, 0.68]), fig.add_axes([0.52, 0.2, 0.20, 0.68]), fig.add_axes([0.83, 0.2, 0.16, 0.68])]
ax = axes[0]
c = compl.sort_values("pct_with_structure")
ax.barh(c.label, c.pct_with_structure, color=BLUE, height=0.62)
for y, v in enumerate(c.pct_with_structure):
    ax.text(v + 1.5, y, f"{v:.1f}%" if v < 1 else f"{v:.0f}%", va="center", fontsize=6.5, color=INK)
ax.set_xlim(0, 85); ax.set_xlabel("Properties with a structure (%)"); ax.set_title("a. Installation gap", loc="left"); ax.tick_params(axis="y", labelsize=6.5)
ax = axes[1]
f = func.sort_values("pct_functional")
ax.barh([SHORT.get(l, l) for l in f.label], f.pct_functional, color=ORANGE, height=0.62)
for y, v in enumerate(f.pct_functional):
    ax.text(v + 1.2, y, f"{r0(v)}%", va="center", fontsize=6.5, color=INK)
ax.axvline(func.pct_functional.median(), color=INK2, lw=0.9, ls="--"); ax.text(func.pct_functional.median() + 1.5, 12.6, f"median {r0(func.pct_functional.median())}%", fontsize=6.3, color=INK2, va="bottom")
ax.set_xlim(0, 100); ax.set_xlabel("Installed systems functional (%)"); ax.set_title("b. Functionality gap", loc="left"); ax.tick_params(axis="y", labelsize=6.8)
ax = axes[2]
labels = ["Man-\ndated", "With\nstruc-\nture", "Func-\ntional", "Deli-\nvered"]
vals = [cascade["mandated"], cascade["with_structure"], cascade["functional"], cascade["delivered"]]
ax.bar(range(4), [v * 100 for v in vals], color=[MUTED, BLUE, ORANGE, INK], width=0.62)
for i, v in enumerate(vals):
    ax.text(i, v * 100 + 2, f"{r0(v*100)}%", ha="center", fontsize=6.8, color=INK)
ax.set_xticks(range(4)); ax.set_xticklabels(labels, fontsize=5.8); ax.set_ylim(0, 115); ax.set_ylabel("Share of mandated potential (%)", fontsize=7.5)
ax.set_title("c. Chennai cascade", loc="left")
save(fig, "fig2_mandate_gap")

# ----------------------------------------------------------------------------
# 3. Failure modes
# ----------------------------------------------------------------------------
FMSHORT = {"No maintenance, abandoned": "No maintenance, abandoned", "No awareness, incentive or enforcement": "No incentive or enforcement", "Poor design or construction": "Poor design or construction",
           "Token structure, built for compliance only": "Token structure for approval", "Recharge pit or well silted or choked": "Recharge pit silted or choked", "Downpipes or conveyance broken or disconnected": "Downpipes disconnected",
           "Other (space, vandalism, roof-only design)": "Other (space, vandalism)", "Storage undersized, overflow or leak": "Storage undersized or leaking", "Filter clogged or absent": "Filter clogged or absent",
           "First flush absent or not operated": "First flush not operated", "Water quality concerns, system disused": "Water quality, system disused"}
fig, ax = plt.subplots(figsize=(3.2, 1.8))
f = fm.sort_values("distinct_sources")
ax.barh(f.category.map(FMSHORT), f.distinct_sources, color=BLUE, height=0.62)
for y, v in enumerate(f.distinct_sources):
    ax.text(v + 0.3, y, str(v), va="center", fontsize=7.5, color=INK)
ax.set_xlabel(f"Sources citing the reason (of {N_FM_SOURCES})"); ax.set_xlim(0, 21); ax.tick_params(axis="y", labelsize=7)
ax.set_title("Reported reasons systems fail", loc="left")
fig.subplots_adjust(left=0.46, right=0.97, top=0.89, bottom=0.22); save(fig, "fig3_failure_modes", tight=False)
R["failure_modes"] = fm.to_dict(orient="records"); R["failure_mode_counts"] = dict(sources=N_FM_SOURCES, mentions=N_FM_MENTIONS, categories=N_FM_CATS)

# ----------------------------------------------------------------------------
# 4. Cost-effectiveness
# ----------------------------------------------------------------------------
cst = {}
cst["overall"] = dict(n=int(len(cost)), **dict(zip(["median", "ci_lo", "ci_hi"], boot_median(cost.cost_per_kL_design_2024))), q25=float(cost.cost_per_kL_design_2024.quantile(.25)), q75=float(cost.cost_per_kL_design_2024.quantile(.75)))
for sc, s in cost.groupby("building_scale"):
    cst[sc] = dict(n=int(len(s)), median=float(s.cost_per_kL_design_2024.median()), min=float(s.cost_per_kL_design_2024.min()), max=float(s.cost_per_kL_design_2024.max()))
for sy, s in cost.groupby("system_type"):
    cst["system_" + sy] = dict(n=int(len(s)), median=float(s.cost_per_kL_design_2024.median()))
kw = stats.kruskal(*[s.cost_per_kL_design_2024.values for _, s in cost.groupby("building_scale")])
cst["kruskal_scale"] = dict(H=float(kw.statistic), p=float(kw.pvalue))
cc = cost.dropna(subset=["catchment_area_m2"])
sp = stats.spearmanr(np.log10(cc.catchment_area_m2), cc.cost_per_kL_design_2024)
cst["spearman_area_cost"] = dict(n=int(len(cc)), rho=float(sp.statistic), p=float(sp.pvalue))
sp2 = stats.spearmanr(np.log10(cc.catchment_area_m2), cc.capital_per_m2_2024)
cst["spearman_area_capital_per_m2"] = dict(n=int(len(cc)), rho=float(sp2.statistic), p=float(sp2.pvalue))
design_ratio = pr["T3"]["median"]; obs_ratio = pr["T1"]["median"]
mult = design_ratio / obs_ratio
cst["delivered_yield_multiplier"] = float(mult)
cst["overall_delivered_median"] = float(cost.cost_per_kL_design_2024.median() * mult)
cst["cse_delhi_only"] = dict(n=int(cost.research_id.str.match(r"C(0\d|1\d|22)").sum()), median=float(cost[cost.research_id.str.match(r"C(0\d|1\d|22)")].cost_per_kL_design_2024.median()))
cst["post2010"] = dict(n=int((cost.cost_year >= 2010).sum()), median=float(cost[cost.cost_year >= 2010].cost_per_kL_design_2024.median()))
# sensitivity: 20-year life, 6 % discount
crf20 = 0.06 * 1.06 ** 20 / (1.06 ** 20 - 1)
alt = cost.capital_2024_inr * (crf20 + 0.02) / cost.annual_yield_kL
cst["sensitivity_20yr_6pct_median"] = float(alt.median())
cst["sensitivity_15pct_median"] = float(cost.cost_per_kL_design_2024_disc15.median())
cst["post2010_delivered_median"] = float(cost[cost.cost_year >= 2010].cost_per_kL_design_2024.median() * mult)
R["cost"] = cst
BENCH = [("Chennai piped water, lowest slab (2025)", 7), ("Chennai piped water, top slab (2025)", 48), ("Delhi piped water, 20-30 kL slab", 26.4),
         ("BWSSB production cost, Cauvery (2021)", 41), ("Chennai desalination O&M (2019)", 68), ("Chennai Metrowater tanker, 9 kL (2025)", 77.8),
         ("Bengaluru private tanker, 12 kL, 2024 crisis", 158), ("Chennai private tanker, 12 kL, 2019 crisis", 375)]
R["cost_benchmarks"] = BENCH

fig, ax = plt.subplots(figsize=(4.2, 1.8))
order = ["individual house", "residential colony", "institutional", "industrial"]
for i, sc in enumerate(order):
    s = cost[cost.building_scale == sc]
    for sy, mk in [("recharge", "o"), ("storage", "s"), ("both", "D")]:
        ss = s[s.system_type == sy]
        if len(ss):
            ax.scatter(i + rng.uniform(-0.18, 0.18, len(ss)), ss.cost_per_kL_design_2024, s=30, c=BLUE, marker=mk, edgecolor="white", linewidth=0.6, zorder=3)
    ax.hlines(s.cost_per_kL_design_2024.median(), i - 0.3, i + 0.3, color=INK, lw=1.6, zorder=4)
    ax.text(i + 0.33, s.cost_per_kL_design_2024.median(), f"Rs {s.cost_per_kL_design_2024.median():.0f}", fontsize=6.5, va="center")
ax.axhspan(7, 48, color="#e6e5e1", alpha=0.6, zorder=0)
ax.axhspan(77.8, 375, color=ORANGE, alpha=0.10, zorder=0)
ax.axhline(68, color=INK2, lw=0.8, ls="--", zorder=1)
ax.text(3.98, 11, "Piped tariffs\nRs 7-48/kL", fontsize=6.3, color=INK2, ha="right", va="bottom")
ax.text(-0.45, 71, "Desalination\nO&M Rs 68/kL", fontsize=6, color=INK2, ha="left", va="bottom")
ax.text(3.98, 400, "Tanker water\nRs 78-375/kL", fontsize=6.3, color=INK2, ha="right", va="bottom")
ax.set_yscale("log"); ax.set_ylim(1, 900); ax.set_xlim(-0.5, 4.0)
ax.set_xticks(range(4)); ax.set_xticklabels([f"{lab}\n(n={int((cost.building_scale==o).sum())})" for o, lab in zip(order, ["House", "Colony", "Institutional", "Industrial"])], fontsize=7)
ax.set_ylabel("Rs per kL of design yield (2024)")
ax.set_title("Cost of harvested water by building scale", loc="left")
handles = [Line2D([], [], marker=m, color=BLUE, ls="", markeredgecolor="white", label=l) for m, l in [("o", "recharge"), ("s", "storage"), ("D", "both")]]
ax.legend(handles=handles, loc="upper left", fontsize=6.5, ncol=3, handletextpad=0.2, columnspacing=0.8, bbox_to_anchor=(0.0, 0.97))
fig.subplots_adjust(left=0.12, right=0.98, top=0.89, bottom=0.22); save(fig, "fig4_cost_per_kL", tight=False)

# ----------------------------------------------------------------------------
# Supplementary figures
# ----------------------------------------------------------------------------
# S1 sensitivity to runoff coefficient
fig, ax = plt.subplots(figsize=(3.6, 2.6))
for t, (lab, col, mk) in TIER.items():
    meds = [perf.loc[perf.tier == t, c].median() * 100 for c in ["performance_ratio_c070", "performance_ratio", "performance_ratio_c090"]]
    ax.plot([0.70, 0.80, 0.90], meds, marker=mk, color=col, label=lab.split(" (")[0])
ax.axhline(100, color=INK2, lw=0.8, ls="--")
ax.set_xlabel("Runoff coefficient assumed"); ax.set_ylabel("Median performance ratio (%)"); ax.set_xticks([0.7, 0.8, 0.9]); ax.legend(fontsize=6.5)
ax.set_title("Sensitivity to runoff coefficient", loc="left"); fig.tight_layout(); save(fig, "figS1_sensitivity_runoff")

# S2 ratio vs catchment area
fig, ax = plt.subplots(figsize=(3.6, 2.6))
for t, (lab, col, mk) in TIER.items():
    s = perf[perf.tier == t]
    ax.scatter(s.catchment_area_m2, s.performance_ratio * 100, s=28, c=col, marker=mk, edgecolor="white", linewidth=0.6, label=lab.split(" (")[0])
ax.set_xscale("log"); ax.set_xlabel("Catchment area (m2)"); ax.set_ylabel("Performance ratio (%)"); ax.axhline(100, color=INK2, lw=0.8, ls="--")
ax.legend(fontsize=6.5); ax.set_title("Ratio against catchment area", loc="left"); fig.tight_layout(); save(fig, "figS2_ratio_vs_area")

# S3 capital cost per m2 vs area (economies of scale)
fig, ax = plt.subplots(figsize=(3.6, 2.6))
ax.scatter(cc.catchment_area_m2, cc.capital_per_m2_2024, s=28, c=BLUE, edgecolor="white", linewidth=0.6)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("Catchment area (m2)"); ax.set_ylabel("Capital cost per m2 (2024 Rs)")
ax.set_title(f"Capital cost per m2 (Spearman rho = {sp2.statistic:.2f})", loc="left"); fig.tight_layout(); save(fig, "figS3_capital_per_m2")

# S4 screening flow diagram
fig, ax = plt.subplots(figsize=(7.4, 4.8)); ax.axis("off")
def box(x, y, w, h, text, fc="#ffffff", ec=INK2):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=0.8)); ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=6.3, color=INK, linespacing=1.25)
def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
ax.set_xlim(0, 100); ax.set_ylim(0, 100)
box(1, 82, 32, 16, "Performance strand\n89 site records identified\n(CGWB, CSE, Lok Sabha replies,\nacademic, campus, company reports)")
box(1, 61, 32, 13, "79 screened in detail\n(17 not accessible; 7 added from the\ncost search and the CGWB compilation)")
box(1, 31, 32, 23, "Excluded 47\n20 potential only\n9 no area or no volume\n3 modelled\n10 agency volumes without roof area\n5 mixed catchment, aggregate\nor inconsistent")
box(1, 4, 32, 22, "Included 32 site records\n= 35 observations at 31 sites\nObserved: 7 obs, 5 sites\nAgency-reported: 9 obs, 7 sites\nDesign calculation: 19 sites", fc="#eef3fb")
arrow(17, 82, 17, 74); arrow(17, 61, 17, 54); arrow(17, 33, 17, 26)
box(35, 82, 30, 16, "Cost strand\n43 case records with a cost figure\n37 benchmark price rows")
box(35, 52, 30, 22, "27 rows with capital cost,\ncost year and annual yield\nlevelised to 2024 Rs\n(15-year life, 8% discount,\nO&M 2% of capital)", fc="#eef3fb")
arrow(50, 82, 50, 74)
box(35, 4, 30, 22, "Benchmarks used\npiped tariffs (Rs 7-48/kL)\ndesalination O&M (Rs 68/kL)\ntanker water (Rs 78-375/kL)")
box(67, 82, 32, 16, "Functionality strand\n46 survey and audit records\n(Chennai, Bengaluru, Delhi, Haryana,\nHyderabad, Mumbai, Karnataka)")
box(67, 52, 32, 22, "13 functional-share estimates\nfrom 12 surveys and audits\n7 installation (compliance) figures\n90 failure-mode mentions\nfrom 40 distinct sources", fc="#eef3fb")
arrow(83, 82, 83, 74)
box(67, 4, 32, 22, "Mandate strand\n24 jurisdictions tabulated\nprimary instruments located for\nTamil Nadu, Karnataka, Maharashtra,\nKerala, Delhi and MBBL 2016")
save(fig, "figS4_screening_flow")

# ----------------------------------------------------------------------------
# write results
# ----------------------------------------------------------------------------
(RESD / "results.json").write_text(json.dumps(R, indent=2, default=float))
lines = ["# MIRAGE results summary (generated by code/analysis.py)", ""]
lines += ["## Performance ratio by tier (runoff coefficient 0.80)"]
for t in ["T1", "T2", "T3"]:
    p = pr[t]; lines.append(f"- {TIER[t][0]}: n={p['n']} obs at {p['sites']} sites; median {p['median']*100:.1f}% (bootstrap 95% CI {p['ci_lo']*100:.0f}-{p['ci_hi']*100:.0f}%), range {p['min']*100:.0f}-{p['max']*100:.0f}%; share >= 99%: {p['share_ge_1']*100:.0f}%; median at C=0.70: {p['median_c070']*100:.0f}%, at C=0.90: {p['median_c090']*100:.0f}%")
lines.append(f"- Mann-Whitney observed vs agency-reported: U={pr['T1_vs_T2_mannwhitney']['U']:.0f}, p={pr['T1_vs_T2_mannwhitney']['p']:.4f}")
lines.append(f"- Observed tier excluding partial-year Goa 2008: n={pr['T1_excl_partial_year']['n']}, median {pr['T1_excl_partial_year']['median']*100:.1f}%")
lines.append(f"- Observed tier excluding storage-limited houses: n={pr['T1_excl_storage_limited']['n']}, median {pr['T1_excl_storage_limited']['median']*100:.1f}%")
lines.append(f"- Warud graded agency-reported instead: observed n={pr['T1_excl_warud']['n']}, median {pr['T1_excl_warud']['median']*100:.1f}%; agency-reported n={pr['T2_incl_warud']['n']}, median {pr['T2_incl_warud']['median']*100:.1f}%; Mann-Whitney U={pr['T2_incl_warud']['mannwhitney_U']:.0f}, p={pr['T2_incl_warud']['mannwhitney_p']:.4f}")
lines.append(f"- Site-level medians (years averaged): observed {pr['site_level']['T1']['median']*100:.1f}% (n={pr['site_level']['T1']['n']}), agency-reported {pr['site_level']['T2']['median']*100:.1f}% (n={pr['site_level']['T2']['n']})")
rg = pr["regression"]
lines.append(f"- OLS ratio ~ observed + log10(area), n={rg['n']}, R2={rg['r2']:.2f}: observed coef {rg['params']['observed']:.2f} (p={rg['pvalues']['observed']:.3f}, 95% CI {rg['conf_int']['observed'][0]:.2f} to {rg['conf_int']['observed'][1]:.2f}); log10 area coef {rg['params']['log10_area']:.2f} (p={rg['pvalues']['log10_area']:.3f})")
lines.append(f"- Spearman ratio vs log area: observed and agency-reported rho={rg['spearman_area_all']['rho']:.2f} (p={rg['spearman_area_all']['p']:.2f}); observed only rho={rg['spearman_area_T1']['rho']:.2f} (p={rg['spearman_area_T1']['p']:.2f})")
lines += ["", "## Mandate gap"]
mg = R["mandate_gap"]
lines.append(f"- Chennai cascade: with structure {mg['chennai']['with_structure']*100:.1f}% -> functional {mg['chennai']['functional']*100:.1f}% -> delivered {mg['chennai']['delivered']*100:.1f}% of mandated potential")
lines.append(f"- Bengaluru cascade: with structure {mg['bengaluru']['with_structure']*100:.1f}% -> functional {mg['bengaluru']['functional']*100:.1f}% -> delivered {mg['bengaluru']['delivered']*100:.1f}%")
lines.append(f"- Functionality: {mg['functionality_n']} estimates from {mg['functionality_surveys']} surveys, median functional {mg['functionality_median']:.0f}% (range {mg['functionality_min']:.0f}-{mg['functionality_max']:.0f}%; structural-only definition: {mg['functionality_structural_only_median']:.0f}%); Chennai delivered with Warud as agency-reported: {mg['chennai_excl_warud_delivered']*100:.1f}%")
lines.append(f"- Failure modes: {N_FM_MENTIONS} mentions from {N_FM_SOURCES} distinct sources in {N_FM_CATS} categories")
lines += ["", "## Failure modes (distinct sources)"] + [f"- {r['category']}: {r['distinct_sources']} sources, {r['mentions']} mentions" for r in R["failure_modes"]]
lines += ["", "## Cost per kL (2024 Rs, design yield, 15 yr, 8%, O&M 2%)"]
o = cst["overall"]; lines.append(f"- All rows n={o['n']}: median Rs {o['median']:.1f}/kL (95% CI {o['ci_lo']:.1f}-{o['ci_hi']:.1f}), IQR {o['q25']:.1f}-{o['q75']:.1f}")
for sc in order: lines.append(f"- {sc}: n={cst[sc]['n']}, median Rs {cst[sc]['median']:.1f}, range {cst[sc]['min']:.1f}-{cst[sc]['max']:.1f}")
for sy in ["recharge", "storage", "both"]: lines.append(f"- system {sy}: n={cst['system_'+sy]['n']}, median Rs {cst['system_'+sy]['median']:.1f}")
lines.append(f"- Kruskal-Wallis across scales: H={cst['kruskal_scale']['H']:.2f}, p={cst['kruskal_scale']['p']:.3f}")
lines.append(f"- Spearman log area vs cost/kL: rho={cst['spearman_area_cost']['rho']:.2f}, p={cst['spearman_area_cost']['p']:.4f} (n={cst['spearman_area_cost']['n']}); log area vs capital/m2: rho={cst['spearman_area_capital_per_m2']['rho']:.2f}, p={cst['spearman_area_capital_per_m2']['p']:.4f}")
lines.append(f"- Delivered-yield multiplier (design-calculated median {design_ratio:.2f} / observed median {obs_ratio:.2f}) = {mult:.2f}; overall median at delivered yield Rs {cst['overall_delivered_median']:.0f}/kL")
lines.append(f"- CSE Delhi-NCR rows only: n={cst['cse_delhi_only']['n']}, median Rs {cst['cse_delhi_only']['median']:.1f}; rows with cost year >= 2010: n={cst['post2010']['n']}, median Rs {cst['post2010']['median']:.1f}")
lines.append(f"- Sensitivity 20-year life, 6% discount: median Rs {cst['sensitivity_20yr_6pct_median']:.1f}/kL; 15% discount (CGWB example): median Rs {cst['sensitivity_15pct_median']:.1f}/kL; post-2010 rows at observed yield: Rs {cst['post2010_delivered_median']:.0f}/kL")
lines += ["", "## Benchmarks (Rs/kL)"] + [f"- {l}: {v}" for l, v in BENCH]
(RESD / "results.md").write_text("\n".join(lines))
print("\n".join(lines))
