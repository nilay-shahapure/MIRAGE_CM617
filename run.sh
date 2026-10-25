#!/bin/sh
# Rebuilds the dataset, the statistics, the figures, the supplementary tables and the two PDFs.
set -e
python3 code/build_dataset.py
python3 code/analysis.py
python3 code/make_supplementary_tables.py
cd report
pdflatex -interaction=batchmode report.tex && pdflatex -interaction=batchmode report.tex
pdflatex -interaction=batchmode supplementary.tex && pdflatex -interaction=batchmode supplementary.tex
pdflatex -interaction=batchmode supplementary_with_code.tex && pdflatex -interaction=batchmode supplementary_with_code.tex
cp report.pdf MIRAGE_report.pdf; cp supplementary.pdf MIRAGE_supplementary.pdf; cp supplementary_with_code.pdf MIRAGE_supplementary_with_code.pdf
