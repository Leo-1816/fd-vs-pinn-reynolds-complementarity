"""Configuration Sphinx du rapport PRI.

Compiler (build propre, recommandé) :
    rm -rf report/_build && uv run sphinx-build -b html report report/_build/html
open report/_build/html/index.html

"""

project = "FD vs PINN : équation de Reynolds avec complémentarité"
author = "Leonard von Fabeck"
language = "fr"

extensions = [
    "sphinx.ext.mathjax",  # équations LaTeX (.. math::, :math:)
    "matplotlib.sphinxext.plot_directive",  # .. plot:: exécute un script de figures/
    "sphinxcontrib.bibtex",  # bibliographie : :cite:p:`cle`, :cite:t:`cle`
]

exclude_patterns = ["_build"]

# Bibliographie (references.bib), citations auteur-année
bibtex_bibfiles = ["references.bib"]
bibtex_reference_style = "author_year"
bibtex_default_style = "plain"

# Numérotation des figures et des équations (:numref:, :eq:)
numfig = True
math_numfig = True
math_eqref_format = "({number})"

# Figures reliées au code : chaque .. plot:: exécute le script de figures/ à la
# compilation. Aucune image n'est versionnée, elles n'existent que dans _build.
plot_include_source = False
plot_html_show_source_link = False
plot_html_show_formats = False
plot_formats = [("png", 150), "pdf"]  # png pour le HTML, pdf pour le futur export LaTeX

# Gabarit à une seule figure : celui de matplotlib crée une figure HTML et une
# figure cachée « not html », et Sphinx numérote les deux (Fig. 1.1 puis 1.3).
# Avec « .* », Sphinx choisit lui-même le bon format selon la sortie.
# (Le bloc « only » sert seulement à indenter : matplotlib pré-indente la
# légende pour un niveau d'imbrication.)
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
html_title = "Rapport PRI : FD vs PINN"
