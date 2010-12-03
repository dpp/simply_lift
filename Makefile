RSYNCFLAGS = "-rv --delete"

all	: Simply_Lift.pdf

html	: Simply_Lift.tex Simply_Lift.aux 
	@echo [Building HTML]
	latex2html -split 3 -local_icons -no_antialias_text -no_antialias -white Simply_Lift.tex
	./highlightHtml.sh
	tar cvzf Simply_Lift.html.tgz Simply_Lift/

pdf	: Simply_Lift.pdf

Simply_Lift.pdf	: Simply_Lift.aux

Simply_Lift.tex	: *.lyx
	@echo [Exporting PDFLaTeX]
	@lyx -e pdflatex Simply_Lift.lyx

Simply_Lift.aux	: Simply_Lift.tex
	@echo [Building PDF]
	pdflatex Simply_Lift.tex
	makeindex Simply_Lift.idx
	@bash -c "while pdflatex Simply_Lift.tex && grep -q \"Rerun to get cross-references right\" Simply_Lift.log ; do echo \"  Rebuilding references\" ; done"
	@echo [Built PDF]

clean:
	rm -f *.tex images/*.eps *.toc *.aux *.dvi *.idx *.lof *.log *.out *.toc *.lol Simply_Lift.pdf
	rm -rf Simply_Lift/

#install: pdf html
#	rsync $(RSYNC_FLAGS) Simply_Lift.pdf Simply_Lift.html.tgz lion.harpoon.me:/home/scalatools/hudson/www/exploring/downloads/
#	rsync $(RSYNC_FLAGS) Simply_Lift/ lion.harpoon.me:/home/scalatools/hudson/www/exploring/Simply_Lift/
