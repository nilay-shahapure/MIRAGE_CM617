"""Build the harmonised MIRAGE dataset from the raw research tables.

Inputs : research/*.csv (raw extraction, one row per source record)
Outputs: data/mirage_performance.csv   performance observations (yield vs potential)
         data/mirage_cost.csv          cost rows with levelised cost per kL
         data/mirage_functionality.csv functionality surveys with a measured split
         data/mirage_failure_modes.csv failure-mode mentions, collapsed to 11 categories
         data/mirage_mandates.csv      cleaned mandate table
         data/screening_log.csv        PRISMA-style counts

Every curated value below is copied from the research tables; the research_id
column points to the raw row, which carries the URL and the verbatim quote.
Run:  python3 code/build_dataset.py   (from the project root)
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "research"
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------
# 1. Performance observations
# ----------------------------------------------------------------------------
# tier: T1 = the source names a measuring instrument (flow meter, recharge-measuring
#            device) or a tank-filling record for the site. Applied mechanically: Ramtek and
#            Warud (identical CGWB wording, both with a flow meter) are both T1.
#       T2 = annual volume reported by an implementing agency with no instrument named,
#            or stated as a share of estimated runoff
#       T3 = design calculation (reported as harvested but equal to a fixed
#            share of area x rainfall)
# rainfall_basis: site-year = rainfall for the site and year of the volume;
#       site-avg = average annual rainfall quoted by the source for the site;
#       city-normal = IMD normal for the city (period in note);
#       implied = rainfall received on the roof reported by the source, divided by roof area.
PERF = [
 # obs_id, site, city, state, bldg, sys, tier, area, rain, rain_basis, year, vol, vol_type, storage_kL, installed, note, source, url, research_id, midway_ratio
 ("P01","KITS Ramtek, IT building","Ramtek (Nagpur dist.)","Maharashtra","institutional","recharge","T1",360,599.2,"implied","2001-02",19.0,"recharged",np.nan,2001,
  "Flow meter in line. CGWB: 215.7 m3 received on roof, 19 m3 recharged (as per estimation). Rainfall = 215.7/360.","CGWB 2011, p.73","https://cgwb.gov.in/cgwbpnm/download/379","A1 (verified from PDF p.73)","9%"),
 ("P02","Panchayat Samiti office, Warud","Warud (Amravati dist.)","Maharashtra","public","recharge","T1",500,622.6,"implied","2002-03",280.17,"recharged",np.nan,2002,
  "Flow meter in line (same CGWB wording as Ramtek). Volume stated as 280.17 m3 (90%) of 311.30 m3 received; the round 90% may be an assumption, see Results. Rainfall = 311.3/500.","CGWB 2011, p.73","https://cgwb.gov.in/cgwbpnm/download/379","A5 (verified from PDF p.73)","90%"),
 ("P03","IIT Delhi, Block VI","New Delhi","Delhi","institutional","recharge","T2",1660,762.3,"city-normal","NR (c. 2001-05)",830.0,"recharged",np.nan,2001,
  "CGWB: about 830 m3 recharged from 1660 m2 roof; period not stated. Rainfall = IMD Safdarjung normal 1991-2020.","CGWB 2011, p.44","https://cgwb.gov.in/cgwbpnm/download/379","A6 (verified from PDF p.44)","NR (rainfall not reported)"),
 ("P05","Goa University, 2010","Taleigao","Goa","institutional","both","T1",400,3700,"site-year","2010",900.0,"recharged",100,2008,
  "Recharge measured with a device at the bore well (CSE); Chachadi 2013 gives 934 kL to 11 Nov 2010. 2010 monsoon rainfall 3.7 m reported.","CSE 2014 Urban RWH report; Chachadi 2013","https://cdn.cseindia.org/userfiles/Urban Rainwater harvesting report.pdf","A2","61-76%"),
 ("P06","Goa University, 2008 (partial year)","Taleigao","Goa","institutional","both","T1",400,2918,"city-normal","2008",260.0,"recharged",100,2008,
  "System built July 2008, so 2008 is a partial season. Rainfall = IMD Panaji normal 1981-2010.","CSE 2014 Urban RWH report","https://cdn.cseindia.org/userfiles/Urban Rainwater harvesting report.pdf","A2",""),
 ("P07","Goa University, 2009","Taleigao","Goa","institutional","both","T1",400,2918,"city-normal","2009",180.0,"recharged",100,2008,
  "Rainfall = IMD Panaji normal 1981-2010 (2009 site rainfall not reported).","CSE 2014 Urban RWH report","https://cdn.cseindia.org/userfiles/Urban Rainwater harvesting report.pdf","A2",""),
 ("P08","Bharat Electronics Ltd, Bengaluru","Bengaluru","Karnataka","industrial","storage","T2",2000,1077.6,"city-normal","annual (post 2003)",1100.0,"harvested (stored)",np.nan,2003,
  "'Around 1100 KL of rainwater harvested annually' for DM water production; method not stated. Rainfall = IMD Bengaluru normal 1991-2020.","NWM/BEL case sheet","https://www.nwm.gov.in/sites/default/files/BEL_RWH-Ctr.pdf","A3","63-75%"),
 ("P09","Panjab University, Basic Medical Sciences block","Chandigarh","Chandigarh","institutional","recharge","T2",2100,1059.3,"city-avg (CSE)","annual (c. 2004)",1985.0,"recharged",np.nan,2001,
  "Lok Sabha reply: 1985 m3 (93% of total generated runoff) recharged annually. Roof area from CSE 2010. No IMD normal located for Chandigarh; CSE city figure used.","Lok Sabha SQ 384 (23.08.2004); CSE 2010","https://eparlib.sansad.in/bitstream/123456789/520443/1/2310.pdf","A4","79%"),
 ("P10","CSIO complex","Chandigarh","Chandigarh","institutional","recharge","T2",3550,1059.3,"city-avg (CSE)","annual (c. 2004)",3812.0,"recharged",np.nan,1999,
  "Lok Sabha reply: 3812 m3 recharged annually. Roof area 3550 m2 from CSE 2010.","Lok Sabha SQ 384 (23.08.2004); CSE 2010","https://eparlib.sansad.in/bitstream/123456789/520443/1/2310.pdf","B2",""),
 ("P11","Hydrology Project building, Bhubaneswar, 2004","Bhubaneswar","Odisha","public","recharge","T2",2250,1096,"site-year","2004",2096.0,"harvested",np.nan,2004,
  "CGWB Table 34; project 'monitored weekly'; method of volume not stated; 2004 value equals 85% of gross rainfall exactly.","CGWB 2011, p.116","https://cgwb.gov.in/cgwbpnm/download/379","new (PDF p.116)",""),
 ("P12","Hydrology Project building, Bhubaneswar, 2005","Bhubaneswar","Odisha","public","recharge","T2",2250,1579,"site-year","2005",2566.86,"harvested",np.nan,2004,
  "CGWB Table 34.","CGWB 2011, p.116","https://cgwb.gov.in/cgwbpnm/download/379","new (PDF p.116)",""),
 ("P13","Hydrology Project building, Bhubaneswar, 2006","Bhubaneswar","Odisha","public","recharge","T2",2250,1881,"site-year","2006",2174.23,"harvested",np.nan,2004,
  "CGWB Table 34.","CGWB 2011, p.116","https://cgwb.gov.in/cgwbpnm/download/379","new (PDF p.116)",""),
 ("P14","Escorts-Mahle-Goetze, Yelahanka","Bengaluru","Karnataka","industrial","storage","T2",1280,970,"city-avg (CSE)","annual (c. 2001)",1050.0,"collected",4.2,2000,
  "CSE: 'collects about 1.05 million litres per year'; method not stated.","CSE case study page","https://www.cseindia.org/node/1099","B25",""),
 ("P15","K.G. Bhawan (CWC office)","Hyderabad","Telangana","public","recharge","T2",1577.8,800,"site-avg","NR",1000.0,"harvested",np.nan,np.nan,
  "CWC: 'Water harvested : 10 lakh litres (approx)'; method not stated.","CWC RWH note","https://cwc.gov.in/sites/default/files/rwh.pdf","B29",""),
 ("P16","R. Ramani residence, Korattur","Chennai","Tamil Nadu","individual house","storage","T1",50,1200,"city-avg (CSE)","annual (c. 2001)",13.5,"collected (tank record)",3,1994,
  "3 kL tank fills four to five times a year (12-15 kL); storage-limited, so a lower bound on roof yield. Midpoint used.","CSE case study page","https://www.cseindia.org/node/1099","B26",""),
 ("P17","R.V. Ramamohan residence","Hyderabad","Telangana","individual house","storage","T1",100,804,"site-avg","2012 (5 months)",15.0,"collected (tank record)",1,2012,
  "About 15,000 L collected over 5 months with a 1 kL tank; storage-limited lower bound.","India Water Portal (Ramamohan 2012)","https://oldiwp.indiawaterportal.org/sites/default/files/iwp2/rooftop_rainwater_harvesting_system___hyderabad___rv_ramamohan___2012.pdf","B27",""),
]
# Design-calculated rows (T3): CSE model projects where "total volume harvested" is a
# fixed share of area x rainfall. Volume and area from research/cost_cases.csv rows C01-C19.
T3 = [
 ("P18","Mira Model School","New Delhi","school","recharge",16200,611,4454,"C01/B13","45% of potential"),
 ("P19","Janki Devi Memorial College","New Delhi","institutional","recharge",32170,611,6880,"C02/B14","35% of potential"),
 ("P20","Jamia Hamdard University","New Delhi","institutional","recharge",315380,611,67444,"C03/B15","35% of potential"),
 ("P21","The Shri Ram School","New Delhi","school","both",6000,611,1890,"C04/B16","55% of potential"),
 ("P22","Tex Corp Ltd, Gurgaon","Gurgaon","industrial","storage",4000,577.8,1962,"C05/B17","85% of potential"),
 ("P23","Ford Foundation","New Delhi","institutional","recharge",12500,611,6491.8,"C06/B18","85% of potential"),
 ("P24","Sri Aurobindo Ashram","New Delhi","institutional","recharge",95870,611,16366,"C07/A7b","43% of potential"),
 ("P25","Tihar Jail wards 1 and 13","New Delhi","public","recharge",4125,611,1280,"C08/B19","50.78% of potential"),
 ("P26","Hero Honda Motors, Daruhera","Daruhera","industrial","recharge",11080,577.8,5441,"C12/B20","85% of potential"),
 ("P27","Defence Colony C block","New Delhi","residential colony","recharge",26087,611.8,9563,"C11/B21","share not stated"),
 ("P28","Indian Spinal Injury Centre","New Delhi","institutional","recharge",52598,611,27317,"C09/B22","share not stated"),
 ("P29","New Friends Club","New Delhi","institutional","recharge",3700,611,960.79,"C16","42% of runoff"),
 ("P30","Delhi Gymkhana Club","New Delhi","institutional","recharge",113344,611,28765.8,"C17","43% of runoff"),
 ("P31","Nizamuddin East colony","New Delhi","residential colony","recharge",200916,611,48531,"C18","39.6% of runoff"),
 ("P32","Royal Bhutanese Embassy","New Delhi","institutional","recharge",31363,611,7867,"C19","26% of runoff"),
 ("P33","Mother Dairy, Mangolpuri","New Delhi","industrial","recharge",89370,611,32250,"C15","59% of runoff"),
 ("P34","Anup Ahuja farm house","New Delhi","individual house","recharge",1250,611,272,"C13","60% of runoff"),
 ("P35","Surya Vihar apartments, Kapas Hera","Gurgaon","residential colony","recharge",44029,611,18207,"C14","share not stated"),
 ("P36","Shram Shakti Bhawan (CGWB design)","New Delhi","institutional","recharge",11965,712.2,3000,"B1 / CGWB 2011 p.44","expected recharge 3000 m3/yr from runoff 3325 m3"),
]
cols = ["obs_id","site","city","state","building_type","system_type","tier","catchment_area_m2","rainfall_mm","rainfall_basis","year_of_volume","reported_volume_kL","volume_type","storage_capacity_kL","year_installed","measurement_note","source","url","research_id","midway_ratio"]
perf = pd.DataFrame(PERF, columns=cols)
t3rows = []
for o in T3:
    t3rows.append(dict(obs_id=o[0], site=o[1], city=o[2], state=("Delhi" if o[0]=="P36" else "Delhi/Haryana"), building_type=o[3], system_type=o[4], tier="T3",
        catchment_area_m2=o[5], rainfall_mm=o[6], rainfall_basis="city-avg (CSE)", year_of_volume="annual (design)", reported_volume_kL=o[7],
        volume_type="harvested (calculated)", storage_capacity_kL=np.nan, year_installed=np.nan,
        measurement_note=(f"CGWB design note: {o[9]}; campus catchment (roof + paved)." if o[0]=="P36" else f"CSE model project page: volume is a calculation ({o[9]}); whole-site catchment (roof + paved + open)."),
        source=("CGWB 2011 p.44; NPTEL design note" if o[0]=="P36" else "CSE model project pages (2000-2004)"), url=("https://cgwb.gov.in/cgwbpnm/download/379" if o[0]=="P36" else "https://www.cseindia.org/rainwater-harvesting-case-studies"), research_id=o[8], midway_ratio=""))
perf = pd.concat([perf, pd.DataFrame(t3rows)], ignore_index=True)

C_CENTRAL, C_LOW, C_HIGH = 0.80, 0.70, 0.90   # CGWB 2007 Table 7.2: concrete 0.7 ... GI sheet 0.9
for tag, c in [("", C_CENTRAL), ("_c070", C_LOW), ("_c090", C_HIGH)]:
    perf["potential_kL"+tag] = perf.catchment_area_m2 * perf.rainfall_mm * c / 1000
    perf["performance_ratio"+tag] = perf.reported_volume_kL / perf["potential_kL"+tag]
perf["share_of_gross_rain"] = perf.reported_volume_kL / (perf.catchment_area_m2 * perf.rainfall_mm / 1000)
perf["log10_area"] = np.log10(perf.catchment_area_m2)
perf["runoff_coefficient_central"] = C_CENTRAL
perf.insert(perf.columns.get_loc("tier") + 1, "tier_name", perf.tier.map({"T1": "observed", "T2": "agency-reported", "T3": "design-calculated"}))
perf.to_csv(DATA / "mirage_performance.csv", index=False)

# ----------------------------------------------------------------------------
# 2. Cost rows
# ----------------------------------------------------------------------------
# capital cost (Rs, nominal in cost_year), annual yield (kL/yr) as reported by the source,
# yield_basis: design = computed by the source; observed = reported from monitoring.
COST = [
 # id, site, city, scale, system, area, capital, year, yield, basis, research_id, url
 ("K01","Mira Model School","New Delhi","institutional","recharge",16200,120000,2001,4454,"design","C01","https://www.cseindia.org/rainwater-harvesting-case-studies"),
 ("K02","Janki Devi Memorial College","New Delhi","institutional","recharge",32170,70000,2001,6880,"design","C02",""),
 ("K03","Jamia Hamdard University","New Delhi","institutional","recharge",315380,652000,2001,67444,"design","C03",""),
 ("K04","The Shri Ram School","New Delhi","institutional","both",6000,125000,2000,1890,"design","C04",""),
 ("K05","Tex Corp Ltd","Gurgaon","industrial","storage",4000,550000,2002,1962,"design","C05",""),
 ("K06","Ford Foundation","New Delhi","institutional","recharge",12500,400000,2000,6491.8,"design","C06",""),
 ("K07","Sri Aurobindo Ashram","New Delhi","institutional","recharge",95870,400000,2003,16366,"design","C07",""),
 ("K08","Tihar Jail wards 1 and 13","New Delhi","institutional","recharge",4125,20000,2002,1280,"design","C08",""),
 ("K09","Indian Spinal Injury Centre","New Delhi","institutional","recharge",52598,80000,2002,27317,"design","C09",""),
 ("K10","BPCL housing complex","Noida","residential colony","recharge",13910,450000,2002,4446,"design","C10",""),
 ("K11","Defence Colony C block","New Delhi","residential colony","recharge",26087,258000,2003,9563,"design","C11",""),
 ("K12","Hero Honda Motors","Daruhera","industrial","recharge",11080,1200000,2004,5441,"design","C12",""),
 ("K13","Anup Ahuja farm house","New Delhi","individual house","recharge",1250,20000,2002,272,"design","C13",""),
 ("K14","Surya Vihar apartments","Gurgaon","residential colony","recharge",44029,65000,2002,18207,"design","C14",""),
 ("K15","Mother Dairy unit","New Delhi","industrial","recharge",89370,435000,2004,32250,"design","C15",""),
 ("K16","New Friends Club","New Delhi","institutional","recharge",3700,40000,2004,960.79,"design","C16",""),
 ("K17","Delhi Gymkhana Club","New Delhi","institutional","recharge",113344,80000,2004,28765.8,"design","C17",""),
 ("K18","Nizamuddin East colony","New Delhi","residential colony","recharge",200916,174000,2004,48531,"design","C18",""),
 ("K19","Royal Bhutanese Embassy","New Delhi","institutional","recharge",31363,110000,2004,7867,"design","C19",""),
 ("K20","Brig. Jagdev Singh residence","New Delhi","individual house","recharge",285,7500,2001,147,"design","C22",""),
 ("K21","Shram Shakti Bhawan","New Delhi","institutional","recharge",11965,410000,2001,3000,"design","C25 / CGWB 2011 p.44","https://cgwb.gov.in/cgwbpnm/download/379"),
 ("K22","Nandi Deepa apartments","Bengaluru","residential colony","recharge",np.nan,2220000,2021,3564,"design","C27",""),
 ("K23","Vidhani village houses, cluster (Saini et al.)","Jaipur","residential colony","storage",2466,131498,2016,1602,"design","C34",""),
 ("K24","TSSM BSCOER and JSPM campuses (Varpe et al.)","Pune","institutional","both",8200,6204336,2019,5453,"design","C35",""),
 ("K25","Bearys modular house system (Raju et al.)","Mangaluru","individual house","storage",81.3,5710,2021,20.83,"design","C36",""),
 ("K26","Punjab govt building standard design (900 m2)","Punjab","institutional","recharge",900,281079,2020,438,"design","C37",""),
 ("K27","Hydrology Project building, Bhubaneswar","Bhubaneswar","institutional","recharge",2250,856000,2004,2279.0,"agency-monitored, method not stated (mean 2004-06)","CGWB 2011 p.116","https://cgwb.gov.in/cgwbpnm/download/379"),
]
cost = pd.DataFrame(COST, columns=["cost_id","site","city","building_scale","system_type","catchment_area_m2","capital_cost_inr","cost_year","annual_yield_kL","yield_basis","research_id","url"])
cpi = pd.read_csv(DATA / "cpi_iw_deflator.csv").set_index("fy_start_year")["linked_2001_100"]
BASE_YEAR = 2024
cost["cpi_factor_to_2024"] = cost.cost_year.map(lambda y: cpi[BASE_YEAR] / cpi[int(y)])
cost["capital_2024_inr"] = cost.capital_cost_inr * cost.cpi_factor_to_2024
LIFE, OM_SHARE, DISC = 15, 0.02, 0.08       # CGWB 2007 example: 15-year life, O&M 2 % of capital; 8 % discount is our assumption (CGWB example uses 15 %)
crf = DISC * (1 + DISC) ** LIFE / ((1 + DISC) ** LIFE - 1)
cost["annual_cost_2024_inr"] = cost.capital_2024_inr * (crf + OM_SHARE)
cost["cost_per_kL_design_2024"] = cost.annual_cost_2024_inr / cost.annual_yield_kL
crf15 = 0.15 * 1.15 ** LIFE / (1.15 ** LIFE - 1)
cost["cost_per_kL_design_2024_disc15"] = cost.capital_2024_inr * (crf15 + OM_SHARE) / cost.annual_yield_kL
cost["capital_per_m2_2024"] = cost.capital_2024_inr / cost.catchment_area_m2
cost["capital_per_kL_yield_2024"] = cost.capital_2024_inr / cost.annual_yield_kL
cc_raw = pd.read_csv(RES / "cost_cases.csv").set_index("case_id")["url"]
cost["url"] = [u if isinstance(u, str) and u.strip() else cc_raw.get(str(rid).split(" ")[0].split("/")[0], "") for u, rid in zip(cost.url, cost.research_id)]
cost.to_csv(DATA / "mirage_cost.csv", index=False)

# ----------------------------------------------------------------------------
# 3. Functionality surveys with a measured split
# ----------------------------------------------------------------------------
FUNC = [
 # id, label, city, year, population, n, pct_functional, definition, who, research_id
 ("F02","Chennai 2019, houses with a structure","Chennai",2019,"houses with an RWH structure (1.62 lakh of 2.72 lakh inspected)",162000,76.5,"1.62 lakh houses had a structure; about 38,000 of them 'needed minor repairs', so 1.24 lakh (76.5%) needed no repair. Single GCC snapshot (Aug-Sep 2019).","Greater Chennai Corporation (The News Minute)","S10"),
 ("F03","Chennai Gandhinagar 2003","Chennai",2003,"independent houses",309,50.0,"'only 50 per cent had implemented RWH properly'","Akashganga Trust (Down To Earth 2004)","S03"),
 ("F04","Chennai approved buildings 2001-02","Chennai",2002,"buildings approved under 1994 rule, with RWH",25,67.0,"a third of installed systems 'not properly designed and therefore ineffective'","MIDS survey for CSE","S01/S02"),
 ("F05","Karnataka school structures 2007","Karnataka (rural)",2007,"government school rooftop structures",1269,11.0,"140 of 1,269 structures functional","Arghyam status report","S21"),
 ("F06","Karnataka model schools 2009","Karnataka (rural)",2009,"school rooftop structures",27,59.3,"16 of 27 functioning; 3 partial; 8 defunct","Arghyam","S22"),
 ("F07","Faridabad public systems 2018-19","Faridabad",2019,"public RWH systems (parks, schools)",190,20.0,"'around 80% had stopped working'","MCF survey (The Tribune)","S30"),
 ("F08","Faridabad public systems 2024","Faridabad",2024,"public RWH systems",200,25.0,"'around 70 to 80 per cent' non-functional (midpoint)","civic sources (The Tribune)","S31"),
 ("F09","Gurugram pits 2023","Gurugram",2023,"RWH pits, public and private",500,30.0,"'around 70%' lying defunct","MCG / GMDA (The Tribune)","S32"),
 ("F10","Delhi Dwarka societies 2024 (structural)","Delhi",2024,"group housing societies with RWH",176,83.5,"176 minus 4 non-functional minus 25 dry pits","DJB action-taken report to NGT","S27"),
 ("F11","Delhi Dwarka societies 2024 (clean recharge)","Delhi",2024,"group housing societies with RWH",176,32.4,"57 of 176 without faecal coliform in recharge water (119 contaminated)","DJB action-taken report to NGT","S27"),
 ("F12","Bengaluru BWSSB connections 2023 (expert estimate)","Bengaluru",2023,"BWSSB connections with RWH",np.nan,40.0,"'only about 40% of BWSSB connections have functional RWH systems' (estimate)","S. Vishwanath (Deccan Herald)","S17"),
 ("F13","Kaithal government buildings 2018","Kaithal",2018,"government-building systems",5,0.0,"all five choked after the first year","The Tribune field report","S33"),
 ("F14","Sirsa park systems 2025","Sirsa",2025,"municipal park systems",4,50.0,"2 of 4 dead within two years","The Tribune field report","S34"),
]
func = pd.DataFrame(FUNC, columns=["func_id","label","city","year","population","sample_n","pct_functional","definition","conducted_by","research_id"])
func.to_csv(DATA / "mirage_functionality.csv", index=False)

# Installation (compliance) figures: share of mandated/connected properties with a structure
COMPL = [
 ("Chennai 2019","Chennai",2019,"houses inspected",272000,162000,59.6,"1.62 lakh of 2.72 lakh inspected had a structure","mandates.csv / S10"),
 ("Bengaluru 2023","Bengaluru",2023,"properties with water connection",1080000,190000,17.6,"1.9 lakh of 10.8 lakh","mandates.csv / S18"),
 ("Hyderabad 2024","Hyderabad",2024,"properties >= 300 sq yd surveyed",39000,22000,56.4,"22,000 installed; 17,000 non-compliant","mandates.csv / S36"),
 ("Mumbai 2007-21","Mumbai",2021,"housing societies (estimate)",20000,3000,15.0,"about 3,000 of about 20,000 societies","mandates.csv / S39"),
 ("Pune FY2022-23","Pune",2023,"taxable properties (rebate claimants)",1250000,3716,0.3,"3,716 rebate claimants of about 12.5 lakh properties","mandates.csv"),
 ("Nagpur 2023","Nagpur",2023,"properties",636000,1123,0.18,"1,123 of about 6.36 lakh properties","mandates.csv / S43"),
 ("Delhi govt buildings 2019","Delhi",2019,"government buildings (building class, not a city rate)",771,212,27.5,"212 of 771 with RWH","S24"),
]
compl = pd.DataFrame(COMPL, columns=["label","city","year","population","denominator","numerator","pct_with_structure","definition","research_id"])
compl.to_csv(DATA / "mirage_compliance.csv", index=False)

# ----------------------------------------------------------------------------
# 4. Failure modes: collapse the raw categories to 11 groups (10 named + other), count distinct sources
# ----------------------------------------------------------------------------
fm = pd.read_csv(RES / "failure_modes.csv")
def collapse(c):
    c = str(c).lower()
    if c.startswith("poor construction"): return "Poor design or construction"
    if c.startswith("no maintenance"): return "No maintenance, abandoned"
    if c.startswith("lack of awareness"): return "No awareness, incentive or enforcement"
    if c.startswith("structure built only"): return "Token structure, built for compliance only"
    if c.startswith("silted"): return "Recharge pit or well silted or choked"
    if c.startswith("disconnected"): return "Downpipes or conveyance broken or disconnected"
    if c.startswith("clogged"): return "Filter clogged or absent"
    if c.startswith("undersized"): return "Storage undersized, overflow or leak"
    if c.startswith("first-flush"): return "First flush absent or not operated"
    if c.startswith("water quality"): return "Water quality concerns, system disused"
    return "Other (space, vandalism, roof-only design)"
fm["category"] = fm.failure_mode_category.map(collapse)
fm_counts = fm.groupby("category").agg(mentions=("fm_id","count"), distinct_sources=("survey_or_source_id","nunique"), cities=("city", lambda s: ", ".join(sorted(set(map(str, s)))))).reset_index().sort_values("distinct_sources", ascending=False)
fm_counts.to_csv(DATA / "mirage_failure_modes.csv", index=False)
fm[["fm_id","survey_or_source_id","city","category","failure_mode_category","raw_description","count_or_pct","url"]].to_csv(DATA / "mirage_failure_modes_long.csv", index=False)

# ----------------------------------------------------------------------------
# 5. Mandates: copy with trimmed text
# ----------------------------------------------------------------------------
m = pd.read_csv(RES / "mandates.csv")
m.to_csv(DATA / "mirage_mandates.csv", index=False)

# ----------------------------------------------------------------------------
# 6. Screening log (PRISMA-style). Counts from the research notes.
# ----------------------------------------------------------------------------
perf_raw = pd.read_csv(RES / "performance_cases.csv")
n_perf_records = len(perf_raw)
LOG = [
 ("Performance strand: site records identified (CGWB, CSE, Lok Sabha replies, academic, campus and company reports)", 89, "72 rows in research/performance_cases.csv plus 17 records logged in performance_notes.md as not accessible"),
 ("Performance strand: records not accessible (documents that could not be opened or were paywalled)", 17, "performance_notes.md access log"),
 ("Performance strand: records screened in detail (72 from the performance search, 6 CSE model projects from the cost search, 1 case read directly from the CGWB 2011 compilation)", 79, "performance_cases.csv; cost_cases.csv C13, C14, C16-C19; CGWB 2011 p.116"),
 ("Excluded: potential only (no actual volume reported)", 20, "rows P1-P19 and B24"),
 ("Excluded: no catchment area or no volume", 9, "rows N1-N9"),
 ("Excluded: modelled volumes (JNTU Hyderabad, 3 structures)", 3, "rows B30a-c"),
 ("Excluded: agency volumes with no roof area (Lok Sabha 2004 list)", 10, "rows B3-B12"),
 ("Excluded: mixed or non-roof catchment, aggregate, or internally inconsistent", 5, "rows B28 (SV Symphony), B31 (Infosys aggregate), B32 (Goa surface runoff), A7a (Umaid Heritage), A7c (PAU, no area)"),
 ("Included site records", 32, "25 rows from performance_cases.csv (A1/A1b count as one site; B1 Shram Shakti as a design calculation) + 6 from cost_cases.csv + 1 from CGWB PDF"),
 ("Included observations (some sites have several years)", int(len(perf)), "data/mirage_performance.csv: 35 observations at 31 sites"),
 ("Included as T1 observed volumes (instrument or tank record named)", int((perf.tier=="T1").sum()), "P01, P02, P05-P07, P16, P17 (5 sites)"),
 ("Included as T2 agency-reported volumes", int((perf.tier=="T2").sum()), "P03, P08-P15 (7 sites)"),
 ("Included as T3 design calculations (CSE model projects and CGWB design note)", int((perf.tier=="T3").sum()), "P18-P36 (19 sites)"),
 ("Cost strand: case records screened", 43, "research/cost_cases.csv"),
 ("Cost strand: rows with both capital cost and annual yield and a cost year, used for levelised cost", len(cost), "data/mirage_cost.csv"),
 ("Cost strand: benchmark price rows", 37, "research/cost_benchmarks.csv"),
 ("Functionality strand: survey records screened", 46, "research/functionality_surveys.csv"),
 ("Functionality strand: surveys with a measured functional / defunct split", len(func), "data/mirage_functionality.csv"),
 ("Functionality strand: city compliance (installation) figures", len(compl), "data/mirage_compliance.csv"),
 ("Failure-mode mentions extracted", len(fm), "research/failure_modes.csv"),
 ("Failure-mode distinct sources", int(fm.survey_or_source_id.nunique()), "research/failure_modes.csv, survey_or_source_id"),
 ("Failure-mode categories after collapsing", int(fm.category.nunique()), "data/mirage_failure_modes.csv"),
 ("Mandate jurisdictions tabulated", len(m), "data/mirage_mandates.csv"),
]
pd.DataFrame(LOG, columns=["step","count","where"]).to_csv(DATA / "screening_log.csv", index=False)

print("performance obs:", len(perf), perf.tier.value_counts().to_dict())
print("cost rows:", len(cost))
print("functionality rows:", len(func), "| compliance rows:", len(compl))
print(fm_counts.to_string(index=False))
