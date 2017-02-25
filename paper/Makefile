OBJECT = paper
LATEXMK = latexmk
LOG_DIR = /tmp/pdflatex
OBJECT_TEX = $(OBJECT).tex
OBJECT_PDF = $(OBJECT).pdf
CHART_TEX = $(CHART).tex
CHART_PDF = $(CHART).pdf

save: $(LOG_DIR)/$(OBJECT_PDF)
	mv $(LOG_DIR)/$(OBJECT_PDF) .

$(LOG_DIR)/$(OBJECT_PDF): $(OBJECT_TEX) $(LOG_DIR)
	$(LATEXMK) -shell-escape -outdir=$(LOG_DIR) -pdf $(OBJECT_TEX)

preview: $(OBJECT_TEX) $(LOG_DIR)
	$(LATEXMK) -shell-escape -outdir=$(LOG_DIR) -pvc -pdf $(OBJECT_TEX)

$(LOG_DIR):
	mkdir -p $(LOG_DIR)/charts

clean:
	$(LATEXMK) -c -outdir=$(LOG_DIR)
	$(LATEXMK) -c -outdir=$(LOG_DIR)/charts
	rm -f $(LOG_DIR)/*.bbl
