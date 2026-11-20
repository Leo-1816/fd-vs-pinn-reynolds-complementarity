"""Sphinx configuration of the PRI report.

Build (clean build, recommended):
    rm -rf report/_build && uv run sphinx-build -b html report report/_build/html
open report/_build/html/index.html

"""

project = "FD vs PINN: the Reynolds equation with complementarity"
author = "Leonard von Fabeck"
language = "en"

extensions = [
    "sphinx.ext.mathjax",  # LaTeX equations (.. math::, :math:)
    "matplotlib.sphinxext.plot_directive",  # .. plot:: runs a script from figures/
    "sphinxcontrib.bibtex",  # bibliography: :cite:p:`key`, :cite:t:`key`
]

exclude_patterns = ["_build"]

# Bibliography (references.bib), author-year citations
bibtex_bibfiles = ["references.bib"]
bibtex_reference_style = "author_year"
bibtex_default_style = "plain"

# Numbering of figures and equations (:numref:, :eq:)
numfig = True
math_numfig = True
math_eqref_format = "({number})"

# Figures linked to the code: each .. plot:: runs its script from figures/ at
# build time. No image is versioned: images only exist in _build.
plot_include_source = False
plot_html_show_source_link = False
plot_html_show_formats = False
plot_formats = [("png", 150), "pdf"]  # png for HTML, pdf for a future LaTeX export

# Single-figure template. The matplotlib template creates one HTML figure and one
# hidden "not html" figure, and Sphinx numbers both (Fig. 1.1, then 1.3).
# With ".*", Sphinx picks the right format for the output by itself.
# (The "only" block is only there for indentation: matplotlib pre-indents the
# caption by one nesting level.)
plot_template = """
.. only:: html or not html

   {% for img in images %}
   .. figure:: {{ build_dir }}/{{ img.basename }}.*
      {% for option in options -%}
      {{ option }}
      {% endfor %}

      {{ caption }}
   {% endfor %}
"""

html_theme = "furo"
html_title = "PRI report: FD vs PINN"
