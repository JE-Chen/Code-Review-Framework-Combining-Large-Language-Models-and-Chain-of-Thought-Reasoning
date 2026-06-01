# Switch latexmk into XeLaTeX mode so the trilingual docs (English +
# Traditional Chinese + Simplified Chinese) render via xeCJK + Noto CJK
# instead of pdflatex (which has no CJK support out of the box). The
# matching preamble lives in docs/conf.py (latex_elements.preamble);
# the apt packages that provide xelatex and the fonts are pinned in
# .readthedocs.yaml (build.apt_packages).

$pdf_mode = 5;   # 5 = use xelatex to make the PDF
$xelatex = "xelatex -interaction=nonstopmode -halt-on-error %O %S";
