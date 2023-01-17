# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import re
from pygments.lexer import RegexLexer, using, bygroups
from pygments.token import Token
from pygments.lexers.data import JsonLexer
from sphinx.highlighting import lexers

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'SECoP'
copyright = '2023, ISSE'
author = 'ISSE'

root_doc = 'index'

# The full version, including alpha/beta/rc tags
release = '1.0'

# -- General configuration ---------------------------------------------------

highlight_language = 'secop'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.todo',
    'sphinx_design',
]

todo_include_todos = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

html_title = 'SECoP'
html_logo = 'spec/images/SECoP_logo.png'

html_additional_pages = {
    # Custom template for landing page
    #'landing': 'landing.html',
    #'': '',
}

html_theme = 'pydata_sphinx_theme'

html_css_files = [
    'custom.css',
]

html_theme_options = {
    #pydata_sphinx_theme
    'logo': {
        'image_light': 'SECoP_logo.png',
        'image_dark': 'SECoP_logo.png',
    },
    'footer_items': ['copyright'],
    'secondary_sidebar_items': ['page-toc', 'sourcelink'],
    #"announcement": "<em>Important</em> announcement!",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

class SECoPLexer(RegexLexer):
    name = 'secop'
    flags = re.MULTILINE

    tokens = {
        'root': [
            (r'(?:([><])( +))?(\w+)(?:( +)(\w+)(:\w+)?)?(?:( +)(.*?))?$',
             bygroups(
                 Token.Generic.Prompt,
                 Token.Whitespace,
                 Token.Keyword,
                 Token.Whitespace,
                 Token.String,
                 Token.Name,
                 Token.Whitespace,
                 using(JsonLexer)
             )),
            (r'\s+', Token.Whitespace),
        ]
    }

lexers['secop'] = SECoPLexer(startinline=True)

latex_documents = [
    ('spec/index', 'secop.tex', 'SECoP Specification', author, 'howto'),
]
