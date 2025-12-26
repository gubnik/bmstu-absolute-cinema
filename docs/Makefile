TEX=xelatex
TEX_FLAGS=

DRAWIO_BUILD_DIR=build/img
DRAWIO=~/.local/share/applications/drawio-x86_64-29.0.3.AppImage

all: main.pdf

main.docx: main.tex
	pandoc main.tex -o main.docx

main.pdf: main.tex $(DRAWIO_BUILD_DIR)/main_menu.png $(DRAWIO_BUILD_DIR)/scenarios.png
	$(TEX) $(TEX_FLAGS) main.tex
	$(TEX) $(TEX_FLAGS) main.tex

$(DRAWIO_BUILD_DIR)/%.png: diagrams/%.drawio
	@mkdir -p $(DRAWIO_BUILD_DIR)
	$(DRAWIO) -x -f png -o $@ $<

clean:
	rm -f *.toc *.out *.aux *.bbl *.blg *.log main.pdf
