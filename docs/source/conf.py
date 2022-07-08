# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('../config/system/run_utils'))

# -- Project information -----------------------------------------------------

project = 'ASCENT'
copyright = '2021, Duke University'
author = 'Musselman ED, Cariello JE, Grill WM, Pelot NA.'

# The full version, including alpha/beta/rc tags
release = 'v1.1.2'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = ['myst_parser',
              'sphinxarg.ext',
              'sphinx.ext.intersphinx',
              'sphinx.ext.autodoc',
              'sphinxcontrib.bibtex',
              'sphinxcontrib.details.directive',
              'sphinx_copybutton',
              'sphinx_rtd_dark_mode']

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'restructuredtext',
    '.md': 'markdown',
}

import mock

MOCK_MODULES = ['numpy', 'pandas']

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = mock.Mock()

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
# These folders are copied to the documentation's HTML output
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'details.css',
]
html_show_copyright = True

# no logo because doesn't look nice
# html_logo="uploads/ascent_media_release_v2.png"

html_show_sphinx = False

myst_heading_anchors = 4

bibtex_bibfiles = ['refs.bib']

bibtex_reference_style = 'author_year'

default_dark_mode = False
