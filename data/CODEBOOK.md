# Codebook for the data tables

All tables are comma-separated text. "NR" means not reported in the source.

## mirage_performance.csv (35 rows, one per observation)
- obs_id: row label (P01 to P36; P04 was merged into P05 during screening).
- site, city, state, building_type, system_type: as in the source. system_type is storage (tank for use), recharge (to groundwater) or both.
- tier: evidence tier code. tier_name gives the word used in the report: observed (the source names a measuring instrument or a tank-filling record), agency-reported (an agency states an annual volume with no instrument named), design-calculated (the source labels the figure a design calculation).
- catchment_area_m2: roof area, or roof plus paved area where the source gives only the combined figure (the design-calculated rows).
- rainfall_mm and rainfall_basis: the rainfall used and where it comes from: site-year (reported for that site and year), site-avg (average quoted by the source), city-avg (CSE city figure), city-normal (IMD normal), implied (rain received on the roof divided by area).
- year_of_volume: the period the volume refers to.
- reported_volume_kL, volume_type: the volume as stated and what the source calls it.
- storage_capacity_kL, year_installed: as stated.
- measurement_note: how the volume was obtained, in the source's words where possible.
- source, url, research_id: the document, its address, and the row in the source extraction tables (research folder) that holds the verbatim quote.
- midway_ratio: the ratio reported at the mid-term progress report, for the six cases that had one.
- potential_kL = catchment_area_m2 x rainfall_mm x 0.80 / 1000; performance_ratio = reported_volume_kL / potential_kL; the _c070 and _c090 columns repeat both with runoff coefficients 0.70 and 0.90; share_of_gross_rain = volume / (area x rainfall / 1000).

## mirage_cost.csv (27 rows, one per system)
- capital_cost_inr, cost_year: capital cost in the rupees of that year.
- annual_yield_kL, yield_basis: the yearly water the source states (design, or agency-monitored).
- cpi_factor_to_2024, capital_2024_inr: CPI-IW deflation to 2024-25 rupees (see cpi_iw_deflator.csv).
- annual_cost_2024_inr = capital_2024_inr x (0.1168 + 0.02): capital recovery factor for 15 years at 8 percent plus 2 percent per year maintenance.
- cost_per_kL_design_2024 = annual_cost_2024_inr / annual_yield_kL. cost_per_kL_design_2024_disc15 repeats this with a 15 percent discount rate.
- capital_per_m2_2024, capital_per_kL_yield_2024: capital cost divided by catchment area and by yearly yield.
- research_id, url: the source row and address.

## cpi_iw_deflator.csv
Consumer Price Index for Industrial Workers, annual averages by financial year, from the RBI Handbook of Statistics on the Indian Economy (Table 37), with the 1982, 2001 and 2016 base series linked to a single 2001 = 100 series using the published linking factors 4.63 and 2.88.

## mirage_functionality.csv (13 rows)
Functional-share estimates: survey, population, sample size (sample_n), percentage functional, the definition the survey used, who conducted it, and the source row.

## mirage_compliance.csv (7 rows)
Installation (compliance) figures: denominator (properties covered), numerator (properties with a structure), percentage.

## mirage_failure_modes.csv and mirage_failure_modes_long.csv
Counts of failure-mode categories (distinct sources citing each, and total mentions), and the full list of 90 mentions with source id, city, category, the raw description and the address.

## mirage_mandates.csv (24 rows)
Jurisdiction, instrument, years enacted and enforced, applicability threshold, penalty or incentive, enforcing agency, reported compliance, address and quote.

## screening_log.csv
Counts for every screening step.

## Source extraction tables (research folder)
performance_cases.csv, cost_cases.csv, cost_benchmarks.csv, functionality_surveys.csv, failure_modes.csv, mandates.csv, reference_inputs.csv: one row per source record with the address and the sentence or field values taken from the page. Where a quote field says "(values as extracted from the page)" or "(paraphrase)", the numbers were read from the page but the sentence was not copied word for word.
