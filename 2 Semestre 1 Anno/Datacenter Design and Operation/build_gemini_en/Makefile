# Makefile per la compilazione del progetto LaTeX

PROJECT = main
TEX = tectonic
FLAGS = -X compile

all: pdf

pdf:
	$(TEX) $(FLAGS) $(PROJECT).tex

clean:
	rm -f *.aux *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.bbl *.blg
	rm -f capitoli/*.aux

cleanall: clean
	rm -f $(PROJECT).pdf

.PHONY: all pdf clean cleanall
