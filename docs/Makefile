TEX=xelatex
TEX_FLAGS=

DRAWIO_BUILD_DIR=build/img
DRAWIO=~/.local/share/applications/drawio-x86_64-29.0.3.AppImage

DIAGRAMS :=
DIAGRAMS += $(DRAWIO_BUILD_DIR)/main_menu.png
DIAGRAMS += $(DRAWIO_BUILD_DIR)/scenarios.png
DIAGRAMS += $(DRAWIO_BUILD_DIR)/auth.png
DIAGRAMS += $(DRAWIO_BUILD_DIR)/queries_menu.png
DIAGRAMS += $(DRAWIO_BUILD_DIR)/query.png
DIAGRAMS += $(DRAWIO_BUILD_DIR)/report_add.png
DIAGRAMS += $(DRAWIO_BUILD_DIR)/report_view.png
DIAGRAMS += $(DRAWIO_BUILD_DIR)/cart_view.png

all: main.pdf

main.docx: main.tex
	pandoc main.tex -o main.docx

main.pdf: main.tex titlepage.tex img/db_infological_smaller.png $(DIAGRAMS)
	$(TEX) $(TEX_FLAGS) main.tex
	$(TEX) $(TEX_FLAGS) main.tex

$(DRAWIO_BUILD_DIR)/%.png: diagrams/%.drawio
	@mkdir -p $(DRAWIO_BUILD_DIR)
	$(DRAWIO) -x -f png -o $@ $<

clean:
	rm -f *.toc *.out *.aux *.bbl *.blg *.log main.pdf
