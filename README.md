# MIRAGE: Measuring the Impact and Reality of Rainwater Harvesting Mandates

CM617 Sustainability Principles and Practices, IIT Bombay. Course project, Pathway 1 (Sustainability Research), Water sector.
Team: Vedant Abhangrao (23B2262), Nilay Shahapure (23B2206), Arjun Jhunjhunwala (23B1245), Yash Krishnani (23B1240).

A meta-analysis of published performance, functionality and cost data for rooftop rainwater harvesting (RWH) systems in Indian cities, asking what the mandates actually deliver.


## Headline results

- Observed systems (the source names a flow meter, measuring device or tank record) deliver a median 28% of theoretical potential (7 observations at 5 sites; 26% if the borderline Warud case is regraded).
- Agency-reported volumes have a median of 99% of potential; 5 of 9 are at or above 99%, so they are design estimates, not measurements (Mann-Whitney p = 0.023; p = 0.001 with Warud regraded).
- Installation: 60% of inspected Chennai houses, 18% of Bengaluru connected properties, below 1% in Pune and Nagpur. Functionality: 13 estimates from 12 surveys, median 40% of installed systems working.
- Failure modes by number of distinct sources (40 sources, 90 mentions, 11 categories): no maintenance (18), no incentive or enforcement (15), poor design or construction (15), token structures (10).
- Levelised cost: median Rs 21 per kL at design yield (2024 rupees; Rs 29 at a 15% discount rate), about Rs 42 at observed yield; piped tariffs Rs 7 to 48, tankers Rs 78 to 375. The five post-2010 systems are far more expensive (about Rs 200 per kL at observed yield).
- Chennai cascade (one 2019 inspection snapshot): 60% with a structure x 77% needing no repair x 28% observed yield = about 13% of the mandated potential delivered.

## Method in one paragraph

Theoretical potential = catchment area x annual rainfall x 0.80 / 1000 (kL/yr), with the runoff coefficient taken from the CGWB 2007 manual (concrete 0.7 to GI sheet 0.9). Performance ratio = reported volume / potential. Each observation is graded by one rule: observed if the source names a measuring instrument or a tank-filling record, agency-reported if an agency states a volume with no instrument named, design-calculated if the source labels the figure a design calculation. Costs are deflated to 2024 rupees with the CPI-IW series, annualised over 15 years (CGWB norm) at 8% (our assumption; CGWB's example uses 15%) with O&M at 2% of capital (CGWB norm), and divided by the design yield. Functionality surveys with a measured functional/defunct split are tabulated as reported; failure-mode mentions are coded into eleven categories and counted by distinct source.

## The six cases from the mid-term progress report

All six cases are kept and were verified against the CGWB 2011 compilation (Ramtek, Warud, IIT Delhi), CSE 2014 (Goa University), the National Water Mission case sheet (BEL) and the Lok Sabha 2004 reply (Panjab University). Ratios were recomputed with one stated runoff coefficient and a stated rainfall basis; the Supplementary Information has the reconciliation table. Final ratios: Ramtek 11%, Warud 112%, Goa 76/28/19% (2010/2008/2009), BEL 64%, Panjab University 112%, IIT Delhi 82%.

## How to rebuild everything

Install the Python packages in requirements.txt (Python 3.10 or later) and a LaTeX distribution with pdflatex, then run `./run.sh` from this folder. It rebuilds the dataset, the statistics, all figures, the supplementary tables and the three PDFs in about two minutes. The presentation is rebuilt with `npm install` and `npm run build` inside the slides folder (Node 18 or later).

## Folders

- research: source extraction tables (one row per source record, each with its URL and the sentence or field values taken from the page) and verbatim extracts from the two CGWB documents. The codebook in the data folder explains every column.
- data: the harmonised dataset, the price-index series used for deflation, the screening log and the codebook.
- code: the Python scripts that rebuild the dataset, the statistics, the figures and the supplementary tables from the source extraction tables. Run them in that order with Python 3 (pandas, numpy, scipy, statsmodels, matplotlib); the report and supplementary are then compiled with pdflatex, and the deck with Node (pptxgenjs).
- figures: all figures as PNG and PDF.
- results: a summary of every number quoted in the report.
- report: the three PDFs (report, supplementary, supplementary with code appendix) and their LaTeX sources.
- slides: the presentation and the script that builds it.
